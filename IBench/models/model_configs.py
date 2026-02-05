"""
Model Configurations
Predefined configurations for different models on the server
"""
import os
from typing import Dict, Any, Optional, Union
from dataclasses import dataclass, field

@dataclass
class ModelConfig:
    """Configuration for a specific model"""
    name: str
    path: str
    load_in_4bit: bool = True
    load_in_8bit: bool = False
    device_map: str = "auto"
    max_new_tokens: int = 512
    temperature: float = 0.0
    description: str = ""
    
    # API Configuration for Qwen (Dashscope)
    api_key: Optional[str] = None
    api_base: str = "https://dashscope.aliyuncs.com/compatible-mode/v1"
    user_model_name: str = "qwen-plus"
    judge_model_name: str = "qwen-max"
    
    # Additional generation parameters
    top_p: float = 0.9
    repetition_penalty: float = 1.0
    system_prompt: Optional[str] = None

# Predefined model configurations
MODEL_REGISTRY: Dict[str, ModelConfig] = {
    "Qwen3-8B": ModelConfig(
        name="Qwen3-8B",
        path="/data/wudy/projects/models/Qwen3-8B",
        load_in_4bit=True,
        load_in_8bit=False,
        device_map="auto",
        description="Base Qwen3-8B model (8B parameters)"
    ),
    
    "qwen3_full_sft": ModelConfig(
        name="qwen3_full_sft",
        path="/data/wudy/projects/models/qwen3_full_sft",
        load_in_4bit=True,
        load_in_8bit=False,
        device_map="auto",
        description="Qwen3-8B fine-tuned with SFT"
    ),
    
    "llama_factory_psy1.32.1_lora_qwen2_7b_dpo": ModelConfig(
        name="llama_factory_psy1.32.1_lora_qwen2_7b_dpo",
        path="/data/wudy/projects/models/llama_factory_psy1.32.1_lora_qwen2_7b_dpo",
        load_in_4bit=True,
        load_in_8bit=False,
        device_map="auto",
        description="Qwen2-7B with LoRA and DPO training"
    )
}

def get_model_config(model_name: str) -> ModelConfig:
    """
    Get model configuration by name
    
    Args:
        model_name: Name of the model (must be in MODEL_REGISTRY)
        
    Returns:
        ModelConfig object
        
    Raises:
        ValueError: If model_name is not found
    """
    if model_name not in MODEL_REGISTRY:
        available = ", ".join(MODEL_REGISTRY.keys())
        raise ValueError(
            f"Model '{model_name}' not found. "
            f"Available models: {available}"
        )
    
    return MODEL_REGISTRY[model_name]

def list_available_models() -> Dict[str, str]:
    """
    List all available models with their descriptions
    
    Returns:
        Dictionary mapping model names to descriptions
    """
    return {
        name: config.description 
        for name, config in MODEL_REGISTRY.items()
    }

def register_model(config: ModelConfig):
    """
    Register a new model configuration
    
    Args:
        config: ModelConfig object
    """
    MODEL_REGISTRY[config.name] = config

def update_model_path(model_name: str, new_path: str):
    """
    Update the path for an existing model
    
    Args:
        model_name: Name of the model
        new_path: New path to the model
    """
    if model_name not in MODEL_REGISTRY:
        raise ValueError(f"Model '{model_name}' not found in registry")
    
    MODEL_REGISTRY[model_name].path = new_path

# Convenience function for common server paths
def setup_server_models(base_path: str = "/data/wudy/projects/models"):
    """
    Setup model configurations for server environment
    
    Args:
        base_path: Base path to models directory
    """
    # Update paths if base_path is different
    if base_path != "/data/wudy/projects/models":
        for config in MODEL_REGISTRY.values():
            config.path = config.path.replace(
                "/data/wudy/projects/models",
                base_path
            )


# ============================================================================
# Configuration Classes (migrated from config.py)
# ============================================================================

@dataclass
class EvaluationConfig:
    """Evaluation-related configuration"""
    output_dir: str = "./data/output"
    batch_size: int = 8
    max_conversation_turns: int = 20
    enable_cache: bool = True


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
    """Main configuration class using model_configs.py"""
    
    def __init__(self, model_name: str = "Qwen3-8B"):
        """
        Initialize configuration
        
        Args:
            model_name: Name of the model to use (must be in MODEL_REGISTRY)
        """
        # Get model configuration from registry
        self.model = get_model_config(model_name)
        
        # Evaluation configuration
        self.evaluation = EvaluationConfig()
        
        # LLM Judge configuration
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
        
        if not os.path.exists(self.model.path):
            print(f"Warning: Local model path {self.model.path} does not exist.")
            return False
        
        os.makedirs(self.evaluation.output_dir, exist_ok=True)
        return True


# Global configuration instance
config = Config()
