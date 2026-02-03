"""
Conversation Module
Manages conversation state and context
"""
from typing import List, Optional
from IBench.utils.common import Message

class Conversation:
    """Conversation manager"""
    
    def __init__(self, conversation_id: str):
        """
        Initialize conversation
        
        Args:
            conversation_id: Unique identifier for this conversation
        """
        self.conversation_id = conversation_id
        self.messages: List[Message] = []
        self.metadata: dict = {}
    
    def add_message(self, message: Message):
        """Add a message to the conversation"""
        self.messages.append(message)
    
    def get_messages(self) -> List[Message]:
        """Get all messages"""
        return self.messages
    
    def get_last_n_messages(self, n: int) -> List[Message]:
        """Get last n messages"""
        return self.messages[-n:] if n > 0 else []
    
    def get_messages_by_role(self, role: str) -> List[Message]:
        """Get all messages from a specific role"""
        return [msg for msg in self.messages if msg.role == role]
    
    def get_current_turn_id(self) -> int:
        """Get the current turn ID"""
        return len([msg for msg in self.messages if msg.role == "assistant"]) + 1
    
    def get_full_context(self) -> str:
        """Get full conversation context as string"""
        context_parts = []
        for msg in self.messages:
            if msg.role == "user":
                context_parts.append(f"用户: {msg.content}")
            else:
                context_parts.append(f"助手: {msg.content}")
        return "\n".join(context_parts)
    
    def clear(self):
        """Clear all messages"""
        self.messages = []
        self.metadata = {}
    
    def to_dict(self) -> dict:
        """Convert to dictionary"""
        return {
            "conversation_id": self.conversation_id,
            "messages": [msg.to_dict() for msg in self.messages],
            "metadata": self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "Conversation":
        """Create from dictionary"""
        conv = cls(data["conversation_id"])
        conv.messages = [Message.from_dict(msg) for msg in data["messages"]]
        conv.metadata = data.get("metadata", {})
        return conv
