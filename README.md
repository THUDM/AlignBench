# AlignBench: 多维度中文对齐评测基准

Read this in [English](README-en.md)

AlignBench 是第一个多维度全面评估中文大模型对齐水平的评测基准。此仓库包含了 AlignBench 的介绍信息、数据和代码。

## 📍 基本信息

对于经过指令微调（instruction tuning）的大语言模型（LLMs），与人类意图的对齐程度已成为其实际应用的关键因素。然而，现有的评测基准已经不能准确反映模型在真实场景中的表现和与人类意图的对齐程度，如何对中文大语言模型的对齐水平进行有效评估已经成为了一个重大的挑战。在实际的应用场景中，我们需要采用多样化、开放式、具有挑战性且自动化的评估方法来专门评估模型的对齐水平。

因此，我们构建了 AlignBench，这是一个用于评估中文大语言模型对齐性能的全面、多维度的评测基准。AlignBench 构建了人类参与的数据构建流程，来保证评测数据的动态更新。AlignBench 采用多维度、规则校准的模型评价方法（LLM-as-Judge），并且结合思维链（Chain-of-Thought）生成对模型回复的多维度分析和最终的综合评分，增强了评测的高可靠性和可解释性。

此外，为了便于中文领域研究人员方便快捷地衡量模型的对齐程度，我们开发了一个专用的评测模型——CritiqueLLM，它能够恢复 GPT-4 95% 的评估能力，并在未来将通过易于访问的 API 向研究人员提供。

![Overall](assets/Overall.png)

AlignBench 的整体框架如上图所示，包括数据构建流程、体系化的分类以及多维度、规则校准的 LLM-as-Judge 评估方法。

想了解 AlignBench 的更多详细信息，请参阅论文：[AlignBench](https://arxiv.org/abs/2311.18743)

想了解 CritiqueLLM 的更多详细信息，请参阅论文：[CritiqueLLM](https://arxiv.org/abs/2311.18702)


---

## 📦 数据集信息

为了进行系统化的评估，我们根据真实用户指令构建了一个全面的大语言模型（LLMs）能力分类体系。我们分析并总结了用户问题，将其归纳为 8 个主要类别，分别是基本能力、中文理解、综合问答、写作能力、逻辑推理、数学能力、角色扮演和专业知识。AlignBench 的分类体系和数据分布如下表所示。

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

为了反映模型在实际应用中的真实表现，AlignBench 中的数据主要来自 ChatGLM 在线服务中真实用户的问题（少部分为研究人员构造的挑战性问题）。AlignBench 总共包含 683 个高质量评测数据。AlignBench 中的每个样本都包含一个任务性的用户指令、一个高质量的参考答案，以及在我们的分类体系中对应的类别。数据保存在`data/data_release.jsonl`中，每一行都以`json`格式包含一个样本。

数据格式如下所示。

- `question_id` (integer)：问题的唯一标识符。
- `category` (string)：问题所属的主要类别。
- `subcategory` (string)：用于进一步分类的次要类别。
- `question` (string)：实际用户查询。
- `reference` (string)：这提供了对问题的参考或标准答案。

以下是`数学能力`类别的一个例子。

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

## ⚙️ 多维度评价方法

为了有效评估响应的质量，AlignBench 目前采用 GPT-4-0613 来分析并随后对响应进行评分。在评估过程中，输入包括用户问题、模型的回复和高质量的参考答案，输出是对模型回复的多维度的分析和最终评分，评分范围从1到10。为了确保可靠性和可解释性，我们实施了以下方法。整个评价流程的示例图如下所示。

![Case](assets/Case.png)

* **单点打分：** 对于每个模型的回答，评估方法将给出一个从 1 到 10 的最终评分。

* **思维链（Chain-of-Thought）：** 由于评分任务涉及到复杂的推理过程，我们采用了思维链方法来增强评价的可靠性和可解释性。具体来说，我们会引导评价模型在给出最终评分之前，从多个维度生成对模型回答的分析解释。

+ **规则校准：** 对于每个问题，我们提供一个高质量的参考答案。为了指导评价模型将模型回答与参考答案进行比较，并生成更加可控的分数，我们提供了详细的评分规则，阐述了分数区间（目前将 1 - 10 五等分）与模型回答的质量之间的关系。这些规则包含在 `prompt` 中。

* **多维度分析：** 由于不同的任务具有不同的性质和特征，对所有任务应用相同的评估流程是不合理的。因此，我们采用多维度的评分方法来全面评估模型回答。具体来说，我们根据不同的问题类型设置了不同的评估维度，并指导评价模型从指定的多个维度分析模型答案并提供单个维度的分数。这些维度及其定义记录在`config`中。


---

## 🚀 如何在 AlignBench 上评测模型

整个评估过程包含三个步骤：获取待评测模型的生成结果、调用评价模型获取分析和打分，最终计算结果。相应的脚本保存在`scripts`中，可以修改其中参数之后调用。

1. **步骤一** 获取待评测模型的生成结果

   首先，您需要获得待评测模型的 API 来生成结果，如果是开源模型，您需要自己部署成可以调用获得回复的 API。（此部分不包含在此仓库中）。

   其次，在`inference/api_models`中实现您自己的 API 调用类，`do_nothing`类可以作为一个示例。（此类主要用于调用 API，注意 API 类名应与文件名相同）

   第三，修改参数并运行以下脚本以获得待评测模型的生成结果。

   ```bash
   MODEL=do_nothing # TODO 修改模型名称（与您的API调用类相同）
   
   python get_answers.py \
       --model do_nothing \
       --workers 2 \
       --question-file data/data_release.jsonl \
       --save-dir data/model_answer
   ```

   待评测模型的回复将被保存在`data/model_answer`中，以备下一步的评测。

2. **步骤二** 调用评价模型获取分析和打分

   目前我们使用 `gpt-4-0613` 作为评测模型，之后为了方便中文社区，我们计划以 API 的形式开放 `CritiqueLLM` 作为 `gpt-4` 的替代评测模型给研究人员使用。

   首先，在`config/multi-dimension.json`中填写您的 GPT-4 API 密钥。

   然后，修改并运行以下脚本以获得评价模型的评测结果。

   ```bash
   MODEL=do_nothing # TODO 修改模型名称（与您的API调用类相同）
   
   python judge.py \
       --config-path config/multi-dimension.json \
       --model-name $MODEL \
       --parallel 2 \
   ```

   评测结果将保存在`data/judgment`

3. **步骤三** 最终计算结果

   运行以下脚本以获取保存在`data/judgment`中的所有模型的最终结果。

   ```bash
   python show_result.py \
       --input-dir data/judgment \
       --ques-file data/data_release.jsonl \
       --save-file data/results/results.xlsx
   ```

   计算结果打印出来，同时将以`xlsx`格式存储在`data/results`中。

---

## 📂 排行榜

我们在 AlignBench 上分别使用`gpt-4-0613`和`CritiqueLLM` 作为打分模型对 17 个支持汉语的大语言模型（LLMs）进行了系统评测，结果显示和`CritiqueLLM` 和`gpt-4-0613` 具有很高的一致性。

`gpt-4-0613` 的评测结果：

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

`CritiqueLLM` 的评测结果：

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

## 👏 引用

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
