"""
IBench - Model-User Dialogue Evaluation Framework
"""
__version__ = "0.1.0"

from .config import Config, config
from .utils.common import (
    Message, RuleResult, TurnEvaluation, EvaluationResult,
    RuleType, EvaluationMode, RuleDefinition
)
from .models import LocalModel, APIModel
from .rules import SingleRuleRegistry, StageRuleRegistry
from .pipeline.context_eval import ContextEvaluator
from .pipeline.interactive_eval import InteractiveEvaluator

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
    
    # Models
    'LocalModel',
    'APIModel',
    
    # Rules
    'SingleRuleRegistry',
    'StageRuleRegistry',
    
    # Evaluators
    'ContextEvaluator',
    'InteractiveEvaluator',
]
