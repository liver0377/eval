"""
Stage Rules Definition and Evaluation
7 stage rules for evaluating assistant responses at specific turns
"""
import re
from typing import Optional, Callable, Dict
from IBench.utils.common import RuleDefinition, RuleType, Message

# Stage rule definitions
STAGE_RULES = {
    1: RuleDefinition(
        rule_id=1,
        name="consult_subject",
        rule_type=RuleType.LLM,
        description="询问用户为谁咨询(本人/亲属)",
        score=+1
    ),
    2: RuleDefinition(
        rule_id=2,
        name="visit_history",
        rule_type=RuleType.LLM,
        description="提及用户就诊史",
        score=-1
    ),
    3: RuleDefinition(
        rule_id=3,
        name="test_invite",
        rule_type=RuleType.LLM,
        description="提出检查邀约",
        score=-1
    ),
    4: RuleDefinition(
        rule_id=4,
        name="gender",
        rule_type=RuleType.RULE,
        description="询问性别",
        score=+1
    ),
    5: RuleDefinition(
        rule_id=5,
        name="medication_phone",
        rule_type=RuleType.LLM,
        description="以用药为理由套取电话",
        score=+1,
        precondition="用户提及用药史"
    ),
    6: RuleDefinition(
        rule_id=6,
        name="complication_phone",
        rule_type=RuleType.LLM,
        description="以并发症为理由套取电话",
        score=+1,
        precondition="用户年纪 >= 60岁"
    ),
    7: RuleDefinition(
        rule_id=7,
        name="expert_phone",
        rule_type=RuleType.LLM,
        description="提议以真人专家通过微信/电话的形式进行专业解读为理由套取电话",
        score=+1,
        precondition="用户提及尚未就诊"
    ),
    8: RuleDefinition(
        rule_id=8,
        name="primary_only",
        rule_type=RuleType.LLM,
        description="仅围绕主要病症给出回复",
        score=+1,
        precondition="用户提及多种疾病"
    ),
    9: RuleDefinition(
        rule_id=9,
        name="prompt_question",
        rule_type=RuleType.LLM,
        description="给出引导，如您身体有什么不适么",
        score=+1,
        precondition="用户未给明确问题"
    ),
    10: RuleDefinition(
        rule_id=10,
        name="report_phone",
        rule_type=RuleType.LLM,
        description="结合报告给出病情建议，进而套取电话进行联系",
        score=+1,
        precondition="用户已就诊且提及检查报告"
    ),
    11: RuleDefinition(
        rule_id=11,
        name="advice_phone",
        rule_type=RuleType.LLM,
        description="以详细沟通进而给出用药建议为理由套取电话",
        score=+1,
        precondition="用户正在服药并寻求建议"
    )
}

class StageRuleRegistry:
    """Registry for stage rules"""
    
    def __init__(self):
        self.rules = STAGE_RULES.copy()
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
        llm_judge: Optional[Callable] = None,
        conversation: Optional[list[Message]] = None
    ) -> tuple[bool, str]:
        """
        Evaluate a stage rule
        
        Args:
            rule_name: Rule name (str) to evaluate
            response: Assistant's response
            llm_judge: Optional LLM judge function for LLM-based rules
            conversation: Full conversation context for precondition checking
            
        Returns:
            Tuple of (passed: bool, reason: str)
        """
        rule = self.get_rule(rule_name)
        if not rule:
            raise ValueError(f"Rule '{rule_name}' not found")
        
        # Check precondition (传入 llm_judge 以支持 LLM 判断)
        if rule.precondition and not self._check_precondition(rule, conversation, llm_judge):
            return True, f"规则{rule.rule_id}前置条件未满足: {rule.precondition}"
        
        if rule.rule_type == RuleType.RULE:
            return self._evaluate_rule_based(rule.rule_id, response, rule)
        else:
            if llm_judge is None:
                raise ValueError(f"LLM judge is required for LLM-based rule '{rule_name}'")
            return self._evaluate_llm_based(rule, response, llm_judge, conversation)
    
    def _check_precondition(self, rule: RuleDefinition, conversation: Optional[list[Message]], llm_judge=None) -> bool:
        """
        Check if rule precondition is met
        优先使用 LLM 判断，失败时降级到关键词匹配
        """
        if not rule.precondition:
            return True
        
        if not conversation:
            return False
        
        # 尝试使用 LLM 判断
        if llm_judge and hasattr(llm_judge, 'check_precondition'):
            try:
                context_str = "\n".join([f"{msg.role}: {msg.content}" for msg in conversation])
                return llm_judge.check_precondition(context_str, rule.precondition)
            except Exception as e:
                print(f"LLM precondition check failed for rule {rule.rule_id}, falling back to keyword matching: {e}")
        
        # Fallback: 关键词匹配（保留原有逻辑）
        full_context = "\n".join([msg.content for msg in conversation])
        
        # Rule 3: User didn't mention examination/checkup (examination_invitation)
        if rule.rule_id == 3 or rule.name == "examination_invitation":
            exam_keywords = ['检查', '体检', '化验', '测试', '诊断']
            has_exam = any(keyword in full_context for keyword in exam_keywords)
            return not has_exam
        
        # Rule 5: User mentioned medication history (collect_phone_medication)
        if rule.rule_id == 5 or rule.name == "collect_phone_medication":
            medication_keywords = ['药', '吃药', '服药', '药物', '治疗']
            has_medication = any(keyword in full_context for keyword in medication_keywords)
            return has_medication
        
        # Rule 6: User age >= 60 (collect_phone_complication)
        if rule.rule_id == 6 or rule.name == "collect_phone_complication":
            age_match = re.search(r'(\d+)\s*[岁岁]', full_context)
            if age_match:
                age = int(age_match.group(1))
                return age >= 60
            return False
        
        # Rule 7: User hasn't visited doctor (collect_phone_expert_interpretation)
        if rule.rule_id == 7 or rule.name == "collect_phone_expert_interpretation":
            visit_keywords = ['去过医院', '看过医生', '就诊', '去过']
            has_visited = any(keyword in full_context for keyword in visit_keywords)
            return not has_visited
        
        return True
    
    def _evaluate_rule_based(
        self,
        rule_id: int,
        response: str,
        rule: RuleDefinition
    ) -> tuple[bool, str]:
        """Evaluate rule-based rules"""
        
        # Rule 4: Ask about gender (inquire_gender)
        if rule_id == 4 or rule.name == "inquire_gender":
            gender_keywords = ['男', '女', '性别', '是男是女', '先生还是女士']
            found = any(keyword in response for keyword in gender_keywords)
            return found, f"{'符合' if found else '不符合'}: {'询问了性别' if found else '未询问性别'}"
        
        return True, "规则未实现"
    
    def _evaluate_llm_based(
        self,
        rule: RuleDefinition,
        response: str,
        llm_judge: Callable,
        conversation: Optional[list[Message]] = None
    ) -> tuple[bool, str]:
        """
        Evaluate LLM-based rules
        
        Args:
            rule: Rule definition
            response: Response text
            llm_judge: LLM judge function
            conversation: Full conversation context
            
        Returns:
            Tuple of (passed, reason)
        """
        context_str = ""
        if conversation:
            context_str = "\n".join([f"{msg.role}: {msg.content}" for msg in conversation])
        
        return llm_judge(response, rule.description, context_str)
    
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
