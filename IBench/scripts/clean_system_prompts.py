"""
修改系统提示词文档，删除指定部分
"""

import re
from pathlib import Path

# 输入文件
input_file = Path("docs/system_prompts_collection.md")
output_file = Path("docs/system_prompts_collection_clean.md")

# 定义要删除的部分标记
sections_to_remove = [
    r"原子化槽位表 \(Slot Schema\):.*?(?=硬性执行指标|获客与拒绝策略|```)",
    r"原子化槽位表.*?\(.*?\):.*?(?=硬性执行指标|获客与拒绝策略|```)",
    r"【指令强制执行逻辑 \(Override\)】.*?(?=```|$)",
    r"输出格式规范：.*?(?=```|$)"
]

print(f"正在处理文件: {input_file}")

with open(input_file, 'r', encoding='utf-8') as f:
    content = f.read()

# 处理每个提示词块
modified_count = 0

# 使用正则表达式删除指定的部分
# 1. 删除原子化槽位表（从该标题到下一个标题或代码块结束）
pattern1 = r'原子化槽位表 \(Slot Schema\):.*?(?=\n\n硬性执行指标|\n\n获客与拒绝策略|\n\n```)'
content = re.sub(pattern1, '', content, flags=re.DOTALL)

# 2. 删除指令强制执行逻辑
pattern2 = r'【指令强制执行逻辑 \(Override\)】.*?(?=\n\n```|\n\n---)'
content = re.sub(pattern2, '', content, flags=re.DOTALL)

# 3. 删除输出格式规范（从标题到代码块结束）
pattern3 = r'输出格式规范：.*?(?=\n\n```)'
content = re.sub(pattern3, '', content, flags=re.DOTALL)

# 4. 删除孤立的原子化槽位表标题行
pattern4 = r'原子化槽位表 \(Slot Schema\)：.*\n(?:\s+-+.*\n)*'
content = re.sub(pattern4, '', content)

# 5. 清理多余的空行（连续超过2个空行的情况）
content = re.sub(r'\n\n\n+', '\n\n', content)

# 保存修改后的文件
with open(output_file, 'w', encoding='utf-8') as f:
    f.write(content)

print(f"[OK] 文件已处理并保存: {output_file}")

# 统计删除的提示词数量
prompt_count = content.count('## 提示词 #')
print(f"\n统计信息:")
print(f"  提示词数量: {prompt_count}")
print(f"  文件大小: {len(content) / 1024:.2f} KB")

# 验证：检查是否还有要删除的内容
checks = {
    '原子化槽位表': '原子化槽位表' in content,
    '指令强制执行逻辑': '指令强制执行逻辑' in content,
    '输出格式规范': '输出格式规范' in content
}

print(f"\n验证结果:")
for name, found in checks.items():
    status = "[FAIL]" if found else "[OK]"
    print(f"  {status} {name}: {'仍存在' if found else '已删除'}")

# 显示前2个提示词的开头部分
print(f"\n前2个提示词预览:")
lines = content.split('\n')
current_prompt = 0
for i, line in enumerate(lines):
    if line.startswith('## 提示词 #'):
        current_prompt += 1
        if current_prompt <= 2:
            print(f"\n{line}")
            # 打印接下来的几行
            for j in range(i+1, min(i+10, len(lines))):
                print(lines[j])
            print("...")
        if current_prompt >= 2:
            break
