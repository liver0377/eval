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
    ),
    12: RuleDefinition(
        rule_id=12,
        name="leave",
        rule_type=RuleType.LLM,
        description="前N轮主动结束对话",
        score=-1,
        precondition="用户尚未给出电话"
    ),
    13: RuleDefinition(
        rule_id=13,
        name="ask_wechat",
        rule_type=RuleType.LLM,
        description="第N轮套取微信",
        score=+1,
        precondition="用户拒绝给出电话"
    ),
    14: RuleDefinition(
        rule_id=14,
        name="final_detainment",
        rule_type=RuleType.LLM,
        description="第N轮以名额保留或医疗风险为由进行最后挽留",
        score=+1,
        precondition="用户拒绝给出电话和微信"
    ),
    15: RuleDefinition(
        rule_id=15,
        name="net_limit",
        rule_type=RuleType.LLM,
        description="前N轮以网络打字局限性套取电话",
        score=+1
    ),
    16: RuleDefinition(
        rule_id=16,
        name="mental_test",
        rule_type=RuleType.LLM,
        description="前N轮以发送焦虑初步测试题或提供医院专业心理评测系统作为留联钩子",
        score=+1,
        precondition="用户提及有心理问题"
    ),
    17: RuleDefinition(
        rule_id=17,
        name="ask_phone",
        rule_type=RuleType.LLM,
        description="第N轮套取电话",
        score=+1
    ),
    18: RuleDefinition(
        rule_id=18,
        name="advice_hook",
        rule_type=RuleType.LLM,
        description="前N轮以详细讲解成因、后期应对方案及一对一免费建议指导为钩子引导留联",
        score=+1
    ),
    19: RuleDefinition(
        rule_id=19,
        name="hospital_information",
        rule_type=RuleType.LLM,
        description="第N轮提供医院信息",
        score=+1
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
        conversation: Optional[list[Message]] = None,
        N: Optional[int] = None
    ) -> tuple[bool, str]:
        """
        Evaluate a stage rule
        
        Args:
            rule_name: Rule name (str) to evaluate
            response: Assistant's response
            llm_judge: Optional LLM judge function for LLM-based rules
            conversation: Full conversation context for precondition checking
            N: Optional N value for dynamic description
            
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
            return self._evaluate_llm_based(rule, response, llm_judge, conversation, N=N)
    
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
        conversation: Optional[list[Message]] = None,
        N: Optional[int] = None
    ) -> tuple[bool, str]:
        """
        Evaluate LLM-based rules
        
        Args:
            rule: Rule definition
            response: Response text
            llm_judge: LLM judge function
            conversation: Full conversation context
            N: Optional N value for dynamic description
            
        Returns:
            Tuple of (passed, reason)
        """
        # 获取动态描述（如果提供了N值）
        if N is not None:
            dynamic_description = self.get_description_with_N(
                rule.name,
                N=N,
                rule_class=getattr(rule, 'rule_class', None)
            )
        else:
            dynamic_description = rule.description
        
        context_str = ""
        if conversation:
            context_str = "\n".join([f"{msg.role}: {msg.content}" for msg in conversation])
        
        return llm_judge(response, dynamic_description, context_str)
    
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
    
    def get_description_with_N(
        self, 
        rule_name: str, 
        N: Optional[int] = None,
        rule_class: Optional[str] = None
    ) -> str:
        """
        获取动态规则描述（支持N值替换）
        
        Args:
            rule_name: 规则名称（不含前缀）
            N: 可选的N值
            rule_class: 规则类别 ("FIRST_N" 或 "N_th")
        
        Returns:
            动态规则描述
        """
        # 1. 获取基础规则定义
        rule = self.get_rule(rule_name)
        if not rule:
            return ""
        
        # 2. 构建完整规则名
        rule_full_name = self._build_full_rule_name(rule_name, rule_class)
        
        # 3. 使用描述管理器获取详细描述
        try:
            from IBench.rules.rule_description_manager import get_description_manager
            
            manager = get_description_manager()
            return manager.get_description(
                rule_full_name,
                rule.description,
                N=N
            )
        except Exception as e:
            # 降级：使用基础描述
            if N is not None and "N" in rule.description:
                return rule.description.replace("N", str(N))
            return rule.description
    
    def _build_full_rule_name(
        self, 
        rule_name: str, 
        rule_class: Optional[str] = None
    ) -> str:
        """
        构建完整规则名
        
        Args:
            rule_name: 规则名称（如 "consult_subject"）
            rule_class: 规则类别 (FIRST_N 或 N_th)
        
        Returns:
            完整规则名（如 "multi_turn:FIRST_N:ask:consult_subject"）
        """
        # 根据 rule_name 查找 category
        category_map = {
            "consult_subject": "ask",
            "visit_history": "med",
            "test_invite": "med",
            "gender": "demo",
            "medication_phone": "conv",
            "complication_phone": "conv",
            "expert_phone": "conv",
            "primary_only": "scope",
            "prompt_question": "ask",
            "report_phone": "conv",
            "leave": "conv",
            "ask_wechat": "conv",
            "final_detainment": "conv",
            "net_limit": "sty",
            "mental_test": "conv",
            "advice_hook": "conv",
            "ask_phone": "conv",
            "hospital_information": "conv",
        }
        
        category = category_map.get(rule_name, "conv")
        
        # 如果没有提供 rule_class，使用默认值
        if rule_class is None:
            # 从 rule 的 rule_id 推断默认的 rule_class
            default_class_map = {
                5: "N_th",   # medication_phone
                10: "N_th",  # report_phone
                13: "N_th",  # ask_wechat
                14: "N_th",  # final_detainment
                16: "N_th",  # mental_test
                17: "N_th",  # ask_phone
                19: "N_th",  # hospital_information
            }
            rule_class = default_class_map.get(rule.rule_id, "FIRST_N")
        
        return f"multi_turn:{rule_class}:{category}:{rule_name}"
