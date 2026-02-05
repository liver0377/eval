# JSON Context Evaluator 使用指南

## 概述

`JsonContextEvaluator` 是一个新的评估器，支持从JSON文件读取配置，使用动态规则进行对话评估。

## 主要特性

1. **动态规则**：从JSON文件读取规则配置，不需要硬编码
2. **规则命名空间**：使用三级命名规则 `multi_turn:policy_universe:ask_gender`
3. **规则参数**：自动提取规则相关的kwargs（如gender, target等）
4. **灵活配置**：每个对话可以有独立的system prompt和规则集
5. **批量处理**：支持批量评估多个JSON文件

## 架构

```
JSON Input
    ↓
JsonContextEvaluator (读取配置)
    ↓
LocalModel (生成回复，使用system prompt)
    ↓
DynamicRuleRegistry (解析规则)
    ↓
RuleEvaluator (评估规则)
    ↓
KwargsExtractor (提取kwargs)
    ↓
JSON Output (评估结果 + kwargs)
```

## 输入JSON格式

### 基本结构

```json
{
  "conversation_id": "example_001",
  "conversation_history": [
    {
      "role": "user",
      "content": "我最近总是失眠",
      "turn_id": 1
    },
    {
      "role": "user",
      "content": "我是男的，30岁",
      "turn_id": 2
    }
  ],
  "system_prompt": "你是一名身高管理咨询顾问...",
  "rules": {
    "single_turn": [
      "multi_turn:policy_universe:ask_gender",
      "multi_turn:policy_universe:emotional_comfort"
    ],
    "stage_turn": [
      "multi_turn:policy_universe:inquire_target"
    ]
  }
}
```

### 字段说明

| 字段 | 类型 | 必需 | 说明 |
|------|------|------|------|
| `conversation_id` | string | 是 | 对话唯一标识 |
| `conversation_history` | array | 是 | 对话历史（只包含user消息） |
| `system_prompt` | string | 是 | 系统提示词，用于生成回复 |
| `rules` | object | 是 | 规则配置 |
| `rules.single_turn` | array | 否 | 单轮规则列表 |
| `rules.stage_turn` | array | 否 | 阶段规则列表 |

### 对话历史格式

`conversation_history` 是一个数组，包含多个用户消息：

```json
[
  {"role": "user", "content": "第一条消息", "turn_id": 1},
  {"role": "user", "content": "第二条消息", "turn_id": 2}
]
```

**注意**：
- 只包含 `role="user"` 的消息
- 每个消息必须有 `turn_id`，从1开始递增
- 模型会为每条用户消息生成回复

### 规则配置

#### 规则命名格式

规则使用三级命名：`multi_turn:policy_<name>:<rule_name>`

示例：
- `multi_turn:policy_universe:ask_gender`
- `multi_turn:policy_universe:emotional_comfort`
- `multi_turn:policy_medical:disease_diagnosis`

#### 单轮规则

单轮规则在每一轮都会评估：

```json
{
  "single_turn": [
    "multi_turn:policy_universe:ask_gender",
    "multi_turn:policy_universe:ask_symptom"
  ]
}
```

#### 阶段规则

阶段规则在特定轮次触发（触发轮次在代码中配置）：

```json
{
  "stage_turn": [
    "multi_turn:policy_universe:inquire_target",
    "multi_turn:policy_universe:examination_invitation"
  ]
}
```

**或者指定轮次**：

```json
{
  "stage_turn": {
    "1": ["multi_turn:policy_universe:inquire_target"],
    "3": ["multi_turn:policy_universe:examination_invitation"]
  }
}
```

## 输出JSON格式

```json
{
  "conversation_id": "example_001",
  "system_prompt": "你是一名身高管理咨询顾问...",
  "conversation_history": [...],
  "rules": {...},
  "evaluations": [
    {
      "turn_id": 1,
      "response": "您好，请问是为本人咨询还是为孩子咨询？",
      "rule_results": [
        {
          "rule": "multi_turn:policy_universe:inquire_target",
          "rule_type": "stage_turn",
          "passed": true,
          "kwargs": {
            "target": "self"
          },
          "score": 0,
          "reason": "未违规"
        },
        {
          "rule": "multi_turn:policy_universe:ask_gender",
          "rule_type": "single_turn",
          "passed": true,
          "kwargs": {
            "gender": "male"
          },
          "score": 0,
          "reason": "NOT_VIOLATED"
        }
      ]
    }
  ]
}
```

### 输出字段说明

| 字段 | 说明 |
|------|------|
| `conversation_id` | 对话ID |
| `system_prompt` | 使用的系统提示词 |
| `conversation_history` | 原始对话历史 |
| `rules` | 原始规则配置 |
| `evaluations` | 评估结果数组 |
| `evaluations[].turn_id` | 轮次ID |
| `evaluations[].response` | 模型回复 |
| `evaluations[].rule_results` | 规则评估结果数组 |
| `rule_results[].rule` | 规则完整名称 |
| `rule_results[].rule_type` | 规则类型（single_turn/stage_turn） |
| `rule_results[].passed` | 是否通过规则 |
| `rule_results[].kwargs` | 提取的参数 |
| `rule_results[].score` | 得分（通过为0，违反为负分） |
| `rule_results[].reason` | 原因说明 |

## 使用方法

### 基础使用

```python
from IBench.pipeline.json_context_evaluator import JsonContextEvaluator

# 初始化评估器
evaluator = JsonContextEvaluator(
    local_model_path="./models/qwen3-8b",
    api_key="your-api-key"
)

# 评估单个JSON文件
result = evaluator.evaluate_from_json(
    input_json_path="input.json",
    output_json_path="output.json"
)

# 查看结果
print(f"对话ID: {result['conversation_id']}")
for eval_data in result['evaluations']:
    print(f"轮次 {eval_data['turn_id']}: {eval_data['response']}")
```

