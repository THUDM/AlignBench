import argparse
import pandas as pd
import jsonlines
import numpy as np
import os

CATEGORIES = {
    "中文语言": ["基本任务", "中文理解", "综合问答", "文本写作", "角色扮演", "专业能力"],
    "中文推理": ["数学计算", "逻辑推理"]
}

def load_category_map(filename):
    qids = {}
    with jsonlines.open(filename, "r") as f:
        for doc in f:
            qids[doc["question_id"]] = doc["category"]
        f.close()
    return qids

def main(args):
    if args.input_dir is None:
        input_dir = "data/judgment"
    else:
        input_dir = args.input_dir
    
    input_files = os.listdir(input_dir)
    input_files = [os.path.join(input_dir, file) for file in input_files if file.endswith(".jsonl")]

    print(f"{len(input_files)} Input files: ", input_files)
    df_all = pd.concat([pd.read_json(input_file, lines=True) for input_file in input_files])

    # create file
    os.makedirs(os.path.dirname(args.save_file), exist_ok=True)

    categories = load_category_map(args.ques_file)
    splits = list(set(categories.values()))
    splits.sort()
    print("> loaded split: ", splits)
    total = {}
    for _, line in df_all.iterrows():
        cat = categories[line["question_id"]]
        model = line["model_id"]
        if model not in total:
            total[model] = {split:[] for split in splits}
        total[model][cat].append(line["score"])

    class_df = []
    for model in total.keys():  
        model_info = [model]
        for split in splits:
            model_info.append(np.mean(total[model][split]))
        reasoning_score = np.mean([np.mean(total[model][cat]) for cat in CATEGORIES["中文推理"]])
        language_score = np.mean([np.mean(total[model][cat]) for cat in CATEGORIES["中文语言"]])
        overall_score = (reasoning_score + language_score) / 2
        model_info.extend([reasoning_score, language_score, overall_score])
        class_df.append(model_info)
    
    columns = ["模型"] + splits + ["中文推理", "中文语言", "总分"]
    class_df = pd.DataFrame(class_df, columns=columns)
    class_df = class_df.sort_values(by="总分", ascending=False)
    print("\n########## AlignBench Results ##########")
    print(class_df)
    class_df.to_excel(args.save_file)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--save-file", type=str, default="data/results/results.xlsx")
    parser.add_argument("--input-dir", type=str)
    parser.add_argument("--ques-file", type=str)
    args = parser.parse_args()

    main(args)
