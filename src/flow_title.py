import http.client
import json
import os
import pandas as pd
import sys
import argparse
from config import API_KEY, API_HOST, API_MODEL

# 自定义输出类，同时写入文件和终端
class DualOutput:
    def __init__(self, filename):
        self.terminal = sys.stdout
        self.log = open(filename, 'w', encoding='utf-8')
    
    def write(self, message):
        self.terminal.write(message)
        self.log.write(message)
    
    def flush(self):
        self.terminal.flush()
        self.log.flush()
    
    def close(self):
        self.log.close()

# 解析命令行参数
parser = argparse.ArgumentParser(description='章节级分类处理')
parser.add_argument('--index', type=int, default=None, help='处理第N个文件（从1开始），-1表示最后一个')
parser.add_argument('--range', type=str, default=None, help='处理文件范围，格式: start-end，例如: 1-10')
parser.add_argument('--all', action='store_true', help='处理所有文件')
parser.add_argument('--data-dir', type=str, default='data/sheets_with_titles_433', help='数据源目录')
parser.add_argument('--output-dir', type=str, default='model_outputs', help='输出目录')
args = parser.parse_args()

# 重定向输出
output_logger = DualOutput('output.txt')
sys.stdout = output_logger

# ============ 配置区域 ============
FILE_INDEX = args.index
FILE_RANGE = None
if args.range:
    start, end = map(int, args.range.split('-'))
    FILE_RANGE = (start, end)
elif args.all:
    FILE_INDEX = None
    FILE_RANGE = None

OUTPUT_JSON_DIR = args.output_dir
DATA_DIR = args.data_dir
# ==================================

# 创建输出目录(如果不存在)
if not os.path.exists(OUTPUT_JSON_DIR):
    os.makedirs(OUTPUT_JSON_DIR)
    print(f"[初始化] 创建输出目录: {OUTPUT_JSON_DIR}\n")

with open('resources/prompts/prompt_chapter.md', 'r', encoding='utf-8') as f:
    prompt_content = f.read().strip()

xlsx_files = sorted([f for f in os.listdir(DATA_DIR) if f.endswith('.xlsx') and not f.startswith('.')])

# 根据配置选择要处理的文件
if FILE_INDEX is not None:
    # 处理单个文件
    if FILE_INDEX == -1:
        # -1表示最后一个文件
        xlsx_files = [xlsx_files[-1]]
        print(f"[配置] 只处理最后一个文件（第{len(xlsx_files)}个）: {xlsx_files[0]}\n")
    elif FILE_INDEX < 1 or FILE_INDEX > len(xlsx_files):
        print(f"[配置错误] FILE_INDEX={FILE_INDEX} 超出范围 (1-{len(xlsx_files)})")
        output_logger.close()
        sys.stdout = output_logger.terminal
        sys.exit(1)
    else:
        xlsx_files = [xlsx_files[FILE_INDEX - 1]]  # 从1开始计数,转换为0索引
        print(f"[配置] 只处理第 {FILE_INDEX} 个文件: {xlsx_files[0]}\n")
elif FILE_RANGE is not None:
    # 处理文件范围
    start_idx, end_idx = FILE_RANGE
    if start_idx < 1 or end_idx > len(xlsx_files) or start_idx > end_idx:
        print(f"[配置错误] FILE_RANGE={FILE_RANGE} 超出范围 (1-{len(xlsx_files)})")
        output_logger.close()
        sys.stdout = output_logger.terminal
        sys.exit(1)
    xlsx_files = xlsx_files[start_idx - 1:end_idx]  # 从1开始计数,转换为0索引
    print(f"[配置] 处理第 {start_idx}-{end_idx} 个文件，共 {len(xlsx_files)} 个文件\n")
else:
    # 处理所有文件
    print(f"[配置] 处理所有 {len(xlsx_files)} 个文件\n")

def is_title(text):
    """判断一行是否是标题（以#开头）"""
    return str(text).strip().startswith('#')

def parse_chapters(df, category_columns):
    """
    解析Excel为章节
    返回: [(章节内容, 章节起始行索引列表, ground_truth列表), ...]
    """
    chapters = []
    current_chapter_lines = []
    current_chapter_indices = []
    current_chapter_gt = []
    
    for idx in range(1, len(df)):
        line_text = df.iloc[idx, 0]
        
        # 遇到空行则结束
        if pd.isna(line_text) or str(line_text).strip() == "":
            # 保存当前章节（如果有内容）
            if current_chapter_lines:
                chapter_content = "\n".join(current_chapter_lines)
                chapters.append((chapter_content, current_chapter_indices, current_chapter_gt))
            break
        
        line_text_str = str(line_text).strip()
        
        # 获取该行的ground truth
        true_category = "NC"
        for col_idx, cat_name in category_columns.items():
            if pd.notna(df.iloc[idx, col_idx]) and str(df.iloc[idx, col_idx]).strip() != "":
                true_category = cat_name
                break
        
        # 如果当前行是标题
        if is_title(line_text_str):
            # 如果当前章节有内容，保存它
            if current_chapter_lines:
                chapter_content = "\n".join(current_chapter_lines)
                chapters.append((chapter_content, current_chapter_indices, current_chapter_gt))
            
            # 开始新章节
            current_chapter_lines = [line_text_str]
            current_chapter_indices = [idx]
            current_chapter_gt = [true_category]
        else:
            # 普通段落，加入当前章节
            current_chapter_lines.append(line_text_str)
            current_chapter_indices.append(idx)
            current_chapter_gt.append(true_category)
    
    # 保存最后一个章节
    if current_chapter_lines:
        chapter_content = "\n".join(current_chapter_lines)
        chapters.append((chapter_content, current_chapter_indices, current_chapter_gt))
    
    return chapters

