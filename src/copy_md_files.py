import os
import shutil

# 定义文件夹路径
md_dir = "data/md"
sheets_dir = "data/sheets_500"
output_dir = "data/md_500"

# 创建输出目录（如果不存在）
if not os.path.exists(output_dir):
    os.makedirs(output_dir)
    print(f"[初始化] 创建目录: {output_dir}\n")

# 获取 sheets_500 中所有文件的名称（不含后缀）
sheets_files = os.listdir(sheets_dir)
sheets_names = set()
for f in sheets_files:
    if os.path.isfile(os.path.join(sheets_dir, f)):
        name_without_ext = os.path.splitext(f)[0]
        sheets_names.add(name_without_ext)

# 遍历 md 文件夹中的所有文件
md_files = os.listdir(md_dir)
copied_count = 0

for md_file in md_files:
    md_path = os.path.join(md_dir, md_file)
    
    if not os.path.isfile(md_path):
        continue
    
    # 获取文件名（不含后缀）
    name_without_ext = os.path.splitext(md_file)[0]
    
    # 检查是否在 sheets_500 中有同名文件
    if name_without_ext in sheets_names:
        # 复制文件到 md_500
        output_path = os.path.join(output_dir, md_file)
        try:
            shutil.copy2(md_path, output_path)
            copied_count += 1
        except Exception as e:
            print(f"[错误] 复制 {md_file} 失败: {str(e)}")

# 统计 md_500 中的文件数量
total_files = len([f for f in os.listdir(output_dir) if os.path.isfile(os.path.join(output_dir, f))])

print(f"✓ 完成！")
print(f"共复制: {copied_count} 个文件")
print(f"data/md_500 中的文件总数: {total_files}")
