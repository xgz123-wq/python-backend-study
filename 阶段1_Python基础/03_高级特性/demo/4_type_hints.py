"""
Demo 4: 类型提示
对应理论文档: 4.类型提示.md

演示基本类型标注、容器类型标注、Optional/Union、
Callable、TypeAlias、TypeVar 泛型、Protocol，
以及后端 Pydantic 风格的数据验证预告。
"""

from typing import (
    Optional, Union, Any, Callable,
    TypeVar, Protocol, TypeAlias
)

# ============================================================
# 第一部分：基本类型标注
# ============================================================

print("=" * 55)
print("第一部分：基本类型标注")
print("=" * 55)

# 变量标注
name: str = "张三"
age: int = 20
price: float = 9.99
is_active: bool = True

print(f"  name: {name} (类型: {type(name).__name__})")
print(f"  age: {age} (类型: {type(age).__name__})")
print(f"  price: {price} (类型: {type(price).__name__})")
print(f"  is_active: {is_active} (类型: {type(is_active).__name__})")


# 函数参数和返回值
def greet(name: str) -> str:
    return f"你好，{name}"

def add(a: int, b: int) -> int:
    return a + b

def log(message: str) -> None:
    print(f"  [LOG] {message}")

print(f"\n  greet('李四') = {greet('李四')}")
print(f"  add(3, 5) = {add(3, 5)}")
log("服务启动成功")


# 注意：类型提示不是运行时强制的！
result = add("hello", " world")    # 不会报错！
print(f"\n  ⚠️ add('hello', ' world') = {result}")
print(f"  类型提示不影响运行，只是给 IDE 和 mypy 看的")


# ============================================================
# 第二部分：容器类型标注
# ============================================================

print("\n" + "=" * 55)
print("第二部分：容器类型标注")
print("=" * 55)

# Python 3.9+ 直接用小写内置类型
names: list[str] = ["张三", "李四", "王五"]
scores: dict[str, int] = {"张三": 90, "李四": 85}
point: tuple[int, int] = (10, 20)
ids: tuple[int, ...] = (1, 2, 3, 4, 5)    # 不定长元组
tags: set[str] = {"python", "backend", "fastapi"}

print(f"  names: {names}")
print(f"  scores: {scores}")
print(f"  point: {point}")
print(f"  ids: {ids}")
print(f"  tags: {tags}")


# 嵌套类型
users: list[dict[str, str | int]] = [
    {"name": "张三", "age": 20},
    {"name": "李四", "age": 25},
]
print(f"\n  嵌套类型 users: {users}")


# 函数中使用容器类型
def get_top_students(
    scores: dict[str, int],
    threshold: int = 85
) -> list[str]:
    """返回分数达到阈值的学生名单"""
    return [name for name, score in scores.items() if score >= threshold]

top = get_top_students({"张三": 90, "李四": 85, "王五": 70})
print(f"  优秀学生: {top}")


# ============================================================
# 第三部分：Optional 和 Union
# ============================================================

print("\n" + "=" * 55)
print("第三部分：Optional 和 Union")
print("=" * 55)


# Optional[X] = X | None
def find_user(user_id: int) -> Optional[dict]:
    """查找用户，找不到返回 None"""
    users = {
        1: {"name": "张三", "email": "zs@qq.com"},
        2: {"name": "李四", "email": "ls@qq.com"},
    }
    return users.get(user_id)

user1 = find_user(1)
user3 = find_user(999)
print(f"  find_user(1)   = {user1}")
print(f"  find_user(999) = {user3}")


# Union[X, Y] = X | Y
def format_id(id_value: Union[int, str]) -> str:
    """接受 int 或 str 类型的 ID"""
    return f"ID-{id_value}"

print(f"\n  format_id(42)      = {format_id(42)}")
print(f"  format_id('abc')   = {format_id('abc')}")


# Python 3.10+ 写法：用 | 代替 Union
def format_price(price: int | float) -> str:
    return f"¥{price:.2f}"

print(f"  format_price(99)   = {format_price(99)}")
print(f"  format_price(9.9)  = {format_price(9.9)}")


# ============================================================
# 第四部分：Callable — 函数类型标注
# ============================================================

print("\n" + "=" * 55)
print("第四部分：Callable — 函数类型标注")
print("=" * 55)


def apply(
    func: Callable[[int, int], int],
    a: int,
    b: int
) -> int:
    """接受一个函数作为参数并调用它"""
    return func(a, b)

print(f"  apply(add, 3, 4) = {apply(add, 3, 4)}")
print(f"  apply(lambda x,y: x*y, 3, 4) = {apply(lambda x, y: x * y, 3, 4)}")


