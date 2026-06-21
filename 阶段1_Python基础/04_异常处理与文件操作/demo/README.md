# 异常处理与文件操作 - Demo 学习指南

## 学习顺序

按编号顺序依次学习，每个 Demo 对应一个或多个理论知识点。本章是后端开发的基石——没有健壮的异常处理，服务一碰就崩；不会文件和 JSON 操作，配置读不了、日志写不了、API 通不了。

---

### Demo 1: 异常处理（程序的安全网）
**文件**: `1_exception_handling.py`

演示 `try/except/else/finally` 完整用法、捕获多种异常、获取异常信息、常见内置异常（ValueError/TypeError/KeyError/IndexError/AttributeError）触发与捕获、自定义异常基础（AppError 体系），以及后端场景中的分层异常处理（数据层→服务层→路由层）和异常链 `raise ... from ...`。

**运行方式**: `python 1_exception_handling.py`
**前置依赖**: 无额外依赖
**涵盖知识点**:
- `try/except/else/finally` 四件套的执行顺序
- 多 `except` 分支按子类→父类排列
- 自定义异常类继承 `Exception`
- 异常链 `raise X from Y` 保留原始上下文
- 后端分层异常传递模式（数据层抛、服务层转、路由层统一捕获）

---

### Demo 2: 自定义异常体系（后端必备技能）
**文件**: `2_custom_exceptions.py`

演示如何构建完整的后端异常体系：AppError 基类 + 按 HTTP 状态码分层的子类（400/401/403/404/409/500/502），在业务代码中使用异常（UserService CRUD），模拟全局异常处理器（装饰器方式，类似 FastAPI），以及携带上下文信息的 ValidationError（422 + 字段级错误详情）。

**运行方式**: `python 2_custom_exceptions.py`
**前置依赖**: 无额外依赖
**涵盖知识点**:
- 异常基类设计（message + code + to_dict）
- 4xx 客户端错误 vs 5xx 服务端错误分类
- 业务代码中的异常抛出与上层统一捕获
- 装饰器实现全局异常处理器（`@global_exception_handler`）
- ValidationError 携带字段级错误详情

---

### Demo 3: 文件读写与 pathlib（数据持久化基础）
**文件**: `3_file_operations.py`

演示文件读取的四种方式（read/readline/readlines/for line in f）、写入模式对比（`w` 覆盖 vs `a` 追加）、pathlib 现代路径操作（拼接/解析/判断/遍历/glob）、pathlib 快捷读写（read_text/write_text），以及后端场景中的 `.env` 配置文件解析和日志文件追加写入。

**运行方式**: `python 3_file_operations.py`
**前置依赖**: 无额外依赖
**注意**: 运行时会在 demo 目录创建 `temp_files/` 临时目录，结束后自动清理
**涵盖知识点**:
- `with open()` 上下文管理器保证文件关闭
- `encoding="utf-8"` 永远不要忘
- `read()` 全量读取 vs `for line in f` 逐行读取（大文件必须逐行）
- `"w"` 覆盖写 vs `"a"` 追加写的区别
- pathlib.Path 取代 os.path 的现代路径操作
- 后端实战：.env 配置解析器、日志写入器

---

### Demo 4: JSON 处理（API 数据交换的基石）
**文件**: `4_json_processing.py`

演示 JSON 四兄弟：`json.dumps`/`json.loads`（字符串转换）、`json.dump`/`json.load`（文件读写）、特殊类型序列化（datetime/Path/set 的 CustomEncoder）、API 响应构造函数、第三方 API 响应安全解析（链式 `.get()`）、JSON 配置管理器（JsonConfig 类），以及常见坑（中文转义、int 键变 str、单引号不合法）。

**运行方式**: `python 4_json_processing.py`
**前置依赖**: 无额外依赖
**注意**: 运行时会在 demo 目录创建 `temp_json/` 临时目录，结束后自动清理
**涵盖知识点**:
- `dumps`/`loads`（s=string）操作字符串 vs `dump`/`load` 操作文件
- `ensure_ascii=False` 保留中文输出
- `indent=2` 格式化输出
- 自定义 `JSONEncoder` 处理 datetime/Path/set
- `default=str` 简单粗暴的序列化方案
- 标准 API 响应格式构造（code/message/data）
- 链式 `.get()` 安全解析嵌套 JSON
- JsonConfig 配置管理器实战

---

## 对应理论文档

| Demo | 文件 | 对应理论文档 | 关键概念 |
|------|------|-------------|----------|
| Demo 1 | `1_exception_handling.py` | `../1.异常处理.md` | try/except/else/finally、异常链 |
| Demo 2 | `2_custom_exceptions.py` | `../2.自定义异常.md` | 异常体系设计、全局处理器 |
| Demo 3 | `3_file_operations.py` | `../3.文件读写.md` | with 语句、pathlib、编码 |
| Demo 4 | `4_json_processing.py` | `../4.JSON处理.md` | JSON 四兄弟、自定义编码器 |

---

## 核心要点

1. **try/except/else/finally**：else 只在无异常时执行，finally 无论如何都执行（资源清理）
2. **精确捕获异常**：不要用裸 `except` 或 `except Exception: pass`，至少记日志
3. **except 顺序**：子类在前，父类在后，否则子类永远匹配不到
4. **自定义异常体系**：一个基类（AppError）+ 按状态码分层（4xx/5xx），配合全局处理器自动转 HTTP 响应
5. **文件操作必用 with**：自动关闭文件，永远指定 `encoding="utf-8"`
6. **大文件用 `for line in f`**：逐行读取不吃内存，不要一次性 `read()` 或 `readlines()`
7. **pathlib 优于 os.path**：`Path("a") / "b"` 比 `os.path.join("a", "b")` 更可读、更安全
8. **JSON 四兄弟**：`dumps`/`loads` 操作字符串（s=string），`dump`/`load` 操作文件
9. **`ensure_ascii=False`**：输出 JSON 时保留中文，这是后端最常见的遗漏
10. **链式 `.get()` 安全取值**：`data.get("a", {}).get("b")` 防止嵌套 KeyError

---

## 学习建议

1. **先读理论文档**：每个 Demo 开始前，先快速浏览对应的 `.md` 理论文档
2. **逐段运行**：每个 Demo 按"部分"划分，建议逐段阅读代码后再运行
3. **动手修改**：尝试修改代码观察效果，比如改变 except 顺序、改 `"w"` 为 `"a"` 模式
4. **关注后端场景**：每个 Demo 的后半部分都有后端实战场景，这些是工作中直接能用的模式

---

## 常见问题

| 问题 | 解决方案 |
|------|----------|
| `except` 顺序导致子类异常匹配不到 | 子类 except 放前面，父类放后面 |
| 自定义异常 `str(e)` 为空 | 忘了 `super().__init__(message)` |
| 读中文文件乱码或 `UnicodeDecodeError` | 加 `encoding="utf-8"` |
| `"w"` 模式把文件清空了 | 追加用 `"a"` 模式 |
| Windows 路径 `\` 报错 | 用 `pathlib.Path` 或正斜杠 `/` |
| `json.dumps` 中文变 `\uXXXX` | 加 `ensure_ascii=False` |
| `json.dumps` datetime 报 TypeError | 用自定义 `JSONEncoder` 或 `default=str` |
| 混淆 `json.loads` 和 `json.load` | `loads` = load **s**tring，`load` = load file |
| JSON 单引号报错 | JSON 标准只认双引号，Python 的 `str()` 输出不是合法 JSON |
| int 键序列化后变 str 键 | JSON 标准只允许字符串键，反序列化后需手动转回 int |
