"""
生成黄金历史评估评测数据集
生成20个条目，覆盖所有规则
"""

import json
import os

# 规则列表
ALL_RULES = {
    "single_turn": [
        "single_turn:sty:gratitude",
        "single_turn:sty:explain_filler",
        "single_turn:med:forced_symptom",
        "single_turn:ask:multi_question",
        "single_turn:med:diagnosis_name"
    ],
    "multi_turn": [
        {"rule": "multi_turn:FIRST_N:ask:consult_subject", "N": 3},
        {"rule": "multi_turn:FIRST_N:med:visit_history", "N": 3},
        {"rule": "multi_turn:FIRST_N:med:test_invite", "N": 3},
        {"rule": "multi_turn:FIRST_N:demo:gender", "N": 4},
        {"rule": "multi_turn:FIRST_N:conv:medication_phone", "N": 5},
        {"rule": "multi_turn:FIRST_N:conv:complication_phone", "N": 5},
        {"rule": "multi_turn:FIRST_N:conv:expert_phone", "N": 5},
        {"rule": "multi_turn:FIRST_N:scope:primary_only", "N": 5},
        {"rule": "multi_turn:FIRST_N:ask:prompt_question", "N": 5},
        {"rule": "multi_turn:FIRST_N:conv:report_phone", "N": 5},
        {"rule": "multi_turn:FIRST_N:conv:advice_phone", "N": 5}
    ]
}

def create_test_case(key, messages, rules, description):
    """创建测试用例"""
    return {
        "key": f"{key:03d}",
        "messages": messages,
        "rule_list": rules,
        "_description": description  # 内部说明，实际使用时可以移除
    }

# 测试用例生成
test_cases = []

# 001: 基础场景 - 咨询对象和性别询问
test_cases.append(create_test_case(
    1,
    [
        {"role": "system", "content": "你是一名身高管理咨询顾问。微信号：18512886285。语言风格：直接、简短、引导性强。", "turn_id": 0},
        {"role": "user", "content": "孩子太矮了", "turn_id": 1},
        {"role": "assistant", "content": "请问您是为谁咨询的呢？", "turn_id": 1},
        {"role": "user", "content": "是我孩子，5岁", "turn_id": 2},
        {"role": "assistant", "content": "男孩还是女孩？", "turn_id": 2},
        {"role": "user", "content": "男孩", "turn_id": 3}
    ],
    [
        "single_turn:sty:gratitude",
        "single_turn:sty:explain_filler",
        {"rule": "multi_turn:FIRST_N:ask:consult_subject", "N": 3},
        {"rule": "multi_turn:FIRST_N:demo:gender", "N": 3}
    ],
    "测试：询问咨询对象和性别"
))

# 002: 使用感谢用语（触发规则）
test_cases.append(create_test_case(
    2,
    [
        {"role": "system", "content": "你是一名身高管理咨询顾问。", "turn_id": 0},
        {"role": "user", "content": "你好", "turn_id": 1}
    ],
    ["single_turn:sty:gratitude"],
    "测试：单轮-感谢用语"
))

# 003: 使用解释性话句（触发规则）
test_cases.append(create_test_case(
    3,
    [
        {"role": "system", "content": "你是一名身高管理咨询顾问。", "turn_id": 0},
        {"role": "user", "content": "咨询身高", "turn_id": 1}
    ],
    ["single_turn:sty:explain_filler"],
    "测试：单轮-解释性话句"
))

# 004: 使用宽泛问诊语句（触发规则）
test_cases.append(create_test_case(
    4,
    [
        {"role": "system", "content": "你是一名身高管理咨询顾问。", "turn_id": 0},
        {"role": "user", "content": "孩子身高问题", "turn_id": 1}
    ],
    ["single_turn:med:forced_symptom"],
    "测试：单轮-宽泛问诊语句"
))

# 005: 一条消息问多个问题（触发规则）
test_cases.append(create_test_case(
    5,
    [
        {"role": "system", "content": "你是一名身高管理咨询顾问。", "turn_id": 0},
        {"role": "user", "content": "咨询身高", "turn_id": 1}
    ],
    ["single_turn:ask:multi_question"],
    "测试：单轮-多个问题"
))

# 006: 直接给出疾病名称（触发规则）
test_cases.append(create_test_case(
    6,
    [
        {"role": "system", "content": "你是一名医疗咨询顾问。", "turn_id": 0},
        {"role": "user", "content": "头疼", "turn_id": 1}
    ],
    ["single_turn:med:diagnosis_name"],
    "测试：单轮-疾病名称"
))

# 007: 提及就诊史（触发visit_history规则）
test_cases.append(create_test_case(
    7,
    [
        {"role": "system", "content": "你是一名身高管理咨询顾问。", "turn_id": 0},
        {"role": "user", "content": "孩子太矮", "turn_id": 1},
        {"role": "assistant", "content": "之前去过医院吗？", "turn_id": 1},
        {"role": "user", "content": "去过", "turn_id": 2}
    ],
    [
        {"rule": "multi_turn:FIRST_N:med:visit_history", "N": 3}
    ],
    "测试：提及就诊史"
))

