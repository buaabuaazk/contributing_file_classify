import os
import subprocess
import sys

# 调整路径以便访问数据文件
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.chdir(project_root)  # 将工作目录改为项目根目录

# 设置目标目录
raw_dir = "std/raw"
output_dir = "std/converted"  # 转换后的文件保存目录

# 创建输出目录
if not os.path.exists(output_dir):
    os.makedirs(output_dir)
    print(f"[初始化] 创建目录: {output_dir}\n")

# 检查目录是否存在
if not os.path.exists(raw_dir):
    print(f"[错误] 目录不存在: {raw_dir}")
    exit(1)

# 获取目录下所有.doc文件
files = [f for f in os.listdir(raw_dir) if f.endswith('.doc') and os.path.isfile(os.path.join(raw_dir, f))]

print(f"[信息] 找到 {len(files)} 个.doc文件")

# ============ 配置区域 ============
# 设置要处理的文件
# None = 处理所有文件
# 整数 = 只处理第N个文件 (例如: FILE_INDEX = 1 只处理第1个文件, 从1开始计数)
FILE_INDEX = None  # 处理所有文件
# ==================================

# 根据配置选择要处理的文件
if FILE_INDEX is not None:
    if FILE_INDEX < 1 or FILE_INDEX > len(files):
        print(f"[配置错误] FILE_INDEX={FILE_INDEX} 超出范围 (1-{len(files)})")
        exit(1)
    files = [files[FILE_INDEX - 1]]  # 从1开始计数,转换为0索引
    print(f"[配置] 只处理第 {FILE_INDEX} 个文件: {files[0]}\n")
else:
    print(f"[配置] 处理所有 {len(files)} 个文件\n")

print("[提示] 需要安装 pandoc 或 python-docx 库来转换Word文件")
print("[提示] 安装命令: pip install python-docx\n")

try:
    import docx
    
    converted_count = 0
    failed_count = 0
    
    for filename in files:
        try:
            doc_path = os.path.join(raw_dir, filename)
            
            # 读取Word文档
            doc = docx.Document(doc_path)
            
            # 提取所有段落文本
            text_content = []
            for para in doc.paragraphs:
                if para.text.strip():
                    text_content.append(para.text)
            
            # 生成输出文件名
            name = os.path.splitext(filename)[0]
            md_filename = name + '.md'  # 改为.md后缀
            md_path = os.path.join(output_dir, md_filename)
            
            # 写入文本文件
            with open(md_path, 'w', encoding='utf-8') as f:
                f.write('\n\n'.join(text_content))
            
            print(f"[成功] {filename} -> {md_filename} ({len(text_content)} 个段落)")
            converted_count += 1
            
        except Exception as e:
            print(f"[失败] {filename}: {str(e)}")
            failed_count += 1
    
    print(f"\n[统计] 成功转换: {converted_count} 个")
    print(f"[统计] 失败: {failed_count} 个")
    print(f"[统计] 总计: {len(files)} 个")
    print(f"\n[输出] 文件已保存到: {output_dir}")
    
except ImportError:
    print("\n[错误] 未安装 python-docx 库")
    print("[解决] 请运行: pip install python-docx")
    print("\n或者使用 pandoc 转换:")
    print("[方案] 安装 pandoc: https://pandoc.org/installing.html")
    print("[命令] pandoc input.doc -o output.txt")