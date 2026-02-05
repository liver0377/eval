"""
批量评估黄金历史评测数据集（JSONL格式）
用于评估 data/dataset/golden_history_input.jsonl 中的80条测试用例
"""

import json
import os
import sys
import uuid
import threading
from pathlib import Path
from typing import List, Dict, Any, Tuple
from concurrent.futures import ThreadPoolExecutor, as_completed

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from IBench.pipeline.json_context_evaluator import JsonContextEvaluator
from IBench.config import Config


def load_jsonl(file_path: str) -> List[Dict[str, Any]]:
    """
    加载JSONL文件
    
    Args:
        file_path: JSONL文件路径
    
    Returns:
        JSON对象列表
    """
    data = []
    with open(file_path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line:
                data.append(json.loads(line))
    return data


def evaluate_single_entry(
    entry: Dict[str, Any],
    index: int,
    total: int,
    output_dir: str,
    evaluator: 'JsonContextEvaluator',
    print_lock: threading.Lock
) -> Tuple[Dict[str, Any], Dict[str, Any]]:
    """
    评估单个条目（线程安全）
    
    Args:
        entry: 数据条目
        index: 条目索引
        total: 总条目数
        output_dir: 输出目录
        evaluator: 评估器
        print_lock: 打印锁
    
    Returns:
        (评估结果, 详情信息) 或 (None, 错误信息)
    """
    key = entry.get('key', f'entry_{index}')
    unique_id = str(uuid.uuid4())[:8]
    temp_input_path = os.path.join(output_dir, f"temp_input_{key}_{unique_id}.json")
    
    try:
        # 线程安全的打印
        with print_lock:
            print(f"[{index}/{total}] 评估条目 {key}")
        
        # 保存临时输入文件
        with open(temp_input_path, 'w', encoding='utf-8') as f:
            json.dump(entry, f, ensure_ascii=False, indent=2)
        
        # 评估
        result = evaluator.evaluate_from_json(temp_input_path, None)
        
        # 提取评估结果
        evaluations = result.get('evaluations', [])
        total_score = sum(e.get('score', 0) for e in evaluations)
        triggered_rules = [e['rule'] for e in evaluations if e.get('triggered', False)]
        
        # 线程安全的打印结果
        with print_lock:
            print(f"  ✓ {key} 得分: {total_score}, 触发规则: {len(triggered_rules)}/{len(evaluations)}")
        
        # 记录详情
        detail = {
            "key": key,
            "score": total_score,
            "triggered_count": len(triggered_rules),
            "total_rules": len(evaluations),
            "triggered_rules": triggered_rules
        }
        
        return result, detail
        
    except Exception as e:
        # 线程安全的打印错误
        with print_lock:
            print(f"  ✗ {key} 评估失败: {e}")
        
        error_detail = {
            "key": key,
            "error": str(e)
        }
        return None, error_detail
        
    finally:
        # 清理临时文件
        try:
            os.remove(temp_input_path)
        except:
            pass


def evaluate_golden_history_jsonl(
    jsonl_path: str,
    output_dir: str,
    api_key: str = None
) -> Dict[str, Any]:
    """
    批量评估黄金历史JSONL数据集
    
    Args:
        jsonl_path: JSONL文件路径
        output_dir: 输出目录
        api_key: API密钥（可选）
    
    Returns:
        汇总统计信息
    """
    # 加载数据集
    print(f"📂 加载数据集: {jsonl_path}")
    entries = load_jsonl(jsonl_path)
    print(f"✓ 找到 {len(entries)} 个条目\n")
    
    # 创建输出目录
    os.makedirs(output_dir, exist_ok=True)
    
    # 创建评估器
    print("🔧 初始化评估器...")
    config = Config()
    if api_key:
        config.model.api_key = api_key
    evaluator = JsonContextEvaluator(config=config)
    print("✓ 评估器初始化完成\n")
    
    # 批量评估
    output_jsonl_path = os.path.join(output_dir, "golden_history_output.jsonl")
    results = []
    summary = {
        "total_entries": len(entries),
        "evaluated_entries": 0,
        "failed_entries": 0,
        "total_score": 0,
        "total_rules_checked": 0,
        "total_rules_triggered": 0,
        "entry_details": []
    }
    
    print("=" * 60)
    print("开始批量评估（并发模式，5线程）")
    print("=" * 60 + "\n")
    
    # 创建打印锁
    print_lock = threading.Lock()
    
    # 使用线程池并发评估
    with ThreadPoolExecutor(max_workers=5) as executor:
        # 提交所有任务
        future_to_entry = {
            executor.submit(evaluate_single_entry, entry, i, len(entries), output_dir, evaluator, print_lock): entry
            for i, entry in enumerate(entries, 1)
        }
        
        # 收集结果
        for future in as_completed(future_to_entry):
            result, detail = future.result()
            
            if result is not None:
                # 成功评估
                results.append(result)
                summary['evaluated_entries'] += 1
                summary['total_score'] += detail['score']
                summary['total_rules_checked'] += detail['total_rules']
                summary['total_rules_triggered'] += detail['triggered_count']
                summary['entry_details'].append(detail)
            else:
                # 评估失败
                summary['failed_entries'] += 1
                summary['entry_details'].append(detail)
    
    # 统一写入JSONL文件
    print("\n" + "=" * 60)
    print("写入评估结果...")
    print("=" * 60)
    with open(output_jsonl_path, 'w', encoding='utf-8') as output_f:
        for result in results:
            output_line = json.dumps(result, ensure_ascii=False)
            output_f.write(output_line + '\n')
    print(f"✓ 已写入 {len(results)} 条结果到 {output_jsonl_path}")
    
    # 生成汇总报告
    print("=" * 60)
    print("评估汇总")
    print("=" * 60)
    
    avg_score = summary['total_score'] / max(summary['evaluated_entries'], 1)
    avg_triggered = summary['total_rules_triggered'] / max(summary['total_rules_checked'], 1) * 100
    
    summary['average_score'] = round(avg_score, 2)
    summary['average_triggered_percent'] = round(avg_triggered, 2)
    
    print(f"总条目数: {summary['total_entries']}")
    print(f"成功评估: {summary['evaluated_entries']}")
    print(f"失败数量: {summary['failed_entries']}")
    print(f"总得分: {summary['total_score']}")
    print(f"平均得分: {avg_score:.2f}")
    print(f"规则触发率: {avg_triggered:.1f}%")
    
    # 保存汇总报告
    summary_path = os.path.join(output_dir, "evaluation_summary.json")
    with open(summary_path, 'w', encoding='utf-8') as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)
    
    print(f"\n✓ 结果已保存: {output_jsonl_path}")
    print(f"✓ 汇总报告已保存: {summary_path}")
    
    return summary


def main():
    """主函数"""
    # 路径配置
    jsonl_path = "data/dataset/golden_history_input.jsonl"
    output_dir = "data/output/golden_history_eval"
    
    # 检查文件是否存在
    if not os.path.exists(jsonl_path):
        print(f"✗ 错误: 文件不存在: {jsonl_path}")
        print(f"  当前工作目录: {os.getcwd()}")
        return 1
    
    # 从环境变量获取API密钥
    api_key = os.getenv("DASHSCOPE_API_KEY")
    
    if not api_key:
        print("⚠ 警告: DASHSCOPE_API_KEY 环境变量未设置")
        print("  评估可能无法正常进行（如需要LLM judge）")
    
    # 批量评估
    try:
        summary = evaluate_golden_history_jsonl(jsonl_path, output_dir, api_key)
        print("\n✓ 批量评估完成！")
        return 0
    except Exception as e:
        print(f"\n✗ 批量评估失败: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
