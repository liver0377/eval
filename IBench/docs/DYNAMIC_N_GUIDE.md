# 动态 N 值功能说明

## 概述

动态 N 值功能允许系统根据前置条件（precondition）自动确定需要评估的轮次，而不需要手动指定具体的轮次编号。

## 使用场景

**规则**：`ask_wechat` - 若用户拒绝电话，必须立即降级索要微信

**传统方式**（手动指定 N）：
```json
{
  "rule": "multi_turn:N_th:conv:ask_wechat",
  "N": 4
}
```
❌ 问题：需要知道用户在第 3 轮拒绝电话，才能指定第 4 轮

**新方式**（自动推断）：
```json
{
  "rule": "multi_turn:N_th:conv:ask_wechat",
  "N": "auto"
}
```
✅ 优势：系统自动找到"用户拒绝电话"的轮次，并在下一轮评估

## JSON 输入格式

### 格式 1：默认 offset（下一轮）

```json
{
  "rule_list": [
    {
      "rule": "multi_turn:N_th:conv:ask_wechat",
      "N": "auto"
    }
  ]
}
```

**行为**：N = (precondition 满足的轮次) + 1

---

### 格式 2：自定义 offset

```json
{
  "rule_list": [
    {
      "rule": "multi_turn:N_th:conv:ask_wechat",
      "N": {
        "value": "auto",
        "offset": 2
      }
    }
  ]
}
```

**行为**：N = (precondition 满足的轮次) + 2

---

### 格式 3：显式指定 N（向后兼容）

```json
{
  "rule_list": [
    {
      "rule": "multi_turn:N_th:conv:ask_wechat",
      "N": 5
    }
  ]
}
```

**行为**：直接使用 N=5，不扫描 precondition

## 工作原理

### 执行流程

1. **读取 precondition**
   - 从 `rule_mappings.py` 中读取规则的 precondition
   - 例如：`ask_wechat` 的 precondition = "用户拒绝给出电话"

2. **扫描对话历史**
   - 使用 LLM Judge 逐轮检测 precondition 是否满足
   - 从第 1 轮开始，检查每一轮的 user 消息

3. **找到满足的轮次**
   - 找到第一个满足 precondition 的轮次（如第 3 轮）
   - 如果多个轮次都满足，选择第一个

4. **计算最终 N 值**
   - N = (满足的轮次) + offset
   - 例如：第 3 轮 + offset(1) = 第 4 轮

5. **执行评估**
   - 在计算出的 N 轮评估规则

### 示例

**对话**：
```
第 1 轮：User: "孩子太矮"
         Assistant: "请问您是为谁咨询？"
         
第 2 轮：User: "是我的孩子"
         Assistant: "请留下电话"
         
第 3 轮：User: "不需要，别打电话了"  ← 满足 precondition
         Assistant: "好的，那我们可以通过微信沟通"
         
第 4 轮：(评估是否索要微信) ← 在这里评估
```

**配置**：
```json
{
  "rule": "multi_turn:N_th:conv:ask_wechat",
  "N": "auto"
}
```

**系统执行**：
1. 读取 precondition = "用户拒绝给出电话"
2. 扫描对话：
   - 第 1 轮：user 消息 = "孩子太矮" → 不满足
   - 第 2 轮：user 消息 = "是我的孩子" → 不满足
   - 第 3 轮：user 消息 = "不需要，别打电话了" → 满足 ✅
3. 计算 N = 3 + 1 = 4
4. 在第 4 轮评估是否索要微信

## 支持的规则

以下规则支持动态 N 值（都有 precondition）：

| rule_id | 规则名 | precondition |
|---------|--------|-------------|
| 5 | medication_phone | 用户提及用药史 |
| 6 | complication_phone | 用户年纪 >= 60岁 |
| 7 | expert_phone | 用户提及其尚未就诊 |
| 8 | primary_only | 用户提及多种疾病 |
| 9 | prompt_question | 用户未给明确问题 |
| 10 | report_phone | 用户已就诊且提及检查报告 |
| 11 | advice_phone | 用户正在服药并寻求建议 |
| 12 | leave | 用户尚未给出电话 |
| 13 | ask_wechat | 用户拒绝给出电话 |
| 14 | final_detainment | 用户拒绝给出电话和微信 |
| 16 | mental_test | 用户提及有心理问题 |

