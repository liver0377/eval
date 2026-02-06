# max_turns 计算修复总结

## 📋 修复位置

### ✅ 已修复的位置

1. **`rules/dynamic_rule_registry.py:295-301`**
   - 用途：N="auto" 时检测 precondition
   - 修复时间：之前
   - 状态：✅ 已修复

2. **`pipeline/json_context_evaluator.py:362-371`**
   - 用途：评估固定 N 值的 multi_turn 规则
   - 修复时间：刚刚
   - 状态：✅ 已修复

---

## 🔍 修复逻辑

### **修复前**
```python
max_turns = (len(messages) - start_idx) // 2
```

### **修复后**
```python
# 考虑最后一条单独的 user 消息（Golden History 评估场景）
# 如果最后一条是 user，说明有一轮未完成，应该计入 max_turns
if messages[-1].role == "user":
    max_turns = (len(messages) - start_idx + 1) // 2
else:
    max_turns = (len(messages) - start_idx) // 2
```

---

## 📊 修复效果对比

### **Entry 004 示例**

**数据结构**：
```
Index 0: system (turn_id=0)
Index 1: user (turn_id=1)
Index 2: assistant (turn_id=1)
Index 3: user (turn_id=2)  ← 最后一条
```

**修复前**：
```
len(messages) = 4
start_idx = 1
max_turns = (4 - 1) // 2 = 1  ❌

规则要求 N=2
→ N=2 > max_turns=1
→ "超出范围" 错误 ❌
```

**修复后**：
```
len(messages) = 4
start_idx = 1
最后一条是 user → max_turns = (4 - 1 + 1) // 2 = 2  ✅

规则要求 N=2
→ N=2 <= max_turns=2
→ 正常评估 ✅
```

---

## 🎯 现在所有地方都已修复

两个关键位置都使用了相同的 max_turns 计算逻辑：
1. ✅ `find_precondition_turn` - N="auto" 的 precondition 检测
2. ✅ `_evaluate_multi_turn_rule` - 固定 N 值的规则评估

**结果**：
- ✅ 不再出现"N=2 超出范围（实际1轮）"的错误
- ✅ 正确识别最后一条 user 消息的轮次
- ✅ 可以正确评估"即将生成的回复"
