"""
Demo 3: 上下文管理器
对应理论文档: 3.上下文管理器.md

演示 with 语句原理、自定义上下文管理器（类方式和生成器方式）、
__enter__/__exit__ 的执行流程、异常处理、
以及后端场景中的数据库连接和计时器。
"""

import time
from contextlib import contextmanager, suppress

# ============================================================
# 第一部分：with 语句的执行流程
# ============================================================

print("=" * 55)
print("第一部分：with 语句的执行流程")
print("=" * 55)


class DemoContext:
    """演示上下文管理器的执行顺序"""

    def __enter__(self):
        print("  1. __enter__ 被调用（获取资源）")
        return "我是 __enter__ 的返回值"

    def __exit__(self, exc_type, exc_val, exc_tb):
        print("  3. __exit__ 被调用（释放资源）")
        if exc_type:
            print(f"     异常类型: {exc_type.__name__}")
            print(f"     异常信息: {exc_val}")
        return False    # 不吞异常


# 正常执行
print("\n  --- 正常执行 ---")
with DemoContext() as value:
    print(f"  2. with 块内: value = {value}")

# 有异常时
print("\n  --- 有异常时 ---")
try:
    with DemoContext() as value:
        print(f"  2. with 块内: 准备抛异常...")
        raise ValueError("测试异常")
except ValueError:
    print("  4. 异常被外部 try/except 捕获")


# ============================================================
# 第二部分：自定义上下文管理器 — 数据库连接
# ============================================================

print("\n" + "=" * 55)
print("第二部分：自定义上下文管理器 — 模拟数据库连接")
print("=" * 55)


class DatabaseConnection:
    """模拟数据库连接上下文管理器"""

    def __init__(self, host, port, db_name):
        self.host = host
        self.port = port
        self.db_name = db_name
        self.connected = False
        self.queries = []

    def __enter__(self):
        print(f"  连接数据库 {self.host}:{self.port}/{self.db_name}...")
        self.connected = True
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type:
            print(f"  ⚠️ 发生异常，回滚事务: {exc_val}")
        else:
            print(f"  ✅ 提交事务（{len(self.queries)} 条操作）")
        print(f"  关闭数据库连接")
        self.connected = False
        return False

    def execute(self, sql):
        if not self.connected:
            raise RuntimeError("未连接数据库")
        self.queries.append(sql)
        print(f"  执行 SQL: {sql}")


# 正常使用
print("\n  --- 正常事务 ---")
with DatabaseConnection("localhost", 3306, "myapp") as db:
    db.execute("INSERT INTO users (name) VALUES ('张三')")
    db.execute("INSERT INTO profiles (user_id, bio) VALUES (1, 'hello')")
print(f"  连接状态: {db.connected}")   # False，已自动关闭

# 异常时自动回滚
print("\n  --- 异常回滚 ---")
try:
    with DatabaseConnection("localhost", 3306, "myapp") as db:
        db.execute("INSERT INTO users (name) VALUES ('李四')")
        raise RuntimeError("模拟业务异常")
except RuntimeError:
    pass
print(f"  连接状态: {db.connected}")   # False，异常时也自动关闭


# ============================================================
# 第三部分：__exit__ 吞异常演示
# ============================================================

print("\n" + "=" * 55)
print("第三部分：__exit__ 返回 True 会吞掉异常")
print("=" * 55)


class IgnoreError:
    """忽略指定异常的上下文管理器"""

    def __init__(self, *exceptions):
        self.exceptions = exceptions

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type and issubclass(exc_type, self.exceptions):
            print(f"  忽略异常: {exc_type.__name__}: {exc_val}")
            return True    # 吞掉异常
        return False


with IgnoreError(FileNotFoundError, KeyError):
    data = {}
    value = data["不存在的键"]   # KeyError 被忽略
print("  程序继续运行，没有崩溃")


# ============================================================
# 第四部分：@contextmanager — 用生成器简化
# ============================================================

print("\n" + "=" * 55)
print("第四部分：@contextmanager — 用生成器简化")
print("=" * 55)


@contextmanager
def timer(label):
    """计时上下文管理器"""
    start = time.time()
    print(f"  [{label}] 开始计时...")
    try:
        yield start    # as 后面的变量就是 yield 的值
    finally:
        elapsed = time.time() - start
        print(f"  [{label}] 耗时: {elapsed:.4f}s")


with timer("数据处理") as start_time:
    time.sleep(0.05)
    total = sum(range(1000000))
    print(f"  计算结果: {total}")


@contextmanager
def temp_config(config, key, temp_value):
    """临时修改配置，退出后自动恢复"""
    original = config.get(key)
    config[key] = temp_value
    print(f"  配置 [{key}] 临时改为: {temp_value}")
    try:
        yield config
    finally:
        if original is None:
            del config[key]
        else:
            config[key] = original
        print(f"  配置 [{key}] 已恢复为: {original}")


print()
app_config = {"debug": False, "db_host": "localhost"}
print(f"  修改前: debug = {app_config['debug']}")

with temp_config(app_config, "debug", True) as cfg:
    print(f"  with 内: debug = {cfg['debug']}")

print(f"  修改后: debug = {app_config['debug']}")


# ============================================================
# 第五部分：suppress — 标准库的异常忽略
# ============================================================

print("\n" + "=" * 55)
print("第五部分：contextlib.suppress")
print("=" * 55)

# 传统写法
try:
    result = int("not_a_number")
except ValueError:
    result = 0
print(f"  传统 try/except: result = {result}")

# suppress 写法（更简洁）
result = None
with suppress(ValueError):
    result = int("not_a_number")
if result is None:
    result = 0
print(f"  suppress 写法:   result = {result}")


# ============================================================
# 第六部分：多个上下文管理器
# ============================================================

print("\n" + "=" * 55)
print("第六部分：同时管理多个资源")
print("=" * 55)


@contextmanager
def resource(name):
    print(f"  获取资源: {name}")
    try:
        yield name
    finally:
        print(f"  释放资源: {name}")


# 同时管理多个资源
with resource("数据库") as db, resource("缓存") as cache:
    print(f"  使用: {db} + {cache}")
# 两个资源都会自动释放（后获取的先释放）


# ============================================================
# 第七部分：后端场景 — 请求日志上下文
# ============================================================

print("\n" + "=" * 55)
print("第七部分：后端场景 — API 请求追踪")
print("=" * 55)

import uuid


@contextmanager
def request_context(method, path):
    """模拟 API 请求上下文，自动记录请求日志"""
    request_id = str(uuid.uuid4())[:8]
    start = time.time()
    print(f"  → [{request_id}] {method} {path}")
    try:
        yield {"request_id": request_id, "method": method, "path": path}
    except Exception as e:
        elapsed = time.time() - start
        print(f"  ← [{request_id}] 500 ERROR ({elapsed:.3f}s) - {e}")
        raise
    else:
        elapsed = time.time() - start
        print(f"  ← [{request_id}] 200 OK ({elapsed:.3f}s)")


# 成功请求
with request_context("GET", "/api/users") as req:
    time.sleep(0.02)
    users = [{"id": 1, "name": "张三"}]
    print(f"    返回 {len(users)} 条数据")

# 失败请求
print()
try:
    with request_context("DELETE", "/api/users/999") as req:
        raise ValueError("用户不存在")
except ValueError:
    pass


print("\n" + "=" * 55)
print("✅ Demo 3 完成！")
print("=" * 55)
