# IBench - Model-User Dialogue Evaluation Framework

IBench 是一个用于评估模型与用户对话质量的评估框架，支持环境历史评估和动态交互评估两种模式。

## 功能特性

- **环境历史评估**：给定完整的对话上下文，评估模型的回复质量
- **动态交互评估**：用户模拟器与模型动态交互，实时评估每轮回复
- **规则引擎**：包含 6 条单轮规则和 7 条阶段规则
- **混合评估**：支持基于规则的自动评估和基于 LLM 的智能评估
- **批量处理**：支持批量评估多个对话场景

## 快速开始

### 环境要求

```bash
pip install torch transformers openai
```

### 配置环境变量

```bash
export DASHSCOPE_API_KEY="your-api-key"
```

### 环境历史评估示例

```python
from IBench import ContextEvaluator, Message, EvaluationMode

# 初始化评估器
evaluator = ContextEvaluator(
    local_model_path="./models/qwen3-8b",
    api_key="your-api-key"
)

# 定义对话历史
conversation_history = [
    Message(role="user", content="我最近总是失眠", turn_id=1),
    Message(role="user", content="每天晚上都睡不着，很焦虑", turn_id=2)
]

# 执行评估
result = evaluator.evaluate(conversation_history)

# 查看结果
print(f"最终得分: {result.final_score}")
print(f"总轮次: {result.total_turns}")
```

### 动态交互评估示例

```python
from IBench import InteractiveEvaluator

# 初始化评估器
evaluator = InteractiveEvaluator(
    local_model_path="./models/qwen3-8b",
    api_key="your-api-key"
)

# 定义初始用户输入
initial_prompt = "我最近总是失眠"

# 执行评估
result = evaluator.evaluate(initial_prompt, max_turns=5)

# 查看结果
print(f"最终得分: {result.final_score}")
```

## 规则说明

### 单轮规则（6条）

| ID | 约束 | 类型 | 得分 |
|----|------|------|------|
| 1 | 使用情感安慰用语 | LLM | -1 |
| 2 | 使用解释性语句 | LLM | -1 |
| 3 | 提到用户的性别 | Rule | -1 |
| 4 | 问用户"有什么症状" | LLM | -1 |
| 5 | 询问多个问题 | Rule | -1 |
| 6 | 给出疾病名称 | LLM | -1 |

### 阶段规则（7条）

| ID | 约束 | 前置条件 | 类型 | 得分 |
|----|------|----------|------|------|
| 1 | 询问用户为谁咨询 | - | LLM | +1 |
| 2 | 提及用户就诊史 | - | LLM | -1 |
| 3 | 提出检查邀约 | 用户未提检查 | LLM | -1 |
| 4 | 询问性别 | - | Rule | +1 |
| 5 | 用用药理由套电话 | 用户提用药 | LLM | +1 |
| 6 | 用并发症理由套电话 | 用户>=60岁 | LLM | +1 |
| 7 | 用专家解读理由套电话 | 用户未就诊 | LLM | +1 |

## 目录结构

```
IBench/
├── config.py                  # 配置管理
├── models/                     # 模型加载器
│   ├── local_model.py         # 本地模型（HuggingFace）
│   └── api_model.py           # API模型（Dashscope）
├── rules/                     # 规则定义
│   ├── single_rules.py        # 单轮规则
│   └── stage_rules.py         # 阶段规则
├── conversation/              # 对话管理
│   ├── conversation.py        # 对话上下文
│   └── user_simulator.py     # 用户模拟器
├── evaluator/                 # 评估引擎
│   ├── rule_evaluator.py     # 规则评估器
│   └── batch_evaluator.py    # 批量评估
├── pipeline/                  # 评估流程
│   ├── context_eval.py       # 环境历史评估
│   └── interactive_eval.py   # 动态交互评估
└── utils/
    └── common.py             # 通用数据结构
```

## 配置说明

### 模型配置

```python
from IBench.config import ModelConfig

model_config = ModelConfig(
    local_model_path="./models/qwen3-8b",
    api_key="your-api-key",
    user_model_name="qwen-plus",      # 用户模拟器模型
    judge_model_name="qwen-max",      # 评估judge模型
    temperature=0.0,
    max_new_tokens=512
)
```

### 评估配置

```python
from IBench.config import EvaluationConfig

eval_config = EvaluationConfig(
    output_dir="./data/output",
    batch_size=8,
    max_conversation_turns=10,
    single_rule_turns={
        1: [1, 2, 3, 4, 5, 6],
        2: [1, 2, 3, 4, 5, 6]
    },
    stage_rule_turns={
        1: [1],
        3: [2, 3],
        4: [4]
    }
)
```

## 输出格式

### 评估结果示例

```json
{
  "conversation_id": "context_conv_2",
  "mode": "context",
  "total_turns": 2,
  "final_score": -2,
  "metadata": {},
  "turn_evaluations": [
    {
      "turn_id": 1,
      "response": "您的失眠问题需要重视...",
      "single_rules": [
        {
          "rule_id": 1,
          "rule_type": "LLM",
          "rule_description": "使用情感安慰用语",
          "passed": false,
          "score": -1,
          "reason": "VIOLATED"
        }
      ],
      "stage_rules": [],
      "total_score": -1
    }
  ]
}
```

## 许可证

MIT License
