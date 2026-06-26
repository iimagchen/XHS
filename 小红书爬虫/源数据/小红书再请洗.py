import pandas as pd

# 读取原始文件
file_path = "小红书_deepseek_帖子详情 - 去重_标准化输出.csv"
df = pd.read_csv(file_path)

# 创建布尔掩码：标题、正文或标签中至少一个包含 "deepseek"（不区分大小写）
mask = (
    df['标题'].str.contains("deepseek", case=False, na=False) |
    df['正文'].str.contains("deepseek", case=False, na=False) |
    df['标签'].str.contains("deepseek", case=False, na=False)
)

# 应用掩码进行数据筛选
filtered_df = df[mask]

# 可选：保存为新文件
filtered_df.to_csv("小红书_deepseek_清洗后.csv", index=False, encoding='utf-8-sig')

# 打印筛选后数据的简要信息（行数）
print(f"原始数据共 {len(df)} 条，清洗后保留 {len(filtered_df)} 条。")
