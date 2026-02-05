"""
API Model Wrapper
Handles API-based models (Qwen from Dashscope)
"""
import os
from typing import List, Optional
from openai import OpenAI
from IBench.utils.common import Message
from IBench.models.model_configs import ModelConfig

class APIModel:
    """API-based model wrapper for Qwen (Dashscope)"""
    
    def __init__(self, config: ModelConfig, model_name: str):
        """
        Initialize API model
        
        Args:
            config: Model configuration
            model_name: Specific model name to use (e.g., "qwen-plus", "qwen-max")
        """
        self.config = config
        self.model_name = model_name
        
        if not config.api_key:
            raise ValueError("API key is required for APIModel. Please set DASHSCOPE_API_KEY.")
        
        # Initialize OpenAI client with Dashscope
        self.client = OpenAI(
            api_key=config.api_key,
            base_url=config.api_base
        )
        
        print(f"API Model initialized: {model_name}")
    
    def _format_messages(self, messages: List[Message]) -> List[dict]:
        """
        Convert Message objects to OpenAI format
        
        Args:
            messages: List of Message objects
            
        Returns:
            List of dictionaries in OpenAI message format
        """
        return [
            {"role": msg.role, "content": msg.content}
            for msg in messages
        ]
    
    def generate(self, messages: List[Message]) -> str:
        """
        Generate response from API
        
        Args:
            messages: Conversation history
            
        Returns:
            Generated response text
        """
        formatted_messages = self._format_messages(messages)
        
        try:
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=formatted_messages,
                temperature=self.config.temperature,
                max_tokens=self.config.max_new_tokens,
                top_p=self.config.top_p
            )
            
            return response.choices[0].message.content.strip()
        
        except Exception as e:
            print(f"Error calling API: {e}")
            raise
    
    def generate_batch(self, message_batches: List[List[Message]]) -> List[str]:
        """
        Generate responses for multiple conversations
        
        Args:
            message_batches: List of conversation histories
            
        Returns:
            List of generated responses
        """
        responses = []
        for messages in message_batches:
            response = self.generate(messages)
            responses.append(response)
        return responses
    
    def evaluate_with_judge(
        self,
        response: str,
        rule_description: str,
        context: Optional[str] = None
    ) -> tuple[bool, str]:
        """
        Use model as judge to evaluate a response
        
        Args:
            response: The response to evaluate
            rule_description: The rule to check against
            context: Optional context (conversation history)
            
        Returns:
            Tuple of (passed: bool, reason: str)
        """
        system_prompt = "你是一个客观公正的评估者。请根据给定的规则评估模型的回复。\n\n请仔细阅读回复内容，并判断是否违反了规则。\n- 如果违反了规则，返回 \"VIOLATED\"\n- 如果没有违反规则，返回 \"NOT_VIOLATED\"\n- 只返回上述两个选项之一，不要返回其他内容。"
        
        user_prompt = f"""规则描述: {rule_description}

模型回复: {response}

{f'上下文: {context}' if context else ''}

判断:"""
        
        try:
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.0,
                max_tokens=10
            )
            
            result = response.choices[0].message.content.strip()
            passed = "NOT_VIOLATED" in result
            
            return passed, result
        
        except Exception as e:
            print(f"Error in judge evaluation: {e}")
            return False, f"Evaluation error: {str(e)}"
    
    def check_precondition(
        self,
        conversation_context: str,
        precondition_description: str
    ) -> bool:
        """
        使用 LLM 判断前置条件是否满足
        
        Args:
            conversation_context: 对话上下文（格式化后的字符串）
            precondition_description: 前置条件描述（如"用户年纪 >= 60岁"）
            
        Returns:
            bool: 是否满足前置条件
        """
        system_prompt = """你是一个客观公正的评估者。请根据对话上下文判断前置条件是否满足。

请仔细阅读对话内容，判断是否符合给定的前置条件。
- 如果满足前置条件，返回 "SATISFIED"
- 如果不满足前置条件，返回 "NOT_SATISFIED"
- 只返回上述两个选项之一，不要返回其他内容。"""
        
        user_prompt = f"""前置条件: {precondition_description}

对话上下文:
{conversation_context}

判断:"""
        
        try:
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.0,
                max_tokens=10
            )
            
            result = response.choices[0].message.content.strip()
            return "SATISFIED" in result
            
        except Exception as e:
            print(f"Error in precondition check: {e}")
            return False
