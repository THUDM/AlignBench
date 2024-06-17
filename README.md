# AlignBench: 多维度中文对齐评测基准 (ACL 2024)

Read this in [English](README-en.md)

AlignBench 是第一个多维度全面评估中文大模型对齐水平的评测基准。此仓库包含了 AlignBench 的介绍信息、数据和代码。

## 🔥 近期更新
[2024.06.15] 更新了 AlignBench v1.1，对涉及较强事实性内容的测试指令的参考答案进行了一轮人工检查修正。其中，约 22% 的答案除了进行修正外，还补充了对应参考信息的来源网页（参考 `evidences` 字段）和引用的信息。欢迎大家继续检查 AlignBench 的答案并提出修改意见。

## 📍 基本信息

对于经过指令微调（instruction tuning）的大语言模型（LLMs），与人类意图的对齐程度已成为其实际应用的关键因素。然而，现有的评测基准已经不能准确反映模型在真实场景中的表现和与人类意图的对齐程度，如何对中文大语言模型的对齐水平进行有效评估已经成为了一个重大的挑战。在实际的应用场景中，我们需要采用多样化、开放式、具有挑战性且自动化的评估方法来专门评估模型的对齐水平。

因此，我们构建了 AlignBench，这是一个用于评估中文大语言模型对齐性能的全面、多维度的评测基准。AlignBench 构建了人类参与的数据构建流程，来保证评测数据的动态更新。AlignBench 采用多维度、规则校准的模型评价方法（LLM-as-Judge），并且结合思维链（Chain-of-Thought）生成对模型回复的多维度分析和最终的综合评分，增强了评测的高可靠性和可解释性。

![Overall](assets/Overall.png)

AlignBench 的整体框架如上图所示，包括数据构建流程、体系化的分类以及多维度、规则校准的 LLM-as-Judge 评估方法。

