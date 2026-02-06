# 黄金历史评估脚本使用说明

## 📝 脚本功能

`scripts/evaluate_golden_history.py` 用于批量评估黄金历史评测数据集（JSONL格式）

## 🚀 使用方法

### 基本用法

```bash
# 使用默认模型（Qwen3-8B）
python scripts/evaluate_golden_history.py

# 指定模型
python scripts/evaluate_golden_history.py --model qwen3_full_sft
```

### 命令行参数

| 参数 | 短选项 | 类型 | 默认值 | 说明 |
|------|--------|------|--------|------|
| `--model` | `-m` | string | Qwen3-8B | 指定使用的模型 |
| `--api-key` | `-k` | string | 环境变量 | API密钥 |
| `--output-dir` | `-o` | string | data/output/golden_history_eval | 输出目录 |
| `--workers` | `-w` | int | 5 | 并发线程数 |
| `--list-models` | - | flag | - | 列出所有可用模型 |

### 可用模型

| 模型名称 | 说明 |
|----------|------|
| `Qwen3-8B` | 基础 Qwen3-8B 模型（8B参数） |
| `qwen3_full_sft` | Qwen3-8B SFT 微调版本 |
| `llama_factory_psy1.32.1_lora_qwen2_7b_dpo` | Qwen2-7B + LoRA + DPO |

### 完整示例

```bash
# 查看所有可用模型
python scripts/evaluate_golden_history.py --list-models

# 使用 SFT 模型，指定输出目录
python scripts/evaluate_golden_history.py \
    --model qwen3_full_sft \
    --output-dir data/output/sft_eval

# 使用 API key，减少并发数
python scripts/evaluate_golden_history.py \
    --model llama_factory_psy1.32.1_lora_qwen2_7b_dpo \
    --api-key your-api-key \
    --workers 3
```

## 📊 输出文件

评估完成后会在输出目录生成：

1. **golden_history_output.jsonl** - 每个测试案例的详细评估结果
2. **evaluation_summary.json** - 汇总统计信息

## 🔧 Bug 修复记录

### ✅ 修复1：Type Error in precondition check
**问题**：`'tuple' object has no attribute 'upper'`

**原因**：
- `llm_judge_func` 返回 `tuple[bool, str]`
- 代码尝试直接调用 `.upper()` 方法

**修复位置**：`rules/dynamic_rule_registry.py:314-321`

**修复代码**：
```python
# 修改前
response = llm_judge_func(user_message, prompt)
if response and "YES" in response.upper():
    return turn_id

# 修改后
result = llm_judge_func(user_message, prompt)
if result and isinstance(result, tuple) and len(result) >= 2:
    response_text = result[1]  # 获取字符串部分
    if "YES" in response_text.upper():
        return turn_id
```

### ✅ 修复2：添加命令行参数支持
**新增功能**：
1. `--model` 参数：指定使用的模型
2. `--api-key` 参数：覆盖环境变量中的 API key
3. `--output-dir` 参数：自定义输出目录
4. `--workers` 参数：控制并发线程数
5. `--list-models` 参数：列出所有可用模型

**修改文件**：`scripts/evaluate_golden_history.py`

## 📋 评估流程

1. 加载 JSONL 数据集
2. 初始化评估器（加载指定模型）
3. 使用线程池并发评估每个测试案例
4. 生成回复并评估规则
5. 汇总统计信息
6. 保存结果到 JSONL 文件

## ⚠️ 注意事项

1. **API Key**：
   - 优先使用 `--api-key` 参数
   - 其次使用环境变量 `DASHSCOPE_API_KEY`
   - 未设置时仍可运行（但 LLM judge 可能失败）

2. **并发数**：
   - 默认 5 个线程
   - 可根据服务器资源调整
   - 过高可能导致 OOM

3. **输出目录**：
   - 会自动创建
   - 每次运行会覆盖之前的输出
