"""
IBench Configuration Module
Manages all configuration settings for the evaluation framework
"""
import os
from dataclasses import dataclass
from typing import Optional, Union

@dataclass
class ModelConfig:
    """Model-related configuration"""
    local_model_path: str = "./models/qwen3-8b"
    local_model_name: str = "qwen3-8b"
    
    # Quantization options
    load_in_4bit: bool = True
    load_in_8bit: bool = False
    device_map: Union[str, dict] = "auto"
    
    # API Configuration for Qwen (Dashscope)
    api_key: Optional[str] = None
    api_base: str = "https://dashscope.aliyuncs.com/compatible-mode/v1"
    user_model_name: str = "qwen-plus"
    judge_model_name: str = "qwen-max"
    
    # Generation parameters
    system_prompt: Optional[str] = None
    temperature: float = 0.0
    max_new_tokens: int = 40
    top_p: float = 0.9
    repetition_penalty: float = 1.0
    
    def validate_dependencies(self) -> tuple[bool, list[str]]:
        """
        Validate that required dependencies are installed
        
        Returns:
            Tuple of (all_valid, missing_dependencies)
        """
        missing = []
        
        if self.load_in_4bit or self.load_in_8bit:
            try:
                import bitsandbytes
            except ImportError:
                missing.append('bitsandbytes')
        
        try:
            import torch
        except ImportError:
            missing.append('torch')
        
        try:
            import transformers
        except ImportError:
            missing.append('transformers')
        
        if self.api_key:
            try:
                import openai
            except ImportError:
                missing.append('openai')
        
        return len(missing) == 0, missing

@dataclass
class EvaluationConfig:
    """Evaluation-related configuration"""
    output_dir: str = "./data/output"
    batch_size: int = 8
    max_conversation_turns: int = 20
    enable_cache: bool = True
    
    # Rule mappings
    single_rule_turns: Optional[dict] = None
    stage_rule_turns: Optional[dict] = None
    
    def __post_init__(self):
        if self.single_rule_turns is None:
            self.single_rule_turns = {
                1: [1, 2, 3, 4, 5, 6],
                2: [1, 2, 3, 4, 5, 6],
                3: [1, 2, 3, 4, 5, 6]
            }
        
        if self.stage_rule_turns is None:
            self.stage_rule_turns = {
                1: [1],
                3: [2, 3],
                4: [4],
                8: [5, 6, 7],
                10: [5, 6, 7],
                12: [5, 6, 7]
            }

@dataclass
class LLMJudgeConfig:
    """LLM Judge configuration for rule evaluation"""
    system_prompt: str = """你是一个客观公正的评估者。请根据给定的规则评估模型的回复。

请仔细阅读回复内容，并判断是否违反了规则。
- 如果违反了规则，返回 "VIOLATED"
- 如果没有违反规则，返回 "NOT_VIOLATED"
- 只返回上述两个选项之一，不要返回其他内容。"""
    
    max_retries: int = 3
    timeout: int = 30

class Config:
    """Main configuration class"""
    def __init__(self):
        self.model = ModelConfig()
        self.evaluation = EvaluationConfig()
        self.llm_judge = LLMJudgeConfig()
        
        # Load from environment variables if available
        self._load_from_env()
    
    def _load_from_env(self):
        """Load configuration from environment variables"""
        if api_key := os.getenv("DASHSCOPE_API_KEY"):
            self.model.api_key = api_key
        
        if api_base := os.getenv("DASHSCOPE_API_BASE"):
            self.model.api_base = api_base
        
        if output_dir := os.getenv("IBENCH_OUTPUT_DIR"):
            self.evaluation.output_dir = output_dir
    
    def validate(self) -> bool:
        """Validate configuration"""
        if not self.model.api_key:
            print("Warning: DASHSCOPE_API_KEY not set. Please set it or pass api_key parameter.")
            return False
        
        if not os.path.exists(self.model.local_model_path):
            print(f"Warning: Local model path {self.model.local_model_path} does not exist.")
            return False
        
        os.makedirs(self.evaluation.output_dir, exist_ok=True)
        return True

# Global configuration instance
config = Config()
