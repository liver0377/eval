"""
生成80个测试用例的脚本
基于20条系统提示词，每条生成4个测试用例
"""
import json
import re
from pathlib import Path
from typing import Dict, List, Any

# 解析系统提示词文件
def parse_system_prompts(file_path: str) -> List[Dict[str, Any]]:
    """
    解析系统提示词文件，提取关键信息
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # 按提示词分割
    prompt_blocks = re.split(r'## 提示词 #(\d+)', content)[1:]  # 跳过第一个空块

    prompts = []
    for i in range(0, len(prompt_blocks), 2):
        if i + 1 < len(prompt_blocks):
            prompt_num = int(prompt_blocks[i])
            prompt_content = prompt_blocks[i + 1]

            # 提取系统提示词内容（在```代码块中）
            code_match = re.search(r'```\n(.*?)\n```', prompt_content, re.DOTALL)
            if code_match:
                system_prompt = code_match.group(1).strip()

                # 提取关键信息
                info = {
                    'id': prompt_num,
                    'system_prompt': system_prompt,
                    'first_contact_turn': extract_first_contact_turn(system_prompt),
                    'max_questions_per_turn': extract_max_questions(system_prompt),
                    'has_mental_test': '心理' in system_prompt or '焦虑' in system_prompt or '测试题' in system_prompt,
                    'hospital_name': extract_hospital_name(system_prompt),
                    'phone': extract_phone(system_prompt),
                }
                prompts.append(info)

    return prompts

def extract_first_contact_turn(prompt: str) -> int:
    """提取首次留联触发轮次"""
    # 查找类似"当对话进行到第 X 轮时"的模式
    patterns = [
        r'第\s*(\d+)\s*轮.*留联',
        r'第\s*(\d+)\s*轮.*启动.*留联',
    ]
    for pattern in patterns:
        match = re.search(pattern, prompt)
        if match:
            return int(match.group(1))
    return 5  # 默认值

def extract_max_questions(prompt: str) -> int:
    """提取每轮最多提问数"""
    patterns = [
        r'每.*轮.*提问.*?(\d+)\s*个问题',
        r'提问.*?(\d+)\s*个问题',
    ]
    for pattern in patterns:
        match = re.search(pattern, prompt)
        if match:
            return int(match.group(1))
    return 2  # 默认值

def extract_hospital_name(prompt: str) -> str:
    """提取医院名称"""
    # 常见医院名称模式
    patterns = [
        r'（(.*?医院.*?)）',
        r'\((.*?医院.*?)\)',
    ]
    for pattern in patterns:
        matches = re.findall(pattern, prompt)
        if matches:
            return matches[0]
    return "医院"

def extract_phone(prompt: str) -> str:
    """提取电话号码"""
    # 提取电话号码
    pattern = r'(\d{11}|\d{3,4}-\d{7,8})'
    matches = re.findall(pattern, prompt)
    if matches:
        return matches[0]
    return "电话号码"

# 生成测试用例
def generate_test_case_01_single_turn_rules(prompt_info: Dict, case_id: str) -> Dict:
    """
    测试用例1：新增单轮规则触发
    测试formula, punctuation, list规则
    """
    messages = [
        {
            "role": "system",
            "content": prompt_info['system_prompt'],
            "turn_id": 0
        },
        {
            "role": "user",
            "content": "孩子注意力不集中，上课走神怎么办？",
            "turn_id": 1
        },
        {
            "role": "assistant",
            "content": "感谢您的咨询，为了更好地为您服务，我需要了解以下情况：1. 孩子年龄 2. 具体症状 3. 持续时间",
            "turn_id": 1
        },
        {
            "role": "user",
            "content": "10岁，上课走神，作业拖拉，已经半年了",
            "turn_id": 2
        },
        {
            "role": "assistant",
            "content": "针对这种情况，我们通常称之为\"注意力缺陷\"，需要专业评估",
            "turn_id": 2
        },
        {
            "role": "user",
            "content": "那需要怎么治疗呢？",
            "turn_id": 3
        }
    ]

    rule_list = [
        "single_turn:sty:formula",
        "single_turn:sty:punctuation",
        "single_turn:sty:list",
        "single_turn:sty:gratitude",
        "single_turn:sty:explain_filler",
        "single_turn:med:forced_symptom",
        "single_turn:ask:multi_question",
    ]

    return {
        "key": case_id,
        "messages": messages,
        "rule_list": rule_list
    }

def generate_test_case_02_conversion_rules(prompt_info: Dict, case_id: str) -> Dict:
    """
    测试用例2：转化规则触发
    测试留联、降级、挽留
    """
    contact_turn = prompt_info['first_contact_turn']
    # 确保不超过5轮
    contact_turn = min(contact_turn, 5)

    messages = [
        {
            "role": "system",
            "content": prompt_info['system_prompt'],
            "turn_id": 0
        },
        {
            "role": "user",
            "content": "孩子心理有问题，很焦虑",
            "turn_id": 1
        },
        {
            "role": "assistant",
            "content": "了解情况，请问孩子多大了？是男孩女孩？",
            "turn_id": 1
        },
        {
            "role": "user",
            "content": "12岁男孩",
            "turn_id": 2
        },
        {
            "role": "assistant",
            "content": "具体有什么表现呢？",
            "turn_id": 2
        },
        {
            "role": "user",
            "content": "不爱说话，总是一个人呆着",
            "turn_id": 3
        },
        {
            "role": "assistant",
            "content": "为了给您详细指导建议，请留个电话",
            "turn_id": 3
        },
        {
            "role": "user",
            "content": "不方便留电话",
            "turn_id": 4
        },
        {
            "role": "assistant",
            "content": "那加个微信也行，方便后续沟通",
            "turn_id": 4
        },
        {
            "role": "user",
            "content": "微信也不方便",
            "turn_id": 5
        }
    ]

    rule_list = [
        {"rule": "multi_turn:FIRST_N:conv:medication_phone", "N": contact_turn},
        {"rule": "multi_turn:N_th:conv:ask_wechat", "N": 4},
        {"rule": "multi_turn:N_th:conv:final_detainment", "N": 5},
        "single_turn:ask:multi_question",
        {"rule": "multi_turn:FIRST_N:ask:consult_subject", "N": 2},
    ]

    return {
        "key": case_id,
        "messages": messages,
        "rule_list": rule_list
    }

def generate_test_case_03_termination_rule(prompt_info: Dict, case_id: str) -> Dict:
    """
    测试用例3：终止红线触发
    测试未获取联系方式前主动结束对话
    """
    messages = [
        {
            "role": "system",
            "content": prompt_info['system_prompt'],
            "turn_id": 0
        },
        {
            "role": "user",
            "content": "孩子不爱学习，成绩下降",
            "turn_id": 1
        },
        {
            "role": "assistant",
            "content": "请问孩子年龄和性别？",
            "turn_id": 1
        },
        {
            "role": "user",
            "content": "10岁男孩",
            "turn_id": 2
        },
        {
            "role": "assistant",
            "content": "了解，建议多关注孩子心理状态",
            "turn_id": 2
        },
        {
            "role": "user",
            "content": "好的",
            "turn_id": 3
        },
        {
            "role": "assistant",
            "content": "好的，祝您顺利",
            "turn_id": 3
        },
        {
            "role": "user",
            "content": "谢谢",
            "turn_id": 4
        }
    ]

    rule_list = [
        {"rule": "multi_turn:FIRST_N:conv:leave", "N": 4},
        {"rule": "multi_turn:FIRST_N:demo:gender", "N": 3},
        "single_turn:sty:gratitude",
    ]

    return {
        "key": case_id,
        "messages": messages,
        "rule_list": rule_list
    }

def generate_test_case_04_special_strategy(prompt_info: Dict, case_id: str) -> Dict:
    """
    测试用例4：特殊转化策略
    测试net_limit, mental_test等
    """
    # 根据提示词特性选择策略
    has_mental_test = prompt_info['has_mental_test']

    if has_mental_test:
        # 心理测试策略
        messages = [
            {
                "role": "system",
                "content": prompt_info['system_prompt'],
                "turn_id": 0
            },
            {
                "role": "user",
                "content": "孩子很焦虑，怎么办？",
                "turn_id": 1
            },
            {
                "role": "assistant",
                "content": "请先告诉我孩子的年龄和性别？",
                "turn_id": 1
            },
            {
                "role": "user",
                "content": "13岁女孩",
                "turn_id": 2
            },
            {
                "role": "assistant",
                "content": "具体表现是什么？",
                "turn_id": 2
            },
            {
                "role": "user",
                "content": "总担心考试，睡不着",
                "turn_id": 3
            },
            {
                "role": "assistant",
                "content": "我们可以先发送一份焦虑初步测试题，您留个联系方式？",
                "turn_id": 3
            },
            {
                "role": "user",
                "content": "测试题要钱吗？",
                "turn_id": 4
            }
        ]

        rule_list = [
            {"rule": "multi_turn:FIRST_N:conv:mental_test", "N": 5},
            {"rule": "multi_turn:FIRST_N:ask:consult_subject", "N": 2},
            "single_turn:ask:multi_question",
        ]
    else:
        # 网络打字限制策略
        messages = [
            {
                "role": "system",
                "content": prompt_info['system_prompt'],
                "turn_id": 0
            },
            {
                "role": "user",
                "content": "孩子注意力不集中",
                "turn_id": 1
            },
            {
                "role": "assistant",
                "content": "请问孩子年龄和性别？",
                "turn_id": 1
            },
            {
                "role": "user",
                "content": "9岁男孩",
                "turn_id": 2
            },
            {
                "role": "assistant",
                "content": "网络打字说不清楚，能留个电话详细跟您说吗？",
                "turn_id": 2
            },
            {
                "role": "user",
                "content": "不想留电话",
                "turn_id": 3
            },
            {
                "role": "assistant",
                "content": "打字太慢了，说不清楚，电话沟通更高效",
                "turn_id": 3
            },
            {
                "role": "user",
                "content": "还是不方便",
                "turn_id": 4
            }
        ]

        rule_list = [
            {"rule": "multi_turn:FIRST_N:sty:net_limit", "N": 5},
            {"rule": "multi_turn:FIRST_N:demo:gender", "N": 3},
            "single_turn:ask:multi_question",
        ]

    return {
        "key": case_id,
        "messages": messages,
        "rule_list": rule_list
    }

def generate_all_test_cases():
    """生成所有80个测试用例"""
    # 解析系统提示词
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    system_prompts_file = project_root / "docs" / "system_prompts_collection.md"
    prompts = parse_system_prompts(str(system_prompts_file))

    print(f"解析到 {len(prompts)} 条系统提示词")

    # 生成测试用例
    test_cases = []

    for prompt_info in prompts:
        prompt_id = prompt_info['id']
        print(f"生成提示词 #{prompt_id} 的测试用例...")

        # 4个测试用例
        case_01 = generate_test_case_01_single_turn_rules(prompt_info, f"{prompt_id:03d}_01")
        case_02 = generate_test_case_02_conversion_rules(prompt_info, f"{prompt_id:03d}_02")
        case_03 = generate_test_case_03_termination_rule(prompt_info, f"{prompt_id:03d}_03")
        case_04 = generate_test_case_04_special_strategy(prompt_info, f"{prompt_id:03d}_04")

        test_cases.extend([case_01, case_02, case_03, case_04])

    return test_cases

def save_to_jsonl(test_cases: List[Dict], output_path: str):
    """保存为JSONL格式"""
    with open(output_path, 'w', encoding='utf-8') as f:
        for case in test_cases:
            f.write(json.dumps(case, ensure_ascii=False) + '\n')

    print(f"\n已生成 {len(test_cases)} 个测试用例")
    print(f"输出文件: {output_path}")

def main():
    """主函数"""
    print("="*60)
    print("生成80个测试用例")
    print("="*60)

    # 生成测试用例
    test_cases = generate_all_test_cases()

    # 保存为JSONL到data/dataset目录
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    output_dir = project_root / "data" / "dataset"
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = str(output_dir / "golden_history_input.jsonl")
    save_to_jsonl(test_cases, output_path)

    # 统计信息
    print("\n测试用例统计:")
    print(f"  总数: {len(test_cases)}")
    print(f"  单轮规则触发: {len([c for c in test_cases if c['key'].endswith('_01')])}")
    print(f"  转化规则触发: {len([c for c in test_cases if c['key'].endswith('_02')])}")
    print(f"  终止红线触发: {len([c for c in test_cases if c['key'].endswith('_03')])}")
    print(f"  特殊策略触发: {len([c for c in test_cases if c['key'].endswith('_04')])}")

    # 验证格式
    print("\n验证测试用例格式...")
    for i, case in enumerate(test_cases[:3]):  # 验证前3个
        print(f"\n测试用例 {case['key']}:")
        print(f"  消息数: {len(case['messages'])}")
        print(f"  规则数: {len(case['rule_list'])}")
        print(f"  最后一条消息角色: {case['messages'][-1]['role']}")

if __name__ == "__main__":
    main()
