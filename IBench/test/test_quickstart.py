"""
Quick start test script for IBench
This script demonstrates the basic functionality without requiring actual models
"""
import os
import sys

# Mock the required libraries for testing
class MockTransformers:
    """Mock transformers for testing"""
    class AutoModelForCausalLM:
        @staticmethod
        def from_pretrained(*args, **kwargs):
            print(f"[MOCK] Loading model from {args[0]}")
            return "mock_model"
    
    class AutoTokenizer:
        @staticmethod
        def from_pretrained(*args, **kwargs):
            print(f"[MOCK] Loading tokenizer from {args[0]}")
            return "mock_tokenizer"

class MockOpenAI:
    """Mock openai for testing"""
    class OpenAI:
        def __init__(self, **kwargs):
            print(f"[MOCK] OpenAI client initialized: {kwargs}")
        
        class chat:
            class completions:
                @staticmethod
                def create(**kwargs):
                    print(f"[MOCK] API call: {kwargs.get('model')}")
                    
                    class MockChoice:
                        class MockMessage:
                            content = "Mock response from API"
                        message = MockMessage()
                    class MockResponse:
                        choices = [MockChoice()]
                    return MockResponse()

# Add mocks to sys.modules
sys.modules['torch'] = type('MockTorch', (), {'cuda': lambda: False, 'cuda_is_available': lambda: False, 'no_grad': lambda: lambda f: f()})()
sys.modules['transformers'] = MockTransformers()
sys.modules['openai'] = MockOpenAI()

# Now we can import IBench modules
from IBench.utils.common import (
    Message, RuleResult, TurnEvaluation, EvaluationResult,
    RuleType, EvaluationMode, RuleDefinition
)

def test_data_structures():
    """Test basic data structures"""
    print("\n=== Testing Data Structures ===\n")
    
    # Test Message
    msg = Message(
        role="user",
        content="Hello, I need help",
        turn_id=1
    )
    print(f"Message: {msg.to_dict()}")
    
    # Test RuleResult
    rule_result = RuleResult(
        rule_id=1,
        rule_type=RuleType.LLM,
        rule_description="使用情感安慰用语",
        passed=True,
        score=0,
        reason="Test passed",
        turn_id=1
    )
    print(f"RuleResult: {rule_result.to_dict()}")
    
    # Test TurnEvaluation
    turn_eval = TurnEvaluation(
        turn_id=1,
        response="I understand your concern..."
    )
    turn_eval.single_rules.append(rule_result)
    print(f"TurnEvaluation score: {turn_eval.total_score}")
    
    # Test EvaluationResult
    result = EvaluationResult(
        conversation_id="test_conv",
        mode=EvaluationMode.CONTEXT
    )
    result.turn_evaluations.append(turn_eval)
    print(f"EvaluationResult final score: {result.final_score}")
    
    print("✓ Data structures test passed")

def test_rule_registries():
    """Test rule registries"""
    print("\n=== Testing Rule Registries ===\n")
    
    from IBench.rules.single_rules import SingleRuleRegistry
    from IBench.rules.stage_rules import StageRuleRegistry
    
    # Test SingleRuleRegistry
    single_registry = SingleRuleRegistry()
    all_single_rules = single_registry.get_all_rules()
    print(f"Total single rules: {len(all_single_rules)}")
    
    for rule_id, rule in all_single_rules.items():
        print(f"  Rule {rule_id}: {rule.description} ({rule.rule_type.value})")
    
    # Test StageRuleRegistry
    stage_registry = StageRuleRegistry()
    all_stage_rules = stage_registry.get_all_rules()
    print(f"\nTotal stage rules: {len(all_stage_rules)}")
    
    for rule_id, rule in all_stage_rules.items():
        print(f"  Rule {rule_id}: {rule.description} ({rule.rule_type.value})")
        if rule.precondition:
            print(f"    Precondition: {rule.precondition}")
    
    print("\n✓ Rule registries test passed")

def test_configuration():
    """Test configuration"""
    print("\n=== Testing Configuration ===\n")
    
    from IBench.config import Config, ModelConfig, EvaluationConfig
    
    # Test ModelConfig
    model_config = ModelConfig(
        local_model_path="./models/qwen3-8b",
        api_key="test-key"
    )
    print(f"Model path: {model_config.local_model_path}")
    print(f"API base: {model_config.api_base}")
    
    # Test EvaluationConfig
    eval_config = EvaluationConfig()
    print(f"\nOutput dir: {eval_config.output_dir}")
    print(f"Max turns: {eval_config.max_conversation_turns}")
    print(f"Single rule turns: {eval_config.single_rule_turns}")
    print(f"Stage rule turns: {eval_config.stage_rule_turns}")
    
    # Test Config
    config = Config()
    print(f"\nGlobal config validation: {config.validate()}")
    
    print("\n✓ Configuration test passed")

def test_conversation():
    """Test conversation management"""
    print("\n=== Testing Conversation ===\n")
    
    from IBench.conversation.conversation import Conversation
    
    conv = Conversation("test_conv")
    
    # Add messages
    conv.add_message(Message(role="user", content="Hello", turn_id=1))
    conv.add_message(Message(role="assistant", content="Hi there!", turn_id=1))
    conv.add_message(Message(role="user", content="How are you?", turn_id=2))
    
    print(f"Conversation ID: {conv.conversation_id}")
    print(f"Total messages: {len(conv.get_messages())}")
    print(f"Current turn ID: {conv.get_current_turn_id()}")
    print(f"\nFull context:\n{conv.get_full_context()}")
    
    print("\n✓ Conversation test passed")

def main():
    """Run all tests"""
    print("=" * 50)
    print("IBench Quick Start Test")
    print("=" * 50)
    
    try:
        test_data_structures()
        test_rule_registries()
        test_configuration()
        test_conversation()
        
        print("\n" + "=" * 50)
        print("All tests passed! ✓")
        print("=" * 50)
        print("\nTo use IBench with real models:")
        print("1. Install dependencies: pip install -r IBench/requirements.txt")
        print("2. Set API key: export DASHSCOPE_API_KEY='your-key'")
        print("3. Run examples: python IBench/examples.py")
        
    except Exception as e:
        print(f"\n✗ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
