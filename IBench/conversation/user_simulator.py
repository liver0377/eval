"""
User Simulator Module
Simulates user behavior using API-based model
"""
from typing import Optional, List
from IBench.utils.common import Message
from IBench.models.api_model import APIModel
from IBench.config import ModelConfig

class UserSimulator:
    """User simulator using API model"""
    
    def __init__(self, config: ModelConfig):
        """
        Initialize user simulator
        
        Args:
            config: Model configuration
        """
        self.api_model = APIModel(config, model_name=config.user_model_name)
        self.config = config
        
        # User persona and behavior settings
        self.user_persona = """你是一个寻求医疗咨询的用户。你的角色是:
1. 描述自己的症状或健康问题
2. 可能会对医生/助手的建议提出疑问
3. 可能会拒绝某些检查或治疗建议
4. 表现得像真实的患者一样，有时会犹豫或不清楚自己的情况

请根据之前的对话历史，自然地回复。"""
    
    def generate_user_message(
        self,
        conversation_history: List[Message],
        initial_prompt: Optional[str] = None
    ) -> Message:
        """
        Generate user message
        
        Args:
            conversation_history: Previous conversation history
            initial_prompt: Optional initial prompt for first turn
            
        Returns:
            Generated user message
        """
        if initial_prompt and not conversation_history:
            # First turn - use initial prompt
            return Message(
                role="user",
                content=initial_prompt,
                turn_id=1
            )
        
        # Format messages for API
        messages = [
            Message(role="system", content=self.user_persona, turn_id=0)
        ] + conversation_history
        
        try:
            response = self.api_model.generate(messages)
            
            turn_id = len(conversation_history) + 1 if conversation_history else 1
            
            return Message(
                role="user",
                content=response,
                turn_id=turn_id
            )
        except Exception as e:
            print(f"Error generating user message: {e}")
            raise
    
    def simulate_conversation(
        self,
        initial_prompt: str,
        max_turns: int = 10,
        assistant_model = None
    ) -> List[Message]:
        """
        Simulate a full conversation between user and assistant
        
        Args:
            initial_prompt: Initial user prompt
            max_turns: Maximum number of turns
            assistant_model: Assistant model to generate responses
            
        Returns:
            Complete conversation history
        """
        conversation = []
        
        # First user message
        user_msg = self.generate_user_message([], initial_prompt)
        conversation.append(user_msg)
        
        for turn in range(1, max_turns + 1):
            # Generate assistant response
            if assistant_model:
                assistant_response = assistant_model.generate(conversation)
                conversation.append(
                    Message(
                        role="assistant",
                        content=assistant_response,
                        turn_id=turn
                    )
                )
            
            # Generate next user message
            user_msg = self.generate_user_message(conversation)
            conversation.append(user_msg)
        
        return conversation
