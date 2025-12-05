import os
import pandas as pd
from collections import defaultdict

# 数据目录
DATA_DIR = "data/sheets_500"

# 类别映射
category_columns = {1: "CF", 2: "CT", 3: "TC", 4: "BW", 5: "DC", 6: "SC"}
all_categories = ["CF", "CT", "TC", "BW", "DC", "SC", "NC"]

# 统计每个类别的总数
category_counts = defaultdict(int)

# 获取所有Excel文件
xlsx_files = sorted([f for f in os.listdir(DATA_DIR) if f.endswith('.xlsx') and not f.startswith('.')])

print(f"正在处理 {len(xlsx_files)} 个文件...")
print("="*60)

# 遍历每个文件
for xlsx_file in xlsx_files:
    xlsx_path = os.path.join(DATA_DIR, xlsx_file)
    
    try:
        df = pd.read_excel(xlsx_path, header=None)
        
        # 从第二行开始遍历（第一行是标题）
        for idx in range(1, len(df)):
            paragraph = df.iloc[idx, 0]
            
            # 遇到空行则停止
            if pd.isna(paragraph) or str(paragraph).strip() == "":
                break
            
            # 判断该段落的类别
            true_category = "NC"  # 默认为无类别
            for col_idx, cat_name in category_columns.items():
                if pd.notna(df.iloc[idx, col_idx]) and str(df.iloc[idx, col_idx]).strip() != "":
                    true_category = cat_name
                    break
            
            # 统计该类别
            category_counts[true_category] += 1
    
    except Exception as e:
        print(f"[错误] 处理文件 {xlsx_file} 时出错: {str(e)}")

# 输出统计结果
print("\n" + "="*60)
print("类别统计结果")
print("="*60)

total = sum(category_counts.values())

for category in all_categories:
    count = category_counts[category]
    percentage = (count / total * 100) if total > 0 else 0
    print(f"{category:3s}: {count:6d} 个段落 ({percentage:5.2f}%)")

print("-"*60)
print(f"总计: {total:6d} 个段落")
print("="*60)

# 按数量排序输出
print("\n按数量排序：")
print("-"*60)
sorted_categories = sorted(category_counts.items(), key=lambda x: -x[1])
for category, count in sorted_categories:
    percentage = (count / total * 100) if total > 0 else 0
    print(f"{category:3s}: {count:6d} ({percentage:5.2f}%)")
