# Model Loading Guide for IBench

## Overview

This guide explains how to load and use models in IBench, specifically for the safetensors format models on your server.

## Server Model Configuration

Your server has the following models available:

```
/data/wudy/projects/models/
├── Qwen3-8B/                    # Base Qwen3-8B model
│   ├── model-00001-of-00005.safetensors
│   ├── model-00002-of-00005.safetensors
│   └── ... (5 shards total)
├── qwen3_full_sft/              # Fine-tuned Qwen3-8B
│   ├── model-00001-of-00004.safetensors
│   └── ... (4 shards total)
└── llama_factory_psy1.32.1_lora_qwen2_7b_dpo/  # LoRA + DPO model
    └── ...
```

## Quick Start

### 1. Using Predefined Model Configurations

```python
from IBench.models import get_model_config

# Get model configuration
model_config = get_model_config("Qwen3-8B")

# Use with evaluator
from IBench import ContextEvaluator

evaluator = ContextEvaluator(
    local_model_path=model_config.path,
    api_key="your-api-key"
)
```

### 2. Running Model Comparison

```bash
# On the server
cd /path/to/eval

# Install dependencies
pip install -r IBench/requirements.txt

# Run comparison
python IBench/scripts/compare_models.py \
    --models Qwen3-8B qwen3_full_sft \
    --prompts "我最近总是失眠" "我头疼" \
    --api-key $DASHSCOPE_API_KEY \
    --max-turns 3
```

## Model Loading Features

### 1. Safetensors Support

IBench automatically detects and loads safetensors format:

```python
# No special configuration needed
model = LocalModel(config)  # Automatically handles safetensors
```

### 2. Quantization (4-bit/8-bit)

Save GPU memory with quantization:

```python
from IBench.models import get_model_config
from IBench.config import ModelConfig

# Get config (4-bit enabled by default)
model_config = get_model_config("Qwen3-8B")

# Create IBench config
ibench_config = ModelConfig(
    local_model_path=model_config.path,
    load_in_4bit=True,  # Enable 4-bit quantization
    device_map="auto"   # Automatic device mapping
)
```

**Memory Savings:**
- Without quantization: ~16GB (Qwen3-8B in fp16)
- With 4-bit quantization: ~5GB
- With 8-bit quantization: ~8GB

### 3. Multi-GPU Support

Automatic device mapping across multiple GPUs:

```python
ibench_config = ModelConfig(
    local_model_path="/data/wudy/projects/models/Qwen3-8B",
    device_map="auto"  # Automatically distribute across GPUs
)
```

For specific device mapping:

```python
# Manual device mapping
device_map = {
    "transformer.embedding": "cuda:0",
    "transformer.encoder.layers.0": "cuda:0",
    "transformer.encoder.layers.1": "cuda:1",
    # ...
}

model = AutoModelForCausalLM.from_pretrained(
    path,
    device_map=device_map
)
```

## Configuration Options

### ModelConfig Parameters

```python
@dataclass
class ModelConfig:
    # Model path
    local_model_path: str = "/data/wudy/projects/models/Qwen3-8B"
    
    # Quantization
    load_in_4bit: bool = True    # 4-bit quantization (NF4)
    load_in_8bit: bool = False   # 8-bit quantization
    device_map: str = "auto"     # Device mapping strategy
    
    # Generation
    max_new_tokens: int = 512
    temperature: float = 0.0
    top_p: float = 0.9
```

### Choosing the Right Configuration

**For 8B model on single 24GB GPU:**
```python
config = ModelConfig(
    local_model_path="/data/wudy/projects/models/Qwen3-8B",
    load_in_4bit=True,    # Use 4-bit to fit in 24GB
    device_map="auto"
)
```

**For 8B model on 48GB GPU:**
```python
config = ModelConfig(
    local_model_path="/data/wudy/projects/models/Qwen3-8B",
    load_in_4bit=False,   # No quantization needed
    load_in_8bit=False,
    device_map="auto"
)
```

## Registering Custom Models

If you have additional models:

```python
from IBench.models.model_configs import register_model, ModelConfig

# Register new model
custom_config = ModelConfig(
    name="my_new_model",
    path="/path/to/new/model",
    load_in_4bit=True,
    description="My newly trained model"
)

register_model(custom_config)

# Use it
config = get_model_config("my_new_model")
```

## Troubleshooting

### Issue 1: Out of Memory

**Solution:** Enable quantization
```python
config = ModelConfig(
    load_in_4bit=True,  # or load_in_8bit=True
    device_map="auto"
)
```

### Issue 2: Model Loading Slow

**Solution:** The first load is slow (downloading/loading shards), subsequent loads are faster.

### Issue 3: CUDA Out of Memory with Multiple Models

**Solution:** Load models sequentially or use CPU offloading
```python
config = ModelConfig(
    device_map="auto",
    load_in_4bit=True
)

# After evaluation, free memory
import torch
del model
torch.cuda.empty_cache()
```

## Performance Tips

1. **Use 4-bit quantization** for most cases (minimal quality loss, huge memory savings)
2. **Set `num_return_sequences=1`** to avoid unnecessary generation
3. **Use `max_new_tokens`** appropriately (don't set too high)
4. **Batch evaluations** when possible (future feature)

## Server-Specific Notes

Your server paths are pre-configured in `IBench/models/model_configs.py`:

```python
MODEL_REGISTRY = {
    "Qwen3-8B": {
        "path": "/data/wudy/projects/models/Qwen3-8B",
        ...
    },
    "qwen3_full_sft": {
        "path": "/data/wudy/projects/models/qwen3_full_sft",
        ...
    }
}
```

Just use:
```python
from IBench.models import get_model_config

config = get_model_config("Qwen3-8B")  # Ready to use!
```

## Next Steps

1. Test model loading: `python IBench/test_model_loading.py`
2. Run comparison: `python IBench/scripts/compare_models.py`
3. Start evaluation: See `IBench/examples.py`
