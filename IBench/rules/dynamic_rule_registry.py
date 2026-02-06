"""
Dynamic Rule Registry
Handles dynamic rule loading from JSON configurations
"""

from typing import List, Dict, Optional, Callable, Any
from dataclasses import dataclass

from IBench.rules.rule_mappings import get_rule_mapping
from IBench.rules.single_rules import SingleRuleRegistry
from IBench.rules.stage_rules import StageRuleRegistry
from IBench.utils.common import Message


@dataclass
class ParsedRule:
    """Parsed rule information"""
    full_name: str  # 完整规则名称，如 "single_turn:sty:gratitude" 或 "multi_turn:FIRST_N:consult_subject"
    type: str  # "single_turn" or "stage_turn"
    rule_class: Optional[str]  # "FIRST_N", "N_th" for stage_turn; None for single_turn
    rule_name: str  # "gratitude", "consult_subject", etc.
    rule_id: int  # 映射的规则ID
    score: int  # 规则分数
    has_kwargs: bool  # 是否需要提取kwargs
    kwargs_schema: dict  # kwargs的schema
    trigger_turns: Optional[List[int]] = None  # 触发轮次（仅用于旧格式）
    N: Optional[int] = None  # FIRST_N或N_th的N值（从JSON配置中读取）


class DynamicRuleRegistry:
    """Registry for dynamic rules loaded from JSON"""

    def __init__(self):
        self.single_rule_registry = SingleRuleRegistry()
        self.stage_rule_registry = StageRuleRegistry()

    def parse_rule(self, rule_full_name: str) -> Optional[ParsedRule]:
        """
        解析规则完整名称

        Args:
            rule_full_name: 完整规则名称
                单轮规则: "single_turn:sty:gratitude"
                阶段规则（新格式）: "multi_turn:FIRST_N:ask:consult_subject"
                阶段规则（旧格式）: "multi_turn:FIRST_N:consult_subject"

        Returns:
            ParsedRule对象，如果未找到则返回None
        """
        # 获取规则映射
        mapping = get_rule_mapping(rule_full_name)
        if not mapping:
            return None

        # 解析规则名称
        parts = rule_full_name.split(":")
        if len(parts) < 3:
            return None

        rule_type = parts[0]

        if rule_type == "single_turn":
            # single_turn:category:rule_name (3 parts)
            if len(parts) != 3:
                return None
            _, category, rule_name = parts
            rule_class = None
        elif rule_type == "multi_turn":
            # 支持两种格式:
            # 新格式: multi_turn:FIRST_N:ask:consult_subject (4 parts)
            # 旧格式: multi_turn:FIRST_N:consult_subject (3 parts)
            if len(parts) == 4:
                # 新格式: multi_turn:turn_class:category:rule_name
                _, rule_class, category, rule_name = parts
            elif len(parts) == 3:
                # 旧格式: multi_turn:turn_class:rule_name
                _, rule_class, rule_name = parts
            else:
                return None
        else:
            return None

        return ParsedRule(
            full_name=rule_full_name,
            type=mapping["type"],
            rule_class=rule_class if rule_type == "multi_turn" else None,
            rule_name=rule_name,
            rule_id=mapping["rule_id"],
            score=mapping["score"],
            has_kwargs=mapping.get("has_kwargs", False),
            kwargs_schema=mapping.get("kwargs_schema", {}),
            trigger_turns=mapping.get("trigger_turns", None),
            N=None  # 从JSON配置中读取
        )

    def get_rules_for_evaluation(
        self,
        rules_config: dict,
        turn_id: int
    ) -> List[ParsedRule]:
        """
        获取指定轮次需要评估的规则

        Args:
            rules_config: JSON中的rules配置
                {
                    "single_turn": ["multi_turn:policy_universe:ask_gender", ...],
                    # stage_turn也可以有，但触发轮次在代码中指定
                }
            turn_id: 当前轮次

        Returns:
            ParsedRule列表
        """
        rules = []

        # 处理单轮规则
        if "single_turn" in rules_config:
            for rule_full_name in rules_config["single_turn"]:
                parsed = self.parse_rule(rule_full_name)
                if parsed and parsed.type == "single_turn":
                    rules.append(parsed)

        # 处理阶段规则
        if "stage_turn" in rules_config:
            # stage_turn可以是：
            # 1. 列表形式：["multi_turn:policy_universe:inquire_target", ...]
            # 2. 字典形式：{1: [...], 2: [...]} 指定轮次
            stage_config = rules_config["stage_turn"]

            if isinstance(stage_config, list):
                # 列表形式，检查trigger_turns
                for rule_full_name in stage_config:
                    parsed = self.parse_rule(rule_full_name)
                    if parsed and parsed.type == "stage_turn":
                        # 检查是否在触发轮次
                        if parsed.trigger_turns and turn_id in parsed.trigger_turns:
                            rules.append(parsed)
            elif isinstance(stage_config, dict):
                # 字典形式，按轮次获取
                for config_turn_id, rule_names in stage_config.items():
                    if int(config_turn_id) == turn_id:
                        for rule_full_name in rule_names:
                            parsed = self.parse_rule(rule_full_name)
                            if parsed and parsed.type == "stage_turn":
                                rules.append(parsed)

        return rules

    def get_rule_definition(self, rule_full_name: str) -> Optional[dict]:
        """
        获取规则定义

        Args:
            rule_full_name: 完整规则名称

        Returns:
            规则定义字典，如果未找到则返回None
        """
        parsed = self.parse_rule(rule_full_name)
        if not parsed:
            return None

        if parsed.type == "single_turn":
            rule_def = self.single_rule_registry.get_rule(parsed.rule_name)
        else:
            rule_def = self.stage_rule_registry.get_rule(parsed.rule_name)

        if not rule_def:
            return None

        return {
            "parsed": parsed,
            "definition": rule_def
        }

    def list_all_policies(self) -> List[str]:
        """
        列出所有可用的策略

        Returns:
            策略名称列表
        """
        # 从rule_mappings中提取所有唯一的policy
        from IBench.rules.rule_mappings import RULE_MAPPINGS

        policies = set()
        for rule_full_name in RULE_MAPPINGS.keys():
            parts = rule_full_name.split(":")
            if len(parts) >= 2:
                policies.add(parts[1])

        return sorted(list(policies))

    def list_rules_by_policy(self, policy_name: str) -> List[str]:
        """
        列出指定策略下的所有规则

        Args:
            policy_name: 策略名称，如 "policy_universe"

        Returns:
            规则完整名称列表
        """
        from IBench.rules.rule_mappings import RULE_MAPPINGS

        prefix = f"multi_turn:{policy_name}:"
        return [
            name for name in RULE_MAPPINGS.keys()
            if name.startswith(prefix)
        ]


