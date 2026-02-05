"""
批量评估黄金历史评测数据集
使用JsonContextEvaluator批量评估dataset_20_items.json中的所有测试用例
"""

import json
import os
import sys
from pathlib import Path

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from IBench.pipeline.json_context_evaluator import JsonContextEvaluator


def batch_evaluate_dataset(dataset_path: str, output_dir: str):
    """
    批量评估数据集

    Args:
        dataset_path: 数据集JSON文件路径
        output_dir: 输出目录
    """
    # 加载数据集
    print(f"📂 加载数据集: {dataset_path}")
    with open(dataset_path, 'r', encoding='utf-8') as f:
        dataset = json.load(f)

    test_cases = dataset['test_cases']
    print(f"✓ 找到 {len(test_cases)} 个测试用例\n")

    # 创建输出目录
    os.makedirs(output_dir, exist_ok=True)

    # 创建评估器
    print("🔧 初始化评估器...")
    evaluator = JsonContextEvaluator()
    print("✓ 评估器初始化完成\n")

    # 批量评估
    results = []
    summary = {
        "total_cases": len(test_cases),
        "evaluated_cases": 0,
        "failed_cases": 0,
        "total_score": 0,
        "case_details": []
    }

    print("="*60)
    print("开始批量评估")
    print("="*60 + "\n")

    for i, test_case in enumerate(test_cases, 1):
        case_key = test_case['key']
        case_desc = test_case.get('description', 'N/A')

        print(f"[{i}/{len(test_cases)}] 测试用例 {case_key}: {case_desc}")

        try:
            # 保存临时输入文件
            temp_input = os.path.join(output_dir, f"temp_input_{case_key}.json")
            with open(temp_input, 'w', encoding='utf-8') as f:
                json.dump(test_case, f, ensure_ascii=False, indent=2)

            # 评估
            temp_output = os.path.join(output_dir, f"output_{case_key}.json")
            result = evaluator.evaluate_from_json(temp_input, temp_output)

            # 提取评估结果
            evaluations = result['evaluations']
            total_score = sum(e['score'] for e in evaluations)
            triggered_rules = [e['rule'] for e in evaluations if e['triggered']]

            results.append(result)
            summary['evaluated_cases'] += 1
            summary['total_score'] += total_score

            print(f"  ✓ 得分: {total_score}")
            print(f"  ✓ 触发规则: {len(triggered_rules)} 条")
            print(f"  ✓ 生成回复: {result['generated_response'][:50]}...")

            # 记录详情
            summary['case_details'].append({
                "key": case_key,
                "description": case_desc,
                "score": total_score,
                "triggered_rules": triggered_rules,
                "total_rules": len(evaluations)
            })

        except Exception as e:
            print(f"  ✗ 评估失败: {e}")
            summary['failed_cases'] += 1
            summary['case_details'].append({
                "key": case_key,
                "description": case_desc,
                "error": str(e)
            })

        print()

    # 生成汇总报告
    print("="*60)
    print("评估汇总")
    print("="*60)

    avg_score = summary['total_score'] / max(summary['evaluated_cases'], 1)
    summary['average_score'] = avg_score

    print(f"总用例数: {summary['total_cases']}")
    print(f"成功评估: {summary['evaluated_cases']}")
    print(f"失败数量: {summary['failed_cases']}")
    print(f"总得分: {summary['total_score']}")
    print(f"平均得分: {avg_score:.2f}")

    # 保存汇总报告
    summary_path = os.path.join(output_dir, "evaluation_summary.json")
    with open(summary_path, 'w', encoding='utf-8') as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)

    print(f"\n✓ 汇总报告已保存: {summary_path}")

    # 保存完整结果
    all_results_path = os.path.join(output_dir, "all_results.json")
    with open(all_results_path, 'w', encoding='utf-8') as f:
        json.dump({
            "summary": summary,
            "results": results
        }, f, ensure_ascii=False, indent=2)

    print(f"✓ 完整结果已保存: {all_results_path}")

    return summary


def main():
    """主函数"""
    # 路径配置
    dataset_path = "examples/golden_history_dataset/dataset_20_items.json"
    output_dir = "data/output/eval_results"

    # 检查数据集文件是否存在
    if not os.path.exists(dataset_path):
        print(f"✗ 错误: 数据集文件不存在: {dataset_path}")
        print(f"  当前工作目录: {os.getcwd()}")
        return 1

    # 批量评估
    try:
        summary = batch_evaluate_dataset(dataset_path, output_dir)
        print("\n✓ 批量评估完成！")
        return 0
    except Exception as e:
        print(f"\n✗ 批量评估失败: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
