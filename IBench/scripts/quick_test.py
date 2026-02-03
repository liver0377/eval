"""
Quick Start Script - Standalone Test
Tests IBench functionality without requiring full dependency installation
"""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_imports():
    """Test basic IBench imports"""
    print("="*60)
    print("Testing IBench Imports")
    print("="*60)
    
    try:
        # These should always work (no external dependencies)
        from IBench import (
            Message, RuleType, EvaluationMode,
            RuleDefinition, Config
        )
        print("✓ Core data structures imported successfully")
        
        from IBench.rules import SingleRuleRegistry, StageRuleRegistry
        print("✓ Rules imported successfully")
        
        from IBench.models.model_configs import (
            get_model_config, list_available_models
        )
        print("✓ Model configurations imported successfully")
        
        return True
        
    except Exception as e:
        print(f"✗ Import failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_model_configs():
    """Test model configuration registry"""
    print("\n" + "="*60)
    print("Testing Model Configurations")
    print("="*60)
    
    try:
        from IBench.models.model_configs import (
            get_model_config, list_available_models
        )
        
        # List available models
        models = list_available_models()
        print(f"\nAvailable models ({len(models)}):")
        for name, desc in models.items():
            print(f"  - {name}")
            print(f"    {desc}")
        
        # Get specific config
        config = get_model_config("Qwen3-8B")
        print(f"\n✓ Got config for Qwen3-8B:")
        print(f"  Path: {config.path}")
        print(f"  4-bit: {config.load_in_4bit}")
        
        return True
        
    except Exception as e:
        print(f"✗ Model config test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_dependency_check():
    """Test dependency checking"""
    print("\n" + "="*60)
    print("Testing Dependency Check")
    print("="*60)
    
    try:
        from IBench import check_dependencies
        
        status = check_dependencies()
        
        print("\nDependency Status:")
        deps = ['torch', 'transformers', 'openai', 'bitsandbytes']
        for dep in deps:
            if status.get(dep):
                version = status.get(f'{dep}_version', 'unknown')
                print(f"  ✓ {dep:20s} {version}")
            else:
                print(f"  ✗ {dep:20s} Not installed")
        
        if status['all_available']:
            print("\n✓ All dependencies available!")
        else:
            print("\n⚠ Some dependencies not installed")
            print("  Install with: pip install torch transformers openai bitsandbytes")
        
        return True
        
    except Exception as e:
        print(f"✗ Dependency check failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_rules():
    """Test rule definitions"""
    print("\n" + "="*60)
    print("Testing Rule Definitions")
    print("="*60)
    
    try:
        from IBench.rules.single_rules import SingleRuleRegistry
        from IBench.rules.stage_rules import StageRuleRegistry
        
        # Test single rules
        single_registry = SingleRuleRegistry()
        single_rules = single_registry.get_all_rules()
        print(f"\nSingle Rules: {len(single_rules)}")
        for rule_id, rule in single_rules.items():
            print(f"  Rule {rule_id}: {rule.description}")
            print(f"    Type: {rule.rule_type.value}, Score: {rule.score}")
        
        # Test stage rules
        stage_registry = StageRuleRegistry()
        stage_rules = stage_registry.get_all_rules()
        print(f"\nStage Rules: {len(stage_rules)}")
        for rule_id, rule in stage_rules.items():
            print(f"  Rule {rule_id}: {rule.description}")
            print(f"    Type: {rule.rule_type.value}, Score: {rule.score}")
        
        return True
        
    except Exception as e:
        print(f"✗ Rules test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all tests"""
    print("\n" + "#"*60)
    print("# IBench Quick Start Test")
    print("#"*60 + "\n")
    
    results = {
        "Basic Imports": test_imports(),
        "Model Configurations": test_model_configs(),
        "Dependency Check": test_dependency_check(),
        "Rule Definitions": test_rules()
    }
    
    # Summary
    print("\n" + "="*60)
    print("Test Summary")
    print("="*60)
    
    for test_name, passed in results.items():
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"  {test_name:30s} {status}")
    
    if all(results.values()):
        print("\n✓ All tests passed!")
        print("\nNext steps:")
        print("  1. Install dependencies (if not already):")
        print("     pip install torch transformers openai bitsandbytes accelerate")
        print("  2. Test model loading:")
        print("     python IBench/scripts/test_model_loading.py")
        print("  3. Run model comparison:")
        print("     python IBench/scripts/compare_models.py --help")
        return 0
    else:
        print("\n✗ Some tests failed")
        return 1

if __name__ == "__main__":
    sys.exit(main())
