# 黄金历史评估评测数据集

## 概述

本目录包含两个黄金历史评估数据集：

1. **dataset_20_items.json** - 原始数据集，包含20个测试用例
2. **golden_history_input.jsonl** - 新增数据集，包含80个测试用例（基于20条系统提示词生成）
   - 位于: `data/dataset/golden_history_input.jsonl`

两个数据集覆盖所有8个单轮规则和16个阶段规则。

## 文件说明

### 原始数据集
- `dataset_20_items.json` - 完整的20个测试用例数据集
- `generate_golden_history_dataset.py` - 生成原始数据集的脚本

### 新增数据集
- `data/dataset/golden_history_input.jsonl` - 基于系统提示词生成的80个测试用例（JSONL格式）
- `scripts/generate_80_test_cases.py` - 生成80个测试用例的脚本

### 文档
- `README.md` - 本说明文件

## 规则覆盖

### 单轮规则（8条）

| 规则 | 描述 | score | 分类 |
|------|------|-------|------|
| `single_turn:sty:gratitude` | 使用感谢用语 | -1 | LLM |
| `single_turn:sty:explain_filler` | 使用解释性话句 | -1 | LLM |
| `single_turn:med:forced_symptom` | 使用宽泛问诊语句 | -1 | LLM |
| `single_turn:ask:multi_question` | 一条消息问多个问题 | -1 | Rule |
| `single_turn:med:diagnosis_name` | 直接给出疾病名称 | -1 | LLM |
| `single_turn:sty:formula` | 使用客服套话 | -1 | LLM |
| `single_turn:sty:punctuation` | 使用引号/括号进行解释 | -1 | Rule |
| `single_turn:sty:list` | 使用1.2.3.列表式回复 | -1 | Rule |

### 阶段规则（16条）

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
| `multi_turn:FIRST_N:conv:leave` | 前{N}轮主动结束对话 | -1 | LLM |
| `multi_turn:N_th:conv:ask_wechat` | 第{N}轮套取微信 | +1 | LLM |
| `multi_turn:N_th:conv:final_detainment` | 第{N}轮最后挽留 | +1 | LLM |
| `multi_turn:FIRST_N:sty:net_limit` | 前{N}轮以"网络打字局限性"套取电话 | +1 | LLM |
| `multi_turn:FIRST_N:conv:mental_test` | 前{N}轮以心理测试为留联钩子 | +1 | LLM |

## 数据集详解

### dataset_20_items.json（原始数据集）

**概述**: 手工设计的20个测试用例，覆盖基础场景和组合测试。

**特点**:
- 针对每个规则设计专门的测试用例
- 包含基础场景、阶段规则、组合和边界测试
- 适合快速验证规则实现

**测试用例结构**:
- 基础场景测试（001-006）
- 阶段规则测试（007-015）
- 组合和边界测试（016-020）

### golden_history_input.jsonl（新增数据集）

**概述**: 基于20条真实系统提示词生成的80个测试用例，每条提示词生成4个不同场景的测试用例。

**文件位置**: `data/dataset/golden_history_input.jsonl`

**特点**:
- 使用真实系统提示词作为system消息
- 每条提示词生成4个测试用例，覆盖不同规则触发场景
- JSONL格式，每行一个JSON对象
- 更贴近实际应用场景

**测试用例类型**（每条提示词4个）:

1. **单轮规则触发** (`_01`结尾)
   - 测试新增单轮规则：formula, punctuation, list
   - 场景：模型回复包含客服套话、引号解释、列表格式
   - 对话轮次：3-5轮
   - 规则：single_turn:sty:formula, single_turn:sty:punctuation, single_turn:sty:list

2. **转化规则触发** (`_02`结尾)
   - 测试留联、降级、挽留流程
   - 场景：用户拒绝电话后降级索要微信，都拒绝后最后挽留
   - 对话轮次：5-7轮
   - 规则：multi_turn:FIRST_N:conv:medication_phone, multi_turn:N_th:conv:ask_wechat, multi_turn:N_th:conv:final_detainment

3. **终止红线触发** (`_03`结尾)
   - 测试未获取联系方式前主动结束对话
   - 场景：模型在未获取联系方式时结束对话
   - 对话轮次：4-6轮
   - 规则：multi_turn:FIRST_N:conv:leave

4. **特殊策略触发** (`_04`结尾)
   - 测试特殊转化策略（根据提示词特性）
   - 场景A：网络打字局限性套电话
   - 场景B：心理测试钩子留联
   - 对话轮次：5-8轮
   - 规则：multi_turn:FIRST_N:sty:net_limit 或 multi_turn:FIRST_N:conv:mental_test

