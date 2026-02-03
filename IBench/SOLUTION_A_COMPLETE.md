# 方案A实施完成 - 条件导入

## ✅ 实施完成

已成功修改 IBench 使用条件导入，现在可以灵活处理依赖！

---

## 📝 修改文件清单

### 核心修改（3个文件）

| 文件 | 修改内容 | 影响 |
|------|----------|------|
| `IBench/__init__.py` | ⭐ 条件导入模型类 | 可以在没有 torch/transformers 时导入基础功能 |
| `IBench/config.py` | ⭐ 添加依赖验证 | `validate_dependencies()` 方法 |
| `IBench/utils/imports.py` | ⭐ 新建导入工具 | 依赖检查装饰器和函数 |

### 新增文件（1个）

| 文件 | 用途 |
|------|------|
| `IBench/scripts/quick_test.py` | 快速测试脚本（无需依赖） |

### 文档更新（1个）

| 文件 | 更新内容 |
|------|----------|
| `IBench/README.md` | 添加基础测试步骤 |

---

## 🎯 新功能

### 1. 条件导入

**现在可以导入 IBench 即使没有安装依赖！**

```python
# 这个现在可以工作，即使没有 torch/transformers
from IBench import (
    Message, RuleType, EvaluationMode,
    SingleRuleRegistry, StageRuleRegistry
)

# 检查依赖状态
from IBench import check_dependencies
status = check_dependencies()
print(status)
# {'torch': False, 'transformers': False, ...}
```

### 2. 依赖检查函数

```python
from IBench import check_dependencies, print_dependency_status

# 检查依赖
status = check_dependencies()
if not status['all_available']:
    print("Some dependencies missing!")

# 打印状态
print_dependency_status()
```

### 3. 可用性标志

```python
from IBench import __models_available__, __pipeline_available__

if __models_available__:
    print("Models can be used!")
else:
    print("Model dependencies not installed")
```

### 4. 导入工具

```python
from IBench.utils.imports import (
    get_missing_dependencies,
    require_model_dependencies,
    ensure_models_available
)

# 检查缺失依赖
missing = get_missing_dependencies()

# 或作为装饰器
@ensure_models_available
def my_function():
    # 这里保证依赖已安装
    from IBench import LocalModel
    model = LocalModel(config)
```

---

## 🚀 使用方式

### 场景 1：基础功能（无需依赖）

```python
# 只使用数据结构和规则
from IBench import (
    Message, RuleType, SingleRuleRegistry
)

# 这总是可以工作
registry = SingleRuleRegistry()
rules = registry.get_all_rules()
print(f"Total rules: {len(rules)}")
```

### 场景 2：条件使用模型

```python
from IBench import LocalModel, __models_available__

if __models_available__:
    # 可以使用模型
    model = LocalModel(config)
else:
    print("Model dependencies not installed")
    print("Install: pip install torch transformers")
```

### 场景 3：强制检查依赖

```python
from IBench.utils.imports import require_model_dependencies

try:
    require_model_dependencies()
    # 如果到了这里，说明依赖都已安装
    from IBench import LocalModel
    model = LocalModel(config)
except ImportError as e:
    print(f"Error: {e}")
```

---

## 🧪 测试步骤

### 步骤 1：基础测试（无需依赖）

```bash
# 在服务器上，即使没有安装 torch 也能运行
python IBench/scripts/quick_test.py
```

**预期输出**：
```
############################################################
# IBench Quick Start Test
############################################################

============================================================
Testing IBench Imports
============================================================
✓ Core data structures imported successfully
✓ Rules imported successfully
✓ Model configurations imported successfully

============================================================
Testing Model Configurations
============================================================

Available models (3):
  - Qwen3-8B
    Base Qwen3-8B model (8B parameters)
  - qwen3_full_sft
    Qwen3-8B fine-tuned with SFT
  - llama_factory_psy1.32.1_lora_qwen2_7b_dpo
    Qwen2-7B with LoRA and DPO training

✓ Got config for Qwen3-8B

============================================================
Testing Dependency Check
============================================================

Dependency Status:
  ✗ torch               Not installed
  ✗ transformers        Not installed
  ✗ openai              Not installed
  ✗ bitsandbytes        Not installed

⚠ Some dependencies not installed

============================================================
Test Summary
============================================================
  Basic Imports                  ✓ PASS
  Model Configurations            ✓ PASS
  Dependency Check               ✓ PASS
  Rule Definitions               ✓ PASS

✓ All tests passed!

Next steps:
  1. Install dependencies:
     pip install torch transformers openai bitsandbytes accelerate
  2. Test model loading:
     python IBench/scripts/test_model_loading.py
```

