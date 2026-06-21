# 基础语法 - Demo 学习指南

## 学习顺序

按编号顺序依次学习，每个 Demo 对应一个理论知识点。

---

### Demo 1: 变量与数据类型（一切数据的起点）
**文件**: `1_variables_types.py`

演示 Python 四种基本数据类型（int/float/str/bool）、变量赋值机制（引用 vs 复制）、类型查看与转换、None 类型。理解"变量是标签不是盒子"是后续所有内容的基础。

**运行方式**: `python 1_variables_types.py`
**前置依赖**: 无额外依赖

---

### Demo 2: 容器类型（存储一组数据）
**文件**: `2_containers.py`

演示 list（有序可变）、dict（键值映射）、tuple（不可变）、set（去重）四种容器的创建、增删改查、遍历方法。重点关注字典嵌套（模拟 API 响应）和容器选择指南。

**运行方式**: `python 2_containers.py`
**前置依赖**: 无额外依赖

---

### Demo 3: 条件判断、循环与推导式（控制程序流程）
**文件**: `3_control_flow.py`

演示 if/elif/else 条件判断、for/while 循环、break/continue、enumerate/zip 实用工具、列表/字典/集合推导式。推导式是 Python 最优雅的特性之一。

**运行方式**: `python 3_control_flow.py`
**前置依赖**: 无额外依赖

---

### Demo 4: 函数定义与参数（代码复用的核心）
**文件**: `4_functions.py`

演示函数定义、位置参数/关键字参数/默认参数/*args/**kwargs、返回值（单值和多值）、变量作用域、lambda 匿名函数。特别注意默认参数使用可变对象的经典坑。

**运行方式**: `python 4_functions.py`
**前置依赖**: 无额外依赖

---

### Demo 5: 字符串格式化（最日常的操作）
**文件**: `5_string_format.py`

演示 f-string（首选）、format()、% 三种格式化方式，以及日志输出、API 响应构造、URL 拼接等实际场景。特别警示 SQL 拼接的安全问题。

**运行方式**: `python 5_string_format.py`
**前置依赖**: 无额外依赖

---

## 对应理论文档

| Demo | 文件 | 对应理论文档 |
|------|------|-------------|
| Demo 1 | `1_variables_types.py` | `../1.变量与数据类型.md` |
| Demo 2 | `2_containers.py` | `../2.容器类型.md` |
| Demo 3 | `3_control_flow.py` | `../3.条件判断与循环.md` |
| Demo 4 | `4_functions.py` | `../4.函数.md` |
| Demo 5 | `5_string_format.py` | `../5.字符串格式化.md` |

---

## 核心要点

1. **变量是引用（标签）**：`b = a` 让 b 指向同一个对象，不是复制
2. **四种容器各有用途**：list 日常最多，dict 键值映射，tuple 不可变，set 去重
3. **推导式是 Pythonic 的标志**：用一行代替循环，但复杂逻辑不要硬塞
4. **函数参数顺序**：位置参数 → *args → 默认参数 → **kwargs
5. **字符串格式化首选 f-string**：最快、最清晰、功能最全
6. **永远不要用 f-string 拼 SQL**：防止 SQL 注入，用参数化查询

---

## 常见问题

| 问题 | 解决方案 |
|------|----------|
| `SyntaxError: invalid syntax` | 检查缩进、冒号、括号是否遗漏 |
| `TypeError: can only concatenate str` | 字符串不能直接 + 数字，用 `str()` 转换或用 f-string |
| `IndexError: list index out of range` | 索引超出列表长度，检查 `len()` |
| `KeyError` | 字典中不存在该 key，用 `.get()` 代替 `[]` |
| `TypeError: unhashable type: 'list'` | list 不能作为 dict 的 key 或 set 的元素，用 tuple 代替 |
