"""
Demo 1: 异常处理
对应理论文档: 1.异常处理.md

演示 try/except/else/finally 的完整用法、
捕获多种异常、异常信息获取、
以及后端场景中的分层异常处理。
"""

# ============================================================
# 第一部分：try/except 基础
# ============================================================

print("=" * 55)
print("第一部分：try/except 基础")
print("=" * 55)

# 不处理异常 → 程序崩溃（这里用 try 包着演示）
print("\n  --- 捕获 ValueError ---")
try:
    num = int("abc")
except ValueError as e:
    print(f"  捕获到异常: {type(e).__name__}")
    print(f"  异常信息: {e}")

# 捕获多种异常
print("\n  --- 捕获多种异常 ---")

test_cases = [("abc", "非数字"), ("0", "除以零"), ("5", "正常")]
for value, desc in test_cases:
    try:
        num = int(value)
        result = 100 / num
    except ValueError:
        print(f"  [{desc}] ValueError: 输入不是数字")
    except ZeroDivisionError:
        print(f"  [{desc}] ZeroDivisionError: 除以零")
    else:
        print(f"  [{desc}] 计算成功: 100 / {num} = {result}")


# ============================================================
# 第二部分：else 和 finally
# ============================================================

print("\n" + "=" * 55)
print("第二部分：else 和 finally")
print("=" * 55)


def divide(a, b):
    """演示 try/except/else/finally 完整流程"""
    print(f"\n  计算 {a} / {b}:")
    try:
        result = a / b
    except ZeroDivisionError:
        print("    except: 除数不能为零")
    except TypeError as e:
        print(f"    except: 类型错误 - {e}")
    else:
        print(f"    else: 计算成功，结果 = {result}")
    finally:
        print("    finally: 无论如何都会执行")


divide(10, 3)       # 正常
divide(10, 0)       # 除以零
divide("10", 3)     # 类型错误


# ============================================================
# 第三部分：常见内置异常
# ============================================================

print("\n" + "=" * 55)
print("第三部分：常见内置异常")
print("=" * 55)

exceptions_demo = [
    ("int('abc')", "ValueError"),
    ("'1' + 1", "TypeError"),
    ("{}['x']", "KeyError"),
    ("[1,2][5]", "IndexError"),
    ("'hello'.foo()", "AttributeError"),
]

for code, expected in exceptions_demo:
    try:
        eval(code)
    except Exception as e:
        print(f"  {code:25s} → {type(e).__name__}: {e}")


# ============================================================
# 第四部分：自定义异常
# ============================================================

print("\n" + "=" * 55)
print("第四部分：自定义异常")
print("=" * 55)


class AppError(Exception):
    """应用基础异常"""
    def __init__(self, message="服务器内部错误", code=500):
        self.message = message
        self.code = code
        super().__init__(self.message)

    def __str__(self):
        return f"[{self.code}] {self.message}"


class NotFoundError(AppError):
    """资源不存在"""
    def __init__(self, resource, resource_id=None):
        msg = f"{resource}不存在" if resource_id is None else f"{resource}(id={resource_id})不存在"
        super().__init__(msg, code=404)


class AuthError(AppError):
    """认证失败"""
    def __init__(self, message="请先登录"):
        super().__init__(message, code=401)


class ForbiddenError(AppError):
    """权限不足"""
    def __init__(self, action=""):
        msg = f"无权执行操作: {action}" if action else "权限不足"
        super().__init__(msg, code=403)


# 使用自定义异常
errors = [
    NotFoundError("用户", 42),
    AuthError(),
    ForbiddenError("删除用户"),
    AppError("未知错误"),
]

for err in errors:
    print(f"  {err}")


# ============================================================
# 第五部分：后端场景 — 分层异常处理
# ============================================================

print("\n" + "=" * 55)
print("第五部分：后端场景 — 模拟 API 请求处理")
print("=" * 55)

# 模拟数据库
USERS_DB = {
    1: {"id": 1, "name": "张三", "role": "admin"},
    2: {"id": 2, "name": "李四", "role": "user"},
}


def query_user(user_id):
    """数据层：查询用户"""
    user = USERS_DB.get(user_id)
    if not user:
        raise NotFoundError("用户", user_id)
    return user


def delete_user(current_user, target_id):
    """服务层：删除用户（需要 admin 权限）"""
    if not current_user:
        raise AuthError("未登录")
    if current_user.get("role") != "admin":
        raise ForbiddenError("删除用户")
    user = query_user(target_id)
    print(f"    → 删除用户: {user['name']}")
    return {"message": f"用户 {user['name']} 已删除"}


def handle_request(current_user, target_id):
    """路由层：处理请求，统一捕获异常"""
    print(f"\n  请求: 删除用户 {target_id} (操作者: {current_user})")
    try:
        result = delete_user(current_user, target_id)
        print(f"    ✅ 200: {result}")
    except AuthError as e:
        print(f"    ❌ {e.code}: {e.message}")
    except ForbiddenError as e:
        print(f"    ❌ {e.code}: {e.message}")
    except NotFoundError as e:
        print(f"    ❌ {e.code}: {e.message}")
    except AppError as e:
        print(f"    ❌ {e.code}: {e.message}")


# 场景1：admin 删除存在的用户
handle_request(USERS_DB[1], 2)

# 场景2：普通用户尝试删除
handle_request(USERS_DB[2], 1)

# 场景3：未登录
handle_request(None, 1)

# 场景4：删除不存在的用户
handle_request(USERS_DB[1], 999)


# ============================================================
# 第六部分：异常链 — from 保留原始异常
# ============================================================

print("\n" + "=" * 55)
print("第六部分：异常链 (raise ... from ...)")
print("=" * 55)

try:
    try:
        int("abc")
    except ValueError as original:
        raise AppError("数据格式错误") from original
except AppError as e:
    print(f"  业务异常: {e}")
    print(f"  原始异常: {e.__cause__}")


# ============================================================
# 第七部分：坑 — except 顺序
# ============================================================

print("\n" + "=" * 55)
print("第七部分：坑 — except 顺序很重要")
print("=" * 55)

# ❌ 父类在前，子类永远匹配不到
print("\n  --- 错误顺序（Exception 在前）---")
try:
    raise NotFoundError("用户", 1)
except AppError as e:
    print(f"  被 AppError 捕获: {e}")
except NotFoundError as e:
    print(f"  被 NotFoundError 捕获: {e}")   # 永远不会执行

# ✅ 子类在前
print("\n  --- 正确顺序（子类在前）---")
try:
    raise NotFoundError("用户", 1)
except NotFoundError as e:
    print(f"  被 NotFoundError 捕获: {e}")   # ✅ 正确匹配
except AppError as e:
    print(f"  被 AppError 捕获: {e}")


print("\n" + "=" * 55)
print("✅ Demo 1 完成！")
print("=" * 55)