## 错误处理

### 情况 1：precondition 从未满足

```json
{
  "rule": "multi_turn:N_th:conv:ask_wechat",
  "N": "auto"
}
```

**如果对话中用户从未拒绝电话**：
- ⚠️ 输出警告：`precondition '用户拒绝给出电话' 从未满足，跳过该规则`
- ✅ 跳过该规则，继续评估其他规则
- ✅ 不中断整个评估流程

**返回结果**：
```json
{
  "triggered": false,
  "score": 0,
  "kwargs": {},
  "reason": "precondition 未满足，无法评估"
}
```

---

### 情况 2：计算的 N 超出对话范围

**如果用户在第 9 轮拒绝电话，但对话只有 9 轮**：
- 计算 N = 9 + 1 = 10
- 但对话只有 9 轮
- ⚠️ 输出警告：`N=10 超出范围，对话仅有 9 轮`
- ✅ 跳过该规则

**返回结果**：
```json
{
  "triggered": false,
  "score": 0,
  "kwargs": {},
  "reason": "N=10 超出范围，对话仅有 9 轮"
}
```

---

### 情况 3：规则没有 precondition

```json
{
  "rule": "multi_turn:N_th:conv:consult_subject",
  "N": "auto"
}
```

**如果规则没有定义 precondition**：
- ❌ 抛出异常：`规则 consult_subject 没有 precondition，无法使用 N=auto`
- ✅ 用户需要手动指定 N 或添加 precondition

## 最佳实践

### 1. 何时使用 `"N": "auto"`

✅ **推荐使用**：
- 规则依赖前置条件（如"用户拒绝电话"）
- 前置条件满足的轮次不确定
- 需要在触发后立即或延迟评估

❌ **不推荐使用**：
- 规则没有前置条件（如 `gender`、`consult_subject`）
- 需要评估固定的轮次（如"前 3 轮"）
- 使用 `FIRST_N` 类型的规则

### 2. offset 的选择

| offset | 含义 | 适用场景 |
|--------|------|---------|
| 1（默认） | 下一轮 | 立即降级（拒绝电话 → 索要微信） |
| 2 | 延迟 2 轮 | 给用户 2 轮反应时间 |
| 0 | 同一轮 | 在满足条件的同一轮评估 |

### 3. 性能考虑

**LLM Judge 调用**：
- 每个使用 `"N": "auto"` 的规则都会调用 LLM Judge
- 如果有 3 个这样的规则，需要 3 次 LLM Judge 调用
- 建议：合理使用，避免不必要的扫描

## 完整示例

### 输入 JSON

```json
{
  "key": "example_001",
  "messages": [...],
  "rule_list": [
    {
      "rule": "multi_turn:N_th:conv:ask_wechat",
      "N": "auto"
    },
    {
      "rule": "multi_turn:N_th:conv:final_detainment",
      "N": {
        "value": "auto",
        "offset": 1
      }
    },
    {
      "rule": "multi_turn:FIRST_N:ask:consult_subject",
      "N": 3
    }
  ]
}
```

### 执行流程

1. **`ask_wechat` (N="auto")**
   - 扫描对话，找到"用户拒绝电话"的轮次（如第 3 轮）
   - 计算 N = 3 + 1 = 4
   - 在第 4 轮评估是否索要微信

2. **`final_detainment` (N={"value": "auto", "offset": 1})**
   - 扫描对话，找到"用户拒绝电话和微信"的轮次（如第 5 轮）
   - 计算 N = 5 + 1 = 6
   - 在第 6 轮评估是否最后挽留

3. **`consult_subject` (N=3)**
   - 直接使用 N=3
   - 在前 3 轮评估是否询问咨询对象

## 优势总结

| 优势 | 说明 |
|------|------|
| **自动化** | 无需手动指定轮次 |
| **准确** | 根据实际对话动态确定评估时机 |
| **灵活** | 支持 offset 调整评估时机 |
| **鲁棒** | 自动处理 precondition 未满足的情况 |
| **兼容** | 保留显式指定 N 的方式 |
