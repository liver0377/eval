r"""
从新数据源提取系统提示词并生成文档
数据源：C:\Users\wudw\Documents\company\tmp\normal_dataset.json
"""

import json
import os
from pathlib import Path
from collections import OrderedDict

# 新数据源路径
input_file = r"C:\Users\wudw\Documents\company\tmp\normal_dataset.json"
# 输出文件路径
output_dir = Path("docs")
output_file = output_dir / "system_prompts_collection.md"

# 用于存储唯一的系统提示词
unique_prompts = OrderedDict()
limit = 20  # 提取前20个

print(f"正在读取文件: {input_file}")
print(f"目标: 提取前 {limit} 个唯一的系统提示词\n")

dataset = None
try:
    with open(input_file, 'r', encoding='utf-8') as f:
        dataset = json.load(f)
        
    print(f"[OK] 数据加载成功，类型: {type(dataset)}")
    
    # 检查数据结构
    if isinstance(dataset, list):
        print(f"[OK] 数据是列表格式，共 {len(dataset)} 个条目")
        
        for i, item in enumerate(dataset, 1):
            if i % 10 == 0:
                print(f"已处理 {i} 个条目，找到 {len(unique_prompts)} 个唯一提示词...")
            
            # 提取 system 字段
            system_prompt = item.get('system', '')
            
            if system_prompt and system_prompt not in unique_prompts:
                # 统计对话轮数
                conversations = item.get('conversations', [])
                # 计算轮次（human+gpt为一对）
                turn_count = len([c for c in conversations if c.get('from') == 'human'])
                
                unique_prompts[system_prompt] = {
                    'index': len(unique_prompts) + 1,
                    'first_seen_index': i,
                    'conversations_count': len(conversations),
                    'turn_count': turn_count
                }
                
                if len(unique_prompts) >= limit:
                    print(f"[OK] 已找到 {limit} 个唯一提示词，停止提取")
                    break
    
    else:
        print(f"[!] 数据格式不支持: {type(dataset)}")

except json.JSONDecodeError as e:
    print(f"[!] JSON解析错误: {e}")
except Exception as e:
    print(f"[!] 读取文件错误: {e}")
    import traceback
    traceback.print_exc()

print(f"\n[OK] 成功提取 {len(unique_prompts)} 个唯一系统提示词\n")

# 生成Markdown文档
os.makedirs(output_dir, exist_ok=True)

with open(output_file, 'w', encoding='utf-8') as f:
    # 写入标题和说明
    f.write("# 系统提示词集合\n\n")
    f.write(f"**数据来源**: `{input_file}`\n")
    f.write(f"**提取日期**: 2026年2月5日\n")
    f.write(f"**提取数量**: 前{len(unique_prompts)}个唯一系统提示词\n")
    if isinstance(dataset, list):
        f.write(f"**总数据量**: {len(dataset)}个条目\n")
    f.write(f"**字段名称**: `system`\n\n")
    f.write("---\n\n")
    
    # 写入每个提示词
    for idx, (prompt, metadata) in enumerate(unique_prompts.items(), 1):
        f.write(f"## 提示词 #{idx}\n\n")
        f.write(f"**首次出现位置**: 第{metadata['first_seen_index']}个条目\n")
        f.write(f"**对话消息数**: {metadata['conversations_count']}条\n")
        f.write(f"**对话轮次数**: {metadata['turn_count']}轮\n\n")
        
        # 提取第一行作为概要
        first_line = prompt.split('\n')[0] if prompt else ""
        if first_line:
            f.write(f"### 概要\n\n{first_line}\n\n")
        
        # 提取关键词来判断类型
        if "角色设定" in prompt:
            f.write(f"### 类型\n\n结构化角色设定提示词\n\n")
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

try:
    file_size = output_file.stat().st_size
    print(f"[OK] 文档已生成: {output_file}")
    print(f"  文件大小: {file_size / 1024:.2f} KB")

    # 生成简要统计
    print("\n统计信息:")
    if isinstance(dataset, list):
        print(f"  总数据量: {len(dataset)}个条目")
    print(f"  唯一提示词数: {len(unique_prompts)}")
    if isinstance(dataset, list):
        coverage = len(unique_prompts) / len(dataset) * 100
        print(f"  覆盖率: {coverage:.2f}%")

    # 显示前3个提示词的概要
    print("\n前3个提示词概要:")
    for idx, (prompt, metadata) in enumerate(list(unique_prompts.items())[:3], 1):
        first_line = prompt.split('\n')[0] if prompt else ""
        print(f"  #{idx}: {first_line[:80]}...")
        
except Exception as e:
    print(f"[!] 文档生成错误: {e}")
