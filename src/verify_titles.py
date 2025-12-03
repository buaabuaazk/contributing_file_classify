import os
import pandas as pd

# 定义文件夹路径
title_dir = "data/title_500"
sheets_dir = "data/sheets_500"
output_file = "verify_titles.txt"

def clean_title_line(line):
    """
    清理标题行，去除开头的所有#和-符号以及其后的空格，
    最后去除所有反引号（`）和星号（*）
    """
    # 去除开头的所有#和-符号以及其后的空格
    clean_line = line.strip()
    while clean_line.startswith('#') or clean_line.startswith('-'):
        if clean_line.startswith('#'):
            clean_line = clean_line[1:].lstrip()
        elif clean_line.startswith('-'):
            clean_line = clean_line[1:].lstrip()
    
    # 去除左右空格
    clean_line = clean_line.strip()
    
    # 去除所有反引号
    clean_line = clean_line.replace('`', '')
    
    # 去除所有星号
    clean_line = clean_line.replace('*', '')
    
    return clean_line

# 获取所有 title 文件
title_files = sorted([f for f in os.listdir(title_dir) if f.endswith('.txt')])

print(f"开始验证全部 {len(title_files)} 个 title 文件...\n")

# 统计变量
files_with_not_found = 0

# 打开输出文件
with open(output_file, 'w', encoding='utf-8') as out_f:
    for title_file in title_files:
        # 获取对应的 Excel 文件名
        file_name_without_ext = os.path.splitext(title_file)[0]
        excel_file = file_name_without_ext + ".xlsx"
        excel_path = os.path.join(sheets_dir, excel_file)
        
        # 检查 Excel 文件是否存在
        if not os.path.isfile(excel_path):
            out_f.write(f"[跳过] {title_file} - 对应的 Excel 文件不存在\n")
            continue
        
        # 读取 Excel 文件的第一列
        try:
            df = pd.read_excel(excel_path, header=None)
            excel_first_column = set()
            for cell in df.iloc[:, 0]:
                if pd.notna(cell):
                    excel_first_column.add(str(cell).strip())
        except Exception as e:
            out_f.write(f"[错误] {title_file} - 无法读取 Excel 文件: {str(e)}\n")
            continue
        
        # 读取 title 文件
        title_path = os.path.join(title_dir, title_file)
        try:
            with open(title_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
        except Exception as e:
            out_f.write(f"[错误] {title_file} - 无法读取文件: {str(e)}\n")
            continue
        
        # 验证每一行
        not_found = []
        for line in lines:
            # 保存原始行用于输出
            original_line = line.rstrip('\n')
            
            # 去除前面的 # 和空格
            clean_line = clean_title_line(line)
            
            if clean_line == "":
                continue
            
            # 检查是否在 Excel 的第一列中
            if clean_line not in excel_first_column:
                not_found.append((original_line, clean_line))
        
        # 输出结果
        if not_found:
            files_with_not_found += 1
            out_f.write(f"=== {title_file} ===\n")
            out_f.write(f"找到 {len(not_found)} 个在 Excel 第一列中找不到的标题：\n")
            for original, cleaned in not_found:
                out_f.write(f"  - 原始的: {original}\n")
                out_f.write(f"    清理后: {cleaned}\n")
            out_f.write("\n")

print(f"✓ 完成！共处理 {len(title_files)} 个文件，其中 {files_with_not_found} 个文件存在在 Excel 第一列中找不到的标题，验证结果已写入 {output_file}")