### 步骤 2：安装依赖（在服务器上）

```bash
pip install torch transformers openai bitsandbytes accelerate
```

### 步骤 3：测试模型加载

```bash
python IBench/scripts/test_model_loading.py
```

---

## 📊 修改详情

### `IBench/__init__.py` 修改

**修改前**：
```python
from .models import LocalModel, APIModel  # 硬导入，失败则整体失败
```

**修改后**：
```python
try:
    from .models import LocalModel, APIModel
    _models_available = True
except ImportError as e:
    LocalModel = None
    APIModel = None
    _models_available = False
```

**新增功能**：
```python
def check_dependencies():
    """检查所有依赖状态"""
    # 返回详细的依赖状态

def print_dependency_status():
    """打印依赖安装状态"""
```

### `IBench/config.py` 修改

**新增方法**：
```python
def validate_dependencies(self) -> tuple[bool, list[str]]:
    """
    验证配置所需的依赖
    
    Returns:
        (all_valid, missing_dependencies)
    """
    missing = []
    if self.load_in_4bit:
        # 检查 bitsandbytes
    # ... 其他检查
    return len(missing) == 0, missing
```

---

## ✨ 优势

### 1. 分层安装

**现在支持三种安装模式**：

| 模式 | 依赖 | 功能 |
|------|------|------|
| **基础** | 无 | 数据结构、规则定义、配置 |
| **标准** | torch, transformers, openai | 模型加载、评估 |
| **完整** | + bitsandbytes, accelerate | 量化、多GPU |

### 2. 优雅降级

```python
from IBench import ContextEvaluator

if __pipeline_available__:
    evaluator = ContextEvaluator(...)
else:
    print("Pipeline not available - missing dependencies")
```

### 3. 更好的错误信息

```python
from IBench.utils.imports import require_model_dependencies

try:
    require_model_dependencies()
except ImportError as e:
    print(e)
    # Missing required dependencies: torch, transformers
    # Install with:
    #   pip install torch transformers openai bitsandbytes accelerate
```

---

## 🎓 使用建议

### 开发环境

```bash
# 只安装需要的依赖
pip install torch transformers
# IBench 基础功能可用
```

### 生产环境

```bash
# 安装所有依赖
pip install torch transformers openai bitsandbytes accelerate
# IBench 完全功能
```

### CI/CD

```python
# 测试时可以导入 IBench
from IBench import check_dependencies

deps = check_dependencies()
if deps['all_available']:
    # 运行完整测试
    test_model_loading()
else:
    # 只运行基础测试
    test_data_structures()
```

---

## ✅ 验证

### 在服务器上验证

```bash
# 1. 基础测试（应该立即成功）
python IBench/scripts/quick_test.py

# 2. 安装依赖
pip install torch transformers openai bitsandbytes accelerate

# 3. 模型测试
python IBench/scripts/test_model_loading.py
```

### Python 验证

```python
# 测试 1：无依赖导入
from IBench import Message, RuleType, SingleRuleRegistry
print("✓ Basic import works")

# 测试 2：检查依赖
from IBench import check_dependencies
status = check_dependencies()
print(f"✓ Dependencies checked: {status}")

# 测试 3：条件使用
from IBench import __models_available__, LocalModel
if __models_available__:
    print("✓ Models available")
else:
    print("✓ Models not available (expected)")
```

---

## 📝 总结

### 已实现

- ✅ 条件导入 `LocalModel` 和 `APIModel`
- ✅ 依赖检查函数 `check_dependencies()`
- ✅ 可用性标志 `__models_available__`
- ✅ 导入工具模块 `utils/imports.py`
- ✅ 快速测试脚本 `scripts/quick_test.py`
- ✅ 配置验证方法 `validate_dependencies()`

### 兼容性

- ✅ 向后兼容：现有代码无需修改
- ✅ 向前兼容：新功能可选使用
- ✅ 错误处理：更友好的错误信息

### 下一步

1. **在服务器上测试**：运行 `quick_test.py`
2. **安装依赖**：`pip install -r requirements.txt`
3. **运行完整测试**：`test_model_loading.py`

---

**方案A实施完成！现在可以在服务器上测试了！** 🚀
