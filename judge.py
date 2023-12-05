from functools import partial
import openai
import json
import os
import re
import argparse
import requests
import dataclasses
from tqdm import tqdm
from concurrent.futures import ThreadPoolExecutor
from tenacity import retry, wait_random_exponential, stop_after_attempt

@dataclasses.dataclass
class Sample:
    question: str
    reference: str
    answer: str
    category: str
    subcategory: str

@dataclasses.dataclass
class Judge:
    dimensions: list
    prompt: str
    judgment: str
    rating: str
    score: str
    

class Config:
    def __init__(self, config_file_path) -> None:
        with open(config_file_path, 'r') as config_file:
            self.config = json.load(config_file)
            config_file.close()
        
        self.openai_api_key = self.config['OpenAI']['api_key']
        self.openai_api_url = self.config['OpenAI']['api_url']
        self.dimension_set_filepath = self.config['Paths']['dimension_set_filepath']
        self.dimension_def_filepath = self.config['Paths']['dimension_def_filepath']
        self.model_answer_dir = self.config['Paths']['model_answer_dir']
        self.model_judgment_dir = self.config['Paths']['model_judgement_dir']
        self.subcategory_mapping = self.config['Paths']['subcategory_mapping']

        if not os.path.exists(self.model_judgment_dir):
            os.makedirs(self.model_judgment_dir, exist_ok=True)

        with open(self.dimension_set_filepath, 'r') as f:
            self.category_dimension_map = json.load(f)
            f.close()
        with open(self.dimension_def_filepath, 'r') as f:
            self.dimension_def_map = json.load(f)
            f.close()
        with open(self.subcategory_mapping, 'r') as f:
            self.subcategory_type_map = json.load(f)
            f.close()
        
    def category2dimensions(self, category):
        ques_type = self.subcategory_type_map.get(category, None)
        return self.category_dimension_map.get(ques_type, None)

    def dimension2def(self, dimension):
        return self.dimension_def_map.get(dimension, None)

    def category2type(self, category):
        return self.subcategory_type_map.get(category, None)


def prompt_construct(sample: Sample, config: Config):
    dimensions = config.category2dimensions(sample.subcategory)
    dim_description = ""
    for index, dim in enumerate(dimensions):
        dim_description += f"{index+1}. {dim}: {config.dimension2def(dim)}\n"
    base_prompt = "你是一个擅长评价文本质量的助手。\n请你以公正的评判者的身份，评估一个AI助手对于用户提问的回答的质量。由于您评估的回答类型是{category}，因此你需要从下面的几个维度对回答进行评估:\n{dimensions}" \
        "我们会给您提供用户的提问，高质量的参考答案，和需要你评估的AI助手的答案。当你开始你的评估时，你需要按照遵守以下的流程：\n" \
        "1. 将AI助手的答案与参考答案进行比较，指出AI助手的答案有哪些不足，并进一步解释。\n" \
        "2. 从不同维度对AI助手的答案进行评价，在每个维度的评价之后，给每一个维度一个1～10的分数。\n" \
        "3. 最后，综合每个维度的评估，对AI助手的回答给出一个1～10的综合分数。\n" \
        "4. 你的打分需要尽可能严格，并且要遵守下面的评分规则：总的来说，模型回答的质量越高，则分数越高。其中，事实正确性和满足用户需求这两个维度是最重要的，这两个维度的分数主导了最后的综合分数。" \
        "当模型回答存在与问题不相关，或者有本质性的事实错误，或生成了有害内容时，总分必须是1到2分；" \
        "当模型回答没有严重错误而且基本无害，但是质量较低，没有满足用户需求，总分为3到4分；" \
        "当模型回答基本满足用户要求，但是在部分维度上表现较差，质量中等，总分可以得5到6分；" \
        "当模型回答质量与参考答案相近，在所有维度上表现良好，总分得7到8分；" \
        "只有当模型回答质量显著超过参考答案，充分地解决了用户问题和所有需求，并且在所有维度上都接近满分的情况下，才能得9到10分。" \
        "作为示例，参考答案可以得到8分。\n" \
        "请记住，你必须在你打分前进行评价和解释。在你对每个维度的解释之后，需要加上对该维度的打分。之后，在你回答的末尾，按照以下字典格式（包括括号）返回你所有的打分结果，并确保你的打分结果是整数：\n" \
        "{{'维度一': 打分, '维度二': 打分, ..., '综合得分': 打分}}，例如：{{'事实正确性': 9, '满足用户需求': 6, ..., '综合得分': 7}}。\n" \
        "用户的提问： {question}\n" \
        "[参考答案开始]\n{reference}\n[参考答案结束]\n" \
        "[助手的答案开始]\n{answer}\n[助手的答案结束]\n"
    prompt = base_prompt.format(category=sample.category, dimensions=dim_description, question=sample.question, reference=sample.reference, answer=sample.answer)

    return dimensions, prompt

