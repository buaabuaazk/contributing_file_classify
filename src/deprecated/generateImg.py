import http.client
import json
import base64
import os
import sys
from datetime import datetime

# 调整路径以便导入 config 模块和访问数据文件
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(project_root, 'src'))
os.chdir(project_root)  # 将工作目录改为项目根目录

from config import API_KEY, API_HOST, IMG_MODEL

# 读取提示词文件
with open('resources/prompts/img.md', 'r', encoding='utf-8') as f:
    prompt_content = f.read().strip()

print(f"[提示词] 长度: {len(prompt_content)} 字符")
print(f"[提示词] 内容预览: {prompt_content[:100]}...\n")

conn = http.client.HTTPSConnection(API_HOST)
payload = json.dumps({
   "prompt": prompt_content,
   "n": 1,
   "model": IMG_MODEL,
   "size": "1024x1024"
})
headers = {
   'Authorization': f'Bearer {API_KEY}',
   'Content-Type': 'application/json'
}

print("[请求] 正在调用图片生成API...")
conn.request("POST", "/v1/images/generations", payload, headers)
res = conn.getresponse()
data = res.read()
conn.close()

print(f"[响应] HTTP状态码: {res.status}\n")

try:
    response_json = json.loads(data.decode("utf-8"))
    print(json.dumps(response_json, indent=2, ensure_ascii=False))
    
    # 创建输出目录
    output_dir = "generated_images"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        print(f"\n[初始化] 创建目录: {output_dir}")
    
    # 保存图片
    if res.status == 200 and 'data' in response_json:
        for idx, image_data in enumerate(response_json['data']):
            if 'url' in image_data:
                # 如果返回的是URL
                image_url = image_data['url']
                print(f"\n[图片URL] {image_url}")
                print("[提示] 请手动下载图片,或使用requests库自动下载")
            elif 'b64_json' in image_data:
                # 如果返回的是base64编码的图片
                image_base64 = image_data['b64_json']
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"method_diagram_{timestamp}_{idx+1}.png"
                filepath = os.path.join(output_dir, filename)
                
                # 解码并保存
                image_bytes = base64.b64decode(image_base64)
                with open(filepath, 'wb') as img_file:
                    img_file.write(image_bytes)
                
                print(f"\n[保存成功] 图片已保存到: {filepath}")
                print(f"[文件大小] {len(image_bytes) / 1024:.2f} KB")
    else:
        print("\n[错误] 图片生成失败或响应格式异常")
        
except json.JSONDecodeError as e:
    print(f"\n[JSON解析错误] {e}")
    print(f"[原始响应] {data.decode('utf-8')}")
except Exception as e:
    print(f"\n[异常] {type(e).__name__}: {str(e)}")