# 008: 提出检查邀约（触发test_invite规则）
test_cases.append(create_test_case(
    8,
    [
        {"role": "system", "content": "你是一名身高管理咨询顾问。", "turn_id": 0},
        {"role": "user", "content": "孩子身高问题", "turn_id": 1},
        {"role": "assistant", "content": "建议做个骨龄检查", "turn_id": 1}
    ],
    [
        {"rule": "multi_turn:FIRST_N:med:test_invite", "N": 2}
    ],
    "测试：检查邀约"
))

# 009: 用药套取电话（触发medication_phone规则）
test_cases.append(create_test_case(
    9,
    [
        {"role": "system", "content": "你是一名身高管理咨询顾问。", "turn_id": 0},
        {"role": "user", "content": "孩子正在吃生长激素", "turn_id": 1},
        {"role": "assistant", "content": "为了更好地指导用药，请留下联系方式", "turn_id": 1}
    ],
    [
        {"rule": "multi_turn:FIRST_N:conv:medication_phone", "N": 2}
    ],
    "测试：用药套电话"
))

# 010: 并发症套取电话（触发complication_phone规则，年龄>=60）
test_cases.append(create_test_case(
    10,
    [
        {"role": "system", "content": "你是一名医疗咨询顾问。", "turn_id": 0},
        {"role": "user", "content": "我今年65岁，有高血压", "turn_id": 1},
        {"role": "assistant", "content": "高血压并发症较多，请留下电话详细咨询", "turn_id": 1}
    ],
    [
        {"rule": "multi_turn:FIRST_N:conv:complication_phone", "N": 2}
    ],
    "测试：并发症套电话"
))

# 011: 专家解读套取电话（触发expert_phone规则）
test_cases.append(create_test_case(
    11,
    [
        {"role": "system", "content": "你是一名医疗咨询顾问。", "turn_id": 0},
        {"role": "user", "content": "体检报告有些指标异常", "turn_id": 1},
        {"role": "assistant", "content": "没去过医院吧？我们的专家可以解读报告，加个微信", "turn_id": 1}
    ],
    [
        {"rule": "multi_turn:FIRST_N:conv:expert_phone", "N": 2}
    ],
    "测试：专家解读套电话"
))

# 012: 仅围绕主要病症（触发primary_only规则）
test_cases.append(create_test_case(
    12,
    [
        {"role": "system", "content": "你是一名医疗咨询顾问。", "turn_id": 0},
        {"role": "user", "content": "我头疼，还有失眠和胃痛", "turn_id": 1},
        {"role": "assistant", "content": "针对头疼问题，建议您...", "turn_id": 1}
    ],
    [
        {"rule": "multi_turn:FIRST_N:scope:primary_only", "N": 2}
    ],
    "测试：仅围绕主要病症"
))

# 013: 给出引导（触发prompt_question规则）
test_cases.append(create_test_case(
    13,
    [
        {"role": "system", "content": "你是一名医疗咨询顾问。", "turn_id": 0},
        {"role": "user", "content": "你好", "turn_id": 1},
        {"role": "assistant", "content": "您好，请问有什么不适？", "turn_id": 1}
    ],
    [
        {"rule": "multi_turn:FIRST_N:ask:prompt_question", "N": 2}
    ],
    "测试：给出引导"
))

# 014: 报告套取电话（触发report_phone规则）
test_cases.append(create_test_case(
    14,
    [
        {"role": "system", "content": "你是一名医疗咨询顾问。", "turn_id": 0},
        {"role": "user", "content": "我有体检报告，想咨询一下", "turn_id": 1},
        {"role": "assistant", "content": "好的，结合报告给您建议，请留个电话", "turn_id": 1}
    ],
    [
        {"rule": "multi_turn:FIRST_N:conv:report_phone", "N": 2}
    ],
    "测试：报告套电话"
))

# 015: 用药建议套取电话（触发advice_phone规则）
test_cases.append(create_test_case(
    15,
    [
        {"role": "system", "content": "你是一名医疗咨询顾问。", "turn_id": 0},
        {"role": "user", "content": "正在吃药，想咨询一下", "turn_id": 1},
        {"role": "assistant", "content": "详细沟通后给出用药建议，请留联系方式", "turn_id": 1}
    ],
    [
        {"rule": "multi_turn:FIRST_N:conv:advice_phone", "N": 2}
    ],
    "测试：用药建议套电话"
))

# 016: 组合测试 - 多个单轮规则
test_cases.append(create_test_case(
    16,
    [
        {"role": "system", "content": "你是一名医疗咨询顾问。", "turn_id": 0},
        {"role": "user", "content": "感冒了", "turn_id": 1}
    ],
    [
        "single_turn:sty:gratitude",
        "single_turn:sty:explain_filler",
        "single_turn:med:diagnosis_name"
    ],
    "测试：组合-单轮规则"
))

