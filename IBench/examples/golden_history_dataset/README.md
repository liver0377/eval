# 黄金历史评估评测数据集

## 概述

本数据集包含**20个测试用例**，用于黄金历史评估，覆盖所有5个单轮规则和11个阶段规则。

## 文件说明

- `dataset_20_items.json` - 完整的20个测试用例数据集
- `generate_golden_history_dataset.py` - 生成数据集的脚本
- `README.md` - 本说明文件

## 规则覆盖

### 单轮规则（5条）

| 规则 | 描述 | score | 分类 |
|------|------|-------|------|
| `single_turn:sty:gratitude` | 使用感谢用语 | -1 | LLM |
| `single_turn:sty:explain_filler` | 使用解释性话句 | -1 | LLM |
| `single_turn:med:forced_symptom` | 使用宽泛问诊语句 | -1 | LLM |
| `single_turn:ask:multi_question` | 一条消息问多个问题 | -1 | Rule |
| `single_turn:med:diagnosis_name` | 直接给出疾病名称 | -1 | LLM |

### 阶段规则（11条）

| 规则 | 描述 | score | 分类 |
|------|------|-------|------|
| `multi_turn:FIRST_N:ask:consult_subject` | 询问咨询对象 | +1 | LLM |
| `multi_turn:FIRST_N:med:visit_history` | 提及就诊史 | -1 | LLM |
| `multi_turn:FIRST_N:med:test_invite` | 提出检查邀约 | -1 | LLM |
| `multi_turn:FIRST_N:demo:gender` | 询问性别 | +1 | Rule |
| `multi_turn:FIRST_N:conv:medication_phone` | 用药套取电话 | +1 | LLM |
| `multi_turn:FIRST_N:conv:complication_phone` | 并发症套取电话 | +1 | LLM |
| `multi_turn:FIRST_N:conv:expert_phone` | 专家解读套取电话 | +1 | LLM |
| `multi_turn:FIRST_N:scope:primary_only` | 仅围绕主要病症 | +1 | LLM |
| `multi_turn:FIRST_N:ask:prompt_question` | 给出引导 | +1 | LLM |
| `multi_turn:FIRST_N:conv:report_phone` | 报告套取电话 | +1 | LLM |
| `multi_turn:FIRST_N:conv:advice_phone` | 用药建议套取电话 | +1 | LLM |

## 测试用例列表

### 基础场景测试（001-006）

| ID | 描述 | 测试规则 |
|----|------|---------|
| 001 | 基础场景 - 咨询对象和性别询问 | consult_subject, gender |
| 002 | 测试单轮-感谢用语 | gratitude |
| 003 | 测试单轮-解释性话句 | explain_filler |
| 004 | 测试单轮-宽泛问诊语句 | forced_symptom |
| 005 | 测试单轮-多个问题 | multi_question |
| 006 | 测试单轮-疾病名称 | diagnosis_name |

### 阶段规则测试（007-015）

| ID | 描述 | 测试规则 |
|----|------|---------|
| 007 | 测试阶段-提及就诊史 | visit_history |
| 008 | 测试阶段-检查邀约 | test_invite |
| 009 | 测试阶段-用药套电话 | medication_phone |
| 010 | 测试阶段-并发症套电话 | complication_phone |
| 011 | 测试阶段-专家解读套电话 | expert_phone |
| 012 | 测试阶段-仅围绕主要病症 | primary_only |
| 013 | 测试阶段-给出引导 | prompt_question |
| 014 | 测试阶段-报告套电话 | report_phone |
| 015 | 测试阶段-用药建议套电话 | advice_phone |

### 组合和边界测试（016-020）

| ID | 描述 | 测试规则 |
|----|------|---------|
| 016 | 测试组合-多个单轮规则 | gratitude, explain_filler, diagnosis_name |
| 017 | 测试组合-前N轮多个阶段规则 | consult_subject, gender, prompt_question |
| 018 | 测试边界-最后一轮触发规则 | primary_only, medication_phone |
| 019 | 测试否定-不触发规则（正确行为） | gratitude, multi_question |
| 020 | 测试综合-所有单轮+多个阶段规则 | 所有单轮规则 + 部分阶段规则 |

## 使用方法

### 方法1：使用单个测试用例

```python
import json
from IBench.pipeline.json_context_evaluator import JsonContextEvaluator

# 加载单个测试用例
with open('test_001.json', 'r', encoding='utf-8') as f:
    test_case = json.load(f)

# 创建评估器
evaluator = JsonContextEvaluator()

# 评估
result = evaluator.evaluate_from_json(
    input_json_path='test_001.json',
    output_json_path='output_001.json'
)

print(f"Generated Response: {result['generated_response']}")
print(f"Total Score: {sum(e['score'] for e in result['evaluations'])}")
```

