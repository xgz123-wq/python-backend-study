"""
Demo 1: 变量与数据类型
对应理论文档: 1.变量与数据类型.md

本 Demo 演示 Python 四种基本数据类型、变量赋值、类型查看与转换。
运行后观察每个 print 输出，理解不同类型的行为差异。
"""

# ============================================================
# 第一部分：变量赋值
# ============================================================

print("=" * 50)
print("第一部分：变量赋值")
print("=" * 50)

# 基本赋值
name = "张三"
age = 20
price = 19.99
is_student = True

print(f"姓名: {name}")
print(f"年龄: {age}")
print(f"价格: {price}")
print(f"是学生: {is_student}")

# 多变量赋值
a, b, c = 1, 2, 3
print(f"\n多变量赋值: a={a}, b={b}, c={c}")

# 变量交换
a, b = b, a
print(f"交换后: a={a}, b={b}")

# 变量是"标签"不是"盒子"
print("\n--- 变量是引用（标签），不是复制（盒子）---")
list_a = [1, 2, 3]
list_b = list_a        # list_b 和 list_a 指向同一个列表
list_b.append(4)
print(f"list_a = {list_a}")   # [1, 2, 3, 4] ← list_a 也变了！
print(f"list_b = {list_b}")   # [1, 2, 3, 4]
print(f"它们是同一个对象吗？ {list_a is list_b}")  # True

# 正确的复制方式
list_c = list_a.copy()  # 或 list_a[:]
list_c.append(5)
print(f"\n复制后修改 list_c:")
print(f"list_a = {list_a}")   # [1, 2, 3, 4] ← 不受影响
print(f"list_c = {list_c}")   # [1, 2, 3, 4, 5]


# ============================================================
# 第二部分：四种基本数据类型
# ============================================================

print("\n" + "=" * 50)
print("第二部分：四种基本数据类型")
print("=" * 50)

# --- int 整数 ---
print("\n--- int 整数 ---")
a = 42
b = -10
big = 1_000_000          # 下划线分隔，提高可读性
print(f"a = {a}, type = {type(a)}")
print(f"大数字: {big}")

# 整数运算
print(f"10 / 3  = {10 / 3}")     # 3.3333 普通除法
print(f"10 // 3 = {10 // 3}")    # 3      整除
print(f"10 % 3  = {10 % 3}")     # 1      取余
print(f"2 ** 10 = {2 ** 10}")    # 1024   幂运算

# --- float 浮点数 ---
print("\n--- float 浮点数 ---")
pi = 3.14159
print(f"pi = {pi}, type = {type(pi)}")

# ⚠️ 经典坑：浮点数精度问题
print(f"\n0.1 + 0.2 = {0.1 + 0.2}")          # 不等于 0.3！
print(f"0.1 + 0.2 == 0.3 ? {0.1 + 0.2 == 0.3}")  # False

# 解决方案
from decimal import Decimal
result = Decimal('0.1') + Decimal('0.2')
print(f"Decimal: 0.1 + 0.2 = {result}")      # 0.3 ✅

# --- str 字符串 ---
print("\n--- str 字符串 ---")
s = "Hello, Python"
print(f"字符串: {s}")
print(f"长度: {len(s)}")
print(f"大写: {s.upper()}")
print(f"小写: {s.lower()}")
print(f"拆分: {s.split(', ')}")
print(f"替换: {s.replace('Python', 'World')}")
print(f"是否以Hello开头: {s.startswith('Hello')}")

# 字符串不可变
# s[0] = "h"  # ← 取消注释会报错 TypeError

# --- bool 布尔值 ---
print("\n--- bool 布尔值 ---")
print(f"True 的类型: {type(True)}")
print(f"True + True = {True + True}")   # 2，因为 True = 1

# 假值演示
print("\n哪些值被视为 False?")
falsy_values = [False, 0, 0.0, "", [], {}, (), set(), None]
for val in falsy_values:
    print(f"  bool({str(val):>8}) = {bool(val)}")


# ============================================================
# 第三部分：类型查看与转换
# ============================================================

print("\n" + "=" * 50)
print("第三部分：类型查看与转换")
print("=" * 50)

# type() 查看类型
print(f"type(42)      = {type(42)}")
print(f"type(3.14)    = {type(3.14)}")
print(f"type('hello') = {type('hello')}")
print(f"type(True)    = {type(True)}")

# isinstance() 判断类型
print(f"\nisinstance(42, int)    = {isinstance(42, int)}")
print(f"isinstance(True, int) = {isinstance(True, int)}")  # True! bool 是 int 的子类

# 类型转换
print("\n--- 类型转换 ---")
print(f"int('42')     = {int('42')}")       # str → int
print(f"str(100)      = {str(100)}")        # int → str
print(f"float('3.14') = {float('3.14')}")   # str → float
print(f"int(3.9)      = {int(3.9)}")        # float → int（截断！）
print(f"round(3.5)    = {round(3.5)}")      # 四舍五入


# ============================================================
# 第四部分：None 类型
# ============================================================

print("\n" + "=" * 50)
print("第四部分：None 类型")
print("=" * 50)

result = None
print(f"result = {result}")
print(f"type(None) = {type(None)}")

# 用 is 判断 None
if result is None:
    print("result 是 None（还没有值）")

# 函数默认返回 None
def say_hello(name):
    print(f"你好, {name}")

ret = say_hello("张三")
print(f"函数返回值: {ret}")  # None


print("\n" + "=" * 50)
print("✅ Demo 1 完成！")
print("=" * 50)
