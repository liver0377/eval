"""
Model Comparison Script
Compare two models on the same evaluation tasks
"""
import os
import sys
import json
from typing import List, Dict, Optional
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from IBench.models.local_model import LocalModel
from IBench.models.model_configs import get_model_config
from IBench.models.api_model import APIModel
from IBench.evaluator.batch_evaluator import BatchEvaluator
from IBench.utils.common import Message, EvaluationMode
from IBench.config import Config

def load_model_from_config(model_config, api_key: str):
    """
    Load a model from ModelConfig
    
    Args:
        model_config: ModelConfig from model_configs.py
        api_key: API key for judge model
        
    Returns:
        Tuple of (local_model, judge_model)
    """
    # Create ModelConfig for LocalModel
    from IBench.config import ModelConfig as IBenchModelConfig
    
    ibench_config = IBenchModelConfig(
        local_model_path=model_config.path,
        load_in_4bit=model_config.load_in_4bit,
        load_in_8bit=model_config.load_in_8bit,
        device_map=model_config.device_map,
        api_key=api_key,
        max_new_tokens=model_config.max_new_tokens,
        temperature=model_config.temperature
    )
    
    # Load models
    print(f"\n{'='*60}")
    print(f"Loading model: {model_config.name}")
    print(f"{'='*60}")
    
    local_model = LocalModel(ibench_config)
    judge_model = APIModel(
        ibench_config,
        model_name=ibench_config.judge_model_name
    )
    
    return local_model, judge_model

def compare_models(
    model_names: List[str],
    test_prompts: List[str],
    api_key: str,
    max_turns: int = 3,
    output_dir: str = "./data/output"
) -> Dict:
    """
    Compare multiple models on the same test prompts
    
    Args:
        model_names: List of model names to compare
        test_prompts: List of test prompts
        api_key: API key for judge model
        max_turns: Maximum turns per conversation
        output_dir: Output directory for results
        
    Returns:
        Comparison results dictionary
    """
    results = {
        "models": model_names,
        "test_prompts": test_prompts,
        "model_results": {},
        "comparison": {},
        "timestamp": datetime.now().isoformat()
    }
    
    # Evaluate each model
    for model_name in model_names:
        print(f"\n\n{'#'*60}")
        print(f"# Evaluating Model: {model_name}")
        print(f"{'#'*60}")
        
        try:
            # Load model
            model_config = get_model_config(model_name)
            local_model, judge_model = load_model_from_config(model_config, api_key)
            
            # Create evaluator
            config = Config()
            config.model.api_key = api_key
            evaluator = BatchEvaluator(config.evaluation, llm_judge=judge_model)
            
            # Evaluate on test prompts
            model_results = []
            
            for i, prompt in enumerate(test_prompts):
                print(f"\nTest {i+1}/{len(test_prompts)}: {prompt[:50]}...")
                
                # Simulate conversation
                conversation_history = [Message(role="user", content=prompt, turn_id=1)]
                responses = []
                
                # Generate responses for each turn
                current_history = conversation_history.copy()
                for turn in range(max_turns):
                    response = local_model.generate(current_history)
                    responses.append(response)
                    current_history.append(
                        Message(role="assistant", content=response, turn_id=turn+1)
                    )
                    if turn < max_turns - 1:
                        # Simple follow-up
                        current_history.append(
                            Message(role="user", content="请继续", turn_id=turn+2)
                        )
                
                # Evaluate
                result = evaluator.evaluate_conversation(
                    conversation_id=f"{model_name}_test_{i+1}",
                    mode=EvaluationMode.CONTEXT,
                    conversation_history=conversation_history,
                    responses=responses
                )
                
                model_results.append({
                    "prompt": prompt,
                    "final_score": result.final_score,
                    "total_turns": result.total_turns
                })
            
            results["model_results"][model_name] = model_results
            
            # Calculate average score
            avg_score = sum(r["final_score"] for r in model_results) / len(model_results)
            results["comparison"][model_name] = {
                "average_score": avg_score,
                "total_tests": len(model_results)
            }
            
        except Exception as e:
            print(f"Error evaluating model {model_name}: {e}")
            results["model_results"][model_name] = {"error": str(e)}
    
    # Save results
    os.makedirs(output_dir, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = os.path.join(output_dir, f"model_comparison_{timestamp}.json")
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    print(f"\n\nResults saved to: {output_file}")
    
    return results

def print_comparison_report(results: Dict):
    """
    Print comparison report
    
    Args:
        results: Results from compare_models
    """
    print("\n" + "="*60)
    print("MODEL COMPARISON REPORT")
    print("="*60)
    
    print(f"\nTimestamp: {results['timestamp']}")
    print(f"Models evaluated: {', '.join(results['models'])}")
    print(f"Test prompts: {len(results['test_prompts'])}")
    
    print("\n" + "-"*60)
    print("AVERAGE SCORES")
    print("-"*60)
    
    # Sort by average score
    sorted_models = sorted(
        results["comparison"].items(),
        key=lambda x: x[1]["average_score"],
        reverse=True
    )
    
    for model_name, stats in sorted_models:
        if "error" not in stats:
            print(f"{model_name:40s} {stats['average_score']:8.2f}")
        else:
            print(f"{model_name:40s} ERROR")
    
    print("\n" + "-"*60)
    print("DETAILED RESULTS")
    print("-"*60)
    
    for model_name in results["models"]:
        model_results = results["model_results"].get(model_name, {})
        if "error" in model_results:
            continue
        
        print(f"\n{model_name}:")
        for i, result in enumerate(model_results):
            print(f"  Test {i+1}: {result['final_score']} - {result['prompt'][:40]}...")

def main():
    """Main function for command-line usage"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Compare multiple models")
    parser.add_argument(
        "--models",
        nargs="+",
        default=["Qwen3-8B", "qwen3_full_sft"],
        help="Models to compare (default: Qwen3-8B qwen3_full_sft)"
    )
    parser.add_argument(
        "--prompts",
        nargs="+",
        default=[
            "我最近总是失眠，晚上睡不着",
            "我头疼，持续三天了",
            "我最近胸闷，特别是晚上"
        ],
        help="Test prompts"
    )
    parser.add_argument(
        "--api-key",
        default=os.getenv("DASHSCOPE_API_KEY"),
        help="API key for judge model (or set DASHSCOPE_API_KEY env var)"
    )
    parser.add_argument(
        "--max-turns",
        type=int,
        default=3,
        help="Maximum turns per conversation"
    )
    parser.add_argument(
        "--output-dir",
        default="./data/output",
        help="Output directory"
    )
    
    args = parser.parse_args()
    
    if not args.api_key:
        print("Error: Please provide --api-key or set DASHSCOPE_API_KEY environment variable")
        return 1
    
    # Run comparison
    results = compare_models(
        model_names=args.models,
        test_prompts=args.prompts,
        api_key=args.api_key,
        max_turns=args.max_turns,
        output_dir=args.output_dir
    )
    
    # Print report
    print_comparison_report(results)
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