### 方法2：批量评估整个数据集

```python
import json
from IBench.pipeline.json_context_evaluator import JsonContextEvaluator

# 加载数据集
with open('dataset_20_items.json', 'r', encoding='utf-8') as f:
    dataset = json.load(f)

# 创建评估器
evaluator = JsonContextEvaluator()

# 批量评估
results = []
for test_case in dataset['test_cases']:
    # 临时保存为文件
    temp_input = f"temp_{test_case['key']}.json"
    with open(temp_input, 'w', encoding='utf-8') as f:
        json.dump(test_case, f, ensure_ascii=False, indent=2)
    
    # 评估
    temp_output = f"temp_output_{test_case['key']}.json"
    result = evaluator.evaluate_from_json(temp_input, temp_output)
    results.append(result)
    print(f"✓ Test {test_case['key']}: Score = {sum(e['score'] for e in result['evaluations'])}")

# 汇总统计
total_score = sum(sum(e['score'] for e in r['evaluations']) for r in results)
avg_score = total_score / len(results)
print(f"\nAverage Score: {avg_score:.2f}")
```

### 方法3：使用Python脚本

```python
# 直接使用测试用例字典
test_case = {
    "key": "001",
    "messages": [
        {"role": "system", "content": "...", "turn_id": 0},
        {"role": "user", "content": "...", "turn_id": 1},
        # ...
    ],
    "rule_list": [
        "single_turn:sty:gratitude",
        # ...
    ]
}

# 评估器可以直接处理字典
from IBench.pipeline.json_context_evaluator import JsonContextEvaluator
evaluator = JsonContextEvaluator()
result = evaluator.evaluate_single_case(test_case)
```

## 数据格式

### 输入格式

```json
{
  "key": "001",
  "messages": [
    {
      "role": "system",
      "content": "系统提示词",
      "turn_id": 0
    },
    {
      "role": "user",
      "content": "用户消息",
      "turn_id": 1
    }
  ],
  "rule_list": [
    "single_turn:sty:gratitude",
    {"rule": "multi_turn:FIRST_N:ask:consult_subject", "N": 3}
  ]
}
```

### 输出格式

```json
{
  "key": "001",
  "generated_response": "模型生成的回复",
  "evaluations": [
    {
      "rule": "single_turn:sty:gratitude",
      "triggered": true,
      "score": -1,
      "kwargs": {"phrase": "感谢"},
      "reason": "使用了感谢用语"
    }
  ],
  "kwargs": [
    {"phrase": "感谢"}
  ]
}
```

## 规则覆盖矩阵

| 规则类别 | 规则名称 | 覆盖测试用例ID |
|---------|---------|---------------|
| 单轮-风格 | gratitude | 001, 002, 016, 019, 020 |
| 单轮-风格 | explain_filler | 001, 003, 016, 020 |
| 单轮-医疗 | forced_symptom | 001, 004, 020 |
| 单轮-提问 | multi_question | 001, 005, 019, 020 |
| 单轮-医疗 | diagnosis_name | 001, 006, 016 |
| 阶段-提问 | consult_subject | 001, 017, 020 |
| 阶段-医疗 | visit_history | 007, 020 |
| 阶段-医疗 | test_invite | 008 |
| 阶段-人口 | gender | 001, 017, 020 |
| 阶段-转化 | medication_phone | 009, 018 |
| 阶段-转化 | complication_phone | 010 |
| 阶段-转化 | expert_phone | 011 |
| 阶段-范围 | primary_only | 012, 018 |
| 阶段-提问 | prompt_question | 013, 017 |
| 阶段-转化 | report_phone | 014 |
| 阶段-转化 | advice_phone | 015 |

## 注意事项

1. **最后一条消息必须是user消息**：黄金历史评估会生成最后一条assistant回复
2. **turn_id从0开始**：system消息使用turn_id=0，后续对话按轮次递增
3. **规则格式支持两种**：
   - 字符串格式：`"single_turn:sty:gratitude"`
   - 对象格式：`{"rule": "multi_turn:FIRST_N:ask:consult_subject", "N": 3}`
4. **N参数含义**：
   - 对于`FIRST_N`规则：前N轮都需要评估
   - 对于`N_th`规则：只在第N轮评估

## 扩展数据集

如需生成更多测试用例，可以运行：

```bash
python scripts/generate_golden_history_dataset.py
```

这将生成20个独立的JSON文件，每个文件包含一个测试用例。

## 贡献

如果发现问题或有改进建议，请提交Issue或Pull Request。

## 许可

本数据集遵循项目整体许可协议。
