"""
提取train.jsonl中的系统提示词并生成文档
"""

import json
import os
from pathlib import Path
from collections import OrderedDict

# 输入文件路径
input_file = r"C:\Users\wudw\Documents\data\train\train.jsonl"
# 输出文件路径
output_dir = Path("docs")
output_file = output_dir / "system_prompts_collection.md"

# 用于存储唯一的系统提示词
unique_prompts = OrderedDict()
limit = 20  # 提取前20个

print(f"正在读取文件: {input_file}")
print(f"目标: 提取前 {limit} 个唯一的系统提示词\n")

with open(input_file, 'r', encoding='utf-8') as f:
    for i, line in enumerate(f, 1):
        if i % 100 == 0:
            print(f"已处理 {i} 行，找到 {len(unique_prompts)} 个唯一提示词...")
        
        try:
            data = json.loads(line.strip())
            system_prompt = data.get('system_prompt', '')
            
            if system_prompt and system_prompt not in unique_prompts:
                unique_prompts[system_prompt] = {
                    'index': len(unique_prompts) + 1,
                    'first_seen_line': i,
                    'conversations_count': len(data.get('conversations', []))
                }
                
                if len(unique_prompts) >= limit:
                    print(f"[OK] 已找到 {limit} 个唯一提示词，停止读取")
                    break
        except json.JSONDecodeError as e:
            print(f"[!] 第 {i} 行JSON解析错误: {e}")
            continue

print(f"\n[OK] 成功提取 {len(unique_prompts)} 个唯一系统提示词\n")

# 生成Markdown文档
os.makedirs(output_dir, exist_ok=True)

with open(output_file, 'w', encoding='utf-8') as f:
    # 写入标题和说明
    f.write("# 系统提示词集合\n\n")
    f.write(f"**数据来源**: `{input_file}`\n")
    f.write(f"**提取日期**: 2026年2月5日\n")
    f.write(f"**提取数量**: 前{len(unique_prompts)}个唯一系统提示词\n")
    f.write(f"**总文件行数**: 8781\n\n")
    f.write("---\n\n")
    
    # 写入每个提示词
    for idx, (prompt, metadata) in enumerate(unique_prompts.items(), 1):
        f.write(f"## 提示词 #{idx}\n\n")
        f.write(f"**首次出现位置**: 第{metadata['first_seen_line']}行\n")
        f.write(f"**对话轮次**: {metadata['conversations_count']}轮\n\n")
        
        # 提取关键信息
        first_line = prompt.split('\n')[0] if prompt else ""
        if "角色设定" in prompt:
            f.write(f"### 类型\n\n角色设定类提示词\n\n")
        elif "你是" in prompt:
            f.write(f"### 类型\n\n角色定义类提示词\n\n")
        else:
            f.write(f"### 类型\n\n通用提示词\n\n")
        
        # 写入提示词内容，使用代码块格式
        f.write("### 内容\n\n")
        f.write("```\n")
        f.write(prompt)
        f.write("\n```\n\n")
        
        f.write("---\n\n")

print(f"[OK] 文档已生成: {output_file}")
print(f"  文件大小: {output_file.stat().st_size / 1024:.2f} KB")

# 生成简要统计
print("\n统计信息:")
print(f"  总行数: 8781")
print(f"  唯一提示词数: {len(unique_prompts)}")

# 显示前3个提示词的概要
print("\n前3个提示词概要:")
for idx, (prompt, metadata) in enumerate(list(unique_prompts.items())[:3], 1):
    # 提取第一句话作为概要
    first_line = prompt.split('\n')[0] if prompt else ""
    print(f"  #{idx}: {first_line[:80]}...")
