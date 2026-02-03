"""
IBench models package
"""

from .local_model import LocalModel
from .api_model import APIModel
from .model_configs import (
    get_model_config,
    list_available_models,
    register_model,
    MODEL_REGISTRY
)

__all__ = [
    'LocalModel',
    'APIModel',
    'get_model_config',
    'list_available_models',
    'register_model',
    'MODEL_REGISTRY'
]
