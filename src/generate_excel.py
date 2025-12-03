import os
from utils.export import create_analysis_file

# ============ 配置区域 ============
# 设置输出的 Excel 文件保存路径
OUTPUT_DIR = "data/genExcel_493"
# 设置输入文件夹和文件类型
INPUT_DIR = "data/txt_493"  # 可选: "data/md_500", "data/doc", "data/txt_493"
FILE_EXTENSION = ".txt"  # 可选: ".md", ".doc", ".txt"
# ==================================

# 获取指定文件夹中的所有文件
input_files = sorted([f for f in os.listdir(INPUT_DIR) if f.endswith(FILE_EXTENSION)])

# 创建输出目录（如果不存在）
if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR)
    print(f"[初始化] 创建输出目录: {OUTPUT_DIR}\n")

print(f"开始处理 {len(input_files)} 个文件...\n")

success_count = 0
failed_count = 0

# 处理所有文件
for idx, selected_file in enumerate(input_files, 1):
    input_filepath = os.path.join(INPUT_DIR, selected_file)
    
    # 生成输出文件路径
    output_filename = os.path.splitext(selected_file)[0] + ".xlsx"
    output_filepath = os.path.join(OUTPUT_DIR, output_filename)
    
    # 使用文件名（不含后缀）作为工作表名称
    worksheet_name = os.path.splitext(selected_file)[0]
    
    # 如果工作表名称超过 31 个字符，进行截断（Excel 限制）
    if len(worksheet_name) > 31:
        worksheet_name = worksheet_name[:31]
    
    # 调用函数生成 Excel 文件
    try:
        create_analysis_file(
            worksheet_name=worksheet_name,
            raw_filepath=input_filepath,
            spreadsheet_filepath=output_filepath
        )
        success_count += 1
        print(f"[成功] ({idx}/{len(input_files)}) {selected_file} -> {output_filename}")
    except Exception as e:
        failed_count += 1
        print(f"[失败] ({idx}/{len(input_files)}) {selected_file}: {str(e)}")

print(f"\n" + "=" * 60)
print(f"✓ 处理完成！")
print(f"成功: {success_count} 个")
print(f"失败: {failed_count} 个")
print(f"输出目录: {OUTPUT_DIR}")
