import jsonlines
import os
import pandas as pd
from collections import defaultdict

# 初始化一个嵌套字典用于存储模型和评分
model_ratings = defaultdict(lambda: defaultdict(int))
model_counts = defaultdict(lambda: defaultdict(int))

# 遍历文件夹中的所有.jsonl文件
folder_path = 'data/judgment'
for filename in os.listdir(folder_path):
    if filename.endswith('.jsonl'):
        model_name = filename[:-6]
        with jsonlines.open(os.path.join(folder_path, filename)) as f:
            for line in f:
                if line['score'] != -1:
                    for k, v in line['rating'].items():
                        if isinstance(v, (int, float)) and ',' not in k:  # 确保值是数字
                            model_ratings[model_name][k] += v
                            model_counts[model_name][k] += 1

# 计算平均得分
model_avg_ratings = defaultdict(lambda: defaultdict(float))

for model, dimensions in model_ratings.items():
    for dimension, total_score in dimensions.items():
        model_avg_ratings[model][dimension] = total_score / model_counts[model][dimension]

# 转换为DataFrame并保存为xlsx文件
df = pd.DataFrame(model_avg_ratings).transpose()
df.to_excel("dimensional_scores.xlsx")