# 更复杂的例子：回调函数
def process_data(
    data: list[int],
    transform: Callable[[int], int],
    on_complete: Callable[[list[int]], None]
) -> list[int]:
    """处理数据：先变换，再回调"""
    result = [transform(x) for x in data]
    on_complete(result)
    return result

process_data(
    [1, 2, 3, 4, 5],
    transform=lambda x: x ** 2,
    on_complete=lambda r: print(f"  处理完成: {r}")
)


# ============================================================
# 第五部分：TypeAlias — 类型别名
# ============================================================

print("\n" + "=" * 55)
print("第五部分：TypeAlias — 类型别名")
print("=" * 55)

# 复杂类型起个别名，提高可读性
UserDict: TypeAlias = dict[str, str | int | bool]
UserList: TypeAlias = list[UserDict]
ApiResponse: TypeAlias = dict[str, str | int | list | None]

def get_users() -> UserList:
    return [
        {"name": "张三", "age": 20, "active": True},
        {"name": "李四", "age": 25, "active": False},
    ]

def make_response(data: Any, message: str = "ok") -> ApiResponse:
    return {"code": 200, "message": message, "data": data}

users = get_users()
response = make_response(users)
print(f"  用户列表: {users}")
print(f"  API 响应: {response}")


# ============================================================
# 第六部分：TypeVar — 泛型
# ============================================================

print("\n" + "=" * 55)
print("第六部分：TypeVar — 泛型")
print("=" * 55)

T = TypeVar("T")

def first(items: list[T]) -> T:
    """返回列表的第一个元素"""
    return items[0]

def last(items: list[T]) -> T:
    """返回列表的最后一个元素"""
    return items[-1]

# IDE 能推断出返回类型
str_first = first(["张三", "李四", "王五"])
int_first = first([100, 200, 300])
print(f"  first(['张三', ...]) = {str_first}")
print(f"  first([100, ...])    = {int_first}")
print(f"  last([100, 200, 300]) = {last([100, 200, 300])}")


# 限定类型范围
Number = TypeVar("Number", int, float)

def double(x: Number) -> Number:
    return x * 2

print(f"\n  double(5)    = {double(5)}")
print(f"  double(3.14) = {double(3.14)}")


# ============================================================
# 第七部分：Protocol — 结构化类型（鸭子类型）
# ============================================================

print("\n" + "=" * 55)
print("第七部分：Protocol — 鸭子类型的类型化")
print("=" * 55)


class Readable(Protocol):
    """协议：任何有 read() 方法的对象"""
    def read(self) -> str:
        ...


class Closeable(Protocol):
    """协议：任何有 close() 方法的对象"""
    def close(self) -> None:
        ...


def process_source(source: Readable) -> str:
    """接受任何可读对象"""
    return source.read().upper()


# 这些类没有继承 Readable，但有 read() 方法就行
class FileSource:
    def read(self) -> str:
        return "data from file"

class ApiSource:
    def read(self) -> str:
        return "data from api"

class DatabaseSource:
    def read(self) -> str:
        return "data from database"


print(f"  FileSource:     {process_source(FileSource())}")
print(f"  ApiSource:      {process_source(ApiSource())}")
print(f"  DatabaseSource: {process_source(DatabaseSource())}")
print(f"  ↑ 三个类没有任何继承关系，但都满足 Readable 协议")


# ============================================================
# 第八部分：后端场景 — 模拟 Pydantic 风格
# ============================================================

print("\n" + "=" * 55)
print("第八部分：后端场景 — 手动实现类型验证（预告 Pydantic）")
print("=" * 55)


def validate_user(
    name: str,
    email: str,
    age: int | None = None
) -> dict[str, str | int | None]:
    """模拟 Pydantic 的类型验证逻辑"""
    errors = []

    if not isinstance(name, str) or len(name) < 1:
        errors.append("name 必须是非空字符串")
    if not isinstance(email, str) or "@" not in email:
        errors.append("email 格式不正确")
    if age is not None and (not isinstance(age, int) or age < 0):
        errors.append("age 必须是非负整数")

    if errors:
        print(f"  ❌ 验证失败: {errors}")
        return {"valid": False, "errors": errors}

    print(f"  ✅ 验证通过")
    return {"valid": True, "name": name, "email": email, "age": age}


validate_user("张三", "zs@qq.com", 20)
validate_user("", "invalid", -5)

print(f"\n  📝 Pydantic 会自动完成上面的验证工作，")
print(f"     只需要定义类和类型标注，第四阶段会详细学习。")


print("\n" + "=" * 55)
print("✅ Demo 4 完成！")
print("=" * 55)
