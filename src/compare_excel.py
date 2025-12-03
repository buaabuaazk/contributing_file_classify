import os
import pandas as pd
import sys

# ============ 配置区域 ============
GEN_DIR = "data/gen_Excel493"
SHEETS_DIR = "data/sheets_500"
OUTPUT_FILE = "data/comparison_result.txt"
# ==================================

# 重定向输出到文件
sys.stdout = open(OUTPUT_FILE, 'w', encoding='utf-8')

# 获取两个文件夹中的文件
gen_files = set([f for f in os.listdir(GEN_DIR) if f.endswith('.xlsx')])
sheets_files = set([f for f in os.listdir(SHEETS_DIR) if f.endswith('.xlsx')])

# 找到同名文件
common_files = sorted(gen_files & sheets_files)

print(f"找到 {len(common_files)} 个同名文件\n")
print("=" * 60)

different_files = []

for idx, filename in enumerate(common_files, 1):
    gen_path = os.path.join(GEN_DIR, filename)
    sheets_path = os.path.join(SHEETS_DIR, filename)
    
    try:
        # 读取两个文件的第一列
        df_gen = pd.read_excel(gen_path, usecols=[0])
        df_sheets = pd.read_excel(sheets_path, usecols=[0])
        
        # 获取第一列的所有值
        col_gen = df_gen.iloc[:, 0].astype(str).tolist()
        col_sheets = df_sheets.iloc[:, 0].astype(str).tolist()
        
        # 比较是否完全相同
        if col_gen != col_sheets:
            different_files.append(filename)
            print(f"\n[不同] ({idx}/{len(common_files)}) {filename}")
            print(f"  生成文件行数: {len(col_gen)}, sheets_500文件行数: {len(col_sheets)}")
            
            # 找出不同的行
            max_len = max(len(col_gen), len(col_sheets))
            diff_count = 0
            for i in range(max_len):
                gen_val = col_gen[i] if i < len(col_gen) else "[缺失]"
                sheets_val = col_sheets[i] if i < len(col_sheets) else "[缺失]"
                
                if gen_val != sheets_val:
                    diff_count += 1
                    print(f"  行 {i+2} 不同:")  # Excel中第一行是表头，所以数据从第2行开始
                    print(f"    生成文件: {gen_val}")
                    print(f"    sheets_500: {sheets_val}")
            
            print(f"  共 {diff_count} 行内容不同")
        # else:
            # print(f"[相同] ({idx}/{len(common_files)}) {filename}")
    
    except Exception as e:
        print(f"[错误] ({idx}/{len(common_files)}) {filename}: {str(e)}")
        different_files.append(filename)

print("\n" + "=" * 60)
print(f"✓ 对比完成！")
print(f"相同: {len(common_files) - len(different_files)} 个")
print(f"不同: {len(different_files)} 个")

if different_files:
    print(f"\n不同的文件列表:")
    for f in different_files:
        print(f"  - {f}")

# 关闭文件并恢复标准输出
sys.stdout.close()
sys.stdout = sys.__stdout__
print(f"\n✓ 对比结果已保存到: {OUTPUT_FILE}")
