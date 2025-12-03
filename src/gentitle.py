import os
import re

# 定义文件夹路径
md_dir = "data/md_500"
output_dir = "data/title_500"

# 创建输出目录（如果不存在）
if not os.path.exists(output_dir):
    os.makedirs(output_dir)
    print(f"[初始化] 创建目录: {output_dir}\n")

# 获取所有 markdown 文件
md_files = sorted([f for f in os.listdir(md_dir) if f.endswith('.md')])

print(f"开始处理 {len(md_files)} 个 markdown 文件...\n")

def is_valid_markdown_title(line):
    """
    判断一行是否是有效的 Markdown 标题
    标题要求：
    1. 行首是 # (可以有0-3个空格缩进)
    2. # 后面必须有至少一个空格
    3. 排除代码块中的内容
    """
    stripped = line.lstrip()
    # 检查是否以 # 开头且后面跟空格
    if stripped.startswith('#'):
        # 找到第一个非 # 字符
        hash_count = 0
        for char in stripped:
            if char == '#':
                hash_count += 1
            else:
                break
        
        # 有效的标题：1-6个#，且后面跟空格
        if 1 <= hash_count <= 6:
            after_hashes = stripped[hash_count:]
            # 后面必须是空格开头（或者只有#没有内容）
            if len(after_hashes) == 0 or after_hashes[0] == ' ':
                return True
    
    return False

# 处理每个文件
for md_file in md_files:
    md_path = os.path.join(md_dir, md_file)
    
    try:
        with open(md_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        lines = content.split('\n')
        titles = []
        in_code_block = False
        code_block_pattern = re.compile(r'^```')
        
        for line in lines:
            # 检查是否进入或退出代码块
            if code_block_pattern.match(line.strip()):
                in_code_block = not in_code_block
                continue
            
            # 如果在代码块中，跳过
            if in_code_block:
                continue
            
            # 检查是否是有效的标题
            if is_valid_markdown_title(line):
                titles.append(line.strip())
        
        if titles:
            # 生成输出文件名（替换后缀为 .txt）
            output_filename = os.path.splitext(md_file)[0] + ".txt"
            output_path = os.path.join(output_dir, output_filename)
            
            # 写入标题到文件
            with open(output_path, 'w', encoding='utf-8') as out_f:
                for title in titles:
                    out_f.write(title + "\n")
        
    except Exception as e:
        print(f"[错误] 无法读取 {md_file}: {str(e)}")

print(f"✓ 完成！标题已写入 {output_dir} 文件夹")
