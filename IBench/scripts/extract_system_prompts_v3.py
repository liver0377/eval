"""
直接按行处理，精确删除三个指定部分
"""

import json
import os
import re
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
print(f"目标: 提取前 {limit} 个唯一的系统提示词（移除原子化槽位表、指令强制执行逻辑、输出格式规范）\n")

try:
    with open(input_file, 'r', encoding='utf-8') as f:
        dataset = json.load(f)
        
    print(f"[OK] 数据加载成功，共 {len(dataset)} 个条目\n")
    
    if isinstance(dataset, list):
        for i, item in enumerate(dataset, 1):
            if i % 10 == 0:
                print(f"已处理 {i} 个条目，找到 {len(unique_prompts)} 个唯一提示词...")
            
            system_prompt = item.get('system', '')
            
            if system_prompt and system_prompt not in unique_prompts:
                # 清理系统提示词
                lines = system_prompt.split('\n')
                cleaned_lines = []
                skip_until_next_section = False
                in_code_block = False
                section_to_skip = None
                
                for line in lines:
                    # 检查是否是要跳过的部分的开始标记
                    if '原子化槽位表' in line and 'Slot Schema' in line:
                        skip_until_next_section = True
                        section_to_skip = 'slot'
                        continue
                    
                    if '【指令强制执行逻辑' in line and 'Override' in line:
                        skip_until_next_section = True
                        section_to_skip = 'override'
                        continue
                    
                    if '输出格式规范：' in line:
                        skip_until_next_section = True
                        section_to_skip = 'format'
                        continue
                    
                    # 如果正在跳过某个部分
                    if skip_until_next_section:
                        # 检查是否到达该部分的结束
                        # 原子化槽位表部分：到硬性执行指标或获客策略结束
                        if section_to_skip == 'slot' and ('硬性执行指标' in line or '获客与拒绝策略' in line):
                            skip_until_next_section = False
                            section_to_skip = None
                        
                        # Override部分：到代码块或文档结束
                        elif section_to_skip == 'override' and ('```' in line or line.strip() == ''):
                            skip_until_next_section = False
                            section_to_skip = None
                        
                        # 格式规范部分：到代码块结束
                        elif section_to_skip == 'format' and '```' in line:
                            skip_until_next_section = False
                            section_to_skip = None
                        
                        continue
                    
                    # 如果不在删除模式，添加该行
                    if not skip_until_next_section:
                        cleaned_lines.append(line)
                
                # 清理多余的空行
                cleaned_prompt = '\n'.join(cleaned_lines)
                cleaned_prompt = re.sub(r'\n\n\n+', '\n\n', cleaned_prompt)
                
                # 统计对话轮数
                conversations = item.get('conversations', [])
                turn_count = len([c for c in conversations if c.get('from') == 'human'])
                
                unique_prompts[cleaned_prompt] = {
                    'index': len(unique_prompts) + 1,
                    'first_seen_index': i,
                    'conversations_count': len(conversations),
                    'turn_count': turn_count
                }
                
                if len(unique_prompts) >= limit:
                    print(f"[OK] 已找到 {limit} 个唯一提示词，停止提取")
                    break

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
    f.write(f"**总数据量**: {len(dataset)}个条目\n")
    f.write(f"**字段名称**: `system`\n")
    f.write(f"**处理说明**: 已移除原子化槽位表、指令强制执行逻辑、输出格式规范三个部分\n\n")
    f.write("---\n\n")
    
    # 写入每个提示词
    for idx, (prompt, metadata) in enumerate(unique_prompts.items(), 1):
        f.write(f"## 提示词 #{idx}\n\n")
        f.write(f"**首次出现位置**: 第{metadata['first_seen_index']}个条目\n")
        f.write(f"**对话消息数**: {metadata['conversations_count']}条\n")
        f.write(f"**对话轮次数**: {metadata['turn_count']}轮\n\n")
        
        # 提取第一行作为概要
        first_line = prompt.split('\n')[0] if prompt else ""
        if first_line and first_line.strip():
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

    # 验证：检查是否还有要删除的内容
    with open(output_file, 'r', encoding='utf-8') as f:
        verify_content = f.read()
    
    checks = {
        '原子化槽位表': '原子化槽位表' in verify_content or 'Slot Schema' in verify_content,
        '指令强制执行逻辑': '指令强制执行逻辑' in verify_content or '【指令强制执行逻辑' in verify_content,
        '输出格式规范': '输出格式规范' in verify_content or 'thought: 思考过程' in verify_content
    }
    
    print("\n验证结果:")
    all_ok = True
    for name, found in checks.items():
        status = "[OK]" if not found else "[FAIL]"
        print(f"  {status} {name}: {'已成功删除' if not found else '仍存在'}")
        if found:
            all_ok = False
    
    if all_ok:
        print("\n[SUCCESS] 所有指定部分已成功删除！")
    else:
        print("\n[WARNING] 部分内容未能完全删除，请手动检查")
    
    # 显示第1个提示词的部分内容
    print(f"\n第1个提示词预览（前60行）:")
    lines = verify_content.split('\n')
    in_first_prompt = False
    line_count = 0
    for line in lines:
        if line.startswith('## 提示词 #1'):
            in_first_prompt = True
        if in_first_prompt:
            print(line)
            line_count += 1
            if line_count >= 60:
                print("...")
                break
            elif line.startswith('---'):
                break

except Exception as e:
    print(f"[!] 错误: {e}")
