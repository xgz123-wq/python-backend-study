# 高级特性 - Demo 学习指南

## 学习顺序

按编号顺序依次学习，每个 Demo 对应一个理论知识点。本章是面试必考内容，建议每个 Demo 都认真跑一遍。

---

### Demo 1: 装饰器（Python 最强黑魔法）
**文件**: `1_decorators.py`

演示闭包基础、无参装饰器、`@` 语法糖、`functools.wraps` 保留函数信息、带参装饰器（三层嵌套）、多装饰器叠加、类装饰器，以及后端场景中的权限检查装饰器。

**运行方式**: `python 1_decorators.py`
**前置依赖**: 无额外依赖

---

### Demo 2: 迭代器与生成器（惰性求值的艺术）
**文件**: `2_iterators_generators.py`

演示可迭代对象与迭代器的区别、for 循环的本质、自定义迭代器、`yield` 生成器、生成器表达式的内存优势、`yield from` 委托、`send()` 高级用法，以及后端日志分析管道场景。

**运行方式**: `python 2_iterators_generators.py`
**前置依赖**: 无额外依赖

---

### Demo 3: 上下文管理器（资源管理的优雅方案）
**文件**: `3_context_manager.py`

演示 `with` 语句执行流程、`__enter__`/`__exit__` 的用法、自定义数据库连接管理器、`__exit__` 吞异常的机制、`@contextmanager` 生成器简化方案、`suppress` 异常忽略，以及 API 请求追踪场景。

**运行方式**: `python 3_context_manager.py`
**前置依赖**: 无额外依赖

---

### Demo 4: 类型提示（代码的说明书）
**文件**: `4_type_hints.py`

演示基本类型标注、容器类型标注、`Optional`/`Union`、`Callable` 函数类型、`TypeAlias` 类型别名、`TypeVar` 泛型、`Protocol` 鸭子类型，以及模拟 Pydantic 风格的数据验证预告。

**运行方式**: `python 4_type_hints.py`
**前置依赖**: 无额外依赖（需要 Python 3.10+，`TypeAlias` 需要 3.10+，`|` 语法需要 3.10+）

---

## 对应理论文档

| Demo | 文件 | 对应理论文档 |
|------|------|-------------|
| Demo 1 | `1_decorators.py` | `../1.装饰器.md` |
| Demo 2 | `2_iterators_generators.py` | `../2.迭代器与生成器.md` |
| Demo 3 | `3_context_manager.py` | `../3.上下文管理器.md` |
| Demo 4 | `4_type_hints.py` | `../4.类型提示.md` |

---

## 核心要点

1. **装饰器 = 闭包 + 函数参数化**：不修改原函数代码，给函数添加新功能。`@wraps(func)` 必不可少
2. **迭代器 vs 生成器**：迭代器需要写 `__iter__` + `__next__`，生成器用 `yield` 一行搞定
3. **惰性求值省内存**：处理大数据时用生成器而非列表，内存差距可达千倍
4. **with = 自动资源管理**：`__enter__` 获取资源，`__exit__` 释放资源，异常也不怕
5. **@contextmanager**：yield 前是 enter，yield 后是 exit，记得用 try/finally
6. **类型提示不是强制的**：Python 运行时不检查类型，但 IDE 和 mypy 会帮你提前发现问题
7. **后端离不开这些特性**：FastAPI 路由用装饰器、数据库连接用上下文管理器、API 参数用类型提示

---

## 常见问题

| 问题 | 解决方案 |
|------|----------|
| 装饰器导致 `__name__` 变成 `wrapper` | 在 wrapper 上面加 `@wraps(func)` |
| 带参装饰器报 `TypeError: missing argument` | 检查是否忘了加括号：`@retry()` 而不是 `@retry` |
| 生成器第二次遍历为空 | 生成器只能遍历一次，需要重新创建或转成 list |
| `send()` 报 `TypeError: can't send non-None value` | 生成器刚创建时必须先 `next(gen)` 启动 |
| with 块里的异常被"吞"了 | 检查 `__exit__` 是否返回了 `True`，改为 `False` |
| `@contextmanager` 退出代码不执行 | yield 后面的代码必须放在 `try/finally` 的 finally 块中 |
| 类型提示传了错误类型但没报错 | 类型提示不做运行时检查，需要 `mypy` 静态分析或 Pydantic 验证 |
| `list[str]` 报 `TypeError` | Python 3.9 以下不支持，需要用 `from typing import List` |
