# JSON to JSONL Merger

将指定目录下的所有 JSON 文件合并成一个 JSONL 文件。

## JSONL 格式说明

JSONL（JSON Lines）是一种每行一个 JSON 对象的文件格式：

```json
{"key": "001", "messages": [...], "rule_list": [...]}
{"key": "002", "messages": [...], "rule_list": [...]}
{"key": "003", "messages": [...], "rule_list": [...]}
```

## 功能特性

- ✅ 按文件名字母序自动排序
- ✅ 验证 JSON 对象的必填字段
- ✅ 显示详细的合并信息
- ✅ 支持 verbose 模式查看详细信息
- ✅ 自动创建输出目录

## 使用方法

### 基本用法

```bash
python scripts/merge_json_to_jsonl.py <输入目录> <输出文件>
```

### 示例

#### 1. 合并 sub_real 目录

```bash
python scripts/merge_json_to_jsonl.py data/dataset/tmp/sub_real output.jsonl
```

#### 2. 合并到指定目录

```bash
python scripts/merge_json_to_jsonl.py data/dataset/tmp/sub_real data/output/merged.jsonl
```

#### 3. 使用详细模式（--verbose）

```bash
python scripts/merge_json_to_jsonl.py data/dataset/tmp/sub_real output.jsonl --verbose
```

#### 4. 跳过验证（--no-validate）

```bash
python scripts/merge_json_to_jsonl.py data/dataset/tmp/sub_real output.jsonl --no-validate
```

## 命令行参数

| 参数 | 说明 |
|------|------|
| `input_dir` | 输入目录路径（包含 JSON 文件） |
| `output_file` | 输出 JSONL 文件路径 |
| `--no-validate` | 跳过 JSON 对象验证 |
| `--verbose, -v` | 显示详细输出信息 |
| `--help, -h` | 显示帮助信息 |

## 输出示例

```
================================================================================
JSON to JSONL Merger
================================================================================
Input directory: data/dataset/tmp/sub_real
Output file: output.jsonl
================================================================================
Found 11 JSON files in data/dataset/tmp/sub_real
  Loaded: ask_phone.json
  Loaded: ask_wechat.json
  Loaded: complication_phone.json
  ...

Validating JSON objects...
  All objects are valid!

Writing JSONL file...

Successfully wrote 11 records to output.jsonl

================================================================================
SUMMARY
================================================================================
Total objects merged: 11
Input directory: data/dataset/tmp/sub_real
Output file: output.jsonl
File size: 25879 bytes
================================================================================
```

## JSON 对象验证

默认情况下，脚本会验证每个 JSON 对象包含以下必填字段：

- `key`: 对象的唯一标识符
- `messages`: 消息列表（非空）
- `rule_list`: 规则列表

如果验证失败，脚本会报错并退出。可以使用 `--no-validate` 跳过验证。

## 注意事项

1. **文件排序**: JSON 文件按文件名字母序排序后合并
2. **文件扩展名**: 只处理 `.json` 扩展名的文件
3. **编码格式**: 输入和输出文件都使用 UTF-8 编码
4. **目录创建**: 如果输出目录不存在，会自动创建

## 常见问题

### Q: 如何验证生成的 JSONL 文件？

```bash
# 查看文件行数（每个 JSON 对象一行）
wc -l output.jsonl

# 查看前几行
head -n 3 output.jsonl | python -m json.tool

# 提取所有 key
cat output.jsonl | python -c "import sys, json; print([json.loads(line)['key'] for line in sys.stdin])"
```

### Q: JSONL 文件损坏了怎么办？

如果脚本中途出错，检查：
1. 输入目录中的 JSON 文件格式是否正确
2. JSON 文件是否包含必填字段（key, messages, rule_list）
3. 文件编码是否为 UTF-8

### Q: 如何处理大量文件？

脚本已经优化，可以处理大量文件。如果遇到内存问题：
- 分批合并（将文件分成多个子目录分别合并）
- 使用 `--no-validate` 跳过验证以加快速度

## 版本历史

- v1.0 (2025-02-06): 初始版本
  - 支持基本的 JSON 到 JSONL 合并
  - 支持验证和详细模式
