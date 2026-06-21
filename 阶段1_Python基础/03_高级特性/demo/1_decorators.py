"""
Demo 1: 装饰器
对应理论文档: 1.装饰器.md

演示闭包基础、无参装饰器、@语法糖、functools.wraps、
带参装饰器、类装饰器、多装饰器叠加。
运行后观察每部分的输出，理解装饰器的执行流程。
"""

import time
from functools import wraps

# ============================================================
# 第一部分：闭包 — 装饰器的前置知识
# ============================================================

print("=" * 55)
print("第一部分：闭包 — 装饰器的前置知识")
print("=" * 55)

# 函数是"一等公民"：可以赋值、传参、返回
def greet(name):
    return f"你好，{name}"

say_hello = greet               # 赋值给变量
print(say_hello("张三"))        # 你好，张三

def call_func(func, arg):      # 作为参数传递
    return func(arg)

print(call_func(greet, "李四"))  # 你好，李四


# 闭包：内部函数记住外部变量
def make_greeter(greeting):
    def greeter(name):
        return f"{greeting}，{name}！"
    return greeter

hello = make_greeter("你好")
print(hello("王五"))    # 你好，王五！

bye = make_greeter("再见")
print(bye("王五"))      # 再见，王五！


# ============================================================
# 第二部分：最简单的装饰器
# ============================================================

print("\n" + "=" * 55)
print("第二部分：最简单的装饰器")
print("=" * 55)


def timer(func):
    """计时装饰器（还没加 @wraps）"""
    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        elapsed = time.time() - start
        print(f"  [{func.__name__}] 耗时: {elapsed:.4f}s")
        return result
    return wrapper


# 手动装饰
def slow_add(a, b):
    """两数相加（慢速版）"""
    time.sleep(0.05)
    return a + b

slow_add = timer(slow_add)       # 手动装饰
result = slow_add(1, 2)
print(f"  结果: {result}")


# @ 语法糖（完全等价于手动装饰）
@timer
def slow_multiply(a, b):
    """两数相乘（慢速版）"""
    time.sleep(0.05)
    return a * b

result = slow_multiply(3, 4)
print(f"  结果: {result}")


# ============================================================
# 第三部分：functools.wraps — 保留原函数信息
# ============================================================

print("\n" + "=" * 55)
print("第三部分：functools.wraps 的重要性")
print("=" * 55)

# 问题演示：不加 @wraps，原函数信息丢失
print(f"  slow_multiply.__name__ = {slow_multiply.__name__}")   # wrapper（不是 slow_multiply！）
print(f"  slow_multiply.__doc__  = {slow_multiply.__doc__}")    # None（文档丢了！）


# 正确的装饰器写法：加 @wraps(func)
def timer_v2(func):
    """改进版计时装饰器，保留原函数信息"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        elapsed = time.time() - start
        print(f"  [{func.__name__}] 耗时: {elapsed:.4f}s")
        return result
    return wrapper

@timer_v2
def slow_divide(a, b):
    """两数相除"""
    time.sleep(0.05)
    return a / b

print(f"\n  加了 @wraps 后：")
print(f"  slow_divide.__name__ = {slow_divide.__name__}")   # slow_divide ✅
print(f"  slow_divide.__doc__  = {slow_divide.__doc__}")    # 两数相除 ✅
slow_divide(10, 3)


# ============================================================
# 第四部分：带参数的装饰器（三层嵌套）
# ============================================================

print("\n" + "=" * 55)
print("第四部分：带参数的装饰器")
print("=" * 55)


def retry(max_attempts=3):
    """带参数的装饰器：失败自动重试"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(1, max_attempts + 1):
                try:
                    result = func(*args, **kwargs)
                    print(f"  [{func.__name__}] 第 {attempt} 次成功！")
                    return result
                except Exception as e:
                    print(f"  [{func.__name__}] 第 {attempt} 次失败: {e}")
                    if attempt == max_attempts:
                        print(f"  [{func.__name__}] 全部 {max_attempts} 次尝试失败")
                        raise
        return wrapper
    return decorator


import random
random.seed(42)    # 固定随机种子，让结果可复现

@retry(max_attempts=5)
def unstable_api():
    """模拟不稳定的 API 调用"""
    if random.random() < 0.6:
        raise ConnectionError("网络超时")
    return {"status": "ok", "data": [1, 2, 3]}

try:
    result = unstable_api()
    print(f"  结果: {result}")
except ConnectionError:
    print("  最终还是失败了")


# ============================================================
# 第五部分：多装饰器叠加
# ============================================================

print("\n" + "=" * 55)
print("第五部分：多装饰器叠加")
print("=" * 55)


def bold(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        return f"<b>{func(*args, **kwargs)}</b>"
    return wrapper

def italic(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        return f"<i>{func(*args, **kwargs)}</i>"
    return wrapper

def underline(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        return f"<u>{func(*args, **kwargs)}</u>"
    return wrapper


@bold
@italic
@underline
def format_text(text):
    return text

# 执行顺序（从下往上包裹）：
# underline(format_text) → italic(underlined) → bold(italicized)
result = format_text("Hello")
print(f"  结果: {result}")
# <b><i><u>Hello</u></i></b>


# ============================================================
# 第六部分：类装饰器
# ============================================================

print("\n" + "=" * 55)
print("第六部分：类装饰器")
print("=" * 55)


class CountCalls:
    """统计函数调用次数的类装饰器"""
    def __init__(self, func):
        self.func = func
        self.count = 0

    def __call__(self, *args, **kwargs):
        self.count += 1
        print(f"  [{self.func.__name__}] 第 {self.count} 次调用")
        return self.func(*args, **kwargs)


@CountCalls
def say_hello(name):
    print(f"  Hello, {name}!")

say_hello("张三")
say_hello("李四")
say_hello("王五")
print(f"  总共调用了 {say_hello.count} 次")


# ============================================================
# 第七部分：实用装饰器示例 — 权限检查
# ============================================================

print("\n" + "=" * 55)
print("第七部分：实用装饰器 — 权限检查（后端场景）")
print("=" * 55)


def require_role(role):
    """权限检查装饰器：检查当前用户是否有指定角色"""
    def decorator(func):
        @wraps(func)
        def wrapper(current_user, *args, **kwargs):
            if current_user.get("role") != role:
                print(f"  ❌ 权限不足！需要 {role}，当前是 {current_user.get('role')}")
                return {"error": "权限不足", "required": role}
            print(f"  ✅ 权限验证通过（{role}）")
            return func(current_user, *args, **kwargs)
        return wrapper
    return decorator


@require_role("admin")
def delete_user(current_user, user_id):
    """删除用户（需要 admin 权限）"""
    return {"message": f"用户 {user_id} 已删除", "by": current_user["name"]}


admin = {"name": "管理员", "role": "admin"}
guest = {"name": "游客", "role": "guest"}

result1 = delete_user(admin, user_id=42)
print(f"  结果: {result1}")

result2 = delete_user(guest, user_id=42)
print(f"  结果: {result2}")


print("\n" + "=" * 55)
print("✅ Demo 1 完成！")
print("=" * 55)
