# IBench 项目结构

## 目录结构

```
IBench/
├── conversation/          # 对话管理模块
├── data/                  # 数据目录
│   ├── output/           # 评估输出结果
│   └── dataset/          # 数据集
│       └── golden_history_input.jsonl  # 80个测试用例
├── deprecated/           # 已弃用的代码
├── docs/                 # 文档目录
│   ├── 评估Bench.md      # 规则说明文档
│   └── system_prompts_collection.md  # 系统提示词集合
├── evaluator/            # 评估器模块
│   ├── batch_evaluator.py
│   └── rule_evaluator.py
├── examples/             # 示例和数据集
│   ├── datasets/         # 示例数据集文件
│   ├── golden_history_dataset/  # 黄金历史数据集
│   │   └── dataset_20_items.json      # 20个测试用例
│   └── usage/           # 使用示例
│       ├── json_evaluator_example.py
│       └── system_prompt_example.py
├── models/              # 模型相关
│   ├── api_model.py
│   ├── local_model.py
│   └── model_configs.py
├── pipeline/            # 评估流程
│   ├── dynamic_interactive_eval.py
│   └── json_context_evaluator.py
├── rules/               # 规则定义
│   ├── dynamic_rule_registry.py
│   ├── kwargs_extractor.py
│   ├── rule_mappings.py
│   ├── single_rules.py
│   └── stage_rules.py
├── scripts/             # 工具脚本
│   ├── batch_evaluate_golden_history.py  # 批量评估
│   ├── generate_80_test_cases.py         # 生成测试用例
│   └── generate_golden_history_dataset.py # 生成数据集
├── test/                # 测试目录
│   ├── check_migration.py          # 迁移检查
│   ├── quick_test.py              # 快速测试
│   ├── test_dynamic_eval.py       # 动态评估测试
│   ├── test_model_loading.py      # 模型加载测试
│   └── test_rule_names.py         # 规则名称测试
├── utils/               # 工具函数
│   ├── common.py
│   └── imports.py
├── config.py            # 配置文件
├── __init__.py          # 包初始化
└── pyproject.toml       # 项目配置
```

## 模块说明

### 核心模块

- **rules/**: 规则定义和评估
  - `single_rules.py`: 单轮规则（8条）
  - `stage_rules.py`: 阶段规则（16条）
  - `rule_mappings.py`: 规则映射配置
  - `dynamic_rule_registry.py`: 动态规则注册

- **evaluator/**: 评估器
  - `rule_evaluator.py`: 规则评估器
  - `batch_evaluator.py`: 批量评估器

- **pipeline/**: 评估流程
  - `json_context_evaluator.py`: JSON上下文评估
  - `dynamic_interactive_eval.py`: 动态交互评估

- **models/**: 模型接口
  - `api_model.py`: API模型
  - `local_model.py`: 本地模型

### 数据和示例

- **examples/datasets/**: 示例数据集文件
- **examples/golden_history_dataset/**: 黄金历史评估数据集
  - 80个测试用例（基于20条系统提示词生成）
  - 20个测试用例（手工设计）
- **examples/usage/**: 使用示例代码

### 测试

- **test/**: 所有测试脚本
  - 规则测试
  - 模型测试
  - 迁移检查

### 工具脚本

- **scripts/**: 数据生成和批量处理
  - `generate_80_test_cases.py`: 生成80个测试用例
  - `generate_golden_history_dataset.py`: 生成黄金历史数据集
  - `batch_evaluate_golden_history.py`: 批量评估

### 文档

- **docs/**: 项目文档
  - `评估Bench.md`: 完整的规则集说明
  - `system_prompts_collection.md`: 20条系统提示词

## 重构说明

### 删除的文件

**scripts目录下已删除的脚本**:
- 清理系统提示词的多个版本脚本（保留统一处理方式）
- 提取系统提示词的多个版本脚本
- 不常用的工具脚本

### 移动的文件

**移动到test/**:
- `scripts/test_dynamic_eval.py` → `test/test_dynamic_eval.py`
- `scripts/test_model_loading.py` → `test/test_model_loading.py`
- `scripts/quick_test.py` → `test/quick_test.py`
- `examples/test_rule_names.py` → `test/test_rule_names.py`
- `examples/check_migration.py` → `test/check_migration.py`
- `test_quickstart.py` → `test/test_quickstart.py`

**examples目录重组**:
- JSON文件 → `examples/datasets/`
- 示例代码 → `examples/usage/`

## 快速开始

### 运行测试

```bash
# 运行所有测试
python -m pytest test/

# 运行特定测试
python test/test_rule_names.py
python test/quick_test.py
```

### 生成数据集

```bash
# 生成80个测试用例
python scripts/generate_80_test_cases.py

# 生成黄金历史数据集
python scripts/generate_golden_history_dataset.py
```

### 批量评估

```bash
# 批量评估数据集
python scripts/batch_evaluate_golden_history.py
```

## 规则覆盖

当前版本支持：
- 8个单轮规则
- 16个阶段规则

详细规则说明请参考 `docs/评估Bench.md`。
