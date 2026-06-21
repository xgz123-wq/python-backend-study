"""
Demo 2: 自定义异常体系
对应理论文档: 2.自定义异常.md

演示如何构建后端项目的异常体系，
包含基类、HTTP 错误码映射、业务异常、
以及模拟全局异常处理器。
"""

# ============================================================
# 第一部分：构建异常体系
# ============================================================

print("=" * 55)
print("第一部分：构建异常体系")
print("=" * 55)


class AppError(Exception):
    """应用基础异常：所有业务异常的父类"""
    def __init__(self, message: str = "服务器内部错误", code: int = 500):
        self.message = message
        self.code = code
        super().__init__(self.message)

    def __str__(self):
        return f"[{self.code}] {self.message}"

    def to_dict(self):
        """转成 API 响应格式"""
        return {"code": self.code, "error": self.message}


# --- 4xx 客户端错误 ---

class BadRequestError(AppError):
    def __init__(self, message: str = "请求参数错误"):
        super().__init__(message, code=400)


class AuthenticationError(AppError):
    def __init__(self, message: str = "请先登录"):
        super().__init__(message, code=401)


class ForbiddenError(AppError):
    def __init__(self, message: str = "权限不足"):
        super().__init__(message, code=403)


class NotFoundError(AppError):
    def __init__(self, resource: str, resource_id=None):
        msg = f"{resource}不存在"
        if resource_id is not None:
            msg = f"{resource}(id={resource_id})不存在"
        self.resource = resource
        self.resource_id = resource_id
        super().__init__(msg, code=404)


class ConflictError(AppError):
    def __init__(self, message: str = "资源已存在"):
        super().__init__(message, code=409)


# --- 5xx 服务端错误 ---

class DatabaseError(AppError):
    def __init__(self, message: str = "数据库操作失败"):
        super().__init__(message, code=500)


class ExternalServiceError(AppError):
    def __init__(self, service: str, detail: str = ""):
        msg = f"调用 {service} 失败"
        if detail:
            msg += f": {detail}"
        self.service = service
        super().__init__(msg, code=502)


# 展示异常体系
print("  异常体系：")
print("  AppError (500)")
print("  ├── BadRequestError (400)")
print("  ├── AuthenticationError (401)")
print("  ├── ForbiddenError (403)")
print("  ├── NotFoundError (404)")
print("  ├── ConflictError (409)")
print("  ├── DatabaseError (500)")
print("  └── ExternalServiceError (502)")


# ============================================================
# 第二部分：在业务代码中使用
# ============================================================

print("\n" + "=" * 55)
print("第二部分：在业务代码中使用异常体系")
print("=" * 55)

# 模拟数据库
USERS = {
    1: {"id": 1, "name": "张三", "email": "zs@qq.com", "role": "admin"},
    2: {"id": 2, "name": "李四", "email": "ls@qq.com", "role": "user"},
}


class UserService:
    """用户服务层"""

    @staticmethod
    def get_user(user_id: int) -> dict:
        user = USERS.get(user_id)
        if not user:
            raise NotFoundError("用户", user_id)
        return user

    @staticmethod
    def create_user(name: str, email: str) -> dict:
        if not name or not email:
            raise BadRequestError("name 和 email 不能为空")

        for u in USERS.values():
            if u["email"] == email:
                raise ConflictError(f"邮箱 {email} 已注册")

        new_id = max(USERS.keys()) + 1
        user = {"id": new_id, "name": name, "email": email, "role": "user"}
        USERS[new_id] = user
        print(f"    创建用户成功: {user}")
        return user

    @staticmethod
    def delete_user(current_user: dict, target_id: int):
        if current_user["role"] != "admin":
            raise ForbiddenError(f"用户 {current_user['name']} 无权删除用户")

        target = UserService.get_user(target_id)
        del USERS[target_id]
        print(f"    删除用户成功: {target['name']}")
        return target


# 测试各种异常场景
test_cases = [
    ("查询存在用户", lambda: UserService.get_user(1)),
    ("查询不存在用户", lambda: UserService.get_user(999)),
    ("创建用户（邮箱冲突）", lambda: UserService.create_user("王五", "zs@qq.com")),
    ("创建用户（参数缺失）", lambda: UserService.create_user("", "")),
    ("普通用户删人", lambda: UserService.delete_user(USERS[2], 1)),
    ("创建新用户", lambda: UserService.create_user("王五", "ww@qq.com")),
]

for desc, action in test_cases:
    print(f"\n  测试: {desc}")
    try:
        result = action()
        print(f"    ✅ 成功: {result}")
    except AppError as e:
        print(f"    ❌ {e}")
        print(f"    响应: {e.to_dict()}")


# ============================================================
# 第三部分：模拟全局异常处理器
# ============================================================

print("\n" + "=" * 55)
print("第三部分：模拟全局异常处理器（类似 FastAPI）")
print("=" * 55)


def global_exception_handler(func):
    """模拟 FastAPI 的全局异常处理器"""
    def wrapper(*args, **kwargs):
        try:
            result = func(*args, **kwargs)
            return {"code": 200, "data": result}
        except AppError as e:
            return {"code": e.code, "error": e.message}
        except Exception as e:
            return {"code": 500, "error": f"未知错误: {e}"}
    return wrapper


@global_exception_handler
def api_get_user(user_id: int):
    return UserService.get_user(user_id)


@global_exception_handler
def api_create_user(name: str, email: str):
    return UserService.create_user(name, email)


# 模拟 API 调用
print(f"\n  GET /users/1:")
print(f"    {api_get_user(1)}")

print(f"\n  GET /users/999:")
print(f"    {api_get_user(999)}")

print(f"\n  POST /users (邮箱冲突):")
print(f"    {api_create_user('赵六', 'ls@qq.com')}")

print(f"\n  POST /users (正常):")
print(f"    {api_create_user('赵六', 'zl@qq.com')}")


# ============================================================
# 第四部分：异常中携带上下文信息
# ============================================================

print("\n" + "=" * 55)
print("第四部分：异常中携带上下文信息")
print("=" * 55)


class ValidationError(AppError):
    """参数验证失败，携带详细的字段错误"""
    def __init__(self, errors: dict):
        self.errors = errors
        msg = f"参数验证失败: {len(errors)} 个错误"
        super().__init__(msg, code=422)

    def to_dict(self):
        return {
            "code": self.code,
            "error": self.message,
            "details": self.errors
        }


def validate_user_input(data: dict) -> dict:
    """验证用户输入"""
    errors = {}
    if not data.get("name"):
        errors["name"] = "姓名不能为空"
    elif len(data["name"]) < 2:
        errors["name"] = "姓名至少 2 个字符"

    if not data.get("email"):
        errors["email"] = "邮箱不能为空"
    elif "@" not in data["email"]:
        errors["email"] = "邮箱格式不正确"

    if data.get("age") is not None:
        if not isinstance(data["age"], int) or data["age"] < 0:
            errors["age"] = "年龄必须是非负整数"

    if errors:
        raise ValidationError(errors)
    return data


# 测试
test_inputs = [
    {"name": "张三", "email": "zs@qq.com", "age": 20},
    {"name": "", "email": "invalid", "age": -5},
    {"name": "A", "email": "", "age": "abc"},
]

for data in test_inputs:
    print(f"\n  验证: {data}")
    try:
        validate_user_input(data)
        print(f"    ✅ 验证通过")
    except ValidationError as e:
        print(f"    ❌ {e}")
        print(f"    详情: {e.to_dict()}")


print("\n" + "=" * 55)
print("✅ Demo 2 完成！")
print("=" * 55)