def resolve_dynamic_N(
    N_config: Any,
    parsed_rule: ParsedRule,
    messages: List[Message],
    llm_judge_func: Optional[Callable] = None
) -> Optional[int]:
    """
    解析动态 N 值（支持 auto 模式）
    
    Args:
        N_config: 可以是 int、"auto" 或 {"value": "auto", "offset": 1}
        parsed_rule: 解析后的规则对象
        messages: 对话历史
        llm_judge_func: LLM judge 函数（用于检测 precondition）
    
    Returns:
        实际的 N 值，如果 precondition 未满足则返回 None
    """
    # Case 1: 显式指定 N
    if isinstance(N_config, int):
        return N_config
    
    if N_config is None:
        return None
    
    # Case 2: "auto" 模式
    offset = 0  # 默认 offset（precondition满足的那一轮）

    if isinstance(N_config, str):
        if N_config == "auto":
            offset = 0  # 保持默认值
        else:
            raise ValueError(f"不支持的 N 值: {N_config}")
    elif isinstance(N_config, dict):
        if N_config.get("value") != "auto":
            raise ValueError(f"不支持的 N 值: {N_config}")
        # 使用 dict 中指定的 offset，如果未指定则使用默认值 0
        offset = N_config.get("offset", 0)
    else:
        raise ValueError(f"不支持的 N 值类型: {type(N_config)}")
    
    # 从 rule_mappings 中获取 precondition
    mapping = get_rule_mapping(parsed_rule.full_name)
    precondition = mapping.get("precondition")
    
    if not precondition:
        raise ValueError(f"规则 {parsed_rule.rule_name} 没有 precondition，无法使用 N=auto")
    
    # 扫描对话，找到 precondition 满足的轮次
    triggered_turn = find_precondition_turn(messages, precondition, llm_judge_func)
    
    if triggered_turn is None:
        print(f"⚠ 警告: precondition '{precondition}' 从未满足，跳过该规则")
        return None
    
    # 计算 N = N' + offset
    return triggered_turn + offset


def find_precondition_turn(
    messages: List[Message],
    precondition: str,
    llm_judge_func: Optional[Callable] = None
) -> Optional[int]:
    """
    扫描对话历史，找到满足 precondition 的第一轮
    
    Args:
        messages: 完整对话历史
        precondition: 前置条件描述
        llm_judge_func: LLM judge 函数
    
    Returns:
        满足条件的第一轮次编号，如果未满足则返回 None
    """
    if not llm_judge_func:
        print(f"⚠ 警告: 没有 LLM judge，无法检测 precondition '{precondition}'")
        return None
    
    # 跳过 system 消息
    start_idx = 1 if messages[0].role == "system" else 0

    # 考虑最后一条单独的 user 消息（Golden History 评估场景）
    # 如果最后一条是 user，说明有一轮未完成，应该计入 max_turns
    if messages[-1].role == "user":
        max_turns = (len(messages) - start_idx + 1) // 2
    else:
        max_turns = (len(messages) - start_idx) // 2

    for turn_id in range(1, max_turns + 1):
        # 获取该轮的 user 消息
        user_idx = start_idx + 2 * (turn_id - 1)
        if user_idx >= len(messages):
            break
        
        user_message = messages[user_idx].content
        
        # 使用 LLM judge 检测是否满足 precondition
        prompt = f"""请检查用户的以下回复是否满足条件：{precondition}

用户回复：{user_message}

只回答：
- "YES"：满足条件
- "NO"：不满足条件
"""
        
        try:
            result = llm_judge_func(user_message, prompt)
            
            # result 是 tuple[bool, str]，解包获取响应文本
            if result and isinstance(result, tuple) and len(result) >= 2:
                response_text = result[1]  # 获取第二个元素（reason）
                if "YES" in response_text.upper():
                    return turn_id
        except Exception as e:
            print(f"⚠ 警告: 检测 precondition 时出错: {e}")
            continue
    
    return None