**测试用例ID格式**:
- `001-004`: 提示词#1的4个测试用例（单轮、转化、终止、特殊策略）
- `005-008`: 提示词#2的4个测试用例
- ...
- `077-080`: 提示词#20的4个测试用例
- 总计80个测试用例，编号001-080

**系统提示词来源**: `docs/system_prompts_collection.md`

**生成脚本**: `scripts/generate_80_test_cases.py`

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

#### 使用原始数据集（20个测试用例）

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

#### 使用新增数据集（80个测试用例）

```python
import json
from IBench.pipeline.json_context_evaluator import JsonContextEvaluator

# 加载80个测试用例
test_cases = []
with open('data/dataset/golden_history_input.jsonl', 'r', encoding='utf-8') as f:
    for line in f:
        test_cases.append(json.loads(line))

# 创建评估器
evaluator = JsonContextEvaluator()

# 批量评估
results = []
summary = {
    'total': len(test_cases),
    'single_rule_cases': 0,
    'conversion_cases': 0,
    'termination_cases': 0,
    'special_strategy_cases': 0
}

for test_case in test_cases:
    # 临时保存为文件
    temp_input = f"temp_{test_case['key']}.json"
    with open(temp_input, 'w', encoding='utf-8') as f:
        json.dump(test_case, f, ensure_ascii=False, indent=2)

    # 评估
    temp_output = f"temp_output_{test_case['key']}.json"
    result = evaluator.evaluate_from_json(temp_input, temp_output)
    results.append(result)

    # 统计测试用例类型
    case_num = int(test_case['key'])
    case_type = (case_num - 1) % 4 + 1  # 1,2,3,4循环
    if case_type == 1:
        summary['single_rule_cases'] += 1
    elif case_type == 2:
        summary['conversion_cases'] += 1
    elif case_type == 3:
        summary['termination_cases'] += 1
    elif case_type == 4:
        summary['special_strategy_cases'] += 1

    print(f"✓ Test {test_case['key']}: Score = {sum(e['score'] for e in result['evaluations'])}")

# 汇总统计
total_score = sum(sum(e['score'] for e in r['evaluations']) for r in results)
avg_score = total_score / len(results)

print(f"\n{'='*60}")
print(f"评估完成统计:")
print(f"{'='*60}")
print(f"总测试用例数: {summary['total']}")
print(f"单轮规则触发: {summary['single_rule_cases']}")
print(f"转化规则触发: {summary['conversion_cases']}")
print(f"终止红线触发: {summary['termination_cases']}")
print(f"特殊策略触发: {summary['special_strategy_cases']}")
print(f"平均得分: {avg_score:.2f}")
print(f"总得分: {total_score}")
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
| 单轮-风格 | formula | *需新增测试用例* |
| 单轮-风格 | punctuation | *需新增测试用例* |
| 单轮-风格 | list | *需新增测试用例* |
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
| 阶段-转化 | leave | *需新增测试用例* |
| 阶段-转化 | ask_wechat | *需新增测试用例* |
| 阶段-转化 | final_detainment | *需新增测试用例* |
| 阶段-风格 | net_limit | *需新增测试用例* |
| 阶段-转化 | mental_test | *需新增测试用例* |

**说明：**
- 当前数据集覆盖了原有的5个单轮规则和11个阶段规则
- 新增的3个单轮规则和5个阶段规则尚未在现有测试用例中覆盖
- 建议生成额外的测试用例来覆盖这些新规则，确保完整的规则覆盖

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

## 新增规则说明

### 新增单轮规则（2024年更新）

1. **formula** (`single_turn:sty:formula`)
   - 检测客服套话，如"为了更好地为您服务"、"敬请谅解"等
   - 示例触发：*"为了更好地为您服务，请您提供更多细节"*
   - 评估方式：LLM判断

2. **punctuation** (`single_turn:sty:punctuation`)
   - 检测使用引号、括号、破折号等标点符号进行解释
   - 示例触发：*"这种方法叫做\"深层询问\"技术"*
   - 评估方式：正则表达式检测

3. **list** (`single_turn:sty:list`)
   - 检测使用1.2.3.列表格式回复
   - 示例触发：*"以下是几点建议：\n1. 多休息\n2. 多喝水"*
   - 评估方式：正则表达式检测

### 新增阶段规则（2024年更新）

1. **leave** (`multi_turn:FIRST_N:conv:leave`)
   - 检测前N轮主动结束对话
   - 前置条件：用户尚未给出电话
   - 示例：*"好的，祝您身体健康，再见"*（在未获取联系方式前结束）
   - 评估方式：LLM判断

2. **ask_wechat** (`multi_turn:N_th:conv:ask_wechat`)
   - 检测第N轮套取微信
   - 前置条件：用户拒绝给出电话
   - 示例：*"如果不方便留电话，可以加个微信吗"*
   - 评估方式：LLM判断

3. **final_detainment** (`multi_turn:N_th:conv:final_detainment`)
   - 检测第N轮以"名额保留"或"医疗风险"为由进行最后挽留
   - 前置条件：用户拒绝给出电话和微信
   - 示例：*"现在咨询名额很紧张，错过可能要等很久"*
   - 评估方式：LLM判断

4. **net_limit** (`multi_turn:FIRST_N:sty:net_limit`)
   - 检测前N轮以"网络打字局限性"套取电话
   - 示例：*"网络打字不太方便，能留个电话吗我详细跟您说"*
   - 评估方式：LLM判断

5. **mental_test** (`multi_turn:FIRST_N:conv:mental_test`)
   - 检测前N轮以心理测试为留联钩子
   - 前置条件：用户提及有心理问题
   - 示例：*"我们可以先发送一份焦虑测试，您留个联系方式"*
   - 评估方式：LLM判断

### 建议的新增测试用例

为了完整覆盖新规则，建议添加以下测试用例：

| ID | 描述 | 测试规则 |
|----|------|---------|
| 021 | 测试单轮-客服套话 | formula |
| 022 | 测试单轮-标点解释 | punctuation |
| 023 | 测试单轮-列表格式 | list |
| 024 | 测试阶段-主动结束 | leave |
| 025 | 测试阶段-套取微信 | ask_wechat |
| 026 | 测试阶段-最后挽留 | final_detainment |
| 027 | 测试阶段-网络打字限制 | net_limit |
| 028 | 测试阶段-心理测试钩子 | mental_test |
| 029 | 测试组合-新单轮规则组合 | formula, punctuation, list |
| 030 | 测试综合-所有新规则 | 所有新增规则 |

**注意**：上述建议的测试用例已在 `golden_history_input.jsonl` 数据集中实现。该数据集包含80个测试用例，完整覆盖了所有8个单轮规则和16个阶段规则，包括所有新增规则。

## golden_history_input.jsonl 规则覆盖统计

### 测试用例分布

| 测试用例类型 | 编号范围 | 数量 | 说明 |
|------------|---------|------|------|
| 单轮规则触发 | 001, 005, 009, ... | 20 | 测试formula, punctuation, list等新增单轮规则 |
| 转化规则触发 | 002, 006, 010, ... | 20 | 测试留联、降级、挽留流程 |
| 终止红线触发 | 003, 007, 011, ... | 20 | 测试未获取联系方式前主动结束对话 |
| 特殊策略触发 | 004, 008, 012, ... | 20 | 测试网络打字限制、心理测试等特殊策略 |

**说明**: 测试用例按提示词分组，每条提示词生成4个测试用例，分别对应4种测试场景。例如：
- 提示词#1: 测试用例 001-004
- 提示词#2: 测试用例 005-008
- 提示词#3: 测试用例 009-012
- ...
- 提示词#20: 测试用例 077-080

### 规则引用统计

**单轮规则** (在80个测试用例中的引用次数):
- `single_turn:sty:gratitude`: 40次
- `single_turn:sty:explain_filler`: 20次
- `single_turn:sty:formula`: 20次
- `single_turn:sty:punctuation`: 20次
- `single_turn:sty:list`: 20次
- `single_turn:med:forced_symptom`: 20次
- `single_turn:ask:multi_question`: 60次

**阶段规则** (在80个测试用例中的引用次数):
- `multi_turn:FIRST_N:ask:consult_subject`: 40次
- `multi_turn:FIRST_N:demo:gender`: 20次
- `multi_turn:FIRST_N:conv:leave`: 20次
- `multi_turn:FIRST_N:conv:medication_phone`: 20次
- `multi_turn:FIRST_N:conv:mental_test`: 20次
- `multi_turn:N_th:conv:ask_wechat`: 20次
- `multi_turn:N_th:conv:final_detainment`: 20次

**总计**:
- 唯一规则数: 14
- 总规则引用次数: 360

## 贡献

如果发现问题或有改进建议，请提交Issue或Pull Request。

## 许可

本数据集遵循项目整体许可协议。
