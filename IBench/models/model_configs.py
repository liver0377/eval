"""
Model Configurations
Predefined configurations for different models on the server
"""
from typing import Dict, Any, Optional
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
