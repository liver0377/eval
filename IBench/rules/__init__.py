"""
IBench rules package
"""

from .single_rules import SingleRuleRegistry
from .stage_rules import StageRuleRegistry

__all__ = ['SingleRuleRegistry', 'StageRuleRegistry']
