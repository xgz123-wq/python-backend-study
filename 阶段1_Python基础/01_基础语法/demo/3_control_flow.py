"""
Demo 3: 条件判断、循环与推导式
对应理论文档: 3.条件判断与循环.md

本 Demo 演示 if 条件判断、for/while 循环、推导式等控制流语法。
"""

# ============================================================
# 第一部分：条件判断 if
# ============================================================

print("=" * 50)
print("第一部分：条件判断 if")
print("=" * 50)

# 基本 if-elif-else
age = 20
if age >= 18:
    print(f"年龄 {age}: 成年人")
elif age >= 12:
    print(f"年龄 {age}: 青少年")
else:
    print(f"年龄 {age}: 儿童")

# 逻辑运算
print("\n--- 逻辑运算 ---")
score = 85
has_certificate = True

if score >= 80 and has_certificate:
    print("条件满足：成绩 >= 80 且有证书")

if score >= 90 or has_certificate:
    print("条件满足：成绩 >= 90 或有证书（至少一个为 True）")

if not (score < 60):
    print("没有不及格")

# 三元表达式
status = "及格" if score >= 60 else "不及格"
print(f"\n三元表达式: {score}分 → {status}")

# 真值判断技巧
print("\n--- 真值判断技巧 ---")
name = ""
users = []
result = None

# Pythonic 写法
if not name:
    print("name 为空")
if not users:
    print("users 列表为空")
if result is None:
    print("result 是 None")


# ============================================================
# 第二部分：for 循环
# ============================================================

print("\n" + "=" * 50)
print("第二部分：for 循环")
print("=" * 50)

# 遍历列表
fruits = ["苹果", "香蕉", "橘子"]
print("遍历列表:")
for fruit in fruits:
    print(f"  {fruit}")

# range() 生成数字序列
print("\nrange(5):", end=" ")
for i in range(5):
    print(i, end=" ")
print()

print("range(1, 6):", end=" ")
for i in range(1, 6):
    print(i, end=" ")
print()

print("range(0, 10, 2):", end=" ")
for i in range(0, 10, 2):
    print(i, end=" ")
print()

# enumerate() —— 同时获取索引和值
print("\nenumerate() 遍历:")
for i, fruit in enumerate(fruits, start=1):
    print(f"  {i}. {fruit}")

# zip() —— 并行遍历
print("\nzip() 并行遍历:")
names = ["张三", "李四", "王五"]
scores = [85, 92, 78]
for name, score in zip(names, scores):
    print(f"  {name}: {score}分")

# 遍历字典
print("\n遍历字典:")
user = {"name": "张三", "age": 20, "city": "北京"}
for key, value in user.items():
    print(f"  {key}: {value}")


# ============================================================
# 第三部分：while 循环
# ============================================================

print("\n" + "=" * 50)
print("第三部分：while 循环")
print("=" * 50)

# 基本 while
print("倒计时:")
count = 5
while count > 0:
    print(f"  {count}...")
    count -= 1
print("  发射！🚀")

# break 和 continue
print("\nbreak 示例（遇到 5 停止）:")
for i in range(10):
    if i == 5:
        break
    print(f"  {i}", end="")
print()

print("\ncontinue 示例（跳过偶数）:")
for i in range(10):
    if i % 2 == 0:
        continue
    print(f"  {i}", end="")
print()

# for-else
print("\nfor-else 示例：")
target = 7
for i in range(10):
    if i == target:
        print(f"  找到了 {target}！")
        break
else:
    print(f"  没找到 {target}")   # 只在循环没被 break 时执行


# ============================================================
# 第四部分：推导式
# ============================================================

print("\n" + "=" * 50)
print("第四部分：推导式")
print("=" * 50)

# 列表推导式
print("--- 列表推导式 ---")
squares = [i ** 2 for i in range(10)]
print(f"平方数: {squares}")

evens = [i for i in range(20) if i % 2 == 0]
print(f"偶数: {evens}")

labels = ["偶" if i % 2 == 0 else "奇" for i in range(6)]
print(f"奇偶标签: {labels}")

# 字典推导式
print("\n--- 字典推导式 ---")
squares_dict = {i: i**2 for i in range(6)}
print(f"平方字典: {squares_dict}")

# 键值互换
original = {"a": 1, "b": 2, "c": 3}
swapped = {v: k for k, v in original.items()}
print(f"键值互换: {original} → {swapped}")

# 集合推导式
print("\n--- 集合推导式 ---")
words = ["Hello", "HELLO", "hello", "World", "WORLD"]
unique = {w.lower() for w in words}
print(f"去重后: {unique}")


# ============================================================
# 第五部分：实用技巧
# ============================================================

print("\n" + "=" * 50)
print("第五部分：实用技巧")
print("=" * 50)

# 内置函数简化循环
nums = [3, 1, 4, 1, 5, 9, 2, 6]
print(f"列表: {nums}")
print(f"总和: {sum(nums)}")
print(f"最大: {max(nums)}")
print(f"最小: {min(nums)}")

# all() / any()
scores = [80, 90, 75, 88, 92]
print(f"\n成绩: {scores}")
print(f"全部及格(>=60)? {all(s >= 60 for s in scores)}")
print(f"有人满分(100)? {any(s == 100 for s in scores)}")

# 九九乘法表
print("\n--- 九九乘法表 ---")
for i in range(1, 10):
    for j in range(1, i + 1):
        print(f"{j}×{i}={i*j:2d}", end="  ")
    print()


print("\n" + "=" * 50)
print("✅ Demo 3 完成！")
print("=" * 50)
