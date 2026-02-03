"""
Generate Conversations Script
Generate interactive conversations using UserSimulator and save to ShareGPT format
"""
import os
import sys
import json
from typing import List, Dict
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from IBench.models.local_model import LocalModel
from IBench.models.model_configs import get_model_config
from IBench.conversation.user_simulator import UserSimulator
from IBench.utils.common import Message
from IBench.config import ModelConfig as IBenchModelConfig

def load_model(model_name: str):
    """
    Load local model and user simulator
    
    Args:
        model_name: Name of the model to load
        
    Returns:
        Tuple of (local_model, user_simulator, model_config)
    """
    model_config = get_model_config(model_name)
    
    ibench_config = IBenchModelConfig(
        local_model_path=model_config.path,
        load_in_4bit=model_config.load_in_4bit,
        load_in_8bit=model_config.load_in_8bit,
        device_map=model_config.device_map,
        max_new_tokens=model_config.max_new_tokens,
        temperature=model_config.temperature
    )
    
    print(f"\n{'='*60}")
    print(f"Loading model: {model_name}")
    print(f"{'='*60}")
    
    local_model = LocalModel(ibench_config)
    user_simulator = UserSimulator(ibench_config)
    
    print(f"✓ Model loaded: {model_name}")
    print(f"  4-bit quantization: {model_config.load_in_4bit}")
    print(f"  User simulator: qwen-plus")
    
    return local_model, user_simulator, model_config

def generate_conversation(
    local_model,
    user_simulator,
    initial_prompt: str,
    max_turns: int,
    conversation_id: str
) -> List[Dict]:
    """
    Generate a single interactive conversation
    
    Args:
        local_model: Loaded local model
        user_simulator: User simulator instance
        initial_prompt: Initial user prompt
        max_turns: Number of turns to generate
        conversation_id: Unique conversation ID
        
    Returns:
        List of messages in ShareGPT format
    """
    conversation = []
    conversation_history = []
    
    print(f"\nGenerating conversation: {conversation_id}")
    print(f"Initial prompt: {initial_prompt[:50]}...")
    
    # First user message
    user_msg = Message(role="user", content=initial_prompt, turn_id=1)
    conversation.append({
        "from": "human",
        "value": initial_prompt
    })
    conversation_history.append(user_msg)
    
    # Interactive loop
    for turn in range(1, max_turns + 1):
        print(f"  Turn {turn}...")
        
        # Generate assistant response
        assistant_response = local_model.generate(conversation_history)
        
        conversation.append({
            "from": "gpt",
            "value": assistant_response
        })
        
        assistant_msg = Message(
            role="assistant",
            content=assistant_response,
            turn_id=turn
        )
        conversation_history.append(assistant_msg)
        
        # Generate next user message (except after last turn)
        if turn < max_turns:
            user_msg = user_simulator.generate_user_message(conversation_history)
            print(f"    User: {user_msg.content[:50]}...")
            
            conversation.append({
                "from": "human",
                "value": user_msg.content
            })
            
            conversation_history.append(user_msg)
    
    print(f"✓ Generated {max_turns + 1} messages")
    return conversation

def generate_all_conversations(
    model_names: List[str],
    prompts: List[str],
    max_turns: int,
    output_dir: str
) -> Dict:
    """
    Generate all conversations for all models and prompts
    
    Args:
        model_names: List of model names
        prompts: List of initial prompts
        max_turns: Maximum turns per conversation
        output_dir: Output directory for conversations
        
    Returns:
        Summary dictionary
    """
    timestamp = datetime.now().isoformat()
    summary = {
        "timestamp": timestamp,
        "models": model_names,
        "prompts": prompts,
        "max_turns": max_turns,
        "conversations": {},
        "total_conversations": 0
    }
    
    os.makedirs(output_dir, exist_ok=True)
    
    # Process each model
    for model_name in model_names:
        print(f"\n\n{'#'*60}")
        print(f"# Processing Model: {model_name}")
        print(f"{'#'*60}")
        
        try:
            # Load model
            local_model, user_simulator, model_config = load_model(model_name)
            
            model_conversations = []
            model_dir = os.path.join(output_dir, model_name)
            os.makedirs(model_dir, exist_ok=True)
            
            # Generate conversation for each prompt
            for i, prompt in enumerate(prompts):
                print(f"\n[{i+1}/{len(prompts)}] Prompt: {prompt[:50]}...")
                
                conversation_id = f"{model_name}_{i+1}_{hash(prompt) % 10000:04d}"
                
                # Generate conversation
                conversation = generate_conversation(
                    local_model=local_model,
                    user_simulator=user_simulator,
                    initial_prompt=prompt,
                    max_turns=max_turns,
                    conversation_id=conversation_id
                )
                
                # Save conversation to file
                output_file = os.path.join(model_dir, f"conv_{i+1}.json")
                with open(output_file, 'w', encoding='utf-8') as f:
                    json.dump(conversation, f, ensure_ascii=False, indent=2)
                
                print(f"  Saved: {output_file}")
                
                # Add to summary
                model_conversations.append({
                    "conversation_id": conversation_id,
                    "prompt": prompt,
                    "output_file": output_file,
                    "num_messages": len(conversation)
                })
                summary["total_conversations"] += 1
            
            summary["conversations"][model_name] = model_conversations
            
        except Exception as e:
            print(f"\n✗ Error processing model {model_name}: {e}")
            import traceback
            traceback.print_exc()
            summary["conversations"][model_name] = {"error": str(e)}
    
    # Save summary
    summary_file = os.path.join(output_dir, "generation_summary.json")
    with open(summary_file, 'w', encoding='utf-8') as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)
    
    print(f"\n\n{'='*60}")
    print(f"Generation Summary")
    print(f"{'='*60}")
    print(f"Total conversations: {summary['total_conversations']}")
    print(f"Output directory: {output_dir}")
    print(f"Summary file: {summary_file}")
    print(f"{'='*60}\n")
    
    return summary

def main():
    """Main function for command-line usage"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Generate conversations in ShareGPT format")
    parser.add_argument(
        "--models",
        nargs="+",
        default=["Qwen3-8B", "qwen3_full_sft"],
        help="Models to generate conversations for"
    )
    parser.add_argument(
        "--prompts",
        nargs="+",
        default=[
            "我最近总是失眠，晚上睡不着",
            "我头疼，持续三天了",
            "我最近胸闷，特别是晚上"
        ],
        help="Initial prompts for conversations"
    )
    parser.add_argument(
        "--max-turns",
        type=int,
        default=3,
        help="Maximum turns per conversation"
    )
    parser.add_argument(
        "--output-dir",
        default="./IBench/data/conversations",
        help="Output directory for conversations"
    )
    
    args = parser.parse_args()
    
    # Generate conversations
    summary = generate_all_conversations(
        model_names=args.models,
        prompts=args.prompts,
        max_turns=args.max_turns,
        output_dir=args.output_dir
    )
    
    print("\n✓ All conversations generated successfully!")
    print("\nNext steps:")
    print("1. Review generated conversations")
    print("2. Run evaluation:")
    print(f"   python IBench/scripts/evaluate_conversations.py --input {args.output_dir}")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
