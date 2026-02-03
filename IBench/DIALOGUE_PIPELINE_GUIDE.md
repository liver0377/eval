# 对话生成和评估系统 - 完整指南

## 📖 系统架构

现在 IBench 支持**两种评估模式**：

1. **在线评估**（原有）：边生成对话边评估
2. **离线评估**（新增）：先生成对话，再统一评估

---

## 🎯 两种模式对比

| 方面 | 在线评估 | 离线评估 |
|------|----------|----------|
| **流程** | 生成 → 评估 | 生成 → 保存 → 读取 → 评估 |
| **脚本** | `compare_models.py` | `generate_conversations.py` + `evaluate_conversations.py` |
| **对话保存** | ❌ 否 | ✅ 是（ShareGPT 格式） |
| **评估时机** | 实时 | 批量 |
| **可重复评估** | ❌ 否 | ✅ 是 |
| **适用场景** | 快速测试 | 生产评估 |

---

## 📂 文件结构

```
IBench/
├── scripts/
│   ├── compare_models.py              # 在线评估（原有）
│   ├── generate_conversations.py       # 新增：生成对话
│   ├── evaluate_conversations.py       # 新增：评估对话
│   └── ...
└── data/
    └── conversations/                   # 新增：对话存储目录
        ├── Qwen3-8B/
        │   ├── conv_1.json
        │   ├── conv_2.json
        │   └── generation_summary.json
        ├── qwen3_full_sft/
        │   ├── conv_1.json
        │   ├── conv_2.json
        │   └── generation_summary.json
        └── evaluation_results/            # 评估结果
            ├── evaluation_summary.json
            └── detailed_results/
```

---

## 🔄 完整工作流程

### 阶段 1：生成对话

```bash
python IBench/scripts/generate_conversations.py \
    --models Qwen3-8B qwen3_full_sft \
    --prompts "我最近总是失眠" "我头疼持续三天" \
    --max-turns 3 \
    --output-dir IBench/data/conversations
```

**生成内容**：
- `IBench/data/conversations/Qwen3-8B/conv_1.json`
- `IBench/data/conversations/Qwen3-8B/conv_2.json`
- `IBench/data/conversations/qwen3_full_sft/conv_1.json`
- `IBench/data/conversations/qwen3_full_sft/conv_2.json`
- `IBench/data/conversations/generation_summary.json`

### 阶段 2：评估对话

```bash
python IBench/scripts/evaluate_conversations.py \
    --input IBench/data/conversations \
    --mode INTERACTIVE \
    --api-key $DASHSCOPE_API_KEY
```

**评估内容**：
- 读取所有对话文件
- 使用 Judge 模型评估
- 保存评估结果到 `evaluation_results/`

---

## 💬 ShareGPT 格式

### 格式定义

```json
[
  {
    "from": "human",
    "value": "用户的问题"
  },
  {
    "from": "gpt",
    "value": "模型的回复"
  },
  {
    "from": "human",
    "value": "用户的追问"
  },
  {
    "from": "gpt",
    "value": "模型的回复"
  }
]
```

### 对话示例

```json
[
  {
    "from": "human",
    "value": "我最近总是失眠"
  },
  {
    "from": "gpt",
    "value": "您的失眠问题需要重视。请问您失眠多长时间了？"
  },
  {
    "from": "human",
    "value": "大概有一个月了，特别影响第二天的工作"
  },
  {
    "from": "gpt",
    "value": "我理解您的困扰。除了失眠，您还有其他症状吗？"
  },
  {
    "from": "human",
    "value": "有时候会头晕，而且很容易焦虑"
  },
  {
    "from": "gpt",
    "value": "让我了解一下您的日常作息情况..."
  }
]
```

---

## 🚀 使用指南

### 步骤 1：生成对话

```bash
# 基本用法
python IBench/scripts/generate_conversations.py \
    --models Qwen3-8B \
    --prompts "我最近总是失眠" \
    --max-turns 3

# 完整用法
python IBench/scripts/generate_conversations.py \
    --models Qwen3-8B qwen3_full_sft \
    --prompts "我最近总是失眠" "我头疼持续三天" "我最近胸闷" \
    --max-turns 3 \
    --output-dir ./IBench/data/conversations
```

**参数说明**：
- `--models`: 要生成对话的模型列表
- `--prompts`: 初始用户问题列表
- `--max-turns`: 每个对话的轮次
- `--output-dir`: 输出目录

