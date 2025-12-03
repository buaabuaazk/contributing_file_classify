import os

# 定义文件夹路径
sheets_dir = "data/sheets_500"
md_dir = "data/md"

# 获取 sheets_500 中所有文件的名称（不含后缀）
sheets_files = os.listdir(sheets_dir)
sheets_names = set()
for f in sheets_files:
    if os.path.isfile(os.path.join(sheets_dir, f)):
        name_without_ext = os.path.splitext(f)[0]
        sheets_names.add(name_without_ext)

# 获取 md 中所有文件的名称（不含后缀）
md_files = os.listdir(md_dir)
md_names = set()
for f in md_files:
    if os.path.isfile(os.path.join(md_dir, f)):
        name_without_ext = os.path.splitext(f)[0]
        md_names.add(name_without_ext)

# 找出在 sheets_500 中但不在 md 中的文件
missing_in_md = sheets_names - md_names

print(f"总共在 data/sheets_500 中: {len(sheets_names)} 个文件")
print(f"总共在 data/md 中: {len(md_names)} 个文件")
print()

if missing_in_md:
    print(f"不符合规律的文件（在 sheets_500 中但不在 md 中）: {len(missing_in_md)} 个")
    print("-" * 60)
    for name in sorted(missing_in_md):
        print(name)
else:
    print("✓ 所有文件都符合规律！")
