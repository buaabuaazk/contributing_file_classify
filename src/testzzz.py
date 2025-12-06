import os
from openai import OpenAI
import openai
import requests
import time
import json
from pathlib import Path

# 加载 .env 文件
def load_env():
    """从项目根目录读取 .env 文件"""
    env_path = Path(__file__).parent.parent / ".env"
    if env_path.exists():
        with open(env_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    if '=' in line:
                        key, value = line.split('=', 1)
                        os.environ[key.strip()] = value.strip()

# 加载环境变量
load_env()

# 从环境变量读取配置
API_zhizengzeng_KEY = os.getenv('API_zhizengzeng_KEY', '')
BASE_URL = os.getenv('BASE_URL_zhizengzeng', 'https://api.zhizengzeng.com/v1/')

if not API_zhizengzeng_KEY:
    raise ValueError("请在 .env 文件中配置 API_zhizengzeng_KEY")

# chat
def chat_completions3(query):
    client = OpenAI(api_key=API_zhizengzeng_KEY, base_url=BASE_URL)
    resp = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": query}
        ]
    )
    print(resp)
    #print(resp.choices[0].message.content)

# chat with other model
def chat_completions4(query):
    client = OpenAI(api_key=API_zhizengzeng_KEY, base_url=BASE_URL)
    resp = client.chat.completions.create(
        model="deepseek-chat",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": query}
        ]
    )
    print(resp)
    print(resp.choices[0].message.content)

# 多轮对话函数
def multi_turn_chat():
    client = OpenAI(api_key=API_zhizengzeng_KEY, base_url=BASE_URL)
    
    # 维护对话历史
    messages = [
        {"role": "system", "content": "You are a helpful assistant."}
    ]
    
    print("多轮对话开始（输入 'quit' 退出）\n")
    
    while True:
        user_input = input("用户: ")
        if user_input.lower() == 'quit':
            break
        
        # 添加用户消息
        messages.append({"role": "user", "content": user_input})
        
        # 调用API
        resp = client.chat.completions.create(
            model="deepseek-chat",
            messages=messages
        )
        
        # 获取助手回复
        assistant_message = resp.choices[0].message.content
        print(f"助手: {assistant_message}\n")
        
        # 将助手回复添加到历史中
        messages.append({"role": "assistant", "content": assistant_message})

# 调用函数测试
if __name__ == "__main__":
    # 单轮对话示例
    print("=== 单轮对话测试 ===")
    print("测试 gpt-3.5-turbo:")
    chat_completions3("Hello, how are you?")
    
    print("\n" + "="*50 + "\n")
    
    # 多轮对话示例
    print("=== 多轮对话测试 ===")
    multi_turn_chat()