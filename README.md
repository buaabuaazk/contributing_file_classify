# LLM 文本分类与图像生成项目

一个基于大语言模型（LLM）的文本分类和图像生成工具，支持批量处理 Excel 数据、调用大模型进行分类、计算准确率，以及使用 DALL-E 生成图像。

## 快速开始

### 1. 配置环境

**安装依赖包：**

```bash
pip install -r requirements.txt
pip install python-docx openpyxl requests
```

### 2. 设置 API Key

在项目根目录创建 `.env` 文件，添加你的 API 密钥：

```bash
cp .env.example .env
# 然后编辑 .env 文件，填入你的 API Key
```

`.env` 文件内容示例：

```
API_KEY=your_actual_api_key_here
API_HOST=api.chatanywhere.tech
API_MODEL=gpt-5-nano
IMG_MODEL=dall-e-3
```

**或者直接设置环境变量：**

```bash
export API_KEY=your_actual_api_key_here
```

### 3. 运行脚本

#### 批量文本分类（推荐）

```bash
cd src
python flow.py
```

**特点：**
- 支持只处理指定文件（通过修改 `FILE_INDEX` 配置）
- 保存模型原始输出到 `model_outputs/` 
- 输出结果同时写入 `output.txt` 和终端
- 计算分类准确率

**配置选项（在 `flow.py` 中修改）：**

```python
FILE_INDEX = 8           # 只处理第 8 个 Excel 文件（None=处理所有）
OUTPUT_JSON_DIR = "model_outputs"  # 模型输出保存目录
```

#### 逐条分类（用于调试）

```bash
python onebyone.py
```

#### Word 文档转换

将 `std/raw/` 中的 `.doc` 文件转为 Markdown：

```bash
python cache.py
```

输出文件保存到 `std/converted/`

#### 图像生成

使用 DALL-E 生成图像：

```bash
python generateImg.py
```

输出图像保存到 `generated_images/`

## 项目结构

```
.
├── .env                    # API 配置（敏感信息，勿上传）
├── .gitignore              # Git 忽略规则
├── requirements.txt        # Python 依赖
├── README.md               # 项目文档
│
├── src/
│   ├── config.py           # 配置管理模块（读取环境变量）
│   ├── flow.py             # 主分类脚本（推荐使用）
│   ├── onebyone.py         # 逐条分类脚本
│   ├── flow1.py            # 备用分类脚本
│   ├── generateImg.py      # 图像生成脚本
│   ├── cache.py            # Word 文档转换脚本
│   ├── test.py             # 测试脚本
│   └── output.txt          # 脚本输出日志
│
├── resources/
│   └── prompts/
│       ├── prompt.md       # 文本分类提示词
│       └── img.md          # 图像生成提示词
│
├── std/                    # 数据源目录
│   ├── raw/                # 原始 Word 文档
│   ├── converted/          # 转换后的 Markdown 文件
│   └── *.xlsx              # Excel 分类数据源
│
├── model_outputs/          # 大模型原始输出（JSON）
└── generated_images/       # 生成的图像
```

## 数据格式说明

### Excel 数据源格式

每个 Excel 文件应包含以下列：

- **第 0 列**：待分类的文本段落
- **第 1-6 列**：分类标签（对应一个标签时在该列标记）
  - 第 1 列：CF（表示分类为 CF）
  - 第 2 列：CT
  - 第 3 列：TC
  - 第 4 列：BW
  - 第 5 列：DC
  - 第 6 列：SC

如果没有对应的标签，则为 NC（不分类）。

## 分类标签说明

| 标签 | 含义 |
|------|------|
| CF | - |
| CT | - |
| TC | - |
| BW | - |
| DC | - |
| SC | - |
| NC | 不分类 |
| NT | 不适用 |

*请根据实际项目补充各标签的具体含义*

## 输出结果解释

脚本会输出以下信息：

```
[配置] 处理所有 N 个文件

example.xlsx
["NC", "CF", "CT", ...]          # 标准答案（ground truth）
["NC", "CF", "CT", ...]          # 模型预测结果
[1, 1, 1, ...]                   # 对比结果（1=正确, 0=错误）
Accuracy: 0.8542                 # 分类准确率
```

## 常见问题

### Q: 如何替换 API Key？

A: 有两种方法：

1. 编辑 `.env` 文件：
   ```
   API_KEY=your_new_key_here
   ```

2. 设置环境变量：
   ```bash
   export API_KEY=your_new_key_here
   python src/flow.py
   ```

### Q: 如何只处理某个特定的 Excel 文件？

A: 在脚本中修改 `FILE_INDEX` 配置：

```python
FILE_INDEX = 3  # 只处理第 3 个文件（从 1 开始计数）
```

### Q: 什么是 `model_outputs/` 目录？

A: 该目录保存大模型的原始 JSON 输出，便于后续分析和调试。

### Q: 如何自定义分类提示词？

A: 编辑 `resources/prompts/prompt.md` 文件中的内容即可。

### Q: 为什么某些请求失败？

A: 检查以下几点：

1. `.env` 文件中的 `API_KEY` 是否正确
2. 网络连接是否正常
3. Excel 文件格式是否正确（没有合并单元格等）
4. 模型 API 配额是否充足

## 依赖包说明

| 包名 | 版本 | 用途 |
|------|------|------|
| pandas | 2.3.3 | Excel 数据读取 |
| python-docx | 最新 | Word 文档转换 |
| openpyxl | 最新 | Excel 引擎 |
| requests | 最新 | HTTP 请求（可选，用于下载生成的图像） |

## 安全提示 ⚠️

- **勿将 API Key 提交到版本控制系统！**
- 确保 `.env` 已添加到 `.gitignore`
- 定期检查 API 调用记录和账单
- 生产环境使用专用的服务账户

## 性能建议

- 单次批处理超过 100 个段落时，建议分成多个 Excel 文件
- 如果请求超时，可以增加 Python 脚本中的超时设置
- 大批量处理时，考虑添加重试机制和速率限制

## 扩展与自定义

### 修改分类标签

编辑 `src/flow.py` 中的 `category_columns` 字典：

```python
category_columns = {1: "YOUR_NEW_LABEL", 2: "ANOTHER_LABEL", ...}
```

### 调整模型参数

在 `.env` 中或直接修改脚本中的 API 调用：

```python
payload = json.dumps({
    "model": API_MODEL,
    "temperature": 0.7,  # 调整创意度（0-1）
    "messages": [...]
})
```

## 许可证

MIT License

## 维护者

如有问题或建议，请联系项目维护者。

---

**最后更新**：2025年11月29日
