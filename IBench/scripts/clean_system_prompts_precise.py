"""
精确修改系统提示词文档，删除代码块内的指定部分
"""

import re
from pathlib import Path

# 输入文件
input_file = Path("docs/system_prompts_collection.md")

print(f"正在处理文件: {input_file}")

with open(input_file, 'r', encoding='utf-8') as f:
    lines = f.readlines()

# 处理每一行，标记是否在要删除的区块中
output_lines = []
skip_mode = False
skip_depth = 0  # 代码块嵌套深度

for i, line in enumerate(lines):
    # 检查是否是要删除的部分
    if re.search(r'原子化槽位表.*Slot Schema.*[:：]', line):
        skip_mode = True
        continue
    
    if '【指令强制执行逻辑' in line:
        skip_mode = True
        continue
    
    if re.search(r'输出格式规范：', line):
        skip_mode = True
        continue
    
    # 检查代码块标记
    if line.strip() == '```':
        if skip_mode:
            skip_mode = False  # 退出删除模式
        else:
            output_lines.append(line)
        continue
    
    # 如果不在删除模式，添加该行
    if not skip_mode:
        output_lines.append(line)

# 清理多余的空行（连续超过2个空行的情况）
content = ''.join(output_lines)
content = re.sub(r'\n\n\n+', '\n\n', content)

# 保存修改后的文件
with open(input_file, 'w', encoding='utf-8') as f:
    f.write(content)

print(f"[OK] 文件已修改: {input_file}")

# 统计信息
prompt_count = content.count('## 提示词 #')
print(f"\n统计信息:")
print(f"  提示词数量: {prompt_count}")
print(f"  文件大小: {len(content) / 1024:.2f} KB")

# 验证：检查是否还有要删除的内容
checks = {
    '原子化槽位表': '原子化槽位表' in content or 'Slot Schema' in content,
    '指令强制执行逻辑': '指令强制执行逻辑' in content or 'Override' in content,
    '输出格式规范': '输出格式规范' in content or 'thought: 思考过程' in content
}

print(f"\n验证结果:")
for name, found in checks.items():
    status = "[FAIL]" if found else "[OK]"
    print(f"  {status} {name}: {'仍存在' if found else '已删除'}")

# 显示第1个提示词的完整内容
print(f"\n第1个提示词完整内容预览:")
in_first_prompt = False
line_count = 0
for line in content.split('\n'):
    if line.startswith('## 提示词 #1'):
        in_first_prompt = True
    if in_first_prompt:
        print(line)
        line_count += 1
        if line_count > 50:  # 只显示前50行
            print("...")
            break
