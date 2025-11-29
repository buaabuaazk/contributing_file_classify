import http.client
import json
import os
import pandas as pd
import sys
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

# 重定向输出
output_logger = DualOutput('output.txt')
sys.stdout = output_logger

# ============ 配置区域 ============
# 设置要处理的Excel文件
# None = 处理所有文件
# 整数 = 只处理第N个文件 (例如: FILE_INDEX = 3 只处理第3个文件, 从1开始计数)
FILE_INDEX = 8
# 设置大模型输出JSON文件的保存目录
OUTPUT_JSON_DIR = "model_outputs"
# ==================================

# 创建输出目录(如果不存在)
if not os.path.exists(OUTPUT_JSON_DIR):
    os.makedirs(OUTPUT_JSON_DIR)
    print(f"[初始化] 创建输出目录: {OUTPUT_JSON_DIR}\n")

with open('resources/prompts/prompt.md', 'r', encoding='utf-8') as f:
    prompt_content = f.read().strip()

std_dir = "std"
xlsx_files = [f for f in os.listdir(std_dir) if f.endswith('.xlsx') and not f.startswith('.')]

# 根据配置选择要处理的文件
if FILE_INDEX is not None:
    if FILE_INDEX < 1 or FILE_INDEX > len(xlsx_files):
        print(f"[配置错误] FILE_INDEX={FILE_INDEX} 超出范围 (1-{len(xlsx_files)})")
        output_logger.close()
        sys.stdout = output_logger.terminal
        sys.exit(1)
    xlsx_files = [xlsx_files[FILE_INDEX - 1]]  # 从1开始计数,转换为0索引
    print(f"[配置] 只处理第 {FILE_INDEX} 个文件: {xlsx_files[0]}\n")
else:
    print(f"[配置] 处理所有 {len(xlsx_files)} 个文件\n")

for xlsx_file in xlsx_files:
    print(xlsx_file)
    
    paragraphs_to_classify = []
    ground_truth = []
    xlsx_path = os.path.join(std_dir, xlsx_file)
    
    df = pd.read_excel(xlsx_path, header=None)
    category_columns = {1: "CF", 2: "CT", 3: "TC", 4: "BW", 5: "DC", 6: "SC"}
    
    for idx in range(1, len(df)):
        paragraph = df.iloc[idx, 0]
        if pd.notna(paragraph) and str(paragraph).strip() != "":
            paragraphs_to_classify.append(str(paragraph).strip())
            true_category = "NC"
            for col_idx, cat_name in category_columns.items():
                if pd.notna(df.iloc[idx, col_idx]) and str(df.iloc[idx, col_idx]).strip() != "":
                    true_category = cat_name
                    break
            ground_truth.append(true_category)
        else:
            break
    
    print(json.dumps(ground_truth, ensure_ascii=False))
    
    # 给每个段落添加序号 (使用方括号格式避免被大模型误判)
    numbered_paragraphs = [f"[{i+1}] {para}" for i, para in enumerate(paragraphs_to_classify)]
    
    results = []
    
    payload = json.dumps({
        "model": API_MODEL,
        "temperature": 0,
        "messages": [
            {"role": "system", "content": prompt_content},
            {"role": "user", "content": json.dumps(numbered_paragraphs, ensure_ascii=False)}
        ]
    })

    headers = {
        'Authorization': f'Bearer {API_KEY}',
        'Content-Type': 'application/json'
    }

    try:
        conn = http.client.HTTPSConnection(API_HOST)
        conn.request("POST", "/v1/chat/completions", payload, headers)
        res = conn.getresponse()
        data_bytes = res.read()
        conn.close()

        api_response = json.loads(data_bytes.decode("utf-8"))
        
        if res.status != 200:
            error_message = api_response.get("error", {}).get("message", "Unknown error")
            results = [f"Error: {error_message}"] * len(paragraphs_to_classify)
        else:
            model_returned_content = api_response["choices"][0]["message"]["content"].strip()
            
            # 保存大模型原始输出到JSON文件
            output_filename = os.path.splitext(xlsx_file)[0] + "_output.json"
            output_path = os.path.join(OUTPUT_JSON_DIR, output_filename)
            try:
                with open(output_path, 'w', encoding='utf-8') as f:
                    f.write(model_returned_content)
            except Exception as save_error:
                print(f"[保存失败] 无法保存到 {output_path}: {str(save_error)}")
            
            # 从模型输出中解析 JSON 数组
            parsed = json.loads(model_returned_content)

            # 防护：确保是 list 且每项是 dict
            if not isinstance(parsed, list):
                raise ValueError("Model output is not a list")

            # 你需要的只是分类结果：category
            results = []
            for item in parsed:
                if isinstance(item, dict) and "category" in item:
                    results.append(item["category"])
                else:
                    results.append("Parse error")

            # 防护：数量对不上也填补
            if len(results) < len(paragraphs_to_classify):
                results.extend(["Missing"] * (len(paragraphs_to_classify) - len(results)))
            elif len(results) > len(paragraphs_to_classify):
                results = results[:len(paragraphs_to_classify)]

    except json.JSONDecodeError:
        results = [f"JSON parse failed: {api_response['choices'][0]['message']['content']}"] * len(paragraphs_to_classify)
    except Exception as e:
        results = [f"Processing exception: {str(e)}"] * len(paragraphs_to_classify)
    
    comparison = [1 if results[i] == ground_truth[i] else 0 for i in range(len(results))]
    
    print(json.dumps(results, ensure_ascii=False))
    print(json.dumps(comparison, ensure_ascii=False))
    
    for i in range(len(results)):
        if results[i] != ground_truth[i]:
            print(f"{ground_truth[i]} {results[i]} {paragraphs_to_classify[i]}")
    
    accuracy = sum(comparison) / len(comparison) if len(comparison) > 0 else 0
    print(f"Accuracy: {accuracy:.4f}")
    #break

# 关闭日志文件
output_logger.close()
sys.stdout = output_logger.terminal
