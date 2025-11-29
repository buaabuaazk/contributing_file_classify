import http.client
import json
import os
import sys
import pandas as pd

# 调整路径以便导入 config 模块和访问数据文件
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(project_root, 'src'))
os.chdir(project_root)  # 将工作目录改为项目根目录

from config import API_KEY, API_HOST, API_MODEL

with open('resources/prompts/prompt.md', 'r', encoding='utf-8') as f:
    prompt_content = f.read().strip()

data_dir = "data"
xlsx_files = [f for f in os.listdir(data_dir) if f.endswith('.xlsx') and not f.startswith('.')]

for xlsx_file in xlsx_files:
    print(xlsx_file)
    
    paragraphs_to_classify = []
    ground_truth = []
    xlsx_path = os.path.join(data_dir, xlsx_file)
    
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
    
    results = []
    
    for paragraph in paragraphs_to_classify:
        payload = json.dumps({
            "model": API_MODEL,
            "temperature": 0,
            "messages": [
                {"role": "system", "content": prompt_content},
                {"role": "user", "content": json.dumps([paragraph], ensure_ascii=False)}
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
                results.append(f"Error: {error_message}")
            else:
                model_returned_content = api_response["choices"][0]["message"]["content"].strip()
                
                category_list = json.loads(model_returned_content)
                
                if not category_list:
                    results.append("Parse failed: model returned empty array")
                else:
                    results.append(category_list[0])
    
        except json.JSONDecodeError:
            results.append(f"JSON parse failed: {api_response['choices'][0]['message']['content']}")
        except Exception as e:
            results.append(f"Processing exception: {str(e)}")
    
    comparison = [1 if results[i] == ground_truth[i] else 0 for i in range(len(results))]
    
    print(json.dumps(results, ensure_ascii=False))
    print(json.dumps(comparison, ensure_ascii=False))
    
    for i in range(len(results)):
        if results[i] != ground_truth[i]:
            print(f"{ground_truth[i]} {results[i]} {paragraphs_to_classify[i]}")
    
    accuracy = sum(comparison) / len(comparison) if len(comparison) > 0 else 0
    print(f"Accuracy: {accuracy:.4f}")
    # break