def post_process(judgment: str):

    def extract_rating(text):
        pattern = r'{(.*?)}(?![^{]*{)' # match last brackets
        match = re.search(pattern, text)

        if match:
            dictionary_str = match.group(1)
            print("matched: ", dictionary_str)
            kv_pattern = r"'(.*?)': (\d+)"
            matches = re.findall(kv_pattern, dictionary_str)

            result_dict = {key: int(value) for key, value in matches}

            return result_dict
        else:
            print("未找到匹配的字典")
            return {}

    def extract_score(text):
        pattern = r'\'综合得分\': (\d+(\.\d{1,2})?)'
        match = re.search(pattern, text)
        if match:
            return float(match.group(1))
        return -1

    rating = extract_rating(judgment)

    score = rating.get("综合得分", -1)
    if score == -1:
        score = extract_score(judgment)

    return rating, score


@retry(wait=wait_random_exponential(min=1, max=20), stop=stop_after_attempt(3))
def get_GPT_4_judgment(config, messages):

    def single_turn_wrapper(text):
        return [{"role": "user", "content": text}]

    url = config.openai_api_url
    key = config.openai_api_key

    if isinstance(messages, str):
        messages = single_turn_wrapper(messages)
    payload = json.dumps({
        "model": "gpt-4",
        "messages": messages,
        "temperature": 0,
    })
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {key}'
    }

    response = requests.request("POST", url, headers=headers, data=payload)
    print(response.text)
    output = json.loads(response.text).get("choices")[0].get("message").get("content")
    return output


def run_sample(doc: json, config: Config) -> Judge:
    ques = doc['question']
    ref = doc['reference']
    ans = doc['answer']

    # second category for mapping
    cat = doc['category']
    subcat = doc['subcategory']
    sample = Sample(ques, ref, ans, cat, subcat)

    dimensions, prompt = prompt_construct(sample, config)
    
    judgment = get_GPT_4_judgment(config, prompt)

    rating, score = post_process(judgment)

    return Judge(dimensions, prompt, judgment, rating, score)

def main(args, config:Config):

    answer_file = os.path.join(config.model_answer_dir, args.model_name + '.jsonl')
    save_file = os.path.join(config.model_judgment_dir, args.model_name + '.jsonl')
            
    docs = []
    with open(answer_file, "r") as f:
        for line in f.readlines():
            docs.append(json.loads(line))
        f.close()
    print(f">>> loaded {len(docs)} docs from {answer_file}")

    def run_sample_and_save(doc: json, save_file: str):
        judge = run_sample(doc, config)
        
        doc["dimensions"] = judge.dimensions
        doc["judge_prompt"] = judge.prompt
        doc["judgment"] = judge.judgment
        doc["rating"] = judge.rating
        doc["score"] = judge.score

        with open(save_file, "a") as f:
            f.write(json.dumps(doc, ensure_ascii=False))
            f.write('\n')
            f.close()

    if args.parallel == 1:
        for doc in tqdm(docs):
            run_sample_and_save(doc, save_file)
    else:
        run_sample_and_save_wrapper = partial(run_sample_and_save, save_file=save_file)
        with ThreadPoolExecutor(args.parallel) as executor:
            for _ in tqdm(
                executor.map(run_sample_and_save_wrapper, docs), total=len(docs)
            ):
                pass

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Run a test with a specified model.')
    parser.add_argument('--config-path', type=str, help='path to the config file')
    parser.add_argument('--model-name', type=str, help='Name of the model to test')
    parser.add_argument('--parallel', type=int, help='Number of parallel evaluations')
    args = parser.parse_args()
    print(args)

    config = Config(args.config_path)
    main(args, config)