# 用于记录所有文件的统计信息
file_stats = []

for xlsx_file in xlsx_files:
    print(xlsx_file)
    
    xlsx_path = os.path.join(DATA_DIR, xlsx_file)
    df = pd.read_excel(xlsx_path, header=None)
    category_columns = {1: "CF", 2: "CT", 3: "TC", 4: "BW", 5: "DC", 6: "SC"}
    
    # 解析章节
    chapters = parse_chapters(df, category_columns)
    print(f"共识别出 {len(chapters)} 个章节")
    
    # 收集所有ground truth（按原始顺序）
    all_ground_truth = []
    for _, _, chapter_gt in chapters:
        all_ground_truth.extend(chapter_gt)
    
    print(json.dumps(all_ground_truth, ensure_ascii=False))
    
    # 对每个章节单独调用API
    all_results = []
    all_model_outputs = []
    
    headers = {
        'Authorization': f'Bearer {API_KEY}',
        'Content-Type': 'application/json'
    }
    
    for chapter_idx, (chapter_content, chapter_indices, chapter_gt) in enumerate(chapters):
        print(f"\n处理章节 {chapter_idx + 1}/{len(chapters)}...")
        
        payload = json.dumps({
            "model": API_MODEL,
            "temperature": 0,
            "messages": [
                {"role": "system", "content": prompt_content},
                {"role": "user", "content": chapter_content}
            ]
        })

        try:
            conn = http.client.HTTPSConnection(API_HOST)
            conn.request("POST", "/v1/chat/completions", payload, headers)
            res = conn.getresponse()
            data_bytes = res.read()
            conn.close()

            api_response = json.loads(data_bytes.decode("utf-8"))
            
            if res.status != 200:
                error_message = api_response.get("error", {}).get("message", "Unknown error")
                chapter_result = f"Error: {error_message}"
                model_output = f"Error: {error_message}"
            else:
                model_returned_content = api_response["choices"][0]["message"]["content"].strip()
                model_output = model_returned_content
                
                # 解析JSON获取category
                try:
                    parsed = json.loads(model_returned_content)
                    if isinstance(parsed, dict) and "category" in parsed:
                        chapter_result = parsed["category"]
                    elif isinstance(parsed, list) and len(parsed) > 0 and isinstance(parsed[0], dict) and "category" in parsed[0]:
                        chapter_result = parsed[0]["category"]
                    else:
                        chapter_result = "Parse error"
                except:
                    chapter_result = "JSON parse failed"
            
            # 将章节结果应用到该章节的所有行
            for _ in range(len(chapter_indices)):
                all_results.append(chapter_result)
            
            all_model_outputs.append({
                "chapter_index": chapter_idx + 1,
                "chapter_content": chapter_content,
                "model_output": model_output,
                "result": chapter_result
            })
            
        except Exception as e:
            error_result = f"Processing exception: {str(e)}"
            for _ in range(len(chapter_indices)):
                all_results.append(error_result)
            all_model_outputs.append({
                "chapter_index": chapter_idx + 1,
                "chapter_content": chapter_content,
                "error": str(e)
            })
    
    # 保存所有章节的模型输出到JSON文件
    output_filename = os.path.splitext(xlsx_file)[0] + "_output.json"
    output_path = os.path.join(OUTPUT_JSON_DIR, output_filename)
    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(all_model_outputs, f, ensure_ascii=False, indent=2)
    except Exception as save_error:
        print(f"[保存失败] 无法保存到 {output_path}: {str(save_error)}")
    
    results = all_results
    
    comparison = [1 if results[i] == all_ground_truth[i] else 0 for i in range(len(results))]
    
    print(json.dumps(results, ensure_ascii=False))
    print(json.dumps(comparison, ensure_ascii=False))
    
    # 收集所有文本内容用于错误展示
    all_texts = []
    for _, chapter_indices, _ in chapters:
        for idx in chapter_indices:
            all_texts.append(str(df.iloc[idx, 0]).strip())
    
    for i in range(len(results)):
        if results[i] != all_ground_truth[i]:
            print(f"{all_ground_truth[i]} {results[i]} {all_texts[i]}")
    
    accuracy = sum(comparison) / len(comparison) if len(comparison) > 0 else 0
    print(f"Accuracy: {accuracy:.4f}\n")
    
    # 记录本文件统计
    file_stats.append({
        'file': xlsx_file,
        'accuracy': accuracy,
        'total_rows': len(comparison),
        'correct': sum(comparison)
    })

# 输出汇总统计
if len(file_stats) > 1:
    print("\n" + "="*80)
    print("汇总统计")
    print("="*80)
    for i, stat in enumerate(file_stats, 1):
        print(f"{i}. {stat['file']:<50} 准确率: {stat['accuracy']:.4f} ({stat['correct']}/{stat['total_rows']})")
    
    simple_avg = sum(s['accuracy'] for s in file_stats) / len(file_stats)
    total_rows = sum(s['total_rows'] for s in file_stats)
    total_correct = sum(s['correct'] for s in file_stats)
    weighted_avg = total_correct / total_rows if total_rows > 0 else 0
    print("\n" + "-"*80)
    print(f"简单平均准确率（每个文件权重相同）: {simple_avg:.4f}")
    print(f"加权平均准确率（按行数加权）: {weighted_avg:.4f}")
    print(f"总计: {total_correct}/{total_rows} 正确")
    print("="*80)

# 关闭日志文件
output_logger.close()
sys.stdout = output_logger.terminal
