import os
import pandas as pd
import re
import sys

# ============ 配置区域 ============
TXT_DIR = "data/txt_493"
EXCEL_DIR = "data/sheets_500"
OUTPUT_FILE = "data/title_match_result.txt"
OUTPUT_EXCEL_DIR = "data/sheets_with_titles"  # 新生成的Excel文件目录
# ==================================

# 创建输出目录
if not os.path.exists(OUTPUT_EXCEL_DIR):
    os.makedirs(OUTPUT_EXCEL_DIR)

# 重定向输出到文件
sys.stdout = open(OUTPUT_FILE, 'w', encoding='utf-8')

def extract_titles_from_txt(txt_path):
    """
    从 txt 文件中提取所有标题
    返回格式: [(原始标题行, 去除#后的纯文本, 行号), ...]
    """
    titles = []
    in_code_block = False
    
    try:
        with open(txt_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        for line_num, line in enumerate(lines, 1):
            stripped = line.strip()
            
            # 检查是否进入或退出代码块
            if stripped.startswith('```'):
                in_code_block = not in_code_block
                continue
            
            # 如果在代码块中，跳过
            if in_code_block:
                continue
            
            # 检查是否是标题行（以 # 开头）
            if stripped.startswith('#'):
                # 计算左边 # 的数量
                hash_count = 0
                for char in stripped:
                    if char == '#':
                        hash_count += 1
                    else:
                        break
                
                # 去除左边的 # 和空格
                title_text = stripped[hash_count:].strip()
                
                # 去除右边的 # 和空格（如果存在）
                # 例如：### Contributor Code of Conduct ###
                if title_text.endswith('#'):
                    # 从右边开始计算 # 的数量
                    right_hash_count = 0
                    for char in reversed(title_text):
                        if char == '#':
                            right_hash_count += 1
                        else:
                            break
                    
                    # 去除右边的 # 和空格
                    if right_hash_count > 0:
                        title_text = title_text[:-right_hash_count].strip()
                
                # 去除HTML标签（例如：<a name="coc"></a>）
                title_text = re.sub(r'<[^>]+>', '', title_text).strip()
                
                # 去除加粗标记 **
                title_text = re.sub(r'\*\*', '', title_text).strip()
                
                # 去除代码标记 `
                title_text = re.sub(r'`', '', title_text).strip()
                
                if title_text:  # 确保不是空标题
                    titles.append((stripped, title_text, line_num))
    
    except Exception as e:
        print(f"[错误] 无法读取 {txt_path}: {str(e)}")
        return []
    
    return titles

def find_title_in_excel(excel_path, title_text, start_row=1):
    """
    在 Excel 第一列中从指定行开始查找与标题文本完全匹配的单元格
    返回: (行号, 单元格内容) 或 None
    """
    try:
        df = pd.read_excel(excel_path, header=None)
        
        # 从指定行开始遍历第一列
        for idx in range(start_row, len(df)):
            cell_value = df.iloc[idx, 0]
            
            # 检查单元格是否为空
            if pd.notna(cell_value):
                cell_text = str(cell_value).strip()
                
                # 精确匹配
                if cell_text == title_text:
                    return (idx + 1, cell_text)  # Excel 行号（1-based）
    
    except Exception as e:
        print(f"[错误] 无法读取 {excel_path}: {str(e)}")
        return None
    
    return None

# 获取所有 txt 文件
txt_files = sorted([f for f in os.listdir(TXT_DIR) if f.endswith('.txt')])

print(f"开始处理 {len(txt_files)} 个文件...\n")
print("=" * 80)

total_titles = 0
matched_titles = 0
unmatched_titles = 0
multiple_matched_titles = 0
total_files = 0
perfect_matched_files = 0  # 所有标题都匹配成功的文件数
perfect_matched_file_list = []  # 存储完美匹配的文件名
# 存储每个文件的标题匹配结果：{filename: [(excel_row, original_title_line), ...]}
file_title_mappings = {}

for txt_file in txt_files:
    # 构造文件路径
    txt_path = os.path.join(TXT_DIR, txt_file)
    excel_file = os.path.splitext(txt_file)[0] + ".xlsx"
    excel_path = os.path.join(EXCEL_DIR, excel_file)
    
    # 检查对应的 Excel 文件是否存在
    if not os.path.exists(excel_path):
        print(f"\n[文件缺失] {txt_file}")
        print(f"  对应的 Excel 文件不存在: {excel_file}")
        continue
    
    # 提取 txt 文件中的标题
    titles = extract_titles_from_txt(txt_path)
    
    if not titles:
        continue
    
    # 统计
    total_files += 1
    total_titles += len(titles)
    
    # 标记是否有问题
    has_issues = False
    issue_details = []
    
    # 记录上次匹配的位置，从下一行开始继续匹配
    last_matched_row = 1  # 从第2行开始（跳过表头）
    
    # 存储当前文件的标题匹配映射
    current_file_mappings = []
    
    # 对每个标题进行匹配
    for original_line, title_text, line_num in titles:
        match = find_title_in_excel(excel_path, title_text, start_row=last_matched_row)
        
        if match is None:
            # 未匹配到
            unmatched_titles += 1
            has_issues = True
            issue_details.append(f"  [未匹配] txt行{line_num}: {original_line}")
            issue_details.append(f"    从Excel行{last_matched_row + 1}开始查找")
        else:
            # 成功匹配到一个
            matched_titles += 1
            excel_row, cell_content = match
            # 记录匹配的映射关系
            current_file_mappings.append((excel_row, original_line))
            # 更新下次查找的起始位置（从当前匹配行的下一行开始）
            last_matched_row = excel_row  # excel_row 是 1-based，转为 0-based 索引
    
    # 如果有问题，输出详细信息
    if has_issues:
        print(f"\n[有问题] {txt_file}")
        print(f"  标题总数: {len(titles)}")
        for detail in issue_details:
            print(detail)
    else:
        # 所有标题都匹配成功
        perfect_matched_files += 1
        perfect_matched_file_list.append(txt_file)
        # 保存完美匹配文件的标题映射
        file_title_mappings[txt_file] = current_file_mappings

print("\n" + "=" * 80)
print(f"✓ 处理完成！")
print(f"文件总数: {len(txt_files)}")
print(f"有效文件数（有标题的）: {total_files}")
print(f"完美匹配文件数（所有标题都匹配）: {perfect_matched_files}")
print(f"文件匹配率: {perfect_matched_files / total_files * 100:.2f}%" if total_files > 0 else "N/A")
print(f"\n标题总数: {total_titles}")
print(f"成功匹配（1对1）: {matched_titles}")
print(f"未匹配到: {unmatched_titles}")
print(f"匹配到多个: {multiple_matched_titles}")
print(f"标题匹配率: {matched_titles / total_titles * 100:.2f}%" if total_titles > 0 else "N/A")

# 关闭文件并恢复标准输出
sys.stdout.close()
sys.stdout = sys.__stdout__

# 保存完美匹配的文件列表到JSON文件
import json
PERFECT_MATCH_FILE = "data/perfect_matched_files.json"
with open(PERFECT_MATCH_FILE, 'w', encoding='utf-8') as f:
    json.dump({
        "total_files": total_files,
        "perfect_matched_count": perfect_matched_files,
        "match_rate": f"{perfect_matched_files / total_files * 100:.2f}%" if total_files > 0 else "N/A",
        "files": perfect_matched_file_list
    }, f, ensure_ascii=False, indent=2)

print(f"\n✓ 匹配结果已保存到: {OUTPUT_FILE}")
print(f"✓ 完美匹配文件列表已保存到: {PERFECT_MATCH_FILE}")

# 处理完美匹配的文件，添加标题层级信息
print(f"\n开始处理完美匹配的文件，添加标题层级信息...")
processed_count = 0

for txt_file, mappings in file_title_mappings.items():
    excel_file = os.path.splitext(txt_file)[0] + ".xlsx"
    source_excel_path = os.path.join(EXCEL_DIR, excel_file)
    target_excel_path = os.path.join(OUTPUT_EXCEL_DIR, excel_file)
    
    try:
        # 读取原始Excel文件
        df = pd.read_excel(source_excel_path, header=None)
        
        # 替换标题行（Excel行号是1-based，DataFrame索引是0-based）
        for excel_row, original_title_line in mappings:
            df_idx = excel_row - 1  # 转换为0-based索引
            if df_idx < len(df):
                df.iloc[df_idx, 0] = original_title_line  # 替换第一列的内容
        
        # 保存到新的Excel文件
        df.to_excel(target_excel_path, index=False, header=False, engine='openpyxl')
        processed_count += 1
        
    except Exception as e:
        print(f"[错误] 处理 {txt_file} 时出错: {str(e)}")

print(f"✓ 完成！共处理 {processed_count} 个完美匹配的文件")
print(f"✓ 新Excel文件已保存到: {OUTPUT_EXCEL_DIR}")
