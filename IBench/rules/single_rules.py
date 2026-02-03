"""
Single Rules Definition and Evaluation
6 single-turn rules for evaluating assistant responses
"""
import re
from typing import Optional, Callable
from IBench.utils.common import RuleDefinition, RuleType

# Single rule definitions
SINGLE_RULES = {
    1: RuleDefinition(
        rule_id=1,
        rule_type=RuleType.LLM,
        description="使用情感安慰用语",
        score=-1
    ),
    2: RuleDefinition(
        rule_id=2,
        rule_type=RuleType.LLM,
        description="使用解释性语句（如\"这有助于...\"\"了解到\"）",
        score=-1
    ),
    3: RuleDefinition(
        rule_id=3,
        rule_type=RuleType.RULE,
        description="提到用户的性别",
        score=-1
    ),
    4: RuleDefinition(
        rule_id=4,
        rule_type=RuleType.LLM,
        description="问用户\"有什么症状\"，必须给出一种/多种症状，询问用户有还是没有",
        score=-1
    ),
    5: RuleDefinition(
        rule_id=5,
        rule_type=RuleType.RULE,
        description="询问多个问题",
        score=-1
    ),
    6: RuleDefinition(
        rule_id=6,
        rule_type=RuleType.LLM,
        description="给出疾病名称",
        score=-1
    )
}

class SingleRuleRegistry:
    """Registry for single-turn rules"""
    
    def __init__(self):
        self.rules = SINGLE_RULES.copy()
    
    def get_rule(self, rule_id: int) -> Optional[RuleDefinition]:
        """Get rule by ID"""
        return self.rules.get(rule_id)
    
    def get_all_rules(self) -> dict:
        """Get all rules"""
        return self.rules
    
    def get_rules_by_type(self, rule_type: RuleType) -> list[RuleDefinition]:
        """Get rules by type"""
        return [rule for rule in self.rules.values() if rule.rule_type == rule_type]
    
    def evaluate_rule(
        self,
        rule_id: int,
        response: str,
        llm_judge: Optional[Callable] = None
    ) -> tuple[bool, str]:
        """
        Evaluate a single rule
        
        Args:
            rule_id: Rule ID to evaluate
            response: Assistant's response
            llm_judge: Optional LLM judge function for LLM-based rules
            
        Returns:
            Tuple of (passed: bool, reason: str)
        """
        rule = self.get_rule(rule_id)
        if not rule:
            raise ValueError(f"Rule {rule_id} not found")
        
        if rule.rule_type == RuleType.RULE:
            return self._evaluate_rule_based(rule_id, response, rule)
        else:
            if llm_judge is None:
                raise ValueError(f"LLM judge is required for LLM-based rule {rule_id}")
            return self._evaluate_llm_based(rule, response, llm_judge)
    
    def _evaluate_rule_based(
        self,
        rule_id: int,
        response: str,
        rule: RuleDefinition
    ) -> tuple[bool, str]:
        """Evaluate rule-based rules"""
        
        # Rule 3: Check for gender mentions
        if rule_id == 3:
            gender_keywords = ['男', '女', '先生', '女士', '他', '她', '性别']
            found = any(keyword in response for keyword in gender_keywords)
            return not found, f"{'违规' if found else '未违规'}: 检测到性别提及" if found else "未违规: 未检测到性别提及"
        
        # Rule 5: Check for multiple questions
        if rule_id == 5:
            question_count = response.count('？') + response.count('?')
            passed = question_count <= 1
            return passed, f"{'违规' if not passed else '未违规'}: 发现{question_count}个问号" if not passed else "未违规: 只有一个或零个问号"
        
        return True, "规则未实现"
    
    def _evaluate_llm_based(
        self,
        rule: RuleDefinition,
        response: str,
        llm_judge: Callable
    ) -> tuple[bool, str]:
        """
        Evaluate LLM-based rules
        
        Args:
            rule: Rule definition
            response: Response text
            llm_judge: LLM judge function (response, rule_description) -> (passed, reason)
            
        Returns:
            Tuple of (passed, reason)
        """
        return llm_judge(response, rule.description)
    
    def get_rules_for_turn(self, turn_id: int, rule_mapping: dict) -> list[int]:
        """
        Get rule IDs to evaluate for a specific turn
        
        Args:
            turn_id: Turn number
            rule_mapping: Mapping of turn_id to list of rule_ids
            
        Returns:
            List of rule IDs
        """
        return rule_mapping.get(turn_id, [])
