"""
Evaluate Conversations Script
Read saved conversations in ShareGPT format and evaluate them offline
"""
import os
import sys
import json
from typing import List, Dict
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from IBench.models.api_model import APIModel
from IBench.evaluator.batch_evaluator import BatchEvaluator
from IBench.utils.common import Message, EvaluationMode, EvaluationResult
from IBench.config import Config

def load_conversation_from_file(file_path: str) -> tuple[List[Message], str]:
    """
    Load conversation from ShareGPT format JSON file

    Expected JSON format:
    [
        {"from": "human", "value": "...", "turn_id": 1},
        {"from": "gpt", "value": "...", "turn_id": 1},
        {"from": "human", "value": "...", "turn_id": 2},
        {"from": "gpt", "value": "...", "turn_id": 2}
    ]

    Args:
        file_path: Path to conversation JSON file

    Returns:
        Tuple of (conversation_messages, conversation_id)
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        conversation_data = json.load(f)
    
    messages = []
    for i, msg in enumerate(conversation_data):
        role = "user" if msg["from"] == "human" else "assistant"
        
        if "turn_id" not in msg:
            raise ValueError(f"Message at index {i} missing required 'turn_id' field: {msg}")
        
        messages.append(
            Message(
                role=role,
                content=msg["value"],
                turn_id=msg["turn_id"]
            )
        )
    
    # Extract conversation_id from filename
    conversation_id = os.path.splitext(os.path.basename(file_path))[0]
    
    return messages, conversation_id

def evaluate_single_conversation(
    conversation: List[Message],
    conversation_id: str,
    evaluator: BatchEvaluator,
    mode: EvaluationMode
) -> EvaluationResult:
    """
    Evaluate a single conversation
    
    Args:
        conversation: List of messages
        conversation_id: Conversation ID
        evaluator: BatchEvaluator instance
        mode: Evaluation mode
        
    Returns:
        EvaluationResult
    """
    # Extract assistant responses
    responses = [msg.content for msg in conversation if msg.role == "assistant"]
    
    # Evaluate
    result = evaluator.evaluate_conversation(
        conversation_id=conversation_id,
        mode=mode,
        conversation_history=conversation,
        responses=responses
    )
    
    return result

def evaluate_model_conversations(
    model_name: str,
    model_dir: str,
    evaluator: BatchEvaluator,
    mode: EvaluationMode,
    output_dir: str
) -> List[Dict]:
    """
    Evaluate all conversations for a specific model
    
    Args:
        model_name: Name of the model
        model_dir: Directory containing conversation files
        evaluator: BatchEvaluator instance
        mode: Evaluation mode
        output_dir: Output directory for results
        
    Returns:
        List of evaluation results
    """
    print(f"\n{'='*60}")
    print(f"Evaluating Model: {model_name}")
    print(f"{'='*60}")
    
    results = []
    
    # Find all conversation files
    conv_files = sorted([f for f in os.listdir(model_dir) if f.startswith("conv_") and f.endswith(".json")])
    
    print(f"Found {len(conv_files)} conversation files")
    
    for i, conv_file in enumerate(conv_files):
        print(f"\n[{i+1}/{len(conv_files)}] Evaluating: {conv_file}...")
        
        try:
            file_path = os.path.join(model_dir, conv_file)
            
            # Load conversation
            conversation, conversation_id = load_conversation_from_file(file_path)
            
            # Evaluate
            result = evaluate_single_conversation(
                conversation=conversation,
                conversation_id=conversation_id,
                evaluator=evaluator,
                mode=mode
            )
            
            # Save result
            result_dict = result.to_dict()
            results.append(result_dict)
            
            print(f"  Score: {result.final_score}, Turns: {result.total_turns}")
            
        except Exception as e:
            print(f"  ✗ Error: {e}")
            import traceback
            traceback.print_exc()
    
    return results

def evaluate_all_conversations(
    conversations_dir: str,
    api_key: str,
    mode: str = "INTERACTIVE",
    output_dir: str = None
) -> Dict:
    """
    Evaluate all conversations from all models
    
    Args:
        conversations_dir: Base directory containing model subdirectories
        api_key: API key for judge model
        mode: Evaluation mode (CONTEXT or INTERACTIVE)
        output_dir: Output directory for results
        
    Returns:
        Summary dictionary
    """
    timestamp = datetime.now().isoformat()
    
    if output_dir is None:
        output_dir = os.path.join(conversations_dir, "evaluation_results")
    
    os.makedirs(output_dir, exist_ok=True)
    
    # Initialize evaluator
    config = Config()
    config.model.api_key = api_key
    
    judge_model = APIModel(
        config.model,
        model_name=config.model.judge_model_name
    )
    
    evaluator = BatchEvaluator(config.evaluation, llm_judge=judge_model)
    
    evaluation_mode = EvaluationMode.CONTEXT if mode.upper() == "CONTEXT" else EvaluationMode.INTERACTIVE
    
    print(f"\n{'#'*60}")
    print(f"# Batch Evaluation - {mode} Mode")
    print(f"{'#'*60}")
    print(f"Input directory: {conversations_dir}")
    print(f"Output directory: {output_dir}")
    print(f"Judge model: {config.model.judge_model_name}")
    
    summary = {
        "timestamp": timestamp,
        "mode": mode,
        "conversations_dir": conversations_dir,
        "output_dir": output_dir,
        "judge_model": config.model.judge_model_name,
        "models": {},
        "total_evaluated": 0,
        "overall_stats": {}
    }
    
    # Process each model directory
    model_dirs = [d for d in os.listdir(conversations_dir) if os.path.isdir(os.path.join(conversations_dir, d))]
    
    for model_name in model_dirs:
        model_dir = os.path.join(conversations_dir, model_name)
        
        model_results = evaluate_model_conversations(
            model_name=model_name,
            model_dir=model_dir,
            evaluator=evaluator,
            mode=evaluation_mode,
            output_dir=output_dir
        )
        
        summary["models"][model_name] = model_results
        summary["total_evaluated"] += len(model_results)
    
    # Calculate overall statistics
    all_scores = []
    for model_name, model_results in summary["models"].items():
        for result in model_results:
            if "final_score" in result:
                all_scores.append(result["final_score"])
    
    if all_scores:
        summary["overall_stats"] = {
            "average_score": sum(all_scores) / len(all_scores),
            "min_score": min(all_scores),
            "max_score": max(all_scores),
            "total_evaluated": len(all_scores)
        }
    
    # Save summary
    summary_file = os.path.join(output_dir, "evaluation_summary.json")
    with open(summary_file, 'w', encoding='utf-8') as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)
    
    print(f"\n\n{'='*60}")
    print(f"Evaluation Summary")
    print(f"{'='*60}")
    print(f"Total conversations evaluated: {summary['total_evaluated']}")
    print(f"Average score: {summary['overall_stats'].get('average_score', 'N/A')}")
    print(f"Summary file: {summary_file}")
    print(f"{'='*60}\n")
    
    return summary

def main():
    """Main function for command-line usage"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Evaluate saved conversations")
    parser.add_argument(
        "--input",
        required=True,
        help="Directory containing generated conversations"
    )
    parser.add_argument(
        "--mode",
        choices=["CONTEXT", "INTERACTIVE"],
        default="INTERACTIVE",
        help="Evaluation mode"
    )
    parser.add_argument(
        "--api-key",
        default=os.getenv("DASHSCOPE_API_KEY"),
        help="API key for judge model (or set DASHSCOPE_API_KEY env var)"
    )
    parser.add_argument(
        "--output-dir",
        default=None,
        help="Output directory for results (default: <input>/evaluation_results)"
    )
    
    args = parser.parse_args()
    
    if not args.api_key:
        print("Error: Please provide --api-key or set DASHSCOPE_API_KEY environment variable")
        return 1
    
    # Evaluate all conversations
    summary = evaluate_all_conversations(
        conversations_dir=args.input,
        api_key=args.api_key,
        mode=args.mode,
        output_dir=args.output_dir
    )
    
    print("\n✓ All conversations evaluated successfully!")
    print(f"\nResults saved to: {summary['output_dir']}")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
