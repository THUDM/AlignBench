import argparse
import jsonlines
import os
import json
from inference.models import get_model_api
from inference.utils import test_api_alive

if __name__ == '__main__':
    """
    singleround inference 
    input question doc format:
        question_doc = {
            "question_id": int,
            "category": str,
            "subcategory": str,
            "question": str,
        }
    output answer file format
         {
            "question_id": int,
            "category": str,
            "subcategory": str,
            "model_id": str,
            "question": str,
            "answer": str
        }
    """
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", type=str, help="Evaluated Model Name")
    parser.add_argument("--repredict", type=bool, default=True, help="Repredict When Encounter Empty Answers")
    parser.add_argument("--workers", type=int)
    parser.add_argument("--question-file", type=str)
    parser.add_argument("--save-dir", type=str)
    parser.add_argument("--temperature-config-file", type=str, default="config/temperature.json", help="Temperature Config")
    parser.add_argument("--first-n", type=int, help="Debug Option")
    args = parser.parse_args()

    ## test api status
    print(">>> testing whether the api is alive ...")
    res = test_api_alive(args.model)
    if res:
        print(f">>> api {args.model} is alive")

    model = get_model_api(args.model, args.workers)
    print(">>> inference model: ", args.model)
    
    ## load questions
    docs = []
    with jsonlines.open(args.question_file, "r") as f:
        for doc in f:
            docs.append(doc)
        f.close()

    if args.first_n:
        docs = docs[: args.first_n]
    print(f">>> running {len(docs)} docs")

    ## load temperature configs
    with open(args.temperature_config_file, "r") as f:
        temp_config = json.loads(f.read())
        temp_config["default"] = 0.7
        f.close()

    ## use subcategory to get temperature for each sample
    samples = []
    for doc in docs:
        if doc.get("category", None) not in temp_config:
            print(">>> warning: category not in temp_config, category: ", doc.get("category", None))
        samples.append({
            "question": doc["question"],
            "temperature": temp_config.get(doc["category"], temp_config["default"])
        })
    outputs = model.generate_text(samples)

    if args.repredict:
        for process in range(3):
            empty_ids = []
            empty_samples = []
            for index, output in enumerate(outputs):
                if output is None or output == "":
                    empty_samples.append(samples[index])
                    empty_ids.append(index)
            if len(empty_samples) == 0:
                print(">>> no empty outputs, inference finished")
                break
            print(f">>> repredicting empty {len(empty_ids)} docs in repredict process {process} / 3")

            empty_outputs = model.generate_text(empty_samples)
            for index, output in zip(empty_ids, empty_outputs):
                if output is not None and output != "":
                    outputs[index] = output

    os.makedirs(args.save_dir, exist_ok=True)
    save_path = os.path.join(args.save_dir, f"{args.model}.jsonl")
    with jsonlines.open(save_path, 'w') as f:
        for doc, output in zip(docs, outputs):
            doc["model_id"] = args.model
            doc["answer_id"] = str(doc["question_id"]) + "_" + args.model
            if output is not None:
                doc["answer"] = output
            else:
                doc["answer"] = None
            f.write(doc)
        f.close()
        