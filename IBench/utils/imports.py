"""
Import utilities for IBench
Helper functions for managing optional dependencies
"""
import sys

def get_missing_dependencies():
    """
    Get list of missing optional dependencies
    
    Returns:
        list: List of missing dependency names
    """
    missing = []
    
    try:
        import torch
    except ImportError:
        missing.append('torch')
    
    try:
        import transformers
    except ImportError:
        missing.append('transformers')
    
    try:
        import openai
    except ImportError:
        missing.append('openai')
    
    try:
        import bitsandbytes
    except ImportError:
        missing.append('bitsandbytes')
    
    try:
        import accelerate
    except ImportError:
        missing.append('accelerate')
    
    return missing

def require_model_dependencies():
    """
    Raise ImportError if model dependencies are missing
    Use this as a decorator or call directly in functions that need models
    
    Raises:
        ImportError: If any required dependency is missing
    """
    missing = get_missing_dependencies()
    
    if missing:
        msg = (
            f"Missing required dependencies: {', '.join(missing)}\n"
            "Install with:\n"
            "  pip install torch transformers openai bitsandbytes accelerate"
        )
        raise ImportError(msg)

def ensure_models_available(func):
    """
    Decorator to ensure model dependencies are available before running function
    
    Usage:
        @ensure_models_available
        def my_function():
            # Your code here
            pass
    """
    def wrapper(*args, **kwargs):
        require_model_dependencies()
        return func(*args, **kwargs)
    return wrapper

def get_install_command(missing_deps=None):
    """
    Get pip install command for missing dependencies
    
    Args:
        missing_deps: List of missing dependencies (auto-detected if None)
    
    Returns:
        str: Installation command
    """
    if missing_deps is None:
        missing_deps = get_missing_dependencies()
    
    if not missing_deps:
        return None
    
    return f"pip install {' '.join(missing_deps)}"
