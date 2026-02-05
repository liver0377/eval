"""
Dynamic Interactive Evaluation Pipeline
Supports the new dynamic interaction evaluation format with FIRST_N and N_th rules
"""

import json
from typing import List, Dict, Any, Optional
from pathlib import Path

from IBench.models.api_model import APIModel
from IBench.rules.dynamic_rule_registry import DynamicRuleRegistry, ParsedRule
from IBench.rules.kwargs_extractor import KwargsExtractor
from IBench.rules.single_rules import SingleRuleRegistry
from IBench.rules.stage_rules import StageRuleRegistry
from IBench.utils.common import Message
from IBench.models.model_configs import Config


class DynamicInteractiveEvaluator:
    """Dynamic interactive evaluator with support for FIRST_N and N_th rules"""

    def __init__(
        self,
        config: Optional[Config] = None,
        api_key: Optional[str] = None
    ):
        """
        Initialize dynamic interactive evaluator

        Args:
            config: Optional configuration object
            api_key: API key for judge model (overrides config)
        """
        self.config = config or Config()

        # Override config if api_key provided
        if api_key:
            self.config.model.api_key = api_key

        # Initialize judge model
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

        print("DynamicInteractiveEvaluator initialized")

    def evaluate_from_json(
        self,
        input_json_path: str,
        output_json_path: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        从JSON文件读取并评估（动态交互评估格式）

        输入格式：
        {
          "key": "001",
          "system_prompt": "...",
          "messages": [
            {"role": "user", "content": "...", "turn_id": 0},
            {"role": "assistant", "content": "...", "turn_id": 0},
            {"role": "user", "content": "...", "turn_id": 1},
            ...
          ],
          "rule_list": [
            "single_turn:sty:gratitude",
            "single_turn:sty:explain_filler",
            {"rule": "multi_turn:FIRST_N:consult_subject", "N": 3},
            {"rule": "multi_turn:N_th:gender", "N": 4}
          ]
        }

        输出格式：
        {
          "key": "001",
          "evaluations": {
            "0": {
              "turn_id": 0,
              "response": "...",
              "rules": [
                {
                  "rule_tag": "...",
                  "passed": true,
                  "score": 1,
                  "kwargs": {...}
                }
              ]
            }
          },
          "summary": {
            "total_score": 5,
            "total_turns": 5
          }
        }

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

        # 3. 组织对话数据
        conversation_by_turn = self._organize_conversation(messages)

        # 4. 评估对话
        print("Evaluating conversation...")
        evaluations = self._evaluate_conversation(
            conversation_by_turn=conversation_by_turn,
            rule_list=rule_list
        )

        # 5. 生成汇总
        summary = self._generate_summary(evaluations)

        # 6. 生成输出
        output_data = {
            "key": key,
            "evaluations": evaluations,
            "summary": summary
        }

        # 7. 保存到文件（如果指定）
        if output_json_path:
            self._save_json(output_data, output_json_path)
            print(f"Results saved to {output_json_path}")

        return output_data

    def _organize_conversation(self, messages: List[Message]) -> Dict[int, Dict]:
        """
        组织对话数据，按轮次分组

        Args:
            messages: 消息列表

        Returns:
            按轮次组织的对话字典 {turn_id: {"user": ..., "assistant": ...}}
        """
        conversation_by_turn = {}
        
        for msg in messages:
            turn_id = msg.turn_id
            if turn_id not in conversation_by_turn:
                conversation_by_turn[turn_id] = {}
            
            conversation_by_turn[turn_id][msg.role] = msg

        return conversation_by_turn

    def _evaluate_conversation(
        self,
        conversation_by_turn: Dict[int, Dict],
        rule_list: List
    ) -> Dict[str, Any]:
        """
        评估对话

        Args:
            conversation_by_turn: 按轮次组织的对话
            rule_list: 规则列表（支持字符串或对象格式）

        Returns:
            评估结果字典
        """
        evaluations = {}

        # 规则分类：单轮规则和阶段规则
        single_turn_rules = []
        stage_turn_rules = []

        for rule_config in rule_list:
            # 支持字符串和对象两种格式（与黄金历史评估统一）
            if isinstance(rule_config, str):
                rule_tag = rule_config
                N = None
            elif isinstance(rule_config, dict):
                rule_tag = rule_config.get("rule")
                N = rule_config.get("N")
            else:
                print(f"⚠ 警告: 不支持的规则配置格式 {type(rule_config)}，跳过")
                continue

            parsed = self.dynamic_registry.parse_rule(rule_tag)
            if not parsed:
                print(f"⚠ 警告: 无法解析规则 {rule_tag}，跳过")
                continue

            # 设置N值
            if N is not None:
                parsed.N = N

            if parsed.type == "single_turn":
                single_turn_rules.append({
                    "parsed": parsed
                })
            elif parsed.type == "stage_turn":
                stage_turn_rules.append({
                    "parsed": parsed
                })

        # 评估每一轮
        for turn_id in sorted(conversation_by_turn.keys()):
            turn_data = conversation_by_turn[turn_id]
            
            # 获取assistant的回复
            if "assistant" not in turn_data:
                continue
            
            response = turn_data["assistant"].content
            
            # 构建对话历史（从第0轮到当前轮）
            conversation_history = []
            for i in range(turn_id + 1):
                if i in conversation_by_turn:
                    if "user" in conversation_by_turn[i]:
                        conversation_history.append(conversation_by_turn[i]["user"])
                    if "assistant" in conversation_by_turn[i]:
                        conversation_history.append(conversation_by_turn[i]["assistant"])
            
            # 评估该轮的规则
            rule_results = []

            # 评估单轮规则（默认应用于所有轮次）
            for rule_info in single_turn_rules:
                result = self._evaluate_single_rule(
                    parsed_rule=rule_info["parsed"],
                    response=response,
                    conversation=conversation_history
                )
                rule_results.append(result)
            
            # 评估阶段规则
            for rule_info in stage_turn_rules:
                rule_class = rule_info["parsed"].rule_class
                N = rule_info["parsed"].N
                
                should_evaluate = False
                
                if rule_class == "N_th":
                    # N_th规则：只在第N轮评估
                    if turn_id == N - 1:  # turn_id从0开始，所以是N-1
                        should_evaluate = True
                elif rule_class == "FIRST_N":
                    # FIRST_N规则：在前N轮都评估（后续会汇总判断"至少触发一次"）
                    if turn_id < N:
                        should_evaluate = True
                
                if should_evaluate:
                    result = self._evaluate_stage_rule(
                        parsed_rule=rule_info["parsed"],
                        response=response,
                        conversation=conversation_history
                    )
                    rule_results.append(result)
            
            evaluations[str(turn_id)] = {
                "turn_id": turn_id,
                "response": response,
                "rules": rule_results
            }

        # 处理FIRST_N规则的"至少触发一次"逻辑
        evaluations = self._process_first_n_rules(
            evaluations,
            stage_turn_rules,
            conversation_by_turn
        )

        return evaluations

    def _evaluate_single_rule(
        self,
        parsed_rule: ParsedRule,
        response: str,
        conversation: List[Message]
    ) -> Dict[str, Any]:
        """评估单轮规则"""
        # 根据规则类型选择评估方式
        if parsed_rule.type == "single_turn":
            triggered, reason = self.single_rule_registry.evaluate_rule(
                rule_name=parsed_rule.rule_name,
                response=response,
                llm_judge=self._get_llm_judge_func()
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
            "rule_tag": parsed_rule.full_name,
            "triggered": triggered,
            "score": parsed_rule.score if triggered else 0,
            "kwargs": kwargs,
            "reason": reason
        }

    def _evaluate_stage_rule(
        self,
        parsed_rule: ParsedRule,
        response: str,
        conversation: List[Message]
    ) -> Dict[str, Any]:
        """评估阶段规则"""
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
            "rule_tag": parsed_rule.full_name,
            "triggered": triggered,
            "score": parsed_rule.score if triggered else 0,
            "kwargs": kwargs,
            "reason": reason
        }

    def _process_first_n_rules(
        self,
        evaluations: Dict[str, Any],
        stage_turn_rules: List[Dict],
        conversation_by_turn: Dict[int, Dict]
    ) -> Dict[str, Any]:
        """
        处理FIRST_N规则的"至少触发一次"逻辑
        
        对于FIRST_N规则，如果在前N轮中至少有一轮触发了规则，
        则保留所有轮的评估结果；如果都没有触发，则标记为失败。
        """
        for rule_info in stage_turn_rules:
            if rule_info["parsed"].rule_class != "FIRST_N":
                continue
            
            N = rule_info["parsed"].N
            rule_tag = rule_info["parsed"].full_name
            
            # 检查前N轮中是否有至少一次触发
            has_triggered = False
            triggered_turn = None
            
            for turn_id in range(N):
                if str(turn_id) not in evaluations:
                    continue
                
                turn_eval = evaluations[str(turn_id)]
                for rule_result in turn_eval["rules"]:
                    if rule_result["rule_tag"] == rule_tag and rule_result["triggered"]:
                        has_triggered = True
                        triggered_turn = turn_id
                        break
                
                if has_triggered:
                    break
            
            # 如果前N轮都没有触发，需要在最后一轮添加失败记录
            if not has_triggered and N > 0:
                last_turn_id = N - 1
                if str(last_turn_id) in evaluations:
                    evaluations[str(last_turn_id)]["rules"].append({
                        "rule_tag": rule_tag,
                        "passed": False,
                        "score": rule_info["parsed"].score,
                        "kwargs": {},
                        "reason": f"FIRST_N规则：在前{N}轮中未触发"
                    })

        return evaluations

    def _get_llm_judge_func(self):
        """获取LLM judge函数"""
        if self.judge_model:
            return lambda response, rule_desc, context=None: (
                self.judge_model.evaluate_with_judge(response, rule_desc, context)
            )
        return None

    def _generate_summary(self, evaluations: Dict[str, Any]) -> Dict[str, Any]:
        """生成汇总信息"""
        total_score = 0
        total_turns = len(evaluations)
        
        for turn_id, turn_eval in evaluations.items():
            for rule_result in turn_eval["rules"]:
                total_score += rule_result["score"]
        
        return {
            "total_score": total_score,
            "total_turns": total_turns
        }

    def _load_json(self, json_path: str) -> Dict[str, Any]:
        """加载JSON文件"""
        with open(json_path, 'r', encoding='utf-8') as f:
            return json.load(f)

    def _save_json(self, data: Dict[str, Any], json_path: str):
        """保存JSON文件"""
        Path(json_path).parent.mkdir(parents=True, exist_ok=True)
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
