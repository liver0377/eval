"""
System Prompt 使用示例
展示如何使用系统提示词约束模型输出
"""

from IBench.models.model_configs import ModelConfig
from IBench.models.local_model import LocalModel
from IBench.utils.common import Message

def example_with_system_prompt():
    """示例1：使用系统提示词约束输出格式"""
    
    # 配置系统提示词
    model_config = ModelConfig(
        local_model_path="./models/qwen3-8b",
        system_prompt="""你是一个专业的医疗咨询助手。请严格遵守以下要求：
1. 回复必须简洁明了，控制在40个字以内
2. 不要使用任何思考标记，如<|file_separator|>
3. 不要输出推理过程或分析步骤
4. 直接给出最终答案，不要添加额外说明""",
        max_new_tokens=40,
        temperature=0.0
    )
    
    # 初始化模型
    model = LocalModel(model_config)
    
    # 测试对话
    messages = [
        Message(role="user", content="我最近总是失眠", turn_id=1)
    ]
    
    # 生成回复
    response = model.generate(messages)
    print(f"模型回复: {response}")
    print(f"回复长度: {len(response)} 字符")


def example_without_system_prompt():
    """示例2：不使用系统提示词"""
    
    # 不配置系统提示词
    model_config = ModelConfig(
        local_model_path="./models/qwen3-8b",
        max_new_tokens=40,
        temperature=0.0
    )
    
    model = LocalModel(model_config)
    
    messages = [
        Message(role="user", content="我最近总是失眠", turn_id=1)
    ]
    
    response = model.generate(messages)
    print(f"模型回复: {response}")


def example_custom_constraints():
    """示例3：自定义约束条件"""
    
    # 自定义系统提示词
    custom_prompt = """你是一个客服助手。请遵循：
1. 只回答用户问题，不主动提供额外信息
2. 回复不超过20个字
3. 使用礼貌用语
4. 不要输出思考过程"""
    
    model_config = ModelConfig(
        local_model_path="./models/qwen3-8b",
        system_prompt=custom_prompt,
        max_new_tokens=40
    )
    
    model = LocalModel(model_config)
    
    messages = [
        Message(role="user", content="你们的营业时间是什么？", turn_id=1)
    ]
    
    response = model.generate(messages)
    print(f"客服回复: {response}")


if __name__ == "__main__":
    print("=" * 50)
    print("示例1：使用系统提示词约束输出")
    print("=" * 50)
    example_with_system_prompt()
    
    print("\n" + "=" * 50)
    print("示例2：不使用系统提示词")
    print("=" * 50)
    example_without_system_prompt()
    
    print("\n" + "=" * 50)
    print("示例3：自定义约束条件")
    print("=" * 50)
    example_custom_constraints()
