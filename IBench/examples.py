"""
Example usage of IBench framework
"""
from IBench import ContextEvaluator, InteractiveEvaluator, Message
from IBench.models import get_model_config, list_available_models
from IBench.config import ModelConfig

# Example 1: Context Evaluation with Model Registry
def example_context_evaluation():
    print("=== Context Evaluation Example ===\n")
    
    # List available models
    print("Available models:")
    for name, desc in list_available_models().items():
        print(f"  - {name}: {desc}")
    
    # Use model from registry
    model_config = get_model_config("Qwen3-8B")
    print(f"\nUsing model: {model_config.name}")
    print(f"Path: {model_config.path}")
    print(f"4-bit quantization: {model_config.load_in_4bit}")
    
    # Initialize evaluator
    evaluator = ContextEvaluator(
        local_model_path=model_config.path,
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
    print(f"\nConversation ID: {result.conversation_id}")
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

# Example 2: Model Comparison
def example_model_comparison():
    print("\n=== Model Comparison Example ===\n")
    
    # Import comparison script
    import sys
    import os
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'scripts'))
    
    from compare_models import compare_models, print_comparison_report
    
    # Compare two models
    results = compare_models(
        model_names=["Qwen3-8B", "qwen3_full_sft"],
        test_prompts=[
            "我最近总是失眠",
            "我头疼，持续三天了"
        ],
        api_key="your-api-key",
        max_turns=2
    )
    
    # Print comparison report
    print_comparison_report(results)

# Example 3: Interactive Evaluation
def example_interactive_evaluation():
    print("\n=== Interactive Evaluation Example ===\n")
    
    # Use model config from registry
    model_config = get_model_config("qwen3_full_sft")
    
    # Initialize evaluator
    evaluator = InteractiveEvaluator(
        local_model_path=model_config.path,
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

# Example 4: Batch Evaluation
def example_batch_evaluation():
    print("\n=== Batch Evaluation Example ===\n")
    
    # Use model config from registry
    model_config = get_model_config("Qwen3-8B")
    
    # Initialize evaluator
    evaluator = ContextEvaluator(
        local_model_path=model_config.path,
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

# Example 5: Using Custom Model Configuration
def example_custom_config():
    print("\n=== Custom Model Configuration Example ===\n")
    
    # Create custom config (e.g., for a new model path)
    from IBench.models.model_configs import register_model, ModelConfig as ModelConfigDef
    
    custom_config = ModelConfigDef(
        name="my_custom_model",
        path="/path/to/your/model",
        load_in_4bit=True,
        description="My custom model"
    )
    
    register_model(custom_config)
    
    # Now you can use it
    model_config = get_model_config("my_custom_model")
    print(f"Registered custom model: {model_config.name}")
    print(f"Path: {model_config.path}")

if __name__ == "__main__":
    # Uncomment to run examples
    # example_context_evaluation()
    # example_model_comparison()
    # example_interactive_evaluation()
    # example_batch_evaluation()
    # example_custom_config()
    print("Examples defined. Uncomment the calls in __main__ to run them.")
    print("\nQuick test - list available models:")
    for name, desc in list_available_models().items():
        print(f"  {name}: {desc}")
