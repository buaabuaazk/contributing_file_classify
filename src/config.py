"""
配置模块 - 从环境变量读取敏感信息
"""
import os
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
                    key, value = line.split('=', 1)
                    os.environ[key.strip()] = value.strip()

# 在模块导入时自动加载
load_env()

# API 配置
API_KEY = os.getenv('API_KEY', '')
API_HOST = os.getenv('API_HOST', 'api.chatanywhere.tech')
API_MODEL = os.getenv('API_MODEL', 'gpt-5-nano')

# 图片生成配置
IMG_MODEL = os.getenv('IMG_MODEL', 'dall-e-3')

# 验证关键配置
if not API_KEY:
    raise ValueError(
        "❌ API_KEY 未配置！\n"
        "请在项目根目录创建 .env 文件，添加以下内容：\n"
        "    API_KEY=your_api_key_here\n"
        "或设置环境变量：\n"
        "    export API_KEY=your_api_key_here"
    )

if __name__ == '__main__':
    print("✅ 配置已加载")
    print(f"API_HOST: {API_HOST}")
    print(f"API_MODEL: {API_MODEL}")
    print(f"IMG_MODEL: {IMG_MODEL}")
    print(f"API_KEY: {'*' * len(API_KEY)} (长度: {len(API_KEY)})")
