"""
Test script for Dynamic Interactive Evaluator
Tests the new FIRST_N and N_th rule functionality
"""

import sys
import os

# Add the parent directory to the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from IBench.pipeline.dynamic_interactive_eval import DynamicInteractiveEvaluator


def test_dynamic_interactive_evaluator():
    """Test the dynamic interactive evaluator"""
    
    print("=" * 60)
    print("Testing Dynamic Interactive Evaluator")
    print("=" * 60)
    
    # Initialize evaluator (without API key for testing)
    try:
        evaluator = DynamicInteractiveEvaluator()
        print("✓ Evaluator initialized successfully")
    except Exception as e:
        print(f"✗ Failed to initialize evaluator: {e}")
        return False
    
    # Test rule parsing
    print("\n--- Testing Rule Parsing ---")
    test_rules = [
        "single_turn:sty:gratitude",
        "multi_turn:FIRST_N:consult_subject",
        "multi_turn:N_th:gender",
    ]
    
    for rule_tag in test_rules:
        parsed = evaluator.dynamic_registry.parse_rule(rule_tag)
        if parsed:
            print(f"✓ Parsed {rule_tag}:")
            print(f"  - Type: {parsed.type}")
            print(f"  - Rule Class: {parsed.rule_class}")
            print(f"  - Rule Name: {parsed.rule_name}")
            print(f"  - Rule ID: {parsed.rule_id}")
            print(f"  - Score: {parsed.score}")
        else:
            print(f"✗ Failed to parse {rule_tag}")
    
    # Test kwargs extraction
    print("\n--- Testing Kwargs Extraction ---")
    test_response = "您好，请问您是为孩子咨询还是本人咨询？"
    test_conversation = []
    
    for rule_tag in test_rules:
        parsed = evaluator.dynamic_registry.parse_rule(rule_tag)
        if parsed and parsed.has_kwargs:
            kwargs = evaluator.kwargs_extractor.extract(
                rule_full_name=rule_tag,
                kwargs_schema=parsed.kwargs_schema,
                response=test_response,
                conversation=test_conversation
            )
            print(f"✓ Extracted kwargs for {rule_tag}: {kwargs}")
    
    print("\n--- All Tests Completed ---")
    return True


def test_json_format():
    """Test the JSON input/output format"""
    
    print("\n" + "=" * 60)
    print("Testing JSON Format")
    print("=" * 60)
    
    import json
    
    # Check if example files exist
    input_file = "examples/dynamic_interactive_input_example.json"
    output_file = "examples/dynamic_interactive_output_example.json"
    
    if os.path.exists(input_file):
        with open(input_file, 'r', encoding='utf-8') as f:
            input_data = json.load(f)
        print(f"✓ Input JSON file loaded successfully")
        print(f"  - Key: {input_data.get('key')}")
        print(f"  - Messages: {len(input_data.get('messages', []))}")
        print(f"  - Rules: {len(input_data.get('rule_list', []))}")
    else:
        print(f"✗ Input JSON file not found: {input_file}")
    
    if os.path.exists(output_file):
        with open(output_file, 'r', encoding='utf-8') as f:
            output_data = json.load(f)
        print(f"✓ Output JSON file loaded successfully")
        print(f"  - Key: {output_data.get('key')}")
        print(f"  - Evaluations: {len(output_data.get('evaluations', {}))}")
        print(f"  - Total Score: {output_data.get('summary', {}).get('total_score')}")
    else:
        print(f"✗ Output JSON file not found: {output_file}")
    
    return True


def main():
    """Run all tests"""
    print("\n" + "=" * 60)
    print("Dynamic Interactive Evaluation Test Suite")
    print("=" * 60 + "\n")
    
    # Run tests
    test_dynamic_interactive_evaluator()
    test_json_format()
    
    print("\n" + "=" * 60)
    print("Test Suite Completed")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    main()
