"""
Demo 5: functools
对应理论文档: 5.functools.md

演示 partial、lru_cache、wraps 的用法和后端场景。
"""

from functools import lru_cache, partial, wraps


print("=" * 55)
print("第一部分：partial")
print("=" * 55)


def log(level, message):
    print(f"[{level}] {message}")


info = partial(log, "INFO")
error = partial(log, "ERROR")

info("服务启动成功")
error("数据库连接失败")


print("\n" + "=" * 55)
print("第二部分：lru_cache")
print("=" * 55)


@lru_cache(maxsize=128)
def fib(n):
    if n < 2:
        return n
    return fib(n - 1) + fib(n - 2)


print(f"fib(10) = {fib(10)}")
print(f"fib(10) 再次调用 = {fib(10)}")
print(f"缓存信息 = {fib.cache_info()}")


print("\n" + "=" * 55)
print("第三部分：wraps")
print("=" * 55)


def timer(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        print(f"调用函数: {func.__name__}")
        return func(*args, **kwargs)
    return wrapper


@timer
def get_user_name(user_id):
    """根据 user_id 返回用户名。"""
    return f"user_{user_id}"


print(get_user_name(7))
print(f"函数名 = {get_user_name.__name__}")
print(f"文档字符串 = {get_user_name.__doc__}")


print("\n" + "=" * 55)
print("第四部分：后端场景模拟")
print("=" * 55)


@lru_cache(maxsize=32)
def load_config(section):
    print(f"真实加载配置: {section}")
    fake_config = {
        "db": {"host": "localhost", "port": 3306},
        "redis": {"host": "localhost", "port": 6379},
    }
    return fake_config[section]


print(load_config("db"))
print(load_config("db"))
print(load_config("redis"))


print("\n" + "=" * 55)
print("Demo 5 完成!")
print("=" * 55)
