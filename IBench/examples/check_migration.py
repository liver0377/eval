"""
规则ID到规则名称迁移检查器
扫描代码库，查找所有使用规则ID的地方，并提供迁移建议
"""

import os
import re
from pathlib import Path

def find_files_to_scan(directory: str, extensions: list[str] = None) -> list[str]:
    """查找需要扫描的文件"""
    if extensions is None:
        extensions = ['.py', '.md']
    
    files = []
    for root, dirs, filenames in os.walk(directory):
        # 跳过虚拟环境和缓存目录
        dirs[:] = [d for d in dirs if d not in ['__pycache__', '.git', 'venv', 'env']]
        
        for filename in filenames:
            if any(filename.endswith(ext) for ext in extensions):
                files.append(os.path.join(root, filename))
    
    return files

def scan_file_for_rule_ids(filepath: str) -> list[dict]:
    """扫描文件，查找使用规则ID的模式"""
    results = []
    
    with open(filepath, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # 规则ID到名称的映射
    single_rule_mapping = {
        '1': 'emotional_comfort',
        '2': 'explanatory_statements',
        '3': 'symptom_inquiry',
        '4': 'multiple_questions',
        '5': 'disease_diagnosis'
    }
    
    stage_rule_mapping = {
        '1': 'inquire_consultation_target',
        '2': 'mention_visit_history',
        '3': 'examination_invitation',
        '4': 'inquire_gender',
        '5': 'collect_phone_medication',
        '6': 'collect_phone_complication',
        '7': 'collect_phone_expert_interpretation'
    }
    
    all_rule_mapping = {**single_rule_mapping, **stage_rule_mapping}
    
    # 模式1: single_rule_turns = {1: [1, 2, 3]}
    pattern1 = re.compile(r'(single_rule_turns|stage_rule_turns)\s*=\s*\{[^}]*\d+[^}]*\}')
    
    # 模式2: get_rule(\d+) 或 get_rule("rule_name")
    pattern2 = re.compile(r'get_rule\((\d+|\"[^\"]+\")\)')
    
    # 模式3: evaluate_rule(rule_id=\d+)
    pattern3 = re.compile(r'evaluate_rule\([^)]*\b(\d+)\b[^)]*\)')
    
    # 模式4: [1, 2, 3] 或 ["rule1", "rule2"]
    pattern4 = re.compile(r'\[([^\]]*(?:\d+|"[^"]+")[^\]]*)\]')
    
    for line_num, line in enumerate(lines, 1):
        # 检查single_rule_turns或stage_rule_turns配置
        if 'single_rule_turns' in line or 'stage_rule_turns' in line:
            matches = pattern1.findall(line)
            if matches:
                results.append({
                    'line': line_num,
                    'type': 'config',
                    'content': line.strip(),
                    'severity': 'error'
                })
        
        # 检查get_rule调用
        matches = pattern2.findall(line)
        for match in matches:
            if match.isdigit():  # 如果是数字ID
                rule_name = all_rule_mapping.get(match, 'UNKNOWN')
                results.append({
                    'line': line_num,
                    'type': 'get_rule_call',
                    'content': line.strip(),
                    'rule_id': match,
                    'suggested_name': rule_name,
                    'severity': 'error'
                })
        
        # 检查evaluate_rule调用
        matches = pattern3.findall(line)
        for match in matches:
            rule_name = all_rule_mapping.get(match, 'UNKNOWN')
            results.append({
                'line': line_num,
                'type': 'evaluate_rule_call',
                'content': line.strip(),
                'rule_id': match,
                'suggested_name': rule_name,
                'severity': 'error'
            })
    
    return results

def print_results(filepath: str, results: list[dict]):
    """打印扫描结果"""
    if not results:
        print(f"✓ {filepath}: 无问题")
        return
    
    print(f"\n{'='*60}")
    print(f"文件: {filepath}")
    print(f"{'='*60}")
    
    for result in results:
        icon = "❌" if result['severity'] == 'error' else "⚠️"
        print(f"\n{icon} 行 {result['line']}: {result['type']}")
        print(f"   代码: {result['content']}")
        
        if 'suggested_name' in result and result['suggested_name'] != 'UNKNOWN':
            print(f"   建议: 将规则ID {result['rule_id']} 替换为 '{result['suggested_name']}'")
        elif result['type'] == 'config':
            print(f"   建议: 将配置中的数字ID替换为规则名称")

def main():
    """主函数"""
    print("="*60)
    print("规则ID迁移检查器")
    print("="*60)
    print("\n扫描代码库，查找所有使用规则ID的地方...\n")
    
    # 获取项目根目录
    project_root = Path(__file__).parent.parent
    print(f"项目根目录: {project_root}")
    
    # 查找需要扫描的文件
    print("\n正在扫描文件...")
    files = find_files_to_scan(str(project_root))
    print(f"找到 {len(files)} 个文件\n")
    
    # 扫描每个文件
    total_issues = 0
    for filepath in files:
        results = scan_file_for_rule_ids(filepath)
        if results:
            print_results(filepath, results)
            total_issues += len(results)
    
    # 打印总结
    print("\n" + "="*60)
    print("扫描总结")
    print("="*60)
    print(f"扫描文件数: {len(files)}")
    print(f"发现问题数: {total_issues}")
    
    if total_issues == 0:
        print("\n✓ 所有问题已解决！")
        print("\n建议：")
        print("1. 运行测试: python examples/test_rule_names.py")
        print("2. 查看文档: RULE_NAME_MAPPING.md")
    else:
        print(f"\n⚠️ 发现 {total_issues} 个需要迁移的问题")
        print("\n迁移步骤：")
        print("1. 根据上述建议替换规则ID为规则名称")
        print("2. 运行测试验证: python examples/test_rule_names.py")
        print("3. 查看完整映射: RULE_NAME_MAPPING.md")
        print("\n快速映射表：")
        print("  单轮规则: 1->emotional_comfort, 2->explanatory_statements,")
        print("            3->symptom_inquiry, 4->multiple_questions, 5->disease_diagnosis")
        print("  阶段规则: 1->inquire_consultation_target, 2->mention_visit_history,")
        print("            3->examination_invitation, 4->inquire_gender,")
        print("            5->collect_phone_medication, 6->collect_phone_complication,")
        print("            7->collect_phone_expert_interpretation")

if __name__ == "__main__":
    main()