**输出**：
```
IBench/data/conversations/
├── Qwen3-8B/
│   ├── conv_1.json    # ShareGPT 格式
│   ├── conv_2.json
│   └── ...
├── qwen3_full_sft/
│   ├── conv_1.json
│   ├── conv_2.json
│   └── ...
└── generation_summary.json
```

### 步骤 2：评估对话

```bash
# 基本用法
python IBench/scripts/evaluate_conversations.py \
    --input IBench/data/conversations \
    --mode INTERACTIVE \
    --api-key $DASHSCOPE_API_KEY

# 指定输出目录
python IBench/scripts/evaluate_conversations.py \
    --input IBench/data/conversations \
    --mode INTERACTIVE \
    --api-key $DASHSCOPE_API_KEY \
    --output-dir ./IBench/data/evaluation_results
```

**参数说明**：
- `--input`: 对话文件目录（`generate_conversations.py` 的输出）
- `--mode`: 评估模式（CONTEXT 或 INTERACTIVE）
- `--api-key`: Judge 模型的 API key
- `--output-dir`: 评估结果输出目录

**输出**：
```
IBench/data/conversations/evaluation_results/
├── evaluation_summary.json    # 汇总信息
└── detailed_results/           # 详细评估结果
```

---

## 📊 评估结果示例

### evaluation_summary.json

```json
{
  "timestamp": "2025-02-03T10:30:00",
  "mode": "INTERACTIVE",
  "conversations_dir": "./IBench/data/conversations",
  "output_dir": "./IBench/data/conversations/evaluation_results",
  "judge_model": "qwen-max",
  "models": {
    "Qwen3-8B": [
      {
        "conversation_id": "conv_1",
        "final_score": -2,
        "total_turns": 3
      },
      {
        "conversation_id": "conv_2",
        "final_score": -1,
        "total_turns": 3
      }
    ],
    "qwen3_full_sft": [
      {
        "conversation_id": "conv_1",
        "final_score": -1,
        "total_turns": 3
      }
    ]
  },
  "total_evaluated": 3,
  "overall_stats": {
    "average_score": -1.33,
    "min_score": -2,
    "max_score": -1
  }
}
```

---

## 🎯 使用场景

### 场景 1：开发测试（在线评估）

```bash
# 快速测试，不需要保存对话
python IBench/scripts/compare_models.py \
    --models Qwen3-8B \
    --prompts "我最近总是失眠" \
    --api-key $DASHSCOPE_API_KEY
```

### 场景 2：生产评估（离线评估）

```bash
# 步骤 1：批量生成对话
python IBench/scripts/generate_conversations.py \
    --models Qwen3-8B qwen3_full_sft \
    --prompts "问题1" "问题2" "问题3" \
    --max-turns 3

# 步骤 2：检查对话质量
# 查看 IBench/data/conversations/Qwen3-8B/conv_1.json

# 步骤 3：统一评估
python IBench/scripts/evaluate_conversations.py \
    --input IBench/data/conversations \
    --mode INTERACTIVE \
    --api-key $DASHSCOPE_API_KEY
```

### 场景 3：调整规则重新评估

```bash
# 已有对话文件，不需要重新生成
# 直接用不同的模式重新评估
python IBench/scripts/evaluate_conversations.py \
    --input IBench/data/conversations \
    --mode CONTEXT \
    --api-key $DASHSCOPE_API_KEY \
    --output-dir ./IBench/data/results_context_mode
```

---

## ✨ 优势

### 离线评估模式的优势

1. ✅ **对话可复用**
   - 一次生成，多次评估
   - 调整规则后无需重新生成

2. ✅ **成本优化**
   - 可以批量评估，降低 API 调用成本
   - 对话生成和评估可以分阶段进行

3. ✅ **质量控制**
   - 先检查对话质量
   - 过滤低质量对话后再评估

4. ✅ **灵活性**
   - 可以对比不同评估模式
   - 可以对比不同 Judge 模型

5. ✅ **可追溯性**
   - 对话文件完整保存
   - 可以重新审视评估结果

---

## 📝 总结

| 功能 | 在线评估 | 离线评估 |
|------|----------|----------|
| **对话保存** | ❌ | ✅ ShareGPT 格式 |
| **可重复评估** | ❌ | ✅ |
| **成本优化** | ❌ | ✅ |
| **灵活性** | ❌ | ✅ |
| **适用场景** | 快速测试 | 生产评估 |

**推荐使用**：
- 开发测试 → 在线评估（compare_models.py）
- 生产评估 → 离线评估（generate + evaluate）

---

**系统已就绪！现在可以选择使用在线或离线评估模式了！** 🎉
