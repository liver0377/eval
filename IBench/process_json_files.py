import json
import os
import re

# 读取system_prompt.json
system_prompt_path = r"C:\Users\wudw\Documents\company\eval\IBench\data\dataset\tmp\system_prompt.json"
with open(system_prompt_path, 'r', encoding='utf-8') as f:
    system_prompt_data = json.load(f)

# 目标目录
target_dir = r"C:\Users\wudw\Documents\company\eval\IBench\data\dataset\tmp\sub_template"

def extract_role_setting(content):
    """提取角色设定部分（第一段）"""
    # 查找第一个换行符之前的内容
    lines = content.split('\n')
    for i, line in enumerate(lines):
        if line.strip() == '' and i > 0:
            return '\n'.join(lines[:i])
    return lines[0] if lines else ""

def get_rule_description(rule_key, rule_obj=None):
    """根据规则key获取描述，并替换{N}"""
    # 判断是single_turn还是multi_turn
    category = None
    if rule_key.startswith('single_turn'):
        category = "[语言风格与去AI味规范]"
    elif rule_key.startswith('multi_turn'):
        category = "[留联约束]"
    
    if not category:
        return None
    
    # 从system_prompt_data中获取描述
    if category in system_prompt_data and rule_key in system_prompt_data[category]:
        description = system_prompt_data[category][rule_key]
        
        # 如果有N值，替换{N}
        if rule_obj and isinstance(rule_obj, dict) and 'N' in rule_obj:
            n_value = rule_obj['N']
            description = description.replace('{N}', str(n_value))
        
        return description
    
    return None

def process_json_file(file_path):
    """处理单个JSON文件"""
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # 提取原始的role setting
    original_content = data['messages'][0]['content']
    role_setting = extract_role_setting(original_content)
    
    # 处理rule_list
    rule_list = data.get('rule_list', [])
    
    single_turn_rules = []
    multi_turn_rules = []
    
    for rule_item in rule_list:
        if isinstance(rule_item, str):
            # 简单字符串格式的规则
            rule_key = rule_item
            rule_obj = None
        elif isinstance(rule_item, dict):
            # 对象格式的规则
            rule_key = rule_item.get('rule', '')
            rule_obj = rule_item
        else:
            continue
        
        description = get_rule_description(rule_key, rule_obj)
        
        if description:
            if rule_key.startswith('single_turn'):
                single_turn_rules.append(description)
            elif rule_key.startswith('multi_turn'):
                multi_turn_rules.append(description)
    
    # 构建新的system消息
    new_content_parts = [role_setting]
    
    # 添加[语言风格与去AI味规范]
    if single_turn_rules:
        new_content_parts.append("\n[语言风格与去AI味规范]：")
        for i, rule_desc in enumerate(single_turn_rules, 1):
            new_content_parts.append(f"{i}. {rule_desc}")
    
    # 添加[留联约束]
    if multi_turn_rules:
        new_content_parts.append("\n[留联约束]：")
        for i, rule_desc in enumerate(multi_turn_rules, 1):
            new_content_parts.append(f"{i}. {rule_desc}")
    
    new_content = '\n'.join(new_content_parts)
    
    # 更新system消息
    data['messages'][0]['content'] = new_content
    
    # 保存文件
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
    
    print(f"已处理: {os.path.basename(file_path)}")

# 处理目录下所有JSON文件
json_files = [f for f in os.listdir(target_dir) if f.endswith('.json')]

print(f"找到 {len(json_files)} 个JSON文件")

for json_file in json_files:
    file_path = os.path.join(target_dir, json_file)
    process_json_file(file_path)

print("所有文件处理完成！")
