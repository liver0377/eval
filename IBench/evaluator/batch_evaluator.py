"""
Batch Evaluator Module
Handles batch evaluation of multiple conversations
"""
import json
import os
from typing import List, Dict
from IBench.evaluator.rule_evaluator import RuleEvaluator
from IBench.utils.common import (
    EvaluationResult, EvaluationMode, TurnEvaluation, Message
)
from IBench.config import EvaluationConfig

class BatchEvaluator:
    """Batch evaluator for multiple conversations"""
    
    def __init__(
        self,
        config: EvaluationConfig,
        llm_judge = None
    ):
        """
        Initialize batch evaluator
        
        Args:
            config: Evaluation configuration
            llm_judge: LLM judge model
        """
        self.config = config
        self.rule_evaluator = RuleEvaluator(config, llm_judge)
    
    def evaluate_conversation(
        self,
        conversation_id: str,
        mode: EvaluationMode,
        conversation_history: List[Message],
        responses: List[str]
    ) -> EvaluationResult:
        """
        Evaluate a complete conversation
        
        Args:
            conversation_id: Unique conversation identifier
            mode: Evaluation mode
            conversation_history: Full conversation history
            responses: List of assistant responses to evaluate
            
        Returns:
            Complete evaluation result
        """
        result = EvaluationResult(
            conversation_id=conversation_id,
            mode=mode,
            metadata={}
        )
        
        # Evaluate each turn
        for i, response in enumerate(responses):
            turn_id = i + 1
            turn_conversation = conversation_history[:2*i + 1]  # History up to this turn
            
            turn_eval = self.rule_evaluator.evaluate_turn(
                turn_id=turn_id,
                response=response,
                conversation=turn_conversation
            )
            
            result.turn_evaluations.append(turn_eval)
        
        return result
    
    def evaluate_batch(
        self,
        conversations: List[Dict],
        mode: EvaluationMode
    ) -> List[EvaluationResult]:
        """
        Evaluate a batch of conversations
        
        Args:
            conversations: List of conversation dictionaries
                Each dict should have: conversation_id, messages, responses
            mode: Evaluation mode
            
        Returns:
            List of evaluation results
        """
        results = []
        
        for conv_data in conversations:
            result = self.evaluate_conversation(
                conversation_id=conv_data["conversation_id"],
                mode=mode,
                conversation_history=conv_data["messages"],
                responses=conv_data["responses"]
            )
            results.append(result)
        
        return results
    
    def save_results(
        self,
        results: List[EvaluationResult],
        output_file: str
    ):
        """
        Save evaluation results to file
        
        Args:
            results: List of evaluation results
            output_file: Output file path
        """
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        
        data = [result.to_dict() for result in results]
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        print(f"Results saved to {output_file}")
    
    def load_results(
        self,
        input_file: str
    ) -> List[EvaluationResult]:
        """
        Load evaluation results from file
        
        Args:
            input_file: Input file path
            
        Returns:
            List of evaluation results
        """
        with open(input_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        results = []
        for item in data:
            mode_str = item["mode"]
            mode = EvaluationMode.CONTEXT if mode_str == "context" else EvaluationMode.INTERACTIVE
            
            result = EvaluationResult(
                conversation_id=item["conversation_id"],
                mode=mode,
                metadata=item.get("metadata", {})
            )
            
            for turn_data in item["turn_evaluations"]:
                turn_eval = TurnEvaluation(
                    turn_id=turn_data["turn_id"],
                    response=turn_data["response"]
                )
                
                for rule_data in turn_data["single_rules"]:
                    rule_type_str = rule_data["rule_type"]
                    rule_type = RuleType.LLM if rule_type_str == "LLM" else RuleType.RULE
                    
                    turn_eval.single_rules.append(
                        RuleResult(
                            rule_id=rule_data["rule_id"],
                            rule_type=rule_type,
                            rule_description=rule_data["rule_description"],
                            triggered=rule_data["triggered"],
                            score=rule_data["score"],
                            reason=rule_data["reason"],
                            turn_id=rule_data["turn_id"]
                        )
                    )
                
                for rule_data in turn_data["stage_rules"]:
                    rule_type_str = rule_data["rule_type"]
                    rule_type = RuleType.LLM if rule_type_str == "LLM" else RuleType.RULE
                    
                    turn_eval.stage_rules.append(
                        RuleResult(
                            rule_id=rule_data["rule_id"],
                            rule_type=rule_type,
                            rule_description=rule_data["rule_description"],
                            triggered=rule_data["triggered"],
                            score=rule_data["score"],
                            reason=rule_data["reason"],
                            turn_id=rule_data["turn_id"]
                        )
                    )
                
                result.turn_evaluations.append(turn_eval)
            
            results.append(result)
        
        return results
    
    def generate_report(
        self,
        results: List[EvaluationResult]
    ) -> Dict:
        """
        Generate summary report from results
        
        Args:
            results: List of evaluation results
            
        Returns:
            Summary report dictionary
        """
        total_conversations = len(results)
        total_turns = sum(r.total_turns for r in results)
        
        total_score = sum(r.final_score for r in results)
        avg_score = total_score / total_conversations if total_conversations > 0 else 0
        
        report = {
            "total_conversations": total_conversations,
            "total_turns": total_turns,
            "total_score": total_score,
            "average_score": avg_score,
            "conversation_details": []
        }
        
        for result in results:
            report["conversation_details"].append({
                "conversation_id": result.conversation_id,
                "mode": result.mode.value,
                "total_turns": result.total_turns,
                "final_score": result.final_score
            })
        
        return report
