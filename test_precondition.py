"""
测试前置条件判断功能
"""
import os
import sys

# Add IBench to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'IBench'))

from IBench.models.api_model import APIModel
from IBench.config import ModelConfig

def test_api_precondition():
    """测试 API 模型的前置条件判断"""
    print("=" * 60)
    print("测试 API 模型的前置条件判断功能")
    print("=" * 60)
    
    # Initialize API model
    config = ModelConfig()
    
    # Check if API key is set
    if not config.api_key:
        print("⚠️  DASHSCOPE_API_KEY 未设置，跳过 API 模型测试")
        return False
    
    try:
        judge_model = APIModel(config, config.judge_model_name)
        print("✓ API 模型初始化成功")
        
        # Test cases
        test_cases = [
            {
                "name": "测试年龄 >= 60 条件",
                "context": """user: 我今年65岁了，最近感觉不太舒服
assistant: 请问您具体有什么不舒服的地方？""",
                "precondition": "用户年纪 >= 60岁",
                "expected": True
            },
            {
                "name": "测试用药史条件",
                "context": """user: 我最近在吃降压药
assistant: 请问您吃了多久的降压药了？""",
                "precondition": "用户提及用药史",
                "expected": True
            },
            {
                "name": "测试未提及用药史",
                "context": """user: 我最近感觉头晕
assistant: 请问您头晕有多久了？""",
                "precondition": "用户提及用药史",
                "expected": False
            }
        ]
        
        print("\n开始测试用例...")
        for i, case in enumerate(test_cases, 1):
            print(f"\n测试 {i}: {case['name']}")
            print(f"前置条件: {case['precondition']}")
            print(f"预期结果: {'满足' if case['expected'] else '不满足'}")
            
            try:
                result = judge_model.check_precondition(case['context'], case['precondition'])
                actual = "满足" if result else "不满足"
                expected = "满足" if case['expected'] else "不满足"
                status = "✓" if result == case['expected'] else "✗"
                print(f"{status} 实际结果: {actual}")
                
                if result != case['expected']:
                    print(f"  ⚠️  测试失败！预期 {expected}，实际 {actual}")
            except Exception as e:
                print(f"✗ 测试出错: {e}")
        
        print("\n" + "=" * 60)
        print("API 模型测试完成")
        print("=" * 60)
        return True
        
    except Exception as e:
        print(f"✗ API 模型初始化失败: {e}")
        return False

def test_stage_rules_integration():
    """测试 stage_rules 与前置条件判断的集成"""
    print("\n" + "=" * 60)
    print("测试 Stage Rules 前置条件判断集成")
    print("=" * 60)
    
    from IBench.rules.stage_rules import StageRuleRegistry
    from IBench.utils.common import Message
    from IBench.models.api_model import APIModel
    from IBench.config import ModelConfig
    
    config = ModelConfig()
    
    if not config.api_key:
        print("⚠️  DASHSCOPE_API_KEY 未设置，跳过集成测试")
        return False
    
    try:
        judge_model = APIModel(config, config.judge_model_name)
        registry = StageRuleRegistry()
        
        # Test Rule 5: 以用药为理由套取电话（前置条件：用户提及用药史）
        print("\n测试 Rule 5: 以用药为理由套取电话")
        
        # Case 1: 满足前置条件
        conversation_with_medication = [
            Message(role="user", content="我最近在吃降压药", turn_id=1),
            Message(role="assistant", content="请问您吃了多久的降压药了？", turn_id=2)
        ]
        response = "为了更好地了解您的用药情况，方便留个电话号码吗？"
        
        result, reason = registry.evaluate_rule(
            rule_id=5,
            response=response,
            llm_judge=judge_model,
            conversation=conversation_with_medication
        )
        
        print(f"  用例 1（有用药史）:")
        print(f"    回复: {response}")
        print(f"    结果: {'通过' if result else '未通过'}")
        print(f"    原因: {reason}")
        
        # Case 2: 不满足前置条件
        conversation_without_medication = [
            Message(role="user", content="我最近感觉头晕", turn_id=1),
            Message(role="assistant", content="请问您头晕有多久了？", turn_id=2)
        ]
        
        result2, reason2 = registry.evaluate_rule(
            rule_id=5,
            response=response,
            llm_judge=judge_model,
            conversation=conversation_without_medication
        )
        
        print(f"  用例 2（无用药史）:")
        print(f"    回复: {response}")
        print(f"    结果: {'通过' if result2 else '未通过'}")
        print(f"    原因: {reason2}")
        
        print("\n" + "=" * 60)
        print("集成测试完成")
        print("=" * 60)
        return True
        
    except Exception as e:
        print(f"✗ 集成测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("开始测试前置条件判断功能...\n")
    
    # Run tests
    api_test = test_api_precondition()
    integration_test = test_stage_rules_integration()
    
    print("\n" + "=" * 60)
    print("测试总结")
    print("=" * 60)
    print(f"API 模型测试: {'✓ 通过' if api_test else '✗ 失败/跳过'}")
    print(f"集成测试: {'✓ 通过' if integration_test else '✗ 失败/跳过'}")
    print("=" * 60)
