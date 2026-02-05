# Deprecated Evaluators

本目录包含已废弃的评估器，请使用新的JSON评估方式。

## 废弃原因

这些评估器使用代码方式（函数参数）进行评估，已被更灵活的JSON方式替代。

## 废弃的评估器

### 1. ContextEvaluator (`context_eval.py`)
- **废弃原因**: 已被 `JsonContextEvaluator` 替代
- **新方式**: 使用JSON文件配置输入
- **迁移指南**: 
  ```python
  # 旧方式（代码方式）
  from IBench.pipeline.context_eval import ContextEvaluator
  evaluator = ContextEvaluator()
  result = evaluator.evaluate(conversation_history)
  
  # 新方式（JSON方式）
  from IBench.pipeline.json_context_evaluator import JsonContextEvaluator
  evaluator = JsonContextEvaluator()
  result = evaluator.evaluate_from_json("input.json", "output.json")
  ```

### 2. InteractiveEvaluator (`interactive_eval.py`)
- **废弃原因**: 已被 `DynamicInteractiveEvaluator` 替代
- **新方式**: 使用JSON文件配置输入
- **迁移指南**:
  ```python
  # 旧方式（代码方式）
  from IBench.pipeline.interactive_eval import InteractiveEvaluator
  evaluator = InteractiveEvaluator()
  result = evaluator.evaluate(initial_prompt)
  
  # 新方式（JSON方式）
  from IBench.pipeline.dynamic_interactive_eval import DynamicInteractiveEvaluator
  evaluator = DynamicInteractiveEvaluator()
  result = evaluator.evaluate_from_json("input.json", "output.json")
  ```

## 新的评估体系

### 黄金历史评估 (JsonContextEvaluator)
- **文件**: `pipeline/json_context_evaluator.py`
- **输入**: JSON文件，包含完整对话（最后一条是user消息）
- **输出**: 生成最后一条回复并评估
- **示例**: `examples/golden_history_input_example.json`

### 动态交互评估 (DynamicInteractiveEvaluator)
- **文件**: `pipeline/dynamic_interactive_eval.py`
- **输入**: JSON文件，包含完整对话（所有user和assistant消息）
- **输出**: 评估每一轮的回复
- **示例**: `examples/dynamic_interactive_input_example.json`

## 迁移建议

1. **对于现有代码方式用户**：
   - 创建对应的JSON输入文件
   - 使用新的JSON评估器
   - 参考示例文件了解格式

2. **对于新用户**：
   - 直接使用JSON评估器
   - 查看 `docs/评估体系说明.md` 了解详细文档

## 联系方式

如有疑问，请查阅项目文档或提交issue。
