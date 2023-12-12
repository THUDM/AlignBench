# AlignBench: Benchmarking Chinese Alignment of Large Language Models

阅读[中文](README.md)版

This repository contains information, data and code of AlignBench: a comprehensive multi-dimensional benchmark for evaluating LLMs’ alignment in Chinese.

## 🔥 Updates

[2023.12.12] AlignBench [Website](https://llmbench.ai/align) is now officially online, welcome everyone to visit! You can use the *Submit* function on the website to perform evaluation with `CritiqueLLM` on AlignBench (results can be obtained in about 5 minutes).

## 📍 Introduction

Alignment has become the critical step for instruction-tuned Large Language Models (LLMs) to become helpful assistants. However, effective evaluation of alignment for emerging Chinese LLMs has become a significant challenge, calling for diverse, open-ended, challenging and automatic evaluation tailored for alignment. To address this, we introduce AlignBench, a comprehensive multi-dimensional benchmark for evaluating LLMs’ alignment in Chinese. Equipped with a human-in-the-loop data curation pipeline, our benchmark employs a multi-dimensional rules-calibrated LLM-as-Judge with Chain-of-Thought to generate an explanation and a final rating, ensuring high reliability and interpretability. Furthermore, we developed a dedicated accompanied evaluator LLM---CritiqueLLM, which could recover 95% of GPT-4's evaluation ability and will be provided via accessible APIs to researchers for convenient evaluation of Chinese alignment.

![Overall](assets/Overall.png)

The overall framework of AlignBench is shown in the above image, including the data curation pipeline, the task taxonomy and the multi-dimensional rule-calibrated LLM-as-Judge evaluation method.

For a full description of AlignBench, please refer to the paper: [AlignBench](https://arxiv.org/abs/2311.18743)

For a full description of CritiqueLLM, please refer to the paper: [CritiqueLLM](https://arxiv.org/abs/2311.18702)


---

## 📦 Dataset

To perform a systematic evaluation, we framed a comprehensive taxonomy of the LLMs’ abilities based on the real-user instructions. We inspect and summarize user queries into 8 main categories, namely Fundamental Language Ability, Chinese Advanced Understanding, Open-ended Questions, Writing Ability, Logical Reasoning, Mathematics, Task-oriented Role Play. The taxonomy and distribution of AlignBench are as follows.

|            Category            |  中文名  | #Samples |
| :----------------------------: | :------: | :------: |
|  Fundamental Language Ability  | 基本任务 |    68    |
| Advanced Chinese Understanding | 中文理解 |    58    |
|      Open-ended Questions      | 综合问答 |    38    |
|        Writing Ability         | 文本写作 |    75    |
|       Logical Reasoning        | 逻辑推理 |    92    |
|          Mathematics           | 数学计算 |   112    |
|    Task-oriented Role Play     | 角色扮演 |   116    |
|     Professional Knowledge     | 专业能力 |   124    |

AlignBench contains 683 high-quality samples in total. Each sample in AlignBench contains a task-oriented query, a high-quality reference answer, and the corresponding category in our taxonomy. The data is placed in `data/data_release.jsonl` and each line contains a sample in `json` format. 

The data format is as follows.

- `question_id` (integer): A unique identifier for the question.
- `category` (string): The primary category under which the question falls.
- `subcategory` (string): The secondary category for further classification. 
- `question` (string): The actual user query. 
- `reference` (string): This provides a reference or standard answer to the question. 

Here is an example of `mathematics` category.

```json
{
    "question_id": 1,
    "category": "数学计算",
    "subcategory": "初等数学",
    "question": "有一串彩珠，按“2红3绿4黄”的顺序依次排列。第600颗是什么颜色?",
    "reference": "一组\"2红3绿4黄\"共有9颗珠子。600除以9的商是66，余数是6。因此，第600颗珠子是在第67组的第6颗，即\"2红3绿4黄\"中的第6颗，也就是黄色。所以，第600颗珠子是黄色。"
}
```

---

## ⚙️ Evaluation Pipeline

In order to effectively evaluate the quality of responses, AlignBench currently employs GPT-4-0613 to analyze and subsequently grade the responses. During the evaluation process, the input is the user query, the model's response, and a high-quality reference answer, and the output is an multi-dimensional analytical explanation and a final rating, ranging from 1 to 10. In order to ensure reliability and interpretability, we implement the following methods. Here is an example.

![Case](assets/Case.png)

* **Point-wise Grading.** For each model answer, the evaluation methods will give a final rating ranging from 1 to 10.

* **Chain-of-Thought.** As the task of grading involves complex reasoning, we have adopted the Chain-of-Thought method to augment both the reliability and interpretability. Specifically, the evaluator LLM is instructed to generate explanations from multiple dimensions before providing a final rating.

+ **Rule-calibrated Referencing.** For each question, we provide a high-quality reference answer. To guide the evaluator to compare the answer with the reference and generate more controllable scores, we provided detailed grading rules elaborating the relationship between score intervals and the answer's quality compared to the reference. The rules are included in the prompt.

* **Multi-dimensional Analysis.** Because tasks vary in their nature and characteristics, applying the same evaluation criteria to all tasks would be unjust. As a solution, we suggest employing a multi-dimensional scoring approach to evaluate LLM's responses, tailoring the evaluation to the specific task at hand. Specifically, we set up different evaluation dimensions based on different types of questions and we instructed GPT-4 evaluator to analyze the model answer from specified dimensions and provide dimensional scores. The dimensions and their definitions are placed in `config`.


---

## 🚀 Evaluation

The whole evaluation process contains three steps: inference, LLM judgments and results display. The corresponding scripts are saved in `scripts`

1. **Step I** inference on target LLM and get the results

   First, you need to deploy your target LLM.(This part is not included in this repository). 

   Second, implement your own API calling class in `inference/api_models`, the `do_nothing` class sevres as an example. (Note that the API class name should be the same as the file name)

   Third, modify and run the following script to get the answers of the target LLM.

   ```bash
   MODEL=do_nothing # TODO modify the model name(the same as your API calling class)
   
   python get_answers.py \
       --model do_nothing \
       --workers 2 \
       --question-file data/data_release.jsonl \
       --save-dir data/model_answer
   ```

   The answers will be saved in `data/model_answer` and ready for the LLM Judge process.

2. **Step II** get the GPT-4 judgments

   First, fill in your GPT-4 API key in `config/multi-dimension.json`.

   Then, modify and run the following script to get the judgments of the target LLM.

   ```bash
   MODEL=do_nothing # TODO modify the model name(the same as your API calling class)
   
   python judge.py \
       --config-path config/multi-dimension.json \
       --model-name $MODEL \
       --parallel 2 \
   ```

   The answers will be stored in `data/jugdment`

3. **Step III** results display

   Run the following script to get the results of all the LLM judgments saved in `data/judgment`.

   ```bash
   python show_result.py \
       --input-dir data/judgment \
       --ques-file data/data_release.jsonl \
       --save-file data/results/results.xlsx
   ```

   The calulated resultss will be stored in `data/results` in `xlsx` format.

---

## 📂 Leaderboard

We report our evaluation results on 17 Chinese-supported LLMs on AlignBench using `gpt-4-0613` and `CritiqueLLM`. 

`gpt-4-0613` judged results:

<table class="tg">
<thead>
  <tr>
    <td class="tg-nrix" rowspan="2">model</td>
    <td class="tg-nrix" rowspan="2">Overall</td>
    <th class="tg-nrix" colspan="3">Reasoning 中文推理</th>
    <th class="tg-nrix" colspan="7">Language 中文语言</th>
  </tr>
  <tr>
    <th class="tg-nrix">Avg.</th>
    <th class="tg-nrix">Math.</th>
    <th class="tg-nrix">Logi.</th>
    <th class="tg-nrix">Avg.</th>
    <th class="tg-nrix">Fund.</th>
    <th class="tg-nrix">Chi.</th>
    <th class="tg-nrix">Open.</th>
    <th class="tg-nrix">Writ.</th>
    <th class="tg-nrix">Role.</th>
    <th class="tg-nrix">Pro.</th>
  </tr>
</thead>
<tbody>
  <tr>
    <td class="tg-nrix">模型</td>
    <td class="tg-nrix">总分</td>
    <td class="tg-nrix">推理<br>总分</td>
    <td class="tg-nrix">数学<br>计算</td>
    <td class="tg-nrix">逻辑<br>推理</td>
    <td class="tg-nrix">语言<br>总分</td>
    <td class="tg-nrix">基本<br>任务</td>
    <td class="tg-nrix">中文<br>理解</td>
    <td class="tg-nrix">综合<br>问答</td>
    <td class="tg-nrix">文本<br>写作</td>
    <td class="tg-nrix">角色<br>扮演</td>
    <td class="tg-nrix">专业<br>能力</td>
  </tr>
  <tr>
    <td class="tg-nrix">gpt-4-1106-preview</td>
    <td class="tg-wa1i">8.01</td>
    <td class="tg-wa1i">7.73</td>
    <td class="tg-wa1i">7.8</td>
    <td class="tg-wa1i">7.66</td>
    <td class="tg-wa1i">8.29</td>
    <td class="tg-wa1i">7.99</td>
    <td class="tg-nrix">7.33</td>
    <td class="tg-wa1i">8.61</td>
    <td class="tg-wa1i">8.67</td>
    <td class="tg-wa1i">8.47</td>
    <td class="tg-wa1i">8.65</td>
  </tr>
  <tr>
    <td class="tg-nrix">gpt-4-0613</td>
    <td class="tg-wa1i">7.53</td>
    <td class="tg-nrix">7.47</td>
    <td class="tg-nrix">7.56</td>
    <td class="tg-nrix">7.37</td>
    <td class="tg-nrix">7.59</td>
    <td class="tg-nrix">7.81</td>
    <td class="tg-nrix">6.93</td>
    <td class="tg-nrix">7.42</td>
    <td class="tg-nrix">7.93</td>
    <td class="tg-nrix">7.51</td>
    <td class="tg-nrix">7.94</td>
  </tr>
  <tr>
    <td class="tg-nrix">chatglm-turbo（智谱清言）</td>
    <td class="tg-wa1i">6.24</td>
    <td class="tg-nrix">5</td>
    <td class="tg-nrix">4.74</td>
    <td class="tg-nrix">5.26</td>
    <td class="tg-nrix">7.49</td>
    <td class="tg-nrix">6.82</td>
    <td class="tg-nrix">7.17</td>
    <td class="tg-nrix">8.16</td>
    <td class="tg-nrix">7.77</td>
    <td class="tg-nrix">7.76</td>
    <td class="tg-nrix">7.24</td>
  </tr>
  <tr>
    <td class="tg-nrix">erniebot-3.0（文心一言）</td>
    <td class="tg-wa1i">6.14</td>
    <td class="tg-nrix">5.15</td>
    <td class="tg-nrix">5.03</td>
    <td class="tg-nrix">5.27</td>
    <td class="tg-nrix">7.13</td>
    <td class="tg-nrix">6.62</td>
    <td class="tg-wa1i">7.6</td>
    <td class="tg-nrix">7.26</td>
    <td class="tg-nrix">7.56</td>
    <td class="tg-nrix">6.83</td>
    <td class="tg-nrix">6.9</td>
  </tr>
  <tr>
    <td class="tg-nrix">gpt-3.5-turbo-0613</td>
    <td class="tg-wa1i">6.08</td>
    <td class="tg-nrix">5.35</td>
    <td class="tg-nrix">5.68</td>
    <td class="tg-nrix">5.02</td>
    <td class="tg-nrix">6.82</td>
    <td class="tg-nrix">6.71</td>
    <td class="tg-nrix">5.81</td>
    <td class="tg-nrix">7.29</td>
    <td class="tg-nrix">7.03</td>
    <td class="tg-nrix">7.28</td>
    <td class="tg-nrix">6.77</td>
  </tr>
  <tr>
    <td class="tg-nrix">chatglm-pro（智谱清言）</td>
    <td class="tg-wa1i">5.83</td>
    <td class="tg-nrix">4.65</td>
    <td class="tg-nrix">4.54</td>
    <td class="tg-nrix">4.75</td>
    <td class="tg-nrix">7.01</td>
    <td class="tg-nrix">6.51</td>
    <td class="tg-nrix">6.76</td>
    <td class="tg-nrix">7.47</td>
    <td class="tg-nrix">7.07</td>
    <td class="tg-nrix">7.34</td>
    <td class="tg-nrix">6.89</td>
  </tr>
  <tr>
    <td class="tg-nrix">spark_desk_v2（讯飞星火）</td>
    <td class="tg-wa1i">5.74</td>
    <td class="tg-nrix">4.73</td>
    <td class="tg-nrix">4.71</td>
    <td class="tg-nrix">4.74</td>
    <td class="tg-nrix">6.76</td>
    <td class="tg-nrix">5.84</td>
    <td class="tg-nrix">6.97</td>
    <td class="tg-nrix">7.29</td>
    <td class="tg-nrix">7.18</td>
    <td class="tg-nrix">6.92</td>
    <td class="tg-nrix">6.34</td>
  </tr>
  <tr>
    <td class="tg-nrix">qwen-14b-chat</td>
    <td class="tg-wa1i">5.72</td>
    <td class="tg-nrix">4.81</td>
    <td class="tg-nrix">4.91</td>
    <td class="tg-nrix">4.71</td>
    <td class="tg-nrix">6.63</td>
    <td class="tg-nrix">6.9</td>
    <td class="tg-nrix">6.36</td>
    <td class="tg-nrix">6.74</td>
    <td class="tg-nrix">6.64</td>
    <td class="tg-nrix">6.59</td>
    <td class="tg-nrix">6.56</td>
  </tr>
  <tr>
    <td class="tg-nrix">baichuan2-13b-chat</td>
    <td class="tg-wa1i">5.25</td>
    <td class="tg-nrix">3.92</td>
    <td class="tg-nrix">3.76</td>
    <td class="tg-nrix">4.07</td>
    <td class="tg-nrix">6.59</td>
    <td class="tg-nrix">6.22</td>
    <td class="tg-nrix">6.05</td>
    <td class="tg-nrix">7.11</td>
    <td class="tg-nrix">6.97</td>
    <td class="tg-nrix">6.75</td>
    <td class="tg-nrix">6.43</td>
  </tr>
  <tr>
    <td class="tg-nrix">chatglm3-6b</td>
    <td class="tg-wa1i">4.97</td>
    <td class="tg-nrix">3.85</td>
    <td class="tg-nrix">3.55</td>
    <td class="tg-nrix">4.14</td>
    <td class="tg-nrix">6.1</td>
    <td class="tg-nrix">5.75</td>
    <td class="tg-nrix">5.29</td>
    <td class="tg-nrix">6.71</td>
    <td class="tg-nrix">6.83</td>
    <td class="tg-nrix">6.28</td>
    <td class="tg-nrix">5.73</td>
  </tr>
  <tr>
    <td class="tg-nrix">baichuan2-7b-chat</td>
    <td class="tg-wa1i">4.97</td>
    <td class="tg-nrix">3.66</td>
    <td class="tg-nrix">3.56</td>
    <td class="tg-nrix">3.75</td>
    <td class="tg-nrix">6.28</td>
    <td class="tg-nrix">5.81</td>
    <td class="tg-nrix">5.5</td>
    <td class="tg-nrix">7.13</td>
    <td class="tg-nrix">6.84</td>
    <td class="tg-nrix">6.53</td>
    <td class="tg-nrix">5.84</td>
  </tr>
  <tr>
    <td class="tg-nrix">internlm-20b</td>
    <td class="tg-wa1i">4.96</td>
    <td class="tg-nrix">3.66</td>
    <td class="tg-nrix">3.39</td>
    <td class="tg-nrix">3.92</td>
    <td class="tg-nrix">6.26</td>
    <td class="tg-nrix">5.96</td>
    <td class="tg-nrix">5.5</td>
    <td class="tg-nrix">7.18</td>
    <td class="tg-nrix">6.19</td>
    <td class="tg-nrix">6.49</td>
    <td class="tg-nrix">6.22</td>
  </tr>
  <tr>
    <td class="tg-nrix">qwen-7b-chat</td>
    <td class="tg-wa1i">4.91</td>
    <td class="tg-nrix">3.73</td>
    <td class="tg-nrix">3.62</td>
    <td class="tg-nrix">3.83</td>
    <td class="tg-nrix">6.09</td>
    <td class="tg-nrix">6.4</td>
    <td class="tg-nrix">5.74</td>
    <td class="tg-nrix">6.26</td>
    <td class="tg-nrix">6.31</td>
    <td class="tg-nrix">6.19</td>
    <td class="tg-nrix">5.66</td>
  </tr>
  <tr>
    <td class="tg-nrix">chatglm2-6b</td>
    <td class="tg-wa1i">4.48</td>
    <td class="tg-nrix">3.39</td>
    <td class="tg-nrix">3.16</td>
    <td class="tg-nrix">3.61</td>
    <td class="tg-nrix">5.58</td>
    <td class="tg-nrix">4.91</td>
    <td class="tg-nrix">4.52</td>
    <td class="tg-nrix">6.66</td>
    <td class="tg-nrix">6.25</td>
    <td class="tg-nrix">6.08</td>
    <td class="tg-nrix">5.08</td>
  </tr>
  <tr>
    <td class="tg-nrix">internlm-chat-7b</td>
    <td class="tg-wa1i">3.65</td>
    <td class="tg-nrix">2.56</td>
    <td class="tg-nrix">2.45</td>
    <td class="tg-nrix">2.66</td>
    <td class="tg-nrix">4.75</td>
    <td class="tg-nrix">4.34</td>
    <td class="tg-nrix">4.09</td>
    <td class="tg-nrix">5.82</td>
    <td class="tg-nrix">4.89</td>
    <td class="tg-nrix">5.32</td>
    <td class="tg-nrix">4.06</td>
  </tr>
  <tr>
    <td class="tg-nrix">Chinese-llama-2-7b-chat</td>
    <td class="tg-wa1i">3.57</td>
    <td class="tg-nrix">2.68</td>
    <td class="tg-nrix">2.29</td>
    <td class="tg-nrix">3.07</td>
    <td class="tg-nrix">4.46</td>
    <td class="tg-nrix">4.31</td>
    <td class="tg-nrix">4.26</td>
    <td class="tg-nrix">4.5</td>
    <td class="tg-nrix">4.63</td>
    <td class="tg-nrix">4.91</td>
    <td class="tg-nrix">4.13</td>
  </tr>
  <tr>
    <td class="tg-nrix">llama-2-13b-Chinese-chat</td>
    <td class="tg-wa1i">3.35</td>
    <td class="tg-nrix">2.47</td>
    <td class="tg-nrix">2.21</td>
    <td class="tg-nrix">2.73</td>
    <td class="tg-nrix">4.23</td>
    <td class="tg-nrix">4.13</td>
    <td class="tg-nrix">3.31</td>
    <td class="tg-nrix">4.79</td>
    <td class="tg-nrix">3.93</td>
    <td class="tg-nrix">4.53</td>
    <td class="tg-nrix">4.71</td>
  </tr>
</tbody>
</table>

`CritiqueLLM` judged results:

<table>
<thead>
  <tr>
    <td rowspan="2">model</td>
    <td rowspan="2">Overall</td>
    <th colspan="3">Reasoning 中文推理</th>
    <th colspan="7">Language 中文语言</th>
  </tr>
  <tr>
    <th>Avg.</th>
    <th>Math.</th>
    <th>Logi.</th>
    <th>Avg.</th>
    <th>Fund.</th>
    <th>Chi.</th>
    <th>Open.</th>
    <th>Writ.</th>
    <th>Role.</th>
    <th>Pro.</th>
  </tr>
</thead>
<tbody>
  <tr>
    <td>模型</td>
    <td>总分</td>
    <td>推理<br>总分</td>
    <td>数学<br>计算</td>
    <td>逻辑<br>推理</td>
    <td>语言<br>总分</td>
    <td>基本<br>任务</td>
    <td>中文<br>理解</td>
    <td>综合<br>问答</td>
    <td>文本<br>写作</td>
    <td>角色<br>扮演</td>
    <td>专业<br>能力</td>
  </tr>
  <tr>
    <td>gpt-4-1106-preview</td>
    <td>7.58</td>
    <td>7.11</td>
    <td>7.39</td>
    <td>6.83</td>
    <td>8.05</td>
    <td>7.69</td>
    <td>7.07</td>
    <td>8.66</td>
    <td>8.23</td>
    <td>8.08</td>
    <td>8.55</td>
  </tr>
  <tr>
    <td>gpt-4-0613</td>
    <td>6.83</td>
    <td>6.41</td>
    <td>6.49</td>
    <td>6.33</td>
    <td>7.26</td>
    <td>7.16</td>
    <td>6.76</td>
    <td>7.26</td>
    <td>7.31</td>
    <td>7.48</td>
    <td>7.56</td>
  </tr>
  <tr>
    <td>chatglm-turbo（智谱清言）</td>
    <td>6.36</td>
    <td>4.99</td>
    <td>4.88</td>
    <td>5.09</td>
    <td>7.73</td>
    <td>7.5</td>
    <td>7.03</td>
    <td>8.45</td>
    <td>8.05</td>
    <td>7.67</td>
    <td>7.7</td>
  </tr>
  <tr>
    <td>erniebot-3.0（文心一言）</td>
    <td>5.91</td>
    <td>4.75</td>
    <td>4.34</td>
    <td>5.15</td>
    <td>7.07</td>
    <td>6.46</td>
    <td>7.21</td>
    <td>7.29</td>
    <td>7.73</td>
    <td>7.03</td>
    <td>6.72</td>
  </tr>
  <tr>
    <td>chatglm-pro（智谱清言）</td>
    <td>5.73</td>
    <td>4.49</td>
    <td>4.55</td>
    <td>4.43</td>
    <td>6.96</td>
    <td>6.47</td>
    <td>6.81</td>
    <td>7.26</td>
    <td>7.25</td>
    <td>7.29</td>
    <td>6.7</td>
  </tr>
  <tr>
    <td>gpt-3.5-turbo-0613</td>
    <td>5.68</td>
    <td>4.85</td>
    <td>4.90</td>
    <td>4.79</td>
    <td>6.52</td>
    <td>6.01</td>
    <td>5.6</td>
    <td>6.97</td>
    <td>7.27</td>
    <td>6.98</td>
    <td>6.29</td>
  </tr>
  <tr>
    <td>spark_desk_v2（讯飞星火）</td>
    <td>5.51</td>
    <td>4.58</td>
    <td>4.53</td>
    <td>4.62</td>
    <td>6.44</td>
    <td>5.76</td>
    <td>6.29</td>
    <td>6.37</td>
    <td>7.25</td>
    <td>7.03</td>
    <td>5.96</td>
  </tr>
  <tr>
    <td>qwen-14b-chat</td>
    <td>5.41</td>
    <td>4.52</td>
    <td>4.54</td>
    <td>4.50</td>
    <td>6.31</td>
    <td>6.46</td>
    <td>5.84</td>
    <td>6.71</td>
    <td>6.47</td>
    <td>6.38</td>
    <td>5.98</td>
  </tr>
  <tr>
    <td>baichuan2-13b-chat</td>
    <td>5.26</td>
    <td>3.96</td>
    <td>3.83</td>
    <td>4.08</td>
    <td>6.56</td>
    <td>5.74</td>
    <td>6.19</td>
    <td>7.03</td>
    <td>7.21</td>
    <td>6.72</td>
    <td>6.49</td>
  </tr>
  <tr>
    <td>baichuan2-7b-chat</td>
    <td>5.05</td>
    <td>3.68</td>
    <td>3.23</td>
    <td>4.13</td>
    <td>6.42</td>
    <td>5.72</td>
    <td>5.71</td>
    <td>7.08</td>
    <td>7.41</td>
    <td>6.86</td>
    <td>5.73</td>
  </tr>
  <tr>
    <td>chatglm3-6b</td>
    <td>5.01</td>
    <td>3.70</td>
    <td>3.44</td>
    <td>3.95</td>
    <td>6.33</td>
    <td>6.13</td>
    <td>5.72</td>
    <td>6.92</td>
    <td>7.11</td>
    <td>6.31</td>
    <td>5.77</td>
  </tr>
  <tr>
    <td>internlm-20b</td>
    <td>4.97</td>
    <td>3.67</td>
    <td>3.46</td>
    <td>3.87</td>
    <td>6.27</td>
    <td>5.65</td>
    <td>5.52</td>
    <td>6.71</td>
    <td>6.77</td>
    <td>6.35</td>
    <td>6.61</td>
  </tr>
  <tr>
    <td>qwen-7b-chat</td>
    <td>4.74</td>
    <td>3.66</td>
    <td>3.51</td>
    <td>3.80</td>
    <td>5.83</td>
    <td>6.01</td>
    <td>5.52</td>
    <td>5.89</td>
    <td>6.28</td>
    <td>6.16</td>
    <td>5.12</td>
  </tr>
  <tr>
    <td>chatglm2-6b</td>
    <td>4.57</td>
    <td>3.32</td>
    <td>3.28</td>
    <td>3.35</td>
    <td>5.83</td>
    <td>5.24</td>
    <td>5.12</td>
    <td>6.68</td>
    <td>6.83</td>
    <td>5.95</td>
    <td>5.15</td>
  </tr>
  <tr>
    <td>Chinese-llama-2-7b-chat</td>
    <td>3.44</td>
    <td>2.42</td>
    <td>2.13</td>
    <td>2.70</td>
    <td>4.46</td>
    <td>4.59</td>
    <td>4.29</td>
    <td>4.39</td>
    <td>4.64</td>
    <td>4.91</td>
    <td>3.94</td>
  </tr>
  <tr>
    <td>internlm-chat-7b</td>
    <td>3.24</td>
    <td>2.10</td>
    <td>2.34</td>
    <td>1.85</td>
    <td>4.39</td>
    <td>3.43</td>
    <td>3.76</td>
    <td>5.37</td>
    <td>4.63</td>
    <td>5.01</td>
    <td>4.15</td>
  </tr>
  <tr>
    <td>llama-2-13b-Chinese-chat</td>
    <td>3.14</td>
    <td>2.35</td>
    <td>2.12</td>
    <td>2.58</td>
    <td>3.93</td>
    <td>4.31</td>
    <td>2.9</td>
    <td>4.34</td>
    <td>3.52</td>
    <td>4.04</td>
    <td>4.47</td>
  </tr>
</tbody>
</table>

## 👏 Citation

```
@misc{liu2023alignbench,
      title={AlignBench: Benchmarking Chinese Alignment of Large Language Models}, 
      author={Xiao Liu and Xuanyu Lei and Shengyuan Wang and Yue Huang and Zhuoer Feng and Bosi Wen and Jiale Cheng and Pei Ke and Yifan Xu and Weng Lam Tam and Xiaohan Zhang and Lichao Sun and Hongning Wang and Jing Zhang and Minlie Huang and Yuxiao Dong and Jie Tang},
      year={2023},
      eprint={2311.18743},
      archivePrefix={arXiv},
      primaryClass={cs.CL}
}
```
