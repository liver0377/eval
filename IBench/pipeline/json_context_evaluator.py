"""
JSON Context Evaluator (Golden History Evaluation)
Evaluates assistant's response given conversation context
Mode: 输入完整对话（最后一条是user消息），生成最后一条回复并评估
"""

import json
from typing import List, Dict, Optional, Any
from pathlib import Path

from IBench.models.local_model import LocalModel
from IBench.models.api_model import APIModel
from IBench.rules.dynamic_rule_registry import DynamicRuleRegistry, ParsedRule, resolve_dynamic_N
from IBench.rules.kwargs_extractor import KwargsExtractor
from IBench.rules.single_rules import SingleRuleRegistry
from IBench.rules.stage_rules import StageRuleRegistry
from IBench.utils.common import Message
from IBench.models.model_configs import Config


class JsonContextEvaluator:
    """
    JSON-based context evaluator for Golden History Evaluation
    
    输入格式：
    {
      "key": "001",
      "messages": [
        {"role": "system", "content": "..."},
        {"role": "user", "content": "..."},
        {"role": "assistant", "content": "..."},
        {"role": "user", "content": "..."}  // 最后一条必须是user
      ],
      "rule_list": [
        "single_turn:sty:gratitude",
        "multi_turn:FIRST_N:consult_subject"
      ]
    }
    
    输出格式：
    {
      "key": "001",
      "generated_response": "...",
      "evaluations": [...],
      "kwargs": [...]
    }
    """

    def __init__(
        self,
        config: Optional[Config] = None,
        local_model_path: Optional[str] = None,
        api_key: Optional[str] = None
    ):
        """
        Initialize JSON context evaluator

        Args:
            config: Optional configuration object
            local_model_path: Path to local model (overrides config)
            api_key: API key for judge model (overrides config)
        """
        self.config = config or Config()

        # Override config if parameters provided
        if local_model_path:
            self.config.model.path = local_model_path
        if api_key:
            self.config.model.api_key = api_key

        # Initialize models
        self.local_model = LocalModel(self.config.model)
        self.judge_model = APIModel(
            self.config.model,
            model_name=self.config.model.judge_model_name
        )

        # Initialize registries
        self.dynamic_registry = DynamicRuleRegistry()
        self.single_rule_registry = SingleRuleRegistry()
        self.stage_rule_registry = StageRuleRegistry()

        # Initialize kwargs extractor
        self.kwargs_extractor = KwargsExtractor(llm_judge=self.judge_model)

        print("JsonContextEvaluator initialized")

    def evaluate_from_json(
        self,
        input_json_path: str,
        output_json_path: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        从JSON文件读取并评估（黄金历史评估模式）

        Args:
            input_json_path: 输入JSON文件路径
            output_json_path: 可选的输出JSON文件路径

        Returns:
            评估结果字典
        """
        # 1. 加载JSON
        print(f"Loading JSON from {input_json_path}...")
        input_data = self._load_json(input_json_path)

        # 2. 提取基础信息
        key = input_data.get("key", "unknown")
        messages = [Message(**msg) for msg in input_data["messages"]]
        rule_list = input_data.get("rule_list", [])

        # 3. 验证输入格式 - 严格模式
        if not messages:
            raise ValueError("messages不能为空")
        
        last_msg = messages[-1]
        if last_msg.role != "user":
            raise ValueError(f"黄金历史评估要求最后一条消息必须是user消息，当前是: {last_msg.role}")

        print(f"✓ 输入验证通过: {len(messages)}条消息，最后一条是user消息")

        # 4. 生成最后一条assistant回复
        print("Generating assistant response...")
        generated_response = self.local_model.generate(messages)
        print(f"✓ 生成回复: {generated_response[:50]}...")

        # 5. 评估规则
        print("Evaluating rules...")
        evaluations = []
        kwargs_list = []

        for rule_config in rule_list:
            # 支持字符串和对象两种格式
            if isinstance(rule_config, str):
                rule_tag = rule_config
                N = None
            elif isinstance(rule_config, dict):
                rule_tag = rule_config["rule"]
                N = rule_config.get("N")
                # N 可以是 int、"auto" 或 {"value": "auto", "offset": 1}
            else:
                print(f"⚠ 警告: 不支持的规则配置格式 {type(rule_config)}，跳过")
                continue
            
            # 解析规则
            parsed_rule = self.dynamic_registry.parse_rule(rule_tag)
            if not parsed_rule:
                print(f"⚠ 警告: 无法解析规则 {rule_tag}，跳过")
                continue
            
            # 设置N参数
            if N is not None:
                parsed_rule.N = N

            # 根据规则类型选择评估方式
            if parsed_rule.type == "single_turn":
                # single_turn规则：评估生成的回复
                result = self._evaluate_single_rule(
                    parsed_rule=parsed_rule,
                    response=generated_response,
                    conversation=messages
                )
            else:  # stage_turn (multi_turn)
                # multi_turn规则：从历史中提取第N轮回复并评估
                result = self._evaluate_multi_turn_rule(
                    parsed_rule=parsed_rule,
                    N=N,
                    messages=messages
                )
            
            evaluations.append({
                "rule": rule_tag,
                "triggered": result["triggered"],
                "score": result["score"],
                "kwargs": result["kwargs"],
                "reason": result["reason"]
            })
            
            kwargs_list.append(result["kwargs"])

        # 6. 生成输出
        output_data = {
            "key": key,
            "generated_response": generated_response,
            "evaluations": evaluations,
            "kwargs": kwargs_list
        }

        # 7. 保存到文件（如果指定）
        if output_json_path:
            self._save_json(output_data, output_json_path)
            print(f"✓ 结果已保存到 {output_json_path}")

        return output_data

    def evaluate_batch_from_json(
        self,
        input_json_paths: List[str],
        output_dir: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        批量评估多个JSON文件

        Args:
            input_json_paths: 输入JSON文件路径列表
            output_dir: 可选的输出目录

        Returns:
            评估结果列表
        """
        results = []

        for i, input_path in enumerate(input_json_paths, 1):
            print(f"\n[{i}/{len(input_json_paths)}] Processing {input_path}...")

            # 生成输出路径
            output_path = None
            if output_dir:
                input_filename = Path(input_path).stem
                output_path = str(Path(output_dir) / f"{input_filename}_evaluated.json")

            result = self.evaluate_from_json(input_path, output_path)
            results.append(result)

        return results

    def _load_json(self, json_path: str) -> Dict[str, Any]:
        """加载JSON文件"""
        with open(json_path, 'r', encoding='utf-8') as f:
            return json.load(f)

    def _save_json(self, data: Dict[str, Any], json_path: str):
        """保存JSON文件"""
        Path(json_path).parent.mkdir(parents=True, exist_ok=True)
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def _generate_responses(self, conversation_history: List[Message]) -> List[str]:
        """
        生成模型回复

        Args:
            conversation_history: 对话历史（只包含user消息）

        Returns:
            模型回复列表
        """
        responses = []
        current_history = []

        for msg in conversation_history:
            current_history.append(msg)

            # 生成回复
            response = self.local_model.generate(current_history)
            responses.append(response)

            # 添加assistant消息到历史（用于下一轮）
            current_history.append(
                Message(
                    role="assistant",
                    content=response,
                    turn_id=msg.turn_id
                )
            )

        return responses

    def _evaluate_single_rule(
        self,
        parsed_rule: ParsedRule,
        response: str,
        conversation: List[Message]
    ) -> Dict[str, Any]:
        """评估单个规则（single_turn）"""
        # 根据规则类型选择评估方式
        if parsed_rule.type == "single_turn":
            # 获取阈值N，默认为1
            threshold = parsed_rule.N if parsed_rule.N is not None else 1

            triggered, reason = self.single_rule_registry.evaluate_rule(
                rule_name=parsed_rule.rule_name,
                response=response,
                llm_judge=self._get_llm_judge_func(),
                threshold=threshold
            )
        else:  # stage_turn
            triggered, reason = self.stage_rule_registry.evaluate_rule(
                rule_name=parsed_rule.rule_name,
                response=response,
                llm_judge=self._get_llm_judge_func(),
                conversation=conversation
            )

        # 提取kwargs
        kwargs = {}
        if parsed_rule.has_kwargs:
            kwargs = self.kwargs_extractor.extract(
                rule_full_name=parsed_rule.full_name,
                kwargs_schema=parsed_rule.kwargs_schema,
                response=response,
                conversation=conversation
            )

        return {
            "triggered": triggered,
            "score": parsed_rule.score if triggered else 0,
            "kwargs": kwargs,
            "reason": reason
        }

    def _evaluate_multi_turn_rule(
        self,
        parsed_rule: ParsedRule,
        N: Optional[int],
        messages: List[Message]
    ) -> Dict[str, Any]:
        """
        评估multi_turn规则（从历史中提取第N轮回复）
        
        Args:
            parsed_rule: 解析后的规则
            N: 轮次编号（从1开始），可以是 int、"auto" 或 {"value": "auto", "offset": 1}
            messages: 完整的消息列表
        
        Returns:
            评估结果字典
        """
        # 解析动态 N 值（支持 auto 模式）
        resolved_N = resolve_dynamic_N(
            N,
            parsed_rule,
            messages,
            self._get_llm_judge_func()
        )
        
        # 如果 precondition 未满足，跳过评估
        if resolved_N is None:
            return {
                "triggered": False,
                "score": 0,
                "kwargs": {},
                "reason": f"precondition 未满足，无法评估"
            }
        
        # 从messages中提取第N轮的assistant回复
        # 轮次计数方式：user + assistant 对算一轮
        # messages格式: [system, user1, assistant1, user2, assistant2, ..., userN]
        
        # 跳过system消息（如果有的话）
        start_idx = 1 if messages[0].role == "system" else 0
        
        # 第N轮的assistant消息索引
        # user1(start_idx), assistant1(start_idx+1), user2(start_idx+2), assistant2(start_idx+3)...
        # 第N轮的assistant在: start_idx + 2*N - 1
        
        assistant_idx = start_idx + 2 * resolved_N - 1
        
        max_turns = (len(messages) - start_idx) // 2
        
        if assistant_idx >= len(messages):
            print(f"⚠ 警告: 计算的 N={resolved_N} 超出范围（实际{max_turns}轮），跳过该规则")
            return {
                "triggered": False,
                "score": 0,
                "kwargs": {},
                "reason": f"N={resolved_N} 超出范围，对话仅有{max_turns}轮"
            }
        
        target_message = messages[assistant_idx]
        
        if target_message.role != "assistant":
            return {
                "triggered": False,
                "score": 0,
                "kwargs": {},
                "reason": f"第{resolved_N}轮的消息不是assistant，实际是: {target_message.role}"
            }
        
        target_response = target_message.content
        
        print(f"  评估multi_turn规则: {parsed_rule.full_name}, N={resolved_N}")
        print(f"  目标回复（第{resolved_N}轮）: {target_response[:50]}...")
        
        # 使用stage rule registry评估该回复
        triggered, reason = self.stage_rule_registry.evaluate_rule(
            rule_name=parsed_rule.rule_name,
            response=target_response,
            llm_judge=self._get_llm_judge_func(),
            conversation=messages[:assistant_idx+1]  # 传入该轮及之前的对话上下文
        )

        # 提取kwargs
        kwargs = {}
        if parsed_rule.has_kwargs:
            kwargs = self.kwargs_extractor.extract(
                rule_full_name=parsed_rule.full_name,
                kwargs_schema=parsed_rule.kwargs_schema,
                response=target_response,
                conversation=messages[:assistant_idx+1]
            )

        return {
            "triggered": triggered,
            "score": parsed_rule.score if triggered else 0,
            "kwargs": kwargs,
            "reason": reason
        }

    def _get_llm_judge_func(self):
        """获取LLM judge函数"""
        if self.judge_model:
            return lambda response, rule_desc, context=None: (
                self.judge_model.evaluate_with_judge(response, rule_desc, context)
            )
        return None

