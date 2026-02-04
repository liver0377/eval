# System Prompt 功能更新说明

## 更新日期
2026-02-04

## 新增功能

### 1. 系统提示词支持
- 在 `ModelConfig` 中新增 `system_prompt` 字段
- 支持通过系统提示词约束模型输出格式
- 自动在每次推理时注入系统提示词

### 2. 输出清理功能
- 自动去除 `<|file_separator|>` 标签及其后的思考内容
- 确保模型输出符合预期格式

### 3. 输出长度限制
- 将 `max_new_tokens` 默认值从 512 调整为 40
- 更好地控制回复长度

## 修改文件

### config.py
- 添加 `system_prompt: Optional[str] = None` 配置项
- 调整 `max_new_tokens: int = 40`

### models/local_model.py
- 添加 `_clean_response()` 静态方法，清理思考内容
- 修改 `_format_messages()` 方法，支持 system prompt
- 在 `generate()` 和 `check_precondition()` 方法中应用清理逻辑

## 使用方法

### 基础使用

```python
from IBench.config import ModelConfig
from IBench.models.local_model import LocalModel
from IBench.utils.common import Message

# 配置模型
model_config = ModelConfig(
    local_model_path="./models/qwen3-8b",
    system_prompt="""你是一个专业的医疗咨询助手。
    请严格遵守：
    1. 回复简洁，不超过40个字
    2. 不要输出思考过程
    3. 直接给出答案""",
    max_new_tokens=40
)

# 初始化模型
model = LocalModel(model_config)

# 生成回复
messages = [Message(role="user", content="我最近总是失眠", turn_id=1)]
response = model.generate(messages)
print(response)
```

### 系统提示词示例

#### 约束输出格式
```
你是一个客服助手。请遵循：
1. 回复不超过20个字
2. 使用礼貌用语
3. 不要输出思考过程或分析
4. 直接给出最终答案
```

#### 禁止特定内容
```
请直接回答用户问题，不要：
- 输出<|file_separator|>标记
- 展示推理过程
- 添加额外说明
```

## 清理逻辑说明

`_clean_response()` 方法会：
1. 查找 `<|file_separator|>` 标签
2. 删除该标签及其后的所有内容（直到 `\n\n` 或字符串结尾）
3. 返回清理后的文本

**示例**：
- 输入：`正常回复<|file_separator|>思考内容\n\n后续内容`
- 输出：`正常回复`

## 配置建议

### 医疗咨询场景
```python
system_prompt = """你是一个专业的医疗咨询助手。
1. 回复简洁明了（40字以内）
2. 不要输出思考过程
3. 直接给出专业建议"""
```

### 客服场景
```python
system_prompt = """你是一个客服助手。
1. 回复简短（20字以内）
2. 使用礼貌用语
3. 只回答问题，不主动提供额外信息"""
```

### 评估场景
```python
system_prompt = """你是一个客观的评估者。
1. 只输出评估结果（VIOLATED/NOT_VIOLATED）
2. 不要输出分析过程
3. 保持客观公正"""
```

## 注意事项

1. **系统提示词优先级**：系统提示词会在对话消息之前注入
2. **清理是自动的**：所有输出都会自动清理，无需手动处理
3. **Token限制**：`max_new_tokens` 控制生成长度，建议与系统提示词配合使用
4. **兼容性**：支持 Qwen3 的 chat template

## 测试

运行示例代码：
```bash
python examples/system_prompt_example.py
```

## 问题排查

如果模型仍然输出思考内容：
1. 检查系统提示词是否正确配置
2. 确认 `system_prompt` 在 `ModelConfig` 中正确传入
3. 查看模型输出，验证清理逻辑是否生效
4. 调整系统提示词，使用更强的约束语言
