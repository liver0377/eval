"""
JSON Context Evaluator 使用示例
演示如何使用JsonContextEvaluator评估对话
"""

from IBench.pipeline.json_context_evaluator import JsonContextEvaluator
from IBench.models.model_configs import Config
import os


def example_single_evaluation():
    """示例1：评估单个JSON文件"""
    print("="*60)
    print("示例1：评估单个JSON文件")
    print("="*60)

    # 初始化评估器
    evaluator = JsonContextEvaluator(
        local_model_path="./models/qwen3-8b",
        api_key=os.getenv("DASHSCOPE_API_KEY")
    )

    # 评估JSON文件
    input_path = "examples/json_input_example.json"
    output_path = "examples/json_output_example.json"

    result = evaluator.evaluate_from_json(
        input_json_path=input_path,
        output_json_path=output_path
    )

    # 打印结果
    print("\n评估结果：")
    print(f"对话ID: {result['conversation_id']}")
    print(f"System Prompt: {result['system_prompt'][:50]}...")
    print(f"总轮次: {len(result['evaluations'])}")

    for eval_data in result['evaluations']:
        print(f"\n轮次 {eval_data['turn_id']}:")
        print(f"  回复: {eval_data['response'][:100]}...")
        print(f"  规则评估:")
        for rule_result in eval_data['rule_results']:
            print(f"    - {rule_result['rule']}: {rule_result['passed']} (得分: {rule_result['score']})")
            print(f"      kwargs: {rule_result['kwargs']}")
            print(f"      原因: {rule_result['reason']}")


def example_batch_evaluation():
    """示例2：批量评估多个JSON文件"""
    print("\n" + "="*60)
    print("示例2：批量评估多个JSON文件")
    print("="*60)

    # 初始化评估器
    evaluator = JsonContextEvaluator(
        local_model_path="./models/qwen3-8b",
        api_key=os.getenv("DASHSCOPE_API_KEY")
    )

    # 批量评估
    input_files = [
        "examples/json_input_example.json",
        # "examples/json_input_example2.json",
        # "examples/json_input_example3.json",
    ]

    results = evaluator.evaluate_batch_from_json(
        input_json_paths=input_files,
        output_dir="examples/output"
    )

    print(f"\n批量评估完成，共处理 {len(results)} 个文件")


def example_custom_rules():
    """示例3：使用自定义规则配置"""
    print("\n" + "="*60)
    print("示例3：自定义规则配置")
    print("="*60)

    # 你可以动态创建不同的规则配置
    from IBench.rules.dynamic_rule_registry import DynamicRuleRegistry

    registry = DynamicRuleRegistry()

    # 查看所有可用的策略
    policies = registry.list_all_policies()
    print(f"\n可用策略: {policies}")

    # 查看特定策略下的所有规则
    if "policy_universe" in policies:
        rules = registry.list_rules_by_policy("policy_universe")
        print(f"\npolicy_universe 下的规则:")
        for rule in rules:
            parsed = registry.parse_rule(rule)
            print(f"  - {rule}")
            print(f"    类型: {parsed.type}, 分数: {parsed.score}")
            print(f"    触发轮次: {parsed.trigger_turns}")


def example_create_custom_json():
    """示例4：创建自定义JSON输入"""
    print("\n" + "="*60)
    print("示例4：创建自定义JSON输入")
    print("="*60)

    import json

    # 创建自定义JSON
    custom_data = {
        "conversation_id": "custom_001",
        "conversation_history": [
            {"role": "user", "content": "你好，我想咨询一下", "turn_id": 1},
            {"role": "user", "content": "是为孩子咨询的", "turn_id": 2},
        ],
        "system_prompt": "你是一名专业的医疗咨询助手...",
        "rules": {
            "single_turn": [
                "multi_turn:policy_universe:inquire_target",
                "multi_turn:policy_universe:ask_gender",
            ]
        }
    }

    # 保存到文件
    output_path = "examples/custom_input.json"
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(custom_data, f, ensure_ascii=False, indent=2)

    print(f"\n自定义JSON已创建: {output_path}")

    # 评估它
    evaluator = JsonContextEvaluator(
        local_model_path="./models/qwen3-8b",
        api_key=os.getenv("DASHSCOPE_API_KEY")
    )

    result = evaluator.evaluate_from_json(
        input_json_path=output_path,
        output_json_path="examples/custom_output.json"
    )

    print("评估完成！")


def main():
    """运行所有示例"""
    print("JSON Context Evaluator 使用示例\n")

    try:
        # 示例1：单个文件评估
        # example_single_evaluation()

        # 示例2：批量评估
        # example_batch_evaluation()

        # 示例3：查看规则
        example_custom_rules()

        # 示例4：自定义JSON
        # example_create_custom_json()

    except Exception as e:
        print(f"\n错误: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
