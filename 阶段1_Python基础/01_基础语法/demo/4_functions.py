"""
Demo 4: 函数定义与参数
对应理论文档: 4.函数.md

本 Demo 演示函数定义、各种参数类型、返回值、作用域和 lambda。
"""

# ============================================================
# 第一部分：基本函数定义
# ============================================================

print("=" * 50)
print("第一部分：基本函数定义")
print("=" * 50)

def greet(name):
    """向用户打招呼"""
    return f"你好, {name}!"

print(greet("张三"))
print(greet("李四"))

# 无返回值的函数
def print_separator(char="=", length=40):
    """打印分隔线"""
    print(char * length)

print_separator()
print_separator("-", 30)
print_separator(char="*", length=20)


# ============================================================
# 第二部分：参数类型
# ============================================================

print("\n" + "=" * 50)
print("第二部分：参数类型")
print("=" * 50)

# --- 位置参数 vs 关键字参数 ---
print("--- 位置参数 vs 关键字参数 ---")

def create_user(name, age, city):
    return {"name": name, "age": age, "city": city}

# 位置参数：按顺序
user1 = create_user("张三", 20, "北京")
print(f"位置参数: {user1}")

# 关键字参数：指定名称，顺序无所谓
user2 = create_user(city="上海", name="李四", age=22)
print(f"关键字参数: {user2}")

# --- 默认参数 ---
print("\n--- 默认参数 ---")

def connect_db(host="localhost", port=3306, db="test"):
    """模拟数据库连接"""
    print(f"连接数据库: {host}:{port}/{db}")

connect_db()                          # 全部使用默认值
connect_db("192.168.1.100")           # 只改 host
connect_db(port=5432, db="myapp")     # 改 port 和 db

# ⚠️ 默认参数的坑
print("\n--- ⚠️ 默认参数的坑 ---")

# ❌ 错误示范：可变对象作为默认值
def bad_add_item(item, items=[]):
    items.append(item)
    return items

print(f"第一次: {bad_add_item('a')}")   # ['a']
print(f"第二次: {bad_add_item('b')}")   # ['a', 'b'] ← 共享了同一个列表！

# ✅ 正确做法
def good_add_item(item, items=None):
    if items is None:
        items = []
    items.append(item)
    return items

print(f"\n正确 - 第一次: {good_add_item('a')}")   # ['a']
print(f"正确 - 第二次: {good_add_item('b')}")     # ['b'] ✅

# --- *args ---
print("\n--- *args（接收任意数量位置参数）---")

def my_sum(*args):
    print(f"  args = {args} (type: {type(args).__name__})")
    return sum(args)

print(f"my_sum(1, 2, 3) = {my_sum(1, 2, 3)}")
print(f"my_sum(1, 2, 3, 4, 5) = {my_sum(1, 2, 3, 4, 5)}")

# --- **kwargs ---
print("\n--- **kwargs（接收任意数量关键字参数）---")

def print_info(**kwargs):
    print(f"  kwargs = {kwargs} (type: {type(kwargs).__name__})")
    for key, value in kwargs.items():
        print(f"  {key}: {value}")

print_info(name="张三", age=20, city="北京")

# --- 混合使用 ---
print("\n--- 混合使用 ---")

def api_request(method, url, *args, timeout=30, **kwargs):
    """模拟 API 请求"""
    print(f"  方法: {method}")
    print(f"  URL: {url}")
    print(f"  额外参数: {args}")
    print(f"  超时: {timeout}s")
    print(f"  其他选项: {kwargs}")

api_request("GET", "/api/users", "v2", timeout=10, auth="Bearer xxx")


# ============================================================
# 第三部分：返回值
# ============================================================

print("\n" + "=" * 50)
print("第三部分：返回值")
print("=" * 50)

# 返回单个值
def square(n):
    return n ** 2

print(f"square(5) = {square(5)}")

# 返回多个值（元组）
def analyze_scores(scores):
    """分析成绩，返回 (最高分, 最低分, 平均分)"""
    return max(scores), min(scores), sum(scores) / len(scores)

scores = [85, 92, 78, 96, 70]
highest, lowest, average = analyze_scores(scores)
print(f"\n成绩: {scores}")
print(f"最高: {highest}, 最低: {lowest}, 平均: {average:.1f}")

# 没有 return 返回 None
def say_hello(name):
    print(f"你好, {name}")

result = say_hello("张三")
print(f"返回值: {result}")  # None


# ============================================================
# 第四部分：变量作用域
# ============================================================

print("\n" + "=" * 50)
print("第四部分：变量作用域")
print("=" * 50)

x = 10  # 全局变量

def func_a():
    x = 20  # 局部变量，与全局的 x 无关
    print(f"  func_a 内部 x = {x}")

func_a()
print(f"  全局 x = {x}")   # 仍然是 10

# global 关键字
def func_b():
    global x
    x = 30  # 修改全局变量

func_b()
print(f"  global 修改后 x = {x}")   # 30


# ============================================================
# 第五部分：Lambda 匿名函数
# ============================================================

print("\n" + "=" * 50)
print("第五部分：Lambda 匿名函数")
print("=" * 50)

# 基本用法
square = lambda x: x ** 2
print(f"lambda square(5) = {square(5)}")

add = lambda a, b: a + b
print(f"lambda add(3, 4) = {add(3, 4)}")

# 最常见用法：排序的 key
print("\n--- 排序应用 ---")
students = [
    {"name": "张三", "score": 80},
    {"name": "李四", "score": 95},
    {"name": "王五", "score": 70},
    {"name": "赵六", "score": 88},
]

# 按成绩排序
students_sorted = sorted(students, key=lambda s: s["score"])
print("按成绩升序:")
for s in students_sorted:
    print(f"  {s['name']}: {s['score']}")

students_sorted = sorted(students, key=lambda s: s["score"], reverse=True)
print("\n按成绩降序:")
for s in students_sorted:
    print(f"  {s['name']}: {s['score']}")


# ============================================================
# 第六部分：文档字符串
# ============================================================

print("\n" + "=" * 50)
print("第六部分：文档字符串")
print("=" * 50)

def calculate_bmi(weight: float, height: float) -> float:
    """
    计算 BMI 指数。
    
    Args:
        weight: 体重（公斤）
        height: 身高（米）
    
    Returns:
        BMI 指数值
    """
    return round(weight / height ** 2, 2)

bmi = calculate_bmi(70, 1.75)
print(f"BMI = {bmi}")

print(f"\n函数文档:\n{calculate_bmi.__doc__}")


print("\n" + "=" * 50)
print("✅ Demo 4 完成！")
print("=" * 50)
