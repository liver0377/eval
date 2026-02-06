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

    # 2. 检查 API key
    print(f"\n🔧 检查 API key...")

    # 获取 API key（优先使用环境变量）
    api_key = os.getenv("DASHSCOPE_API_KEY") or os.getenv("OPENAI_API_KEY")

    if not api_key:
        print("\n❌ 错误：未找到 API key")
        print("   请设置环境变量：")
        print("   - Linux/Mac: export DASHSCOPE_API_KEY='your-api-key'")
        print("   - Windows: set DASHSCOPE_API_KEY=your-api-key")
        return False

    print(f"✓ 找到 API key: {api_key[:10]}...{api_key[-4:]}")

    # 3. 初始化评估器
    print(f"\n🚀 初始化评估器...")

    try:
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

    # 4. 运行评估
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


if __name__ == "__main__":
    success = test_golden_history_evaluation()

    print("\n" + "=" * 80)

    if success:
        print("✅ 测试完成：Pipeline 运行正常")
        print("\n下一步：")
        print("1. 批量评估：使用 evaluate_batch_from_json()")
        print("2. 自定义规则：添加新的评估规则")
        print("3. 调整配置：修改 models/model_configs.py")
    else:
        print("❌ 测试失败：请检查错误信息")

    print("=" * 80)

    sys.exit(0 if success else 1)
