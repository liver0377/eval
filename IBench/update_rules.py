import json
import os

# Read system_prompt.json
with open(r'C:\Users\wudw\Documents\company\eval\IBench\data\dataset\tmp\system_prompt.json', 'r', encoding='utf-8') as f:
    system_prompt = json.load(f)

# Directory path
dir_path = r'C:\Users\wudw\Documents\company\eval\IBench\data\dataset\tmp\sub_template'

# Get all JSON files
files = [f for f in os.listdir(dir_path) if f.endswith('.json')]

print(f'Found {len(files)} JSON files')
print(f'System prompt structure:')
for key in system_prompt.keys():
    print(f'  {key}: {len(system_prompt[key])} rules')

for filename in files[:3]:  # Process first 3 files
    file_path = os.path.join(dir_path, filename)
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    print(f'\nFile: {filename}')
    print(f'  rule_list: {data.get("rule_list", [])}')
    
    # Extract role设定 and 语言风格 sections
    content = data['messages'][0]['content']
    if '角色设定：' in content and '[语言风格与去AI味规范]' in content:
        role_part = content.split('[语言风格与去AI味规范]')[0].strip()
        print(f'  role_part: {role_part[:50]}...')
