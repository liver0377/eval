"""
Local Model Loader
Loads and manages local model inference using HuggingFace Transformers
Supports safetensors format, quantization, and multi-GPU device mapping
"""
import os
import re
import torch
from typing import Optional, List, Dict, Any
from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig
from IBench.utils.common import Message
from IBench.models.model_configs import ModelConfig

class LocalModel:
    """Local model wrapper using HuggingFace Transformers with optimizations"""
    
    def __init__(self, config: ModelConfig):
        """
        Initialize local model
        
        Args:
            config: Model configuration
        """
        self.config = config
        self.system_prompt = config.system_prompt
        self.model = None
        self.tokenizer = None
        self.device = self._get_device()
        
        print(f"Loading local model from {config.path}...")
        self._load_model()
    
    def _get_device(self) -> str:
        """Get the best available device"""
        if torch.cuda.is_available():
            device_count = torch.cuda.device_count()
            print(f"Found {device_count} CUDA device(s)")
            for i in range(device_count):
                props = torch.cuda.get_device_properties(i)
                print(f"  GPU {i}: {props.name} ({props.total_memory / 1024**3:.1f}GB)")
            return "cuda"
        elif hasattr(torch.backends, 'mps') and torch.backends.mps.is_available():
            return "mps"
        else:
            return "cpu"
    
    def _get_quantization_config(self) -> Optional[BitsAndBytesConfig]:
        """
        Get quantization configuration based on config settings
        
        Returns:
            BitsAndBytesConfig if quantization is enabled, None otherwise
        """
        if self.config.load_in_4bit:
            print("Using 4-bit quantization (NF4)")
            return BitsAndBytesConfig(
                load_in_4bit=True,
                bnb_4bit_compute_dtype=torch.float16,
                bnb_4bit_use_double_quant=True,
                bnb_4bit_quant_type="nf4"
            )
        elif self.config.load_in_8bit:
            print("Using 8-bit quantization")
            return BitsAndBytesConfig(
                load_in_8bit=True,
                llm_int8_threshold=6.0
            )
        return None
    
    def _get_torch_dtype(self) -> torch.dtype:
        """
        Get appropriate torch dtype based on device and quantization
        
        Returns:
            torch dtype
        """
        if self.config.load_in_4bit or self.config.load_in_8bit:
            return torch.float32  # Quantization handles this
        
        if self.device == "cuda":
            return torch.float16
        elif self.device == "mps":
            return torch.float16
        else:
            return torch.float32
    
    def _load_model(self):
        """Load model and tokenizer with optimizations"""
        try:
            # Load tokenizer with Qwen3 compatibility
            print("Loading tokenizer...")
            self.tokenizer = AutoTokenizer.from_pretrained(
                self.config.path,
                trust_remote_code=True,
                use_fast=False,
                padding_side="left"
            )
            
            # Set pad token if not present
            if self.tokenizer.pad_token is None:
                self.tokenizer.pad_token = self.tokenizer.eos_token
                print("Set pad_token to eos_token")
            
            # Prepare model loading arguments
            model_kwargs = {
                "trust_remote_code": True,
                "low_cpu_mem_usage": True,
            }
            
            # Add quantization config if enabled
            quantization_config = self._get_quantization_config()
            if quantization_config:
                model_kwargs["quantization_config"] = quantization_config
                model_kwargs["device_map"] = self.config.device_map or "auto"
            else:
                # No quantization - use standard dtype and device mapping
                model_kwargs["torch_dtype"] = self._get_torch_dtype()
                model_kwargs["device_map"] = self.config.device_map or "auto"
            
            # Load model
            print(f"Loading model from {self.config.path}...")
            print(f"  Device map: {model_kwargs.get('device_map', 'default')}")
            print(f"  Low CPU memory usage: {model_kwargs['low_cpu_mem_usage']}")
            
            self.model = AutoModelForCausalLM.from_pretrained(
                self.config.path,
                **model_kwargs
            )
            
            # Print model info
            print(f"Model loaded successfully!")
            if hasattr(self.model, 'get_memory_footprint'):
                memory_mb = self.model.get_memory_footprint() / 1024**2
                print(f"Model memory footprint: {memory_mb:.1f} MB")
            
        except Exception as e:
            print(f"Error loading model: {e}")
            print("\nTroubleshooting tips:")
            print("1. Check if model path is correct")
            print("2. Ensure you have enough GPU memory")
            print("3. Try enabling quantization (load_in_4bit=True)")
            print("4. Install bitsandbytes: pip install bitsandbytes")
            raise
    
    @staticmethod
    def _clean_response(response: str) -> str:
        """
        清理模型输出，去除思考内容
        删除 <|file_separator|> 及其后的所有内容（直到\n\n）
        """
        pattern = r'<\|file_separator\|>.*?(?=\n\n|$)'
        cleaned = re.sub(pattern, '', response, flags=re.DOTALL)
        return cleaned.strip()
    
    def _format_messages(self, messages: List[Message]) -> str:
        """
        Format messages to prompt string
        Supports Qwen chat template and system prompt
        
        Args:
            messages: List of message objects
            
        Returns:
            Formatted prompt string
        """
        formatted_messages = []
        
        if self.system_prompt:
            formatted_messages.append({
                "role": "system",
                "content": self.system_prompt
            })
        
        for msg in messages:
            formatted_messages.append({
                "role": msg.role,
                "content": msg.content
            })
        
        if hasattr(self.tokenizer, 'apply_chat_template'):
            try:
                formatted = self.tokenizer.apply_chat_template(
                    formatted_messages,
                    tokenize=False,
                    add_generation_prompt=True
                )
                return formatted
            except:
                pass
        
        prompt = ""
        for msg in formatted_messages:
            if msg["role"] == "system":
                prompt += f"System: {msg['content']}\n"
            elif msg["role"] == "user":
                prompt += f"用户: {msg['content']}\n"
            elif msg["role"] == "assistant":
                prompt += f"助手: {msg['content']}\n"
        prompt += "助手:"
        return prompt
    
    def generate(self, messages: List[Message]) -> str:
        """
        Generate response from model
        
        Args:
            messages: Conversation history
            
        Returns:
            Generated response text
        """
        if self.model is None or self.tokenizer is None:
            raise RuntimeError("Model not loaded")
        
        prompt = self._format_messages(messages)
        
        # Tokenize
        inputs = self.tokenizer(
            prompt,
            return_tensors="pt",
            truncation=True,
            max_length=4096,  # Support longer context
            padding=False
        )
        
        # Move inputs to correct device - smart device mapping (方案A)
        if self.config.load_in_4bit or self.config.load_in_8bit:
            # 对于量化模型（device_map="auto"），获取模型实际设备
            try:
                # 获取模型第一个参数的设备
                device = next(self.model.parameters()).device
                # 只移动 Tensor 类型的输入
                inputs = {k: v.to(device) if isinstance(v, torch.Tensor) else v 
                         for k, v in inputs.items()}
            except StopIteration:
                # 模型没有参数（极少见情况），保持默认
                pass
        elif self.device == "cuda":
            # 对于非量化模型，移到指定设备
            inputs = {k: v.to(self.device) for k, v in inputs.items()}
        
        # Generate
        with torch.no_grad():
            outputs = self.model.generate(
                **inputs,
                max_new_tokens=self.config.max_new_tokens,
                temperature=self.config.temperature,
                top_p=self.config.top_p,
                do_sample=self.config.temperature > 0,
                pad_token_id=self.tokenizer.pad_token_id or self.tokenizer.eos_token_id,
                eos_token_id=self.tokenizer.eos_token_id,
                repetition_penalty=1.0
            )
        
        # Decode only the generated part
        input_length = inputs['input_ids'].shape[1]
        generated_ids = outputs[0][input_length:]
        response = self.tokenizer.decode(generated_ids, skip_special_tokens=True)
        
        return self._clean_response(response)
    
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
    
    def check_precondition(
        self,
        conversation_context: str,
        precondition_description: str
    ) -> bool:
        """
        使用本地模型判断前置条件是否满足
        
        Args:
            conversation_context: 对话上下文（格式化后的字符串）
            precondition_description: 前置条件描述
            
        Returns:
            bool: 是否满足前置条件
        """
        if self.model is None or self.tokenizer is None:
            raise RuntimeError("Model not loaded")
        
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
            # 使用 Qwen 的 chat template
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ]
            
            # Format with chat template if available
            if hasattr(self.tokenizer, 'apply_chat_template'):
                prompt = self.tokenizer.apply_chat_template(
                    messages,
                    tokenize=False,
                    add_generation_prompt=True
                )
            else:
                prompt = f"System: {system_prompt}\nUser: {user_prompt}\nAssistant:"
            
            inputs = self.tokenizer(
                prompt,
                return_tensors="pt",
                truncation=True,
                max_length=4096,
                padding=False
            )
            
            # Move to device
            if self.config.load_in_4bit or self.config.load_in_8bit:
                device = next(self.model.parameters()).device
                inputs = {k: v.to(device) if isinstance(v, torch.Tensor) else v 
                         for k, v in inputs.items()}
            elif self.device == "cuda":
                inputs = {k: v.to(self.device) for k, v in inputs.items()}
            
            # Generate
            with torch.no_grad():
                outputs = self.model.generate(
                    **inputs,
                    max_new_tokens=10,
                    temperature=0.0,
                    do_sample=False,
                    pad_token_id=self.tokenizer.pad_token_id or self.tokenizer.eos_token_id,
                    eos_token_id=self.tokenizer.eos_token_id
                )
            
            # Decode result
            input_length = inputs['input_ids'].shape[1]
            generated_ids = outputs[0][input_length:]
            result = self._clean_response(
                self.tokenizer.decode(generated_ids, skip_special_tokens=True)
            )
            
            return "SATISFIED" in result
            
        except Exception as e:
            print(f"Error in precondition check: {e}")
            return False
