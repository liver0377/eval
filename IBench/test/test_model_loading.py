"""
Test script to verify model loading works correctly
Run this on the server to test model loading
"""
import os
import sys

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_model_registry():
    """Test model registry"""
    print("="*60)
    print("Testing Model Registry")
    print("="*60)
    
    from IBench.models import list_available_models, get_model_config
    
    # List all models
    print("\nAvailable models:")
    for name, desc in list_available_models().items():
        print(f"  - {name}")
        print(f"    {desc}")
    
    # Test getting config
    try:
        config = get_model_config("Qwen3-8B")
        print(f"\n✓ Successfully got config for Qwen3-8B")
        print(f"  Path: {config.path}")
        print(f"  4-bit: {config.load_in_4bit}")
    except Exception as e:
        print(f"\n✗ Error getting config: {e}")
        return False
    
    return True

def test_model_loading():
    """Test actual model loading"""
    print("\n" + "="*60)
    print("Testing Model Loading")
    print("="*60)
    
    try:
        from IBench.models.model_configs import get_model_config
        from IBench.models.local_model import LocalModel
        
        # Get model config
        model_config = get_model_config("Qwen3-8B")
        
        print(f"\nLoading model: {model_config.name}")
        print(f"  Path: {model_config.path}")
        print(f"4-bit quantization: {model_config.load_in_4bit}")
        
        # Load model
        model = LocalModel(model_config)
        
        print("\n✓ Model loaded successfully!")
        
        # Test generation
        from IBench.utils.common import Message
        
        test_messages = [
            Message(role="user", content="你好", turn_id=1)
        ]
        
        print("\nTesting generation...")
        response = model.generate(test_messages)
        print(f"Response: {response[:100]}...")
        print("\n✓ Generation test passed!")
        
        return True
        
    except Exception as e:
        print(f"\n✗ Error loading model: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_tokenizer():
    """Test tokenizer loading"""
    print("\n" + "="*60)
    print("Testing Tokenizer")
    print("="*60)
    
    try:
        from transformers import AutoTokenizer
        from IBench.models import get_model_config
        
        model_config = get_model_config("Qwen3-8B")
        
        print(f"\nLoading tokenizer from: {model_config.path}")
        
        tokenizer = AutoTokenizer.from_pretrained(
            model_config.path,
            trust_remote_code=True,
            use_fast=False
        )
        
        print("✓ Tokenizer loaded successfully!")
        
        # Test tokenization
        test_text = "你好，世界"
        tokens = tokenizer.encode(test_text)
        decoded = tokenizer.decode(tokens)
        
        print(f"  Original: {test_text}")
        print(f"  Tokens: {len(tokens)} tokens")
        print(f"  Decoded: {decoded}")
        
        return True
        
    except Exception as e:
        print(f"\n✗ Error loading tokenizer: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all tests"""
    print("\n" + "#"*60)
    print("# IBench Model Loading Test")
    print("#"*60 + "\n")
    
    # Check environment
    print("Environment check:")
    print(f"  Python: {sys.version}")
    print(f"  Working directory: {os.getcwd()}")
    
    try:
        import torch
        print(f"  PyTorch: {torch.__version__}")
        if torch.cuda.is_available():
            print(f"  CUDA: Available")
            print(f"  GPUs: {torch.cuda.device_count()}")
            for i in range(torch.cuda.device_count()):
                props = torch.cuda.get_device_properties(i)
                print(f"    GPU {i}: {props.name} ({props.total_memory / 1024**3:.1f}GB)")
        else:
            print(f"  CUDA: Not available")
    except ImportError:
        print("  PyTorch: Not installed")
        return 1
    
    # Run tests
    results = {
        "Registry": test_model_registry(),
        "Tokenizer": test_tokenizer(),
        "Model Loading": test_model_loading()
    }
    
    # Summary
    print("\n" + "="*60)
    print("Test Summary")
    print("="*60)
    
    for test_name, passed in results.items():
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"  {test_name:20s} {status}")
    
    all_passed = all(results.values())
    
    if all_passed:
        print("\n✓ All tests passed! Model loading is working correctly.")
        print("\nNext steps:")
        print("  1. Run model comparison: python IBench/scripts/compare_models.py")
        print("  2. Run evaluation: python IBench/examples.py")
        return 0
    else:
        print("\n✗ Some tests failed. Please check the errors above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
