import http.client
import json
import os
import sys
import pandas as pd

# 调整路径以便导入 config 模块和访问数据文件
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(project_root, 'src'))
os.chdir(project_root) 

from config import API_KEY, API_HOST, API_MODEL

with open('prompt.md', 'r', encoding='utf-8') as f:
    prompt_content = f.read().strip()

data_dir = "data/sheets_for_training"
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
            
            true_category = "NT"
            for col_idx, cat_name in category_columns.items():
                if pd.notna(df.iloc[idx, col_idx]) and str(df.iloc[idx, col_idx]).strip() != "":
                    true_category = cat_name
                    break
            ground_truth.append(true_category)
        else:
            break
    
    results = []
    
    combined_paragraphs = "\n".join(paragraphs_to_classify)
    
    payload = json.dumps({
        "model": API_MODEL,
        "temperature": 0,
        "messages": [
            {"role": "system", "content": prompt_content},
            {"role": "user", "content": json.dumps(paragraphs_to_classify, ensure_ascii=False)}
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
            
            results = json.loads(model_returned_content)
            
            if not results:
                results = ["Parse failed: model returned empty array"] * len(paragraphs_to_classify)

    except json.JSONDecodeError:
        results = [f"JSON parse failed: {api_response['choices'][0]['message']['content']}"] * len(paragraphs_to_classify)
    except Exception as e:
        results = [f"Processing exception: {str(e)}"] * len(paragraphs_to_classify)
    
    comparison = [1 if results[i] == ground_truth[i] else 0 for i in range(len(results))]
    
    print(json.dumps(results, ensure_ascii=False))
    print(json.dumps(comparison, ensure_ascii=False))