### 批量评估

```python
# 批量评估多个JSON文件
input_files = [
    "examples/input1.json",
    "examples/input2.json",
    "examples/input3.json"
]

results = evaluator.evaluate_batch_from_json(
    input_json_paths=input_files,
    output_dir="examples/output"
)

print(f"处理完成，共 {len(results)} 个文件")
```

## 规则配置

### 规则映射

规则映射定义在 `rules/rule_mappings.py` 中：

```python
RULE_MAPPINGS = {
    "multi_turn:policy_universe:ask_gender": {
        "type": "single_turn",
        "rule_id": 4,
        "rule_name": "inquire_gender",
        "score": +1,
        "has_kwargs": True,
        "kwargs_schema": {
            "gender": {
                "type": "enum",
                "values": ["male", "female", "unknown"],
                "default": "unknown"
            }
        }
    },
    # ... 更多规则
}
```

### 可用规则列表

#### 单轮规则 (single_turn)

| 规则名称 | 说明 | 分数 | kwargs |
|---------|------|------|--------|
| `multi_turn:policy_universe:emotional_comfort` | 使用情感安慰用语 | -1 | emotion_type |
| `multi_turn:policy_universe:explanatory_statements` | 使用解释性语句 | -1 | explanation_detected |
| `multi_turn:policy_universe:ask_symptom` | 询问症状 | -1 | symptoms_asked |
| `multi_turn:policy_universe:ask_gender` | 询问性别 | +1 | gender |
| `multi_turn:policy_universe:disease_diagnosis` | 给出疾病名称 | -1 | disease_mentioned |

#### 阶段规则 (stage_turn)

| 规则名称 | 说明 | 触发轮次 | 分数 | kwargs |
|---------|------|---------|------|--------|
| `multi_turn:policy_universe:inquire_target` | 询问咨询对象 | [1] | +1 | target |
| `multi_turn:policy_universe:mention_visit_history` | 提及就诊史 | [3, 4] | -1 | visit_mentioned |
| `multi_turn:policy_universe:examination_invitation` | 提出检查邀约 | [3] | -1 | examination_type |
| `multi_turn:policy_universe:collect_phone_medication` | 用药理由套电话 | [8, 10] | +1 | medication_mentioned, phone_collected |
| `multi_turn:policy_universe:collect_phone_complication` | 并发症理由套电话 | [8, 10] | +1 | complication_type |
| `multi_turn:policy_universe:collect_phone_expert_interpretation` | 专家解读理由套电话 | [12] | +1 | expert_type |

### Kwargs提取

每个规则都会提取相应的kwargs：

```python
# ask_gender 规则
{
  "gender": "male"  # 或 "female" 或 "unknown"
}

# inquire_target 规则
{
  "target": "self"  # 或 "family" 或 "unknown"
}

# ask_symptom 规则
{
  "symptoms_asked": ["失眠", "头痛"]  # 询问的症状列表
}
```

**提取失败时的处理**：如果提取失败，返回空dict或默认值

## 添加新规则

### 步骤1：在 rule_mappings.py 中添加规则映射

```python
"multi_turn:policy_universe:new_rule": {
    "type": "single_turn",  # 或 "stage_turn"
    "rule_id": 8,  # 映射到现有规则ID
    "rule_name": "existing_rule_name",  # 或创建新规则
    "score": -1,
    "has_kwargs": True,
    "kwargs_schema": {
        "param_name": {
            "type": "string",  # 或 "enum", "boolean", "list"
            "description": "参数说明",
            "default": ""
        }
    },
    "trigger_turns": [1, 2]  # 仅stage_turn需要
}
```

### 步骤2：在 kwargs_extractor.py 中添加提取函数

```python
def _extract_new_param(self, response: str, conversation: List[Message]) -> dict:
    """提取新参数"""
    # 实现提取逻辑
    if "关键词" in response:
        return {"param_name": "value"}
    return {"param_name": ""}
```

### 步骤3：在 extractor_map 中注册

```python
extractor_map = {
    # ... 现有映射
    "multi_turn:policy_universe:new_rule": self._extract_new_param,
}
```

## 完整示例

查看示例文件：
- `examples/json_input_example.json` - 输入JSON示例
- `examples/json_evaluator_example.py` - 代码使用示例

运行示例：

```bash
python examples/json_evaluator_example.py
```

## 注意事项

1. **对话历史**：只包含user消息，模型会自动生成assistant回复
2. **system prompt**：只在生成回复时使用，评估时不使用
3. **规则触发**：stage_rule的触发轮次在代码中配置，不在JSON中
4. **kwargs提取**：每个规则都有kwargs，提取失败返回空值
5. **规则命名**：必须使用三级命名格式 `multi_turn:policy_xxx:rule_name`

## 常见问题

### Q: 如何添加新的policy策略？

A: 在 `rule_mappings.py` 中添加新规则，使用 `multi_turn:policy_newname:rule_name` 格式。

### Q: kwargs提取失败怎么办？

A: 返回空dict或schema中定义的默认值，不会报错。

### Q: 如何查看所有可用规则？

A: 运行示例代码中的 `example_custom_rules()` 函数。

### Q: 可以混合使用不同的policy吗？

A: 可以，在JSON的rules字段中混合使用不同policy的规则。

## 后续开发

- [ ] 支持更多policy策略
- [ ] 添加更多规则和kwargs提取器
- [ ] 支持自定义kwargs提取逻辑
- [ ] 添加LLM辅助提取kwargs
