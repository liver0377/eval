"""
重写：精确删除系统提示词中的三个指定部分
"""

import re
from pathlib import Path

# 输入文件
input_file = Path("docs/system_prompts_collection.md")

print(f"正在处理文件: {input_file}")

with open(input_file, 'r', encoding='utf-8') as f:
    content = f.read()

# 分割成各个提示词
prompt_blocks = re.split(r"(?=\n## 提示词 #\d+\n)", content)

# 处理每个提示词块
cleaned_blocks = []
for i, block in enumerate(prompt_blocks, 1):
    if not block.strip():
        continue
    
    # 删除原子化槽位表部分（包括标题和内容）
    # 从标题到硬性执行指标或获客策略之前
    block = re.sub(r'原子化槽位表 \(Slot Schema\):.*?(?=\n\n硬性执行指标|\n\n获客与拒绝策略|\n\n###)', '', block, flags=re.DOTALL)
    
    # 删除残留的原子化槽位表列表项（- 开头的行）
    # 这需要删除整个列表块
    lines = block.split('\n')
    cleaned_lines = []
    skip_next = False
    
    for line in lines:
        # 跳过原子化槽位表相关的行
        if re.search(r'^- (age|gender|name|phone|wechat|symptom|duration|medical_history|relationship|基础信息|联系方式|医疗信息|规则)', line):
            skip_next = True
            continue
        
        # 跳过空行（如果之前跳过了内容）
        if skip_next and line.strip() == '':
            continue
        
        # 重置跳过标记
        if not re.search(r'^- ', line):
            skip_next = False
        
        cleaned_lines.append(line)
    
    block = '\n'.join(cleaned_lines)
    
    # 删除【指令强制执行逻辑】部分
    block = re.sub(r'【指令强制执行逻辑 \(Override\)】.*?(?=\n\n```|\n\n---)', '', block, flags=re.DOTALL)
    
    # 删除输出格式规范部分
    block = re.sub(r'输出格式规范：.*?(?=\n\n```)', '', block, flags=re.DOTALL)
    
    # 清理多余空行
    block = re.sub(r'\n\n\n+', '\n\n', block)
    
    if block.strip():
        # 添加回提示词编号（如果是第一个块需要添加标题）
        if i == 1:
            # 第一个块应该已经有标题了
            pass
        else:
            # 恢复提示词编号
            block = f"\n## 提示词 #{i}\n\n{block}"
        
        cleaned_blocks.append(block)

# 合并所有块
final_content = ''.join(cleaned_blocks)

# 保存修改后的文件
with open(input_file, 'w', encoding='utf-8') as f:
    f.write(final_content)

print(f"[OK] 文件已修改: {input_file}")

# 统计信息
prompt_count = final_content.count('## 提示词 #')
print(f"\n统计信息:")
print(f"  提示词数量: {prompt_count}")
print(f"  文件大小: {len(final_content) / 1024:.2f} KB")

# 验证
checks = {
    '原子化槽位表': '原子化槽位表' in final_content or 'Slot Schema' in final_content,
    '指令强制执行逻辑': '指令强制执行逻辑' in final_content or 'Override' in final_content,
    '输出格式规范': '输出格式规范' in final_content or 'thought: 思考过程' in final_content
}

print(f"\n验证结果:")
for name, found in checks.items():
    status = "[FAIL]" if found else "[OK]"
    print(f"  {status} {name}: {'仍存在' if found else '已删除'}")

# 显示第1个提示词的部分内容
print(f"\n第1个提示词预览（前50行）:")
lines = final_content.split('\n')
for i, line in enumerate(lines):
    if i >= 50:
        print("...")
        break
    print(line)
