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
        name="gratitude",
        rule_type=RuleType.LLM,
        description="使用感谢用语",
        score=-1
    ),
    2: RuleDefinition(
        rule_id=2,
        name="explain_filler",
        rule_type=RuleType.LLM,
        description="使用解释性话句，如这有助于或了解到",
        score=-1
    ),
    3: RuleDefinition(
        rule_id=3,
        name="forced_symptom",
        rule_type=RuleType.LLM,
        description="使用宽泛问诊语句，如有什么症状而不是有症状么",
        score=-1
    ),
    4: RuleDefinition(
        rule_id=4,
        name="multi_question",
        rule_type=RuleType.RULE,
        description="一条消息问多个问题",
        score=-1
    ),
    5: RuleDefinition(
        rule_id=5,
        name="diagnosis_name",
        rule_type=RuleType.LLM,
        description="直接给出疾病名称",
        score=-1
    ),
    6: RuleDefinition(
        rule_id=6,
        name="formula",
        rule_type=RuleType.LLM,
        description="使用客服套话，如为了更好地为您服务或敬请谅解",
        score=-1
    ),
    7: RuleDefinition(
        rule_id=7,
        name="punctunation",
        rule_type=RuleType.RULE,
        description="使用引号或括号进行解释",
        score=-1
    ),
    8: RuleDefinition(
        rule_id=8,
        name="list",
        rule_type=RuleType.RULE,
        description="使用1.2.3.列表式回复",
        score=-1
    ),
    9: RuleDefinition(
        rule_id=9,
        name="hospital",
        rule_type=RuleType.LLM,
        description="编造医院名称",
        score=-1
    )
}

class SingleRuleRegistry:
    """Registry for single-turn rules"""
    
    def __init__(self):
        self.rules = SINGLE_RULES.copy()
        self.name_to_id = {rule.name: rule_id for rule_id, rule in self.rules.items()}
    
    def get_rule(self, rule_name: str) -> Optional[RuleDefinition]:
        """
        Get rule by name
        
        Args:
            rule_name: Rule name (str)
            
        Returns:
            RuleDefinition if found, None otherwise
        """
        rule_id = self.name_to_id.get(rule_name)
        return self.rules.get(rule_id) if rule_id else None
    
    def get_all_rules(self) -> dict:
        """Get all rules"""
        return self.rules
    
    def get_rules_by_type(self, rule_type: RuleType) -> list[RuleDefinition]:
        """Get rules by type"""
        return [rule for rule in self.rules.values() if rule.rule_type == rule_type]
    
    def evaluate_rule(
        self,
        rule_name: str,
        response: str,
        llm_judge: Optional[Callable] = None
    ) -> tuple[bool, str]:
        """
        Evaluate a single rule
        
        Args:
            rule_name: Rule name (str) to evaluate
            response: Assistant's response
            llm_judge: Optional LLM judge function for LLM-based rules
            
        Returns:
            Tuple of (passed: bool, reason: str)
        """
        rule = self.get_rule(rule_name)
        if not rule:
            raise ValueError(f"Rule '{rule_name}' not found")
        
        if rule.rule_type == RuleType.RULE:
            return self._evaluate_rule_based(rule.rule_id, response, rule)
        else:
            if llm_judge is None:
                raise ValueError(f"LLM judge is required for LLM-based rule '{rule_name}'")
            return self._evaluate_llm_based(rule, response, llm_judge)
    
    def _evaluate_rule_based(
        self,
        rule_id: int,
        response: str,
        rule: RuleDefinition
    ) -> tuple[bool, str]:
        """Evaluate rule-based rules"""

        # Rule 4: Check for multiple questions (multiple_questions)
        if rule_id == 4 or rule.name == "multiple_questions":
            question_count = response.count('？') + response.count('?')
            passed = question_count <= 1
            return passed, f"{'违规' if not passed else '未违规'}: 发现{question_count}个问号" if not passed else "未违规: 只有一个或零个问号"

        # Rule 7: Check for punctuation used for explanation (punctunation)
        if rule_id == 7 or rule.name == "punctunation":
            # Check for quotes or brackets used for explanation
            has_quotes = bool(re.search(r'["\"][^\"\"]*["\"]', response))
            has_single_quotes = bool(re.search(r"['\'][^'\']*['\']", response))
            has_parens = bool(re.search(r'\([^)]*\)', response))
            has_dashes = bool(re.search(r'—[^—]*—', response))
            has_hyphens = bool(re.search(r'-[^-]*-', response))

            if has_quotes or has_single_quotes or has_parens or has_dashes or has_hyphens:
                return False, "违规: 使用了标点符号进行解释"
            return True, "未违规: 未使用标点符号进行解释"

        # Rule 8: Check for list format (list)
        if rule_id == 8 or rule.name == "list":
            # Check for numbered list format like "1.", "2.", "3."
            list_pattern = r'^\s*\d+\.\s'
            lines = response.split('\n')
            list_count = sum(1 for line in lines if re.match(list_pattern, line))
            passed = list_count == 0
            return passed, f"{'违规' if not passed else '未违规'}: 发现{list_count}个列表项" if not passed else "未违规: 未使用列表格式"

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
        Convert rule names to rule IDs for a specific turn
        
        Args:
            turn_id: Turn number
            rule_mapping: Mapping of turn_id to list of rule_names
            
        Returns:
            List of rule IDs
        """
        rule_names = rule_mapping.get(turn_id, [])
        rule_ids = []
        for rule_name in rule_names:
            rule_id = self.name_to_id.get(rule_name)
            if rule_id:
                rule_ids.append(rule_id)
        return rule_ids
