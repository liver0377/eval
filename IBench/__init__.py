"""
IBench - Model-User Dialogue Evaluation Framework
"""
__version__ = "0.1.0"

# Core imports (no external dependencies)
from .models.model_configs import Config, config
from .utils.common import (
    Message, RuleResult, TurnEvaluation, EvaluationResult,
    RuleType, EvaluationMode, RuleDefinition
)

# Conditional model imports (requires torch, transformers, openai)
try:
    from .models import LocalModel, APIModel
    _models_available = True
except ImportError as e:
    # Dependencies not installed - models will be None
    LocalModel = None
    APIModel = None
    _models_available = False
    _models_import_error = str(e)

# Rules imports (no external dependencies)
from .rules import SingleRuleRegistry, StageRuleRegistry

# Conditional pipeline imports (requires models)
try:
    from .pipeline.context_eval import ContextEvaluator
    from .pipeline.interactive_eval import InteractiveEvaluator
    _pipeline_available = True
except ImportError:
    ContextEvaluator = None
    InteractiveEvaluator = None
    _pipeline_available = False

__all__ = [
    # Configuration
    'Config',
    'config',
    
    # Data structures
    'Message',
    'RuleResult',
    'TurnEvaluation',
    'EvaluationResult',
    'RuleType',
    'EvaluationMode',
    'RuleDefinition',
    
    # Models (may be None if dependencies not installed)
    'LocalModel',
    'APIModel',
    
    # Rules
    'SingleRuleRegistry',
    'StageRuleRegistry',
    
    # Evaluators (may be None if dependencies not installed)
    'ContextEvaluator',
    'InteractiveEvaluator',
]

# Public attributes for checking availability
__models_available__ = _models_available
__pipeline_available__ = _pipeline_available

def check_dependencies():
    """
    Check if all optional dependencies are installed
    
    Returns:
        dict: Dictionary with dependency status
    """
    status = {
        'torch': False,
        'transformers': False,
        'openai': False,
        'bitsandbytes': False,
        'all_available': _models_available
    }
    
    try:
        import torch
        status['torch'] = True
        status['torch_version'] = torch.__version__
    except ImportError:
        pass
    
    try:
        import transformers
        status['transformers'] = True
        status['transformers_version'] = transformers.__version__
    except ImportError:
        pass
    
    try:
        import openai
        status['openai'] = True
        status['openai_version'] = openai.__version__
    except ImportError:
        pass
    
    try:
        import bitsandbytes
        status['bitsandbytes'] = True
        status['bitsandbytes_version'] = bitsandbytes.__version__
    except ImportError:
        pass
    
    return status

def print_dependency_status():
    """Print dependency installation status"""
    status = check_dependencies()
    
    print("\n" + "="*60)
    print("IBench Dependency Status")
    print("="*60)
    
    deps = ['torch', 'transformers', 'openai', 'bitsandbytes']
    for dep in deps:
        if status.get(dep):
            version = status.get(f'{dep}_version', 'unknown')
            print(f"  ✓ {dep:20s} {version}")
        else:
            print(f"  ✗ {dep:20s} Not installed")
    
    if status['all_available']:
        print("\n✓ All dependencies installed - IBench fully functional")
    else:
        print("\n⚠ Some dependencies missing - Install with:")
        print("  pip install torch transformers openai bitsandbytes accelerate")
    
    print("="*60 + "\n")