想了解 AlignBench 的更多详细信息，请参阅论文：[AlignBench](https://arxiv.org/abs/2311.18743)

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

以下是`专业能力`类别的一个例子。

```json
{
    "question_id": 8,
    "category": "专业能力",
    "subcategory": "历史",
    "question": "麦哲伦航队在全球旅行时使用了六分仪测量经纬度么？",
    "reference": "不，麦哲伦航队在全球旅行时没有使用六分仪来测量经纬度。麦哲伦环球航行的时间是1519年—1522年，六分仪的原理由伊萨克·牛顿提出，而牛顿的出生时间是1643年1月4日，所以再麦哲伦航行的时间六分仪尚未被发明，使用六分仪是不可能的。",
    "evidences":
    [
        {
            "url": "https://baike.baidu.com/item/%E6%96%90%E8%BF%AA%E5%8D%97%C2%B7%E9%BA%A6%E5%93%B2%E4%BC%A6/7397066#SnippetTab\n\n",
            "quote": "1519年，率领船队开始环球航行。1521年4月27日夜间，麦哲伦在菲律宾死于部落冲突。船队在他死后继续向西航行，回到欧洲，并完成了人类首次环球航行。\n\n"
        },
        {
            "url": "https://baike.baidu.com/item/%E5%85%AD%E5%88%86%E4%BB%AA/749782?fr=ge_ala#3",
            "quote": "六分仪的原理由伊萨克·牛顿提出，1732年，英国海军开始将原始仪器安装在船艇上，因为当时最大测量角度是90度，因此被称为八分仪。1757年，约翰·坎贝尔船长将八分仪的测量夹角提高到120度，发展成为六分仪。其后六分仪的测量夹角虽然逐渐提升到144度，但是其名称却一直保持不变。"
        }
    ]
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
       --question-file data/data_v1.1_release.jsonl \
       --save-dir data/model_answer
   ```

   待评测模型的回复将被保存在`data/model_answer`中，以备下一步的评测。

2. **步骤二** 调用评价模型获取分析和打分

   目前我们使用 `gpt-4-0613` 作为评测模型。

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

我们在 AlignBench v1.1 上使用 `gpt-4-0613` 作为打分模型对当前一系列支持汉语的大语言模型（LLMs）进行了系统评测。感谢 [清华大学基础模型中心](https://fm.ai.tsinghua.edu.cn/) 的 [SuperBench](https://fm.ai.tsinghua.edu.cn/superbench/#/) 评估团队采用 AlignBench v1.1 作为周期性评估的一部分。后续希望进行评估的模型，可以利用 `gpt-4-0613` 进行自测评估并汇报，或与 SuperBench 评估团队进行联系。

`gpt-4-0613` 的评测结果（2024.06更新）：

<table class="tg"><thead>
  <tr>
    <th class="tg-0pky" rowspan="3">AlignBench v1.1</th>
    <th class="tg-c3ow" rowspan="2">Overall</th>
    <th class="tg-c3ow" colspan="3">Reasoning 中文推理</th>
    <th class="tg-c3ow" colspan="7">Language 中文语言</th>
  </tr>
  <tr>
    <th class="tg-c3ow">Avg.</th>
    <th class="tg-c3ow">Math.</th>
    <th class="tg-c3ow">Logi.</th>
    <th class="tg-c3ow">Avg.</th>
    <th class="tg-c3ow">Fund.</th>
    <th class="tg-c3ow">Chi.</th>
    <th class="tg-c3ow">Open.</th>
    <th class="tg-c3ow">Writ.</th>
    <th class="tg-c3ow">Role.</th>
    <th class="tg-c3ow">Pro.</th>
  </tr>
  <tr>
    <th class="tg-c3ow">总分</th>
    <th class="tg-c3ow">推理<br>总分</th>
    <th class="tg-c3ow">数学<br>计算</th>
    <th class="tg-c3ow">逻辑<br>推理</th>
    <th class="tg-c3ow">语言<br>总分</th>
    <th class="tg-c3ow">基本<br>任务</th>
    <th class="tg-c3ow">中文<br>理解</th>
    <th class="tg-c3ow">综合<br>问答</th>
    <th class="tg-c3ow">文本<br>写作</th>
    <th class="tg-c3ow">角色<br>扮演</th>
    <th class="tg-c3ow">专业<br>能力</th>
  </tr></thead>
<tbody>
  <tr>
    <td class="tg-0pky">GPT-4o</td>
    <td class="tg-c3ow">8.38</td>
    <td class="tg-c3ow">8.44</td>
    <td class="tg-c3ow">8.62</td>
    <td class="tg-c3ow">8.25</td>
    <td class="tg-c3ow">8.32</td>
    <td class="tg-c3ow">8.25</td>
    <td class="tg-c3ow">7.97</td>
    <td class="tg-c3ow">8.79</td>
    <td class="tg-c3ow">7.95</td>
    <td class="tg-c3ow">8.35</td>
    <td class="tg-c3ow">8.62</td>
  </tr>
  <tr>
    <td class="tg-0pky">通义千问2.5</td>
    <td class="tg-c3ow">8.17</td>
    <td class="tg-c3ow">7.79</td>
    <td class="tg-c3ow">7.97</td>
    <td class="tg-c3ow">7.60</td>
    <td class="tg-c3ow">8.55</td>
    <td class="tg-c3ow">7.87</td>
    <td class="tg-c3ow">8.40</td>
    <td class="tg-c3ow">8.94</td>
    <td class="tg-c3ow">8.60</td>
    <td class="tg-c3ow">8.73</td>
    <td class="tg-c3ow">8.76</td>
  </tr>
  <tr>
    <td class="tg-0pky">GPT-4 Turbo-20240409</td>
    <td class="tg-c3ow">8.00</td>
    <td class="tg-c3ow">8.00</td>
    <td class="tg-c3ow">8.32</td>
    <td class="tg-c3ow">7.67</td>
    <td class="tg-c3ow">8.01</td>
    <td class="tg-c3ow">7.60</td>
    <td class="tg-c3ow">7.57</td>
    <td class="tg-c3ow">8.37</td>
    <td class="tg-c3ow">7.75</td>
    <td class="tg-c3ow">8.18</td>
    <td class="tg-c3ow">8.59</td>
  </tr>
  <tr>
    <td class="tg-0pky">Abab 6.5(MoE)</td>
    <td class="tg-c3ow">7.94</td>
    <td class="tg-c3ow">7.73</td>
    <td class="tg-c3ow">7.82</td>
    <td class="tg-c3ow">7.63</td>
    <td class="tg-c3ow">8.16</td>
    <td class="tg-c3ow">8.21</td>
    <td class="tg-c3ow">7.81</td>
    <td class="tg-c3ow">8.31</td>
    <td class="tg-c3ow">8.14</td>
    <td class="tg-c3ow">8.24</td>
    <td class="tg-c3ow">8.22</td>
  </tr>
  <tr>
    <td class="tg-0pky">GLM-4-0520</td>
    <td class="tg-c3ow">7.89</td>
    <td class="tg-c3ow">7.66</td>
    <td class="tg-c3ow">7.67</td>
    <td class="tg-c3ow">7.64</td>
    <td class="tg-c3ow">8.13</td>
    <td class="tg-c3ow">7.78</td>
    <td class="tg-c3ow">8.22</td>
    <td class="tg-c3ow">8.21</td>
    <td class="tg-c3ow">8.09</td>
    <td class="tg-c3ow">7.99</td>
    <td class="tg-c3ow">8.47</td>
  </tr>
  <tr>
    <td class="tg-0pky">Sensechat 5.0</td>
    <td class="tg-c3ow">7.89</td>
    <td class="tg-c3ow">7.54</td>
    <td class="tg-c3ow">7.96</td>
    <td class="tg-c3ow">7.12</td>
    <td class="tg-c3ow">8.23</td>
    <td class="tg-c3ow">8.27</td>
    <td class="tg-c3ow">7.69</td>
    <td class="tg-c3ow">8.45</td>
    <td class="tg-c3ow">8.15</td>
    <td class="tg-c3ow">8.53</td>
    <td class="tg-c3ow">8.29</td>
  </tr>
  <tr>
    <td class="tg-0pky">Qwen 1.5-110B-Chat</td>
    <td class="tg-c3ow">7.86</td>
    <td class="tg-c3ow">7.49</td>
    <td class="tg-c3ow">7.69</td>
    <td class="tg-c3ow">7.28</td>
    <td class="tg-c3ow">8.23</td>
    <td class="tg-c3ow">7.76</td>
    <td class="tg-c3ow">8.12</td>
    <td class="tg-c3ow">8.46</td>
    <td class="tg-c3ow">8.20</td>
    <td class="tg-c3ow">8.30</td>
    <td class="tg-c3ow">8.52</td>
  </tr>
  <tr>
    <td class="tg-0pky">文心一言4.0</td>
    <td class="tg-c3ow">7.85</td>
    <td class="tg-c3ow">7.81</td>
    <td class="tg-c3ow">7.60</td>
    <td class="tg-c3ow">8.02</td>
    <td class="tg-c3ow">7.89</td>
    <td class="tg-c3ow">7.33</td>
    <td class="tg-c3ow">8.35</td>
    <td class="tg-c3ow">8.16</td>
    <td class="tg-c3ow">8.11</td>
    <td class="tg-c3ow">8.07</td>
    <td class="tg-c3ow">7.29</td>
  </tr>
  <tr>
    <td class="tg-0pky">Yi-Large</td>
    <td class="tg-c3ow">7.80</td>
    <td class="tg-c3ow">7.44</td>
    <td class="tg-c3ow">7.65</td>
    <td class="tg-c3ow">7.23</td>
    <td class="tg-c3ow">8.17</td>
    <td class="tg-c3ow">7.81</td>
    <td class="tg-c3ow">7.85</td>
    <td class="tg-c3ow">8.51</td>
    <td class="tg-c3ow">7.96</td>
    <td class="tg-c3ow">8.18</td>
    <td class="tg-c3ow">8.69</td>
  </tr>
  <tr>
    <td class="tg-0pky">DeepSeek-V2</td>
    <td class="tg-c3ow">7.72</td>
    <td class="tg-c3ow">7.26</td>
    <td class="tg-c3ow">7.51</td>
    <td class="tg-c3ow">7.00</td>
    <td class="tg-c3ow">8.19</td>
    <td class="tg-c3ow">8.10</td>
    <td class="tg-c3ow">7.83</td>
    <td class="tg-c3ow">8.16</td>
    <td class="tg-c3ow">8.20</td>
    <td class="tg-c3ow">8.41</td>
    <td class="tg-c3ow">8.44</td>
  </tr>
  <tr>
    <td class="tg-0pky">GLM-4-Air</td>
    <td class="tg-c3ow">7.58</td>
    <td class="tg-c3ow">7.20</td>
    <td class="tg-c3ow">7.19</td>
    <td class="tg-c3ow">7.20</td>
    <td class="tg-c3ow">7.97</td>
    <td class="tg-c3ow">7.53</td>
    <td class="tg-c3ow">7.71</td>
    <td class="tg-c3ow">8.18</td>
    <td class="tg-c3ow">7.97</td>
    <td class="tg-c3ow">8.10</td>
    <td class="tg-c3ow">8.32</td>
  </tr>
  <tr>
    <td class="tg-0pky">Claude 3 Opus</td>
    <td class="tg-c3ow">7.53</td>
    <td class="tg-c3ow">7.19</td>
    <td class="tg-c3ow">7.27</td>
    <td class="tg-c3ow">7.11</td>
    <td class="tg-c3ow">7.87</td>
    <td class="tg-c3ow">7.94</td>
    <td class="tg-c3ow">7.71</td>
    <td class="tg-c3ow">8.21</td>
    <td class="tg-c3ow">7.61</td>
    <td class="tg-c3ow">7.73</td>
    <td class="tg-c3ow">8.02</td>
  </tr>
  <tr>
    <td class="tg-0pky">Gemini 1.5 Pro</td>
    <td class="tg-c3ow">7.47</td>
    <td class="tg-c3ow">7.07</td>
    <td class="tg-c3ow">7.77</td>
    <td class="tg-c3ow">6.36</td>
    <td class="tg-c3ow">7.87</td>
    <td class="tg-c3ow">7.31</td>
    <td class="tg-c3ow">7.22</td>
    <td class="tg-c3ow">8.55</td>
    <td class="tg-c3ow">7.83</td>
    <td class="tg-c3ow">7.79</td>
    <td class="tg-c3ow">8.52</td>
  </tr>
  <tr>
    <td class="tg-0pky">Baichuan 4</td>
    <td class="tg-c3ow">7.45</td>
    <td class="tg-c3ow">7.28</td>
    <td class="tg-c3ow">7.34</td>
    <td class="tg-c3ow">7.22</td>
    <td class="tg-c3ow">7.63</td>
    <td class="tg-c3ow">7.34</td>
    <td class="tg-c3ow">7.40</td>
    <td class="tg-c3ow">7.74</td>
    <td class="tg-c3ow">7.60</td>
    <td class="tg-c3ow">7.36</td>
    <td class="tg-c3ow">8.33</td>
  </tr>
  <tr>
    <td class="tg-0pky">Llama 3-70B</td>
    <td class="tg-c3ow">7.42</td>
    <td class="tg-c3ow">7.02</td>
    <td class="tg-c3ow">7.18</td>
    <td class="tg-c3ow">6.86</td>
    <td class="tg-c3ow">7.82</td>
    <td class="tg-c3ow">7.75</td>
    <td class="tg-c3ow">6.63</td>
    <td class="tg-c3ow">8.65</td>
    <td class="tg-c3ow">7.80</td>
    <td class="tg-c3ow">8.02</td>
    <td class="tg-c3ow">8.08</td>
  </tr>
  <tr>
    <td class="tg-0pky">Gemini 1.5 Flash</td>
    <td class="tg-c3ow">7.38</td>
    <td class="tg-c3ow">7.29</td>
    <td class="tg-c3ow">7.96</td>
    <td class="tg-c3ow">6.61</td>
    <td class="tg-c3ow">7.47</td>
    <td class="tg-c3ow">6.75</td>
    <td class="tg-c3ow">7.16</td>
    <td class="tg-c3ow">8.05</td>
    <td class="tg-c3ow">6.96</td>
    <td class="tg-c3ow">7.73</td>
    <td class="tg-c3ow">8.16</td>
  </tr>
  <tr>
    <td class="tg-0pky">WizardLM-2-8x22B</td>
    <td class="tg-c3ow">7.34</td>
    <td class="tg-c3ow">6.99</td>
    <td class="tg-c3ow">6.99</td>
    <td class="tg-c3ow">6.98</td>
    <td class="tg-c3ow">7.70</td>
    <td class="tg-c3ow">7.57</td>
    <td class="tg-c3ow">6.60</td>
    <td class="tg-c3ow">8.40</td>
    <td class="tg-c3ow">7.60</td>
    <td class="tg-c3ow">8.17</td>
    <td class="tg-c3ow">7.83</td>
  </tr>
  <tr>
    <td class="tg-0pky">moonshot-v1-8k</td>
    <td class="tg-c3ow">7.31</td>
    <td class="tg-c3ow">6.76</td>
    <td class="tg-c3ow">6.94</td>
    <td class="tg-c3ow">6.58</td>
    <td class="tg-c3ow">7.86</td>
    <td class="tg-c3ow">7.56</td>
    <td class="tg-c3ow">7.83</td>
    <td class="tg-c3ow">7.82</td>
    <td class="tg-c3ow">7.76</td>
    <td class="tg-c3ow">7.93</td>
    <td class="tg-c3ow">8.25</td>
  </tr>
  <tr>
    <td class="tg-0pky">Step-1-32k</td>
    <td class="tg-c3ow">7.08</td>
    <td class="tg-c3ow">6.43</td>
    <td class="tg-c3ow">6.77</td>
    <td class="tg-c3ow">6.09</td>
    <td class="tg-c3ow">7.72</td>
    <td class="tg-c3ow">8.09</td>
    <td class="tg-c3ow">7.74</td>
    <td class="tg-c3ow">7.34</td>
    <td class="tg-c3ow">7.56</td>
    <td class="tg-c3ow">7.74</td>
    <td class="tg-c3ow">7.86</td>
  </tr>
  <tr>
    <td class="tg-0pky">讯飞星火3.5</td>
    <td class="tg-c3ow">6.90</td>
    <td class="tg-c3ow">6.47</td>
    <td class="tg-c3ow">7.30</td>
    <td class="tg-c3ow">5.63</td>
    <td class="tg-c3ow">7.33</td>
    <td class="tg-c3ow">7.28</td>
    <td class="tg-c3ow">7.71</td>
    <td class="tg-c3ow">7.24</td>
    <td class="tg-c3ow">7.12</td>
    <td class="tg-c3ow">7.41</td>
    <td class="tg-c3ow">7.24</td>
  </tr>
  <tr>
    <td class="tg-0pky">Claude 3 Sonnet</td>
    <td class="tg-c3ow">6.71</td>
    <td class="tg-c3ow">6.17</td>
    <td class="tg-c3ow">6.24</td>
    <td class="tg-c3ow">6.10</td>
    <td class="tg-c3ow">7.25</td>
    <td class="tg-c3ow">7.56</td>
    <td class="tg-c3ow">6.39</td>
    <td class="tg-c3ow">7.37</td>
    <td class="tg-c3ow">7.14</td>
    <td class="tg-c3ow">7.76</td>
    <td class="tg-c3ow">7.26</td>
  </tr>
  <tr>
    <td class="tg-0pky">Mixtral-8x22B (MoE)</td>
    <td class="tg-c3ow">6.48</td>
    <td class="tg-c3ow">6.23</td>
    <td class="tg-c3ow">6.47</td>
    <td class="tg-c3ow">5.98</td>
    <td class="tg-c3ow">6.73</td>
    <td class="tg-c3ow">6.87</td>
    <td class="tg-c3ow">5.72</td>
    <td class="tg-c3ow">7.00</td>
    <td class="tg-c3ow">6.61</td>
    <td class="tg-c3ow">7.14</td>
    <td class="tg-c3ow">7.01</td>
  </tr>
  <tr>
    <td class="tg-0pky">Claude 3 Haiku</td>
    <td class="tg-c3ow">6.38</td>
    <td class="tg-c3ow">5.58</td>
    <td class="tg-c3ow">6.06</td>
    <td class="tg-c3ow">5.10</td>
    <td class="tg-c3ow">7.18</td>
    <td class="tg-c3ow">7.15</td>
    <td class="tg-c3ow">6.74</td>
    <td class="tg-c3ow">7.58</td>
    <td class="tg-c3ow">6.95</td>
    <td class="tg-c3ow">7.26</td>
    <td class="tg-c3ow">7.37</td>
  </tr>
</tbody></table>

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
