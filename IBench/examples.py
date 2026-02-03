"""
Example usage of IBench framework
"""
from IBench import ContextEvaluator, InteractiveEvaluator, Message

# Example 1: Context Evaluation
def example_context_evaluation():
    print("=== Context Evaluation Example ===\n")
    
    # Initialize evaluator
    evaluator = ContextEvaluator(
        local_model_path="./models/qwen3-8b",
        api_key="your-api-key"  # Or set DASHSCOPE_API_KEY environment variable
    )
    
    # Define conversation history
    conversation_history = [
        Message(role="user", content="我最近总是失眠，晚上睡不着", turn_id=1),
        Message(role="user", content="持续大概一个月了，很焦虑", turn_id=2)
    ]
    
    # Evaluate
    result = evaluator.evaluate(conversation_history)
    
    # Print results
    print(f"Conversation ID: {result.conversation_id}")
    print(f"Mode: {result.mode.value}")
    print(f"Total Turns: {result.total_turns}")
    print(f"Final Score: {result.final_score}")
    
    # Print turn details
    for turn_eval in result.turn_evaluations:
        print(f"\nTurn {turn_eval.turn_id}:")
        print(f"  Response: {turn_eval.response[:100]}...")
        print(f"  Total Score: {turn_eval.total_score}")
        print(f"  Single Rules Passed: {turn_eval.passed_single_rules}/{len(turn_eval.single_rules)}")
        print(f"  Stage Rules Passed: {turn_eval.passed_stage_rules}/{len(turn_eval.stage_rules)}")

# Example 2: Interactive Evaluation
def example_interactive_evaluation():
    print("\n=== Interactive Evaluation Example ===\n")
    
    # Initialize evaluator
    evaluator = InteractiveEvaluator(
        local_model_path="./models/qwen3-8b",
        api_key="your-api-key"
    )
    
    # Define initial prompt
    initial_prompt = "我最近总是失眠，晚上睡不着"
    
    # Evaluate with 3 turns
    result = evaluator.evaluate(initial_prompt, max_turns=3)
    
    # Print results
    print(f"Conversation ID: {result.conversation_id}")
    print(f"Mode: {result.mode.value}")
    print(f"Total Turns: {result.total_turns}")
    print(f"Final Score: {result.final_score}")

# Example 3: Batch Evaluation
def example_batch_evaluation():
    print("\n=== Batch Evaluation Example ===\n")
    
    # Initialize evaluator
    evaluator = ContextEvaluator(
        local_model_path="./models/qwen3-8b",
        api_key="your-api-key"
    )
    
    # Define multiple conversation histories
    conversation_batches = [
        [
            Message(role="user", content="我头疼", turn_id=1),
            Message(role="user", content="持续三天了", turn_id=2)
        ],
        [
            Message(role="user", content="我最近胸闷", turn_id=1),
            Message(role="user", content="特别是晚上", turn_id=2)
        ]
    ]
    
    # Evaluate batch
    results = evaluator.evaluate_batch(
        conversation_batches,
        output_file="./data/output/batch_results.json"
    )
    
    # Print summary
    evaluator.print_summary(results)

if __name__ == "__main__":
    # Uncomment to run examples
    # example_context_evaluation()
    # example_interactive_evaluation()
    # example_batch_evaluation()
    print("Examples defined. Uncomment the calls in __main__ to run them.")
