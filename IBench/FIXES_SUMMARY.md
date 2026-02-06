# 代码修复总结

## 📋 修复内容

### ✅ 修复1：修正 max_turns 计算
**文件**：`rules/dynamic_rule_registry.py:293-300`

**问题**：对于 Golden History 评估，最后一条消息是 user，但算法没有将这个未完成的轮次计入 max_turns。

**修复前**：
```python
start_idx = 1 if messages[0].role == "system" else 0
max_turns = (len(messages) - start_idx) // 2
```

**修复后**：
```python
start_idx = 1 if messages[0].role == "system" else 0

# 考虑最后一条单独的 user 消息（Golden History 评估场景）
# 如果最后一条是 user，说明有一轮未完成，应该计入 max_turns
if messages[-1].role == "user":
    max_turns = (len(messages) - start_idx + 1) // 2
else:
    max_turns = (len(messages) - start_idx) // 2
```

---

### ✅ 修复2：将 offset 默认值改为 0
**文件**：`rules/dynamic_rule_registry.py:239-251`

**问题**：offset 默认值为 1，导致 N_th 规则在 precondition 满足后的下一轮才触发，而实际应该在满足的那一轮触发。

**修复前**：
```python
offset = 1  # 默认 offset
```

**修复后**：
```python
offset = 0  # 默认 offset（precondition满足的那一轮）

if isinstance(N_config, str):
    if N_config == "auto":
        offset = 0  # 保持默认值
    ...
elif isinstance(N_config, dict):
    ...
    offset = N_config.get("offset", 0)  # 默认值改为 0
```

---

## 📊 修复效果

### **Entry 002 示例**

**对话结构**：
```
Turn 1-4: 完整对话（4轮）
Turn 5: user="不方便留电话"（最后一条，无assistant回复）
```

**规则**：`{"rule": "multi_turn:N_th:conv:ask_wechat", "N": "auto", "offset": 0}`

**修复前**：
- `max_turns = 4`（未计算Turn 5）
- 只检查 turn_id 1-4 的user消息
- ❌ 不会检查 Turn 5 的 "不方便留电话"
- `triggered_turn = None` 或错误的值

**修复后**：
- `max_turns = 5`（正确计算包括Turn 5）
- 检查 turn_id 1-5 的user消息
- ✅ 正确识别 Turn 5 的 "不方便留电话"
- `triggered_turn = 5`
- `N = 5 + 0 = 5`（评估即将生成的第5轮assistant回复）
- ✅ 不再出现"超出范围"警告

---

## 🎯 语义说明

### **offset 的含义**

- **offset = 0**（默认）：precondition满足的那一轮必须触发规则
  - 示例：用户拒绝电话的那一轮必须套微信

- **offset = 1**：precondition满足后的下一轮必须触发规则
  - 示例：用户拒绝电话后的下一轮必须套微信

---

## 📁 修改的文件

1. ✅ `rules/dynamic_rule_registry.py` - 修复 max_turns 计算和 offset 默认值
2. ✅ `data/dataset/golden_history_input.jsonl` - 重新生成（11条记录）

---

## 🚀 验证方法

运行评估脚本：
```bash
python scripts/evaluate_golden_history.py
```

应该不再出现：
- ❌ "⚠ 警告: 计算的 N=5 超出范围（实际4轮）"
- ❌ "⚠ 警告: precondition '用户拒绝给出电话' 从未满足"

应该正确：
- ✅ 识别 precondition 在 Turn 5 满足
- ✅ 计算 N = 5 + 0 = 5
- ✅ 评估即将生成的第5轮回复
