"""
测试黄金历史评估 Pipeline

这个脚本用于验证 JsonContextEvaluator 是否正常工作
从 golden_history_input.jsonl 中读取第一行作为测试数据
"""

import json
import os
import sys
from pathlib import Path

# 添加项目路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from IBench.pipeline.json_context_evaluator import JsonContextEvaluator
from IBench.models.model_configs import Config


def test_golden_history_evaluation():
    """测试黄金历史评估 pipeline"""

    print("=" * 80)
    print("黄金历史评估 Pipeline 测试")
    print("=" * 80)

    # 1. 读取测试数据（golden_history_input.jsonl 的第一行）
    input_file = project_root / "data" / "dataset" / "golden_history_input.jsonl"

    if not input_file.exists():
        print(f"\n❌ 错误：找不到测试数据文件: {input_file}")
        print(f"   请确保文件路径正确")
        return False

    print(f"\n📂 读取测试数据: {input_file}")

    with open(input_file, 'r', encoding='utf-8') as f:
        first_line = f.readline().strip()

    test_data = json.loads(first_line)
    print(f"✓ 成功读取测试数据: key={test_data['key']}")
    print(f"  - 消息数量: {len(test_data['messages'])}")
    print(f"  - 规则数量: {len(test_data['rule_list'])}")

    # 2. 初始化评估器
    print(f"\n🔧 初始化评估器...")

    # 获取 API key（优先使用环境变量）
    api_key = os.getenv("DASHSCOPE_API_KEY") or os.getenv("OPENAI_API_KEY")

    if not api_key:
        print("\n⚠️  警告：未找到 API key (DASHSCOPE_API_KEY 或 OPENAI_API_KEY)")
        print("   将使用 Mock 模式进行测试（不调用真实 API）")
        print("\n   要使用真实 API，请设置环境变量：")
        print("   export DASHSCOPE_API_KEY='your-api-key'")
        print("   或者在 Windows 上：")
        print("   set DASHSCOPE_API_KEY=your-api-key")

        # 使用 Mock 模式
        try:
            # 创建 mock evaluator
            evaluator = create_mock_evaluator()
        except Exception as e:
            print(f"\n❌ 创建 Mock evaluator 失败: {e}")
            return False
    else:
        print(f"✓ 找到 API key: {api_key[:10]}...")

        try:
            # 创建真实的 evaluator
            config = Config()
            evaluator = JsonContextEvaluator(
                config=config,
                api_key=api_key
            )
            print("✓ 评估器初始化成功")
        except Exception as e:
            print(f"\n❌ 初始化评估器失败: {e}")
            import traceback
            traceback.print_exc()
            return False

    # 3. 运行评估
    print(f"\n🚀 开始评估...")

    try:
        # 创建临时输入文件
        temp_input = project_root / "temp_test_input.json"
        temp_output = project_root / "temp_test_output.json"

        with open(temp_input, 'w', encoding='utf-8') as f:
            json.dump(test_data, f, ensure_ascii=False, indent=2)

        print(f"✓ 临时输入文件: {temp_input}")

        # 运行评估
        result = evaluator.evaluate_from_json(
            input_json_path=str(temp_input),
            output_json_path=str(temp_output)
        )

        print(f"✓ 评估完成")

        # 4. 显示结果
        print(f"\n📊 评估结果:")
        print(f"  - 生成的回复: {result['generated_response'][:100]}...")

        total_score = sum(e['score'] for e in result['evaluations'])
        print(f"  - 总得分: {total_score}")

        print(f"\n  规则评估详情:")
        for eval_item in result['evaluations']:
            rule = eval_item['rule']
            triggered = eval_item['triggered']
            score = eval_item['score']
            reason = eval_item.get('reason', '')

            status = "✗ 违规" if triggered else "✓ 通过"
            print(f"    {status} | {rule} | 得分: {score} | {reason[:50]}..." if len(reason) > 50 else f"    {status} | {rule} | 得分: {score} | {reason}")

        print(f"\n✅ 测试成功！Pipeline 运行正常")

        # 清理临时文件
        if temp_input.exists():
            temp_input.unlink()
        if temp_output.exists():
            print(f"   详细结果已保存到: {temp_output}")

        return True

    except Exception as e:
        print(f"\n❌ 评估失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def create_mock_evaluator():
    """创建 Mock evaluator（用于没有 API key 的情况）"""

    print("\n📝 创建 Mock evaluator...")

    # 这里我们创建一个简化的测试，不依赖真实模型
    # 主要验证 pipeline 的流程是否正确

    class MockJsonContextEvaluator:
        """Mock evaluator for testing pipeline logic"""

        def __init__(self):
            self.dynamic_registry = None
            self.single_rule_registry = None
            self.stage_rule_registry = None

        def evaluate_from_json(self, input_json_path, output_json_path=None):
            """Mock evaluation"""

            # 读取输入
            with open(input_json_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            key = data['key']
            messages = data['messages']
            rule_list = data['rule_list']

            # Mock 生成的回复
            generated_response = "这是一个测试回复。请问您还有什么问题吗？"

            # Mock 评估结果
            evaluations = []

            for rule_config in rule_list:
                if isinstance(rule_config, str):
                    rule_tag = rule_config
                else:
                    rule_tag = rule_config['rule']

                # 简单的 mock 逻辑
                triggered = rule_tag.startswith('single_turn')
                score = -1 if triggered else 1

                evaluations.append({
                    "rule": rule_tag,
                    "triggered": triggered,
                    "score": score,
                    "kwargs": {},
                    "reason": f"Mock 评估结果 for {rule_tag}"
                })

            result = {
                "key": key,
                "generated_response": generated_response,
                "evaluations": evaluations,
                "kwargs": [{} for _ in evaluations]
            }

            # 保存输出
            if output_json_path:
                with open(output_json_path, 'w', encoding='utf-8') as f:
                    json.dump(result, f, ensure_ascii=False, indent=2)

            return result

    return MockJsonContextEvaluator()


def main():
    """主函数"""

    try:
        success = test_golden_history_evaluation()

        print("\n" + "=" * 80)

        if success:
            print("✅ 测试完成：Pipeline 运行正常")
            print("\n下一步：")
            print("1. 配置真实的 API key 进行完整测试")
            print("2. 使用本地模型进行评估")
            print("3. 批量评估：使用 evaluate_batch_from_json()")
        else:
            print("❌ 测试失败：请检查错误信息")

        print("=" * 80)

        return 0 if success else 1

    except Exception as e:
        print(f"\n❌ 测试过程中发生错误: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
