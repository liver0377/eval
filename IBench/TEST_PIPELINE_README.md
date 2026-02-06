# 黄金历史评估 Pipeline 测试脚本

## 📝 说明

这个测试脚本用于验证 IBench 的黄金历史评估（Golden History Evaluation）pipeline 是否正常工作。

## 🚀 快速开始

### 1. 无需 API key 的快速测试（Mock 模式）

```bash
python test_golden_history_pipeline.py
```

这将：
- 从 `golden_history_input.jsonl` 读取第一行作为测试数据
- 使用 Mock evaluator 进行测试（不调用真实 API）
- 验证 pipeline 的基本流程是否正常

### 2. 使用真实 API 进行完整测试

```bash
# 设置 API key（Linux/Mac）
export DASHSCOPE_API_KEY='your-api-key'

# 或者使用 OpenAI API
export OPENAI_API_KEY='your-api-key'

# 运行测试
python test_golden_history_pipeline.py
```

这将：
- 使用真实的 API 模型生成回复
- 使用真实的 Judge LLM 进行评估
- 输出完整的评估结果

## 📊 测试内容

测试脚本会验证以下功能：

1. ✅ **数据读取**：从 JSONL 文件读取测试数据
2. ✅ **评估器初始化**：初始化 JsonContextEvaluator
3. ✅ **回复生成**：使用模型生成最后一条回复
4. ✅ **规则评估**：评估所有规则（single_turn 和 multi_turn）
5. ✅ **{N} 替换**：验证 {N} 占位符是否正确替换
6. ✅ **结果输出**：保存评估结果到 JSON 文件

## 📁 输入输出

### 输入
- **测试数据**：`data/dataset/golden_history_input.jsonl`（第一行）
- **规则列表**：包含 single_turn 和 multi_turn 规则

### 输出
- **临时文件**：
  - `temp_test_input.json` - 临时输入文件
  - `temp_test_output.json` - 临时输出文件
- **控制台输出**：
  - 生成的回复
  - 每条规则的评估结果
  - 总得分

## 🔧 测试数据示例

从 `golden_history_input.jsonl` 读取的数据格式：

```json
{
  "key": "001",
  "messages": [
    {"role": "system", "content": "角色设定：..."},
    {"role": "user", "content": "孩子注意力不集中"},
    {"role": "assistant", "content": "请问孩子年龄？"},
    ...
    {"role": "user", "content": "那太好了，具体怎么操作？我想给他试试"}
  ],
  "rule_list": [
    "single_turn:sty:formula",
    {"rule": "single_turn:ask:multi_question", "N": 2},
    {"rule": "multi_turn:N_th:conv:ask_phone", "N": 8}
  ]
}
```

## 📋 预期输出

### Mock 模式输出
```
================================================================================
黄金历史评估 Pipeline 测试
================================================================================

📂 读取测试数据: data\dataset\golden_history_input.jsonl
✓ 成功读取测试数据: key=001
  - 消息数量: 17
  - 规则数量: 12

🔧 初始化评估器...
⚠️  警告：未找到 API key
   将使用 Mock 模式进行测试

📝 创建 Mock evaluator...
🚀 开始评估...
✓ 临时输入文件: ...temp_test_input.json
✓ 评估完成

📊 评估结果:
  - 生成的回复: 这是一个测试回复。请问您还有什么问题吗？...
  - 总得分: -6

  规则评估详情:
    ✗ 违规 | single_turn:sty:formula | 得分: -1 | Mock 评估结果 for single_turn:sty:formula
    ...

✅ 测试成功！Pipeline 运行正常
```

### 真实 API 模式输出
```
================================================================================
黄金历史评估 Pipeline 测试
================================================================================

📂 读取测试数据: ...
✓ 找到 API key: sk-xxx...
✓ 评估器初始化成功
🚀 开始评估...
✓ 评估完成

📊 评估结果:
  - 生成的回复: 好的，建议您带孩子到专业的儿童医院进行...
  - 总得分: 3

  规则评估详情:
    ✓ 通过 | single_turn:sty:formula | 得分: 1 | 未使用客服套话
    ✓ 通过 | single_turn:ask:multi_question | 得分: 1 | 问题数量符合阈值
    ...

✅ 测试成功！Pipeline 运行正常
```

## 🐛 故障排查

### 问题 1：找不到测试数据文件
```
❌ 错误：找不到测试数据文件: data/dataset/golden_history_input.jsonl
```

**解决方法**：确保从项目根目录运行脚本

### 问题 2：API key 未设置
```
⚠️  警告：未找到 API key
```

**解决方法**：
- 设置环境变量 `DASHSCOPE_API_KEY` 或 `OPENAI_API_KEY`
- 或使用 Mock 模式进行测试

### 问题 3：模型加载失败
```
❌ 初始化评估器失败: ...
```

**解决方法**：
- 检查依赖是否安装：`pip install -r requirements.txt`
- 检查配置文件：`models/model_configs.py`

## 🎯 下一步

测试通过后，你可以：

1. **批量评估**：使用 `evaluate_batch_from_json()` 评估多个测试案例
2. **自定义规则**：添加新的规则到规则注册表
3. **调整配置**：修改 `models/model_configs.py` 中的配置
4. **查看详细结果**：检查输出的 JSON 文件

## 📖 相关文档

- [评估体系说明](docs/评估体系说明.md)
- [规则文档](docs/评估Bench.md)
- [README](README.md)
