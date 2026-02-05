"""
测试规则名称映射功能
验证规则名称的使用（已移除ID兼容）
"""

from IBench.rules.single_rules import SingleRuleRegistry
from IBench.rules.stage_rules import StageRuleRegistry
from IBench.models.model_configs import EvaluationConfig

def test_single_rule_registry():
    """测试单轮规则注册表"""
    print("=" * 60)
    print("测试单轮规则注册表")
    print("=" * 60)
    
    registry = SingleRuleRegistry()
    
    # 测试1：通过名称获取规则
    print("\n1. 通过名称获取规则:")
    rule = registry.get_rule("emotional_comfort")
    print(f"   规则ID: {rule.rule_id}")
    print(f"   规则名称: {rule.name}")
    print(f"   规则描述: {rule.description}")
    assert rule.name == "emotional_comfort"
    assert rule.rule_id == 1
    print("   ✓ 通过名称获取规则成功")
    
    # 测试2：获取所有规则
    print("\n2. 获取所有规则:")
    all_rules = registry.get_all_rules()
    print(f"   总规则数: {len(all_rules)}")
    for rule_id, rule in all_rules.items():
        print(f"   - {rule_id}: {rule.name}")
    assert len(all_rules) == 5
    print("   ✓ 获取所有规则成功")
    
    # 测试3：规则名称到ID的映射
    print("\n3. 规则名称到ID的映射:")
    print(f"   name_to_id: {registry.name_to_id}")
    expected_mapping = {
        "emotional_comfort": 1,
        "explanatory_statements": 2,
        "symptom_inquiry": 3,
        "multiple_questions": 4,
        "disease_diagnosis": 5
    }
    assert registry.name_to_id == expected_mapping
    print("   ✓ 名称到ID映射正确")
    
    # 测试4：get_rules_for_turn使用名称
    print("\n4. get_rules_for_turn使用规则名称:")
    rule_mapping = {
        1: ["emotional_comfort", "explanatory_statements"],
        2: ["symptom_inquiry", "multiple_questions"],
        3: ["disease_diagnosis"]
    }
    
    for turn_id in [1, 2, 3]:
        rule_ids = registry.get_rules_for_turn(turn_id, rule_mapping)
        print(f"   轮次{turn_id}的规则IDs: {rule_ids}")
        assert all(isinstance(rid, int) for rid in rule_ids)
    print("   ✓ 规则名称转换成功")


def test_stage_rule_registry():
    """测试阶段规则注册表"""
    print("\n" + "=" * 60)
    print("测试阶段规则注册表")
    print("=" * 60)
    
    registry = StageRuleRegistry()
    
    # 测试1：通过名称获取规则
    print("\n1. 通过名称获取规则:")
    rule = registry.get_rule("collect_phone_medication")
    print(f"   规则ID: {rule.rule_id}")
    print(f"   规则名称: {rule.name}")
    print(f"   规则描述: {rule.description}")
    assert rule.name == "collect_phone_medication"
    assert rule.rule_id == 5
    print("   ✓ 通过名称获取规则成功")
    
    # 测试2：获取所有规则
    print("\n2. 获取所有规则:")
    all_rules = registry.get_all_rules()
    print(f"   总规则数: {len(all_rules)}")
    for rule_id, rule in all_rules.items():
        print(f"   - {rule_id}: {rule.name}")
    assert len(all_rules) == 7
    print("   ✓ 获取所有规则成功")
    
    # 测试3：get_rules_for_turn使用名称
    print("\n3. get_rules_for_turn使用规则名称:")
    rule_mapping = {
        1: ["inquire_consultation_target"],
        4: ["inquire_gender"],
        8: ["collect_phone_medication", "collect_phone_complication"]
    }
    
    for turn_id in [1, 4, 8]:
        rule_ids = registry.get_rules_for_turn(turn_id, rule_mapping)
        print(f"   轮次{turn_id}的规则IDs: {rule_ids}")
        assert all(isinstance(rid, int) for rid in rule_ids)
    print("   ✓ 规则名称转换成功")


# DEPRECATED: test_evaluation_config() function removed
# Rule mapping functionality has been removed from EvaluationConfig
# Rules are now dynamically loaded from JSON files


def main():
    """运行所有测试"""
    print("\n" + "=" * 60)
    print("开始测试规则名称映射功能（仅支持规则名称）")
    print("=" * 60)
    
    try:
        test_single_rule_registry()
        test_stage_rule_registry()
        # test_evaluation_config()  # Removed - rule mapping deprecated
        
        print("\n" + "=" * 60)
        print("✓ 所有测试通过！")
        print("=" * 60)
        
    except AssertionError as e:
        print(f"\n✗ 测试失败: {e}")
        raise
    except Exception as e:
        print(f"\n✗ 发生错误: {e}")
        raise


if __name__ == "__main__":
    main()
