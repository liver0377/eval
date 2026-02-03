# compare_models.py 修改完成 - 使用 INTERACTIVE 模式

## ✅ 修改完成

已成功修改 `compare_models.py`，使用 **INTERACTIVE 模式**和 **UserSimulator**！

---

## 🔧 修改内容

### 文件：`IBench/scripts/compare_models.py`

### 修改 1：导入 UserSimulator（第 14-18 行）

**修改前**：
```python
from IBench.models.local_model import LocalModel
from IBench.models.model_configs import get_model_config
from IBench.models.api_model import APIModel
from IBench.evaluator.batch_evaluator import BatchEvaluator
from IBench.utils.common import Message, EvaluationMode
from IBench.config import Config
```

**修改后**：
```python
from IBench.models.local_model import LocalModel
from IBench.models.model_configs import get_model_config
from IBench.models.api_model import APIModel
from IBench.conversation.user_simulator import UserSimulator  # ← 新增
from IBench.evaluator.batch_evaluator import BatchEvaluator
from IBench.utils.common import Message, EvaluationMode
from IBench.config import Config
```

---

### 修改 2：load_model_from_config 返回 UserSimulator（第 21-56 行）

**修改前**：
```python
def load_model_from_config(model_config, api_key: str):
    ...
    return local_model, judge_model
```

**修改后**：
```python
def load_model_from_config(model_config, api_key: str):
    ...
    # 新增：创建 UserSimulator
    user_simulator = UserSimulator(ibench_config)
    print("UserSimulator initialized")
    
    return local_model, judge_model, user_simulator  # ← 返回三个值
```

---

### 修改 3：使用 INTERACTIVE 模式生成对话（第 105-140 行）

**修改前（固定"请继续"）**：
```python
for turn in range(max_turns):
    response = local_model.generate(current_history)
    responses.append(response)
    current_history.append(
        Message(role="assistant", content=response, turn_id=turn+1)
    )
    if turn < max_turns - 1:
        # Simple follow-up
        current_history.append(
            Message(role="user", content="请继续", turn_id=turn+2)
        )
```

**修改后（UserSimulator 生成）**：
```python
# Interactive loop
for turn in range(1, max_turns + 1):
    print(f"  Turn {turn}...")
    
    # Generate assistant response
    assistant_response = local_model.generate(conversation_history)
    responses.append(assistant_response)
    
    assistant_msg = Message(
        role="assistant",
        content=assistant_response,
        turn_id=turn
    )
    conversation_history.append(assistant_msg)
    
    # Generate next user message using UserSimulator
    if turn < max_turns:
        user_msg = user_simulator.generate_user_message(conversation_history)
        print(f"    User: {user_msg.content[:50]}...")
        conversation_history.append(user_msg)
```

---

### 修改 4：使用 INTERACTIVE 评估模式（第 127 行）

**修改前**：
```python
result = evaluator.evaluate_conversation(
    conversation_id=f"{model_name}_test_{i+1}",
    mode=EvaluationMode.CONTEXT,  # ← CONTEXT 模式
    conversation_history=conversation_history,
    responses=responses
)
```

**修改后**：
```python
result = evaluator.evaluate_conversation(
    conversation_id=f"{model_name}_test_{i+1}",
    mode=EvaluationMode.INTERACTIVE,  # ← INTERACTIVE 模式
    conversation_history=conversation_history,
    responses=responses
)
```

---

## 🎯 修改效果对比

### 修改前（CONTEXT 模式 + 固定"请继续"）

```
Test 1: 我最近总是失眠

Turn 1:
  Assistant: 您的失眠问题需要重视。请问多久了？
  User: 请继续  ← 固定的

Turn 2:
  Assistant: 失眠可能由多种原因引起...
  User: 请继续  ← 固定的

Turn 3:
  Assistant: 建议您保持规律作息...
```

**问题**：
- ❌ 用户输入不真实
- ❌ 无法测试模型的真实对话能力
- ❌ 对话流程僵硬

---

### 修改后（INTERACTIVE 模式 + UserSimulator）

