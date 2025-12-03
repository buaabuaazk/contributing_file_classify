import os
import docx

# ============ 配置区域 ============
# 设置输入和输出目录
INPUT_DIR = "data/docx_493"
OUTPUT_DIR = "data/txt_493"
# ==================================

# 创建输出目录（如果不存在）
if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR)
    print(f"[初始化] 创建输出目录: {OUTPUT_DIR}\n")

# 获取所有 docx 文件
docx_files = sorted([f for f in os.listdir(INPUT_DIR) if f.endswith(('.doc', '.docx'))])

print(f"开始处理 {len(docx_files)} 个文档文件...\n")

success_count = 0
failed_count = 0

for doc_file in docx_files:
    input_path = os.path.join(INPUT_DIR, doc_file)
    
    # 生成输出文件名
    output_filename = os.path.splitext(doc_file)[0] + ".txt"
    output_path = os.path.join(OUTPUT_DIR, output_filename)
    
    try:
        # 读取 Word 文档
        doc = docx.Document(input_path)
        
        # 提取所有段落，包括空段落以保留原始结构
        paragraphs = []
        for para in doc.paragraphs:
            text = para.text.rstrip()  # 只去除右侧空格，保留左侧缩进
            paragraphs.append(text)  # 即使是空段落也保留
        
        # 写入 txt 文件，保持原始段落结构
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(paragraphs))
        
        success_count += 1
        print(f"[成功] {doc_file} -> {output_filename}")
        
    except Exception as e:
        failed_count += 1
        print(f"[失败] {doc_file}: {str(e)}")

print(f"\n" + "=" * 60)
print(f"✓ 转换完成！")
print(f"成功: {success_count} 个")
print(f"失败: {failed_count} 个")
print(f"输出目录: {OUTPUT_DIR}")