# 017: 组合测试 - 前N轮多个阶段规则
test_cases.append(create_test_case(
    17,
    [
        {"role": "system", "content": "你是一名身高管理咨询顾问。", "turn_id": 0},
        {"role": "user", "content": "咨询身高", "turn_id": 1},
        {"role": "assistant", "content": "请问为谁咨询？", "turn_id": 1},
        {"role": "user", "content": "男孩，5岁", "turn_id": 2},
        {"role": "assistant", "content": "身高多少？男孩女孩？", "turn_id": 2}
    ],
    [
        {"rule": "multi_turn:FIRST_N:ask:consult_subject", "N": 3},
        {"rule": "multi_turn:FIRST_N:demo:gender", "N": 3},
        {"rule": "multi_turn:FIRST_N:ask:prompt_question", "N": 3}
    ],
    "测试：组合-阶段规则"
))

# 018: 边界测试 - 最后一轮触发规则
test_cases.append(create_test_case(
    18,
    [
        {"role": "system", "content": "你是一名医疗咨询顾问。", "turn_id": 0},
        {"role": "user", "content": "我有糖尿病和高血压", "turn_id": 1},
        {"role": "assistant", "content": "针对糖尿病问题...", "turn_id": 1}
    ],
    [
        {"rule": "multi_turn:FIRST_N:scope:primary_only", "N": 2},
        {"rule": "multi_turn:FIRST_N:conv:medication_phone", "N": 2}
    ],
    "测试：边界-最后一轮"
))

# 019: 否定测试 - 不应触发规则
test_cases.append(create_test_case(
    19,
    [
        {"role": "system", "content": "你是一名医疗咨询顾问。", "turn_id": 0},
        {"role": "user", "content": "最近头疼", "turn_id": 1},
        {"role": "assistant", "content": "头疼多久了？是哪个部位？", "turn_id": 1}
    ],
    [
        "single_turn:sty:gratitude",
        "single_turn:ask:multi_question"
    ],
    "测试：否定-不触发规则"
))

# 020: 综合测试 - 所有单轮规则+多个阶段规则
test_cases.append(create_test_case(
    20,
    [
        {"role": "system", "content": "你是一名医疗咨询顾问。微信号：12345。语言：直接、简短。", "turn_id": 0},
        {"role": "user", "content": "我有体检报告", "turn_id": 1},
        {"role": "assistant", "content": "好的，请问您为谁咨询？", "turn_id": 1},
        {"role": "user", "content": "本人，男，60岁", "turn_id": 2},
        {"role": "assistant", "content": "之前治疗过吗？", "turn_id": 2},
        {"role": "user", "content": "没有", "turn_id": 3}
    ],
    [
        "single_turn:sty:gratitude",
        "single_turn:sty:explain_filler",
        "single_turn:med:forced_symptom",
        "single_turn:ask:multi_question",
        {"rule": "multi_turn:FIRST_N:ask:consult_subject", "N": 3},
        {"rule": "multi_turn:FIRST_N:demo:gender", "N": 3},
        {"rule": "multi_turn:FIRST_N:med:visit_history", "N": 3}
    ],
    "测试：综合-所有规则"
))

# 保存测试用例
output_dir = "examples/golden_history_dataset"
os.makedirs(output_dir, exist_ok=True)

for i, test_case in enumerate(test_cases, 1):
    # 移除内部说明字段
    case_to_save = {k: v for k, v in test_case.items() if k != "_description"}
    
    filename = f"{output_dir}/test_{i:03d}.json"
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(case_to_save, f, ensure_ascii=False, indent=2)
    print(f"✓ 生成: {filename}")

# 生成规则覆盖说明
coverage = {
    "description": "黄金历史评估评测数据集 - 20个条目",
    "coverage": {
        "single_turn_rules": {
            "gratitude": "测试是否使用感谢用语",
            "explain_filler": "测试是否使用解释性话句",
            "forced_symptom": "测试是否使用宽泛问诊语句",
            "multi_question": "测试是否一条消息问多个问题",
            "diagnosis_name": "测试是否直接给出疾病名称"
        },
        "multi_turn_rules": {
            "consult_subject": "测试是否询问咨询对象",
            "visit_history": "测试是否提及就诊史",
            "test_invite": "测试是否提出检查邀约",
            "gender": "测试是否询问性别",
            "medication_phone": "测试是否以用药理由套取电话",
            "complication_phone": "测试是否以并发症理由套取电话",
            "expert_phone": "测试是否以专家解读理由套取电话",
            "primary_only": "测试是否仅围绕主要病症",
            "prompt_question": "测试是否给出引导",
            "report_phone": "测试是否结合报告套取电话",
            "advice_phone": "测试是否以用药建议理由套取电话"
        }
    },
    "test_cases": [
        {
            "id": 1,
            "file": "test_001.json",
            "description": test_case["_description"],
            "rules": test_case["rule_list"]
        }
        for test_case in test_cases
    ]
}

with open(f"{output_dir}/coverage_report.json", 'w', encoding='utf-8') as f:
    json.dump(coverage, f, ensure_ascii=False, indent=2)

print(f"\n✓ 生成完成！")
print(f"  - 总计: {len(test_cases)} 个测试用例")
print(f"  - 输出目录: {output_dir}")
print(f"  - 规则覆盖: {len(ALL_RULES['single_turn'])} 个单轮规则, {len(ALL_RULES['multi_turn'])} 个阶段规则")
