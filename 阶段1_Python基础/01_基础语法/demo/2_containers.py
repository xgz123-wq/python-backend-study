"""
Demo 2: 容器类型 - list / dict / tuple / set
对应理论文档: 2.容器类型.md

本 Demo 演示四种容器的创建、增删改查、遍历和实用技巧。
"""

# ============================================================
# 第一部分：列表 list
# ============================================================

print("=" * 50)
print("第一部分：列表 list")
print("=" * 50)

# 创建
fruits = ["苹果", "香蕉", "橘子", "葡萄", "西瓜"]
print(f"水果列表: {fruits}")

# 索引访问
print(f"\n第一个: {fruits[0]}")
print(f"最后一个: {fruits[-1]}")

# 切片
print(f"\n切片 [1:3]: {fruits[1:3]}")
print(f"前三个 [:3]: {fruits[:3]}")
print(f"反转 [::-1]: {fruits[::-1]}")

# 增删改查
print("\n--- 增删改查 ---")
fruits.append("芒果")
print(f"append 芒果: {fruits}")

fruits.insert(1, "草莓")
print(f"insert 草莓到位置1: {fruits}")

fruits.remove("草莓")
print(f"remove 草莓: {fruits}")

popped = fruits.pop()
print(f"pop 最后一个: {popped}, 剩余: {fruits}")

fruits[0] = "红苹果"
print(f"修改第一个: {fruits}")

print(f"'香蕉' in fruits? {'香蕉' in fruits}")
print(f"长度: {len(fruits)}")

# 排序
nums = [3, 1, 4, 1, 5, 9, 2, 6]
print(f"\n原始: {nums}")
print(f"sorted(): {sorted(nums)}")          # 不修改原列表
nums.sort()
print(f"sort()后: {nums}")                  # 原地排序
nums.sort(reverse=True)
print(f"降序: {nums}")


# ============================================================
# 第二部分：字典 dict
# ============================================================

print("\n" + "=" * 50)
print("第二部分：字典 dict")
print("=" * 50)

# 创建
user = {
    "name": "张三",
    "age": 20,
    "city": "北京"
}
print(f"用户信息: {user}")

# 访问
print(f"\n名字: {user['name']}")
print(f"get email: {user.get('email', '未设置')}")  # key 不存在返回默认值

# 增改
user["email"] = "zhangsan@qq.com"
user["age"] = 21
print(f"增加 email 并修改 age: {user}")

# 删除
del user["email"]
print(f"删除 email: {user}")

# 遍历
print("\n遍历字典:")
for key, value in user.items():
    print(f"  {key}: {value}")

# 嵌套字典（模拟 API 响应）
print("\n--- 嵌套字典（模拟 API 响应）---")
api_response = {
    "code": 200,
    "message": "success",
    "data": {
        "users": [
            {"id": 1, "name": "张三", "role": "admin"},
            {"id": 2, "name": "李四", "role": "user"},
        ],
        "total": 2
    }
}

# 访问嵌套数据
first_user = api_response["data"]["users"][0]
print(f"第一个用户: {first_user['name']}, 角色: {first_user['role']}")
print(f"用户总数: {api_response['data']['total']}")


# ============================================================
# 第三部分：元组 tuple
# ============================================================

print("\n" + "=" * 50)
print("第三部分：元组 tuple")
print("=" * 50)

# 创建
point = (3, 4)
rgb = (255, 128, 0)
single = (42,)    # 注意逗号！

print(f"坐标: {point}")
print(f"RGB: {rgb}")
print(f"单元素元组: {single}, type = {type(single)}")
print(f"不是元组:   {(42)}, type = {type((42))}")   # 只是整数

# 拆包
x, y = point
print(f"\n拆包: x={x}, y={y}")

# 不可变
print(f"\n元组不可变:")
print(f"  point[0] = {point[0]}")
# point[0] = 10  # ← 取消注释会报错 TypeError

# 函数返回多个值
def min_max(numbers):
    return min(numbers), max(numbers)

lo, hi = min_max([3, 1, 4, 1, 5, 9])
print(f"\nmin_max: 最小={lo}, 最大={hi}")


# ============================================================
# 第四部分：集合 set
# ============================================================

print("\n" + "=" * 50)
print("第四部分：集合 set")
print("=" * 50)

# 去重
nums = [1, 2, 2, 3, 3, 3, 4, 4, 4, 4]
unique = set(nums)
print(f"原始列表: {nums}")
print(f"去重后:   {unique}")
print(f"转回列表: {sorted(unique)}")

# 集合运算
print("\n--- 集合运算 ---")
a = {1, 2, 3, 4, 5}
b = {4, 5, 6, 7, 8}
print(f"a = {a}")
print(f"b = {b}")
print(f"并集 a | b = {a | b}")
print(f"交集 a & b = {a & b}")
print(f"差集 a - b = {a - b}")
print(f"对称差 a ^ b = {a ^ b}")

# 实际用途：快速判断是否存在
print("\n--- 快速判断（set 比 list 快得多）---")
allowed_methods = {"GET", "POST", "PUT", "DELETE"}
method = "POST"
print(f"'{method}' 是否允许? {method in allowed_methods}")


# ============================================================
# 第五部分：容器选择指南
# ============================================================

print("\n" + "=" * 50)
print("第五部分：容器选择指南")
print("=" * 50)

print("""
┌─────────────────────────────────────────┐
│ 需要存一组有序数据？                     │
│ ├── 需要修改？    → list                │
│ └── 不需要修改？  → tuple               │
│                                         │
│ 需要键值对映射？  → dict                │
│                                         │
│ 需要去重/集合运算？→ set                │
└─────────────────────────────────────────┘
""")


print("=" * 50)
print("✅ Demo 2 完成！")
print("=" * 50)
