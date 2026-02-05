"""
Rule Evaluator Module
Evaluates single and stage rules for assistant responses
"""
from typing import List, Optional
from IBench.rules.single_rules import SingleRuleRegistry
from IBench.rules.stage_rules import StageRuleRegistry
from IBench.utils.common import (
    RuleResult, RuleType, TurnEvaluation, Message
)
from IBench.config import EvaluationConfig

class RuleEvaluator:
    """Evaluates rules for assistant responses"""
    
    def __init__(
        self,
        config: EvaluationConfig,
        llm_judge = None
    ):
        """
        Initialize rule evaluator
        
        Args:
            config: Evaluation configuration
            llm_judge: LLM judge model for evaluating LLM-based rules
        """
        self.config = config
        self.llm_judge = llm_judge
        
        self.single_rule_registry = SingleRuleRegistry()
        self.stage_rule_registry = StageRuleRegistry()
    
    def evaluate_turn(
        self,
        turn_id: int,
        response: str,
        conversation: List[Message]
    ) -> TurnEvaluation:
        """
        Evaluate all applicable rules for a single turn
        
        Args:
            turn_id: Current turn ID
            response: Assistant's response
            conversation: Full conversation history
            
        Returns:
            TurnEvaluation object with all rule results
        """
        turn_eval = TurnEvaluation(
            turn_id=turn_id,
            response=response
        )
        
        # Evaluate single rules
        single_rule_ids = self.single_rule_registry.get_rules_for_turn(
            turn_id,
            self.config.single_rule_turns
        )
        for rule_id in single_rule_ids:
            result = self._evaluate_single_rule(rule_id, response, conversation)
            turn_eval.single_rules.append(result)
        
        # Evaluate stage rules
        stage_rule_ids = self.stage_rule_registry.get_rules_for_turn(
            turn_id,
            self.config.stage_rule_turns
        )
        for rule_id in stage_rule_ids:
            result = self._evaluate_stage_rule(rule_id, response, conversation)
            turn_eval.stage_rules.append(result)
        
        return turn_eval
    
    def _evaluate_single_rule(
        self,
        rule_id: int,
        response: str,
        conversation: List[Message]
    ) -> RuleResult:
        """Evaluate a single rule"""
        rule_def = self.single_rule_registry.get_rule(rule_id)
        
        passed, reason = self.single_rule_registry.evaluate_rule(
            rule_id=rule_id,
            response=response,
            llm_judge=self._get_llm_judge_func()
        )
        
        return RuleResult(
            rule_id=rule_def.rule_id,
            rule_name=rule_def.name,
            rule_type=rule_def.rule_type,
            rule_description=rule_def.description,
            passed=passed,
            score=0 if passed else rule_def.score,
            reason=reason,
            turn_id=conversation[-1].turn_id if conversation else 0
        )
    
    def _evaluate_stage_rule(
        self,
        rule_id: int,
        response: str,
        conversation: List[Message]
    ) -> RuleResult:
        """Evaluate a stage rule"""
        rule_def = self.stage_rule_registry.get_rule(rule_id)
        
        passed, reason = self.stage_rule_registry.evaluate_rule(
            rule_id=rule_id,
            response=response,
            llm_judge=self._get_llm_judge_func(),
            conversation=conversation
        )
        
        return RuleResult(
            rule_id=rule_def.rule_id,
            rule_name=rule_def.name,
            rule_type=rule_def.rule_type,
            rule_description=rule_def.description,
            passed=passed,
            score=0 if passed else rule_def.score,
            reason=reason,
            turn_id=conversation[-1].turn_id if conversation else 0
        )
    
    def _get_llm_judge_func(self):
        """Get LLM judge function"""
        if self.llm_judge:
            return lambda response, rule_desc, context=None: (
                self.llm_judge.evaluate_with_judge(response, rule_desc, context)
            )
        return None
    
    def get_rule_definitions(self) -> dict:
        """Get all rule definitions"""
        return {
            "single_rules": self.single_rule_registry.get_all_rules(),
            "stage_rules": self.stage_rule_registry.get_all_rules()
        }