```
Test 1: 我最近总是失眠

Turn 1:
  Assistant: 您的失眠问题需要重视。请问多久了？
  User: 大概有一个月了，特别影响工作  ← UserSimulator 生成

Turn 2:
  Assistant: 我理解您的困扰。除了失眠，您还有其他症状吗？
  User: 有时候会头晕，而且很容易焦虑  ← UserSimulator 生成

Turn 3:
  Assistant: 让我了解一下您的日常作息情况...
  User: 我一般晚上12点才睡，但躺床上也睡不着  ← UserSimulator 生成
```

**优势**：
- ✅ 用户输入真实自然
- ✅ 测试模型的真实对话能力
- ✅ 对话流程流畅
- ✅ 符合实际应用场景

---

## 📊 修改对比总结

| 项目 | 修改前 | 修改后 |
|------|--------|--------|
| **评估模式** | CONTEXT | INTERACTIVE |
| **用户输入** | 固定"请继续" | UserSimulator 动态生成 |
| **对话真实性** | ❌ 低 | ✅ 高 |
| **模型测试** | 只测回复生成 | 测回复生成 + 对话能力 |
| **API 调用** | 只有 Judge | Judge + UserSimulator |
| **评估准确性** | ❌ 低 | ✅ 高 |

---

## 🧪 测试验证

### 在服务器上测试

```bash
cd /data/wudy/projects/eval

# 运行模型对比
python IBench/scripts/compare_models.py \
    --models Qwen3-8B qwen3_full_sft \
    --prompts "我最近总是失眠" \
    --max-turns 3 \
    --api-key $DASHSCOPE_API_KEY
```

### 预期输出

```
============================================================
Loading model: Qwen3-8B
============================================================
Loading model from /data/wudy/projects/models/Qwen3-8B...
...
UserSimulator initialized

Test 1/1: 我最近总是失眠
  Turn 1...
    User: 大概有一个月了，特别影响工作
  Turn 2...
    User: 有时候会头晕，而且很容易焦虑
  Turn 3...
    User: 我一般晚上12点才睡，但躺床上也睡不着

Results saved to: ./data/output/model_comparison_20250203_XXXXXX.json
```

---

## 💡 使用说明

### 基本用法

```bash
python IBench/scripts/compare_models.py \
    --models Qwen3-8B qwen3_full_sft \
    --prompts "我最近总是失眠" "我头疼持续三天" \
    --max-turns 3 \
    --api-key $DASHSCOPE_API_KEY
```

### 参数说明

- `--models`: 要对比的模型列表
- `--prompts`: 初始用户问题列表
- `--max-turns`: 每个对话的轮次
- `--api-key`: Judge 和 UserSimulator 的 API key

### 对话流程

1. **Turn 1**: 模型回复初始问题
2. **Turn 2**: UserSimulator 根据上下文生成回复 → 模型回复
3. **Turn 3**: UserSimulator 根据上下文生成回复 → 模型回复
4. ...（继续直到 max_turns）
5. **评估**: 对每个模型的每条回复应用规则

---

## 📝 UserSimulator 的 Persona

UserSimulator 使用以下 persona（user_simulator.py 第 24-30 行）：

```python
self.user_persona = """你是一个寻求医疗咨询的用户。你的角色是:
1. 描述自己的症状或健康问题
2. 可能会对医生/助手的建议提出疑问
3. 可能会拒绝某些检查或治疗建议
4. 表现得像真实的患者一样，有时会犹豫或不清楚自己的情况

请根据之前的对话历史，自然地回复。"""
```

**特点**：
- ✅ 模拟真实患者
- ✅ 根据对话历史调整回复
- ✅ 可能会质疑或拒绝建议
- ✅ 表现自然，不会只说"请继续"

---

## ✨ 修改完成总结

### 修改文件

- ✅ `IBench/scripts/compare_models.py`
  - 导入 UserSimulator
  - 修改 load_model_from_config
  - 使用 INTERACTIVE 模式
  - 动态生成用户输入

### 修改效果

- ✅ 使用 UserSimulator 生成真实用户回复
- ✅ 采用 INTERACTIVE 评估模式
- ✅ 更真实的对话场景
- ✅ 更准确的模型评估

### 下一步

**立即在服务器上测试**：

```bash
python IBench/scripts/compare_models.py \
    --models Qwen3-8B qwen3_full_sft \
    --prompts "我最近总是失眠" \
    --max-turns 3 \
    --api-key $DASHSCOPE_API_KEY
```

---

**修改完成！现在 compare_models.py 使用真实的 INTERACTIVE 模式了！** 🎉
