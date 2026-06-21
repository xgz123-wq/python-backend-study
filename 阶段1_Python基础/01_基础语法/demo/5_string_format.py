"""
Demo 5: 字符串格式化
对应理论文档: 5.字符串格式化.md

本 Demo 演示 f-string、format()、% 三种格式化方式及实际应用场景。
"""

# ============================================================
# 第一部分：f-string（推荐 ⭐⭐⭐）
# ============================================================

print("=" * 50)
print("第一部分：f-string（推荐）")
print("=" * 50)

name = "张三"
age = 20
score = 95.678

# 基本用法
print(f"姓名: {name}")
print(f"明年 {age + 1} 岁")
print(f"状态: {'通过' if score >= 60 else '未通过'}")

# 格式控制
print(f"\n--- 格式控制 ---")
print(f"保留2位小数:  {score:.2f}")       # 95.68
print(f"百分比:       {0.856:.1%}")        # 85.6%
print(f"补零到5位:    {42:05d}")           # 00042
print(f"千分位:       {1234567:,}")        # 1,234,567

# 对齐
print(f"\n--- 对齐 ---")
print(f"|{'左对齐':<15}|")
print(f"|{'右对齐':>15}|")
print(f"|{'居中':^15}|")

# 实际应用：格式化表格
print(f"\n--- 格式化表格 ---")
items = [
    ("Python入门", 49.90),
    ("FastAPI实战", 79.00),
    ("数据库原理", 128.50),
]

print(f"{'商品名称':<15} {'价格':>10}")
print("-" * 27)
for item_name, price in items:
    print(f"{item_name:<15} ¥{price:>8.2f}")
total = sum(p for _, p in items)
print("-" * 27)
print(f"{'合计':<15} ¥{total:>8.2f}")

# 调试技巧 (Python 3.8+)
print(f"\n--- 调试技巧 ---")
x = 42
y = "hello"
print(f"{x = }")     # x = 42
print(f"{y = }")     # y = 'hello'
print(f"{len(y) = }")  # len(y) = 5


# ============================================================
# 第二部分：format() 方法
# ============================================================

print("\n" + "=" * 50)
print("第二部分：format() 方法")
print("=" * 50)

# 位置参数
print("我叫{}，今年{}岁".format("张三", 20))

# 索引参数
print("{0}喜欢{1}，{1}也喜欢{0}".format("张三", "李四"))

# 命名参数
print("姓名: {name}, 年龄: {age}".format(name="张三", age=20))

# 格式控制
print("保留2位: {:.2f}".format(3.14159))

# format 的独特优势：模板可以是变量
print("\n--- format 的独特优势 ---")
template = "欢迎 {name}，您的角色是 {role}"
# 模板可以在运行时决定
print(template.format(name="张三", role="管理员"))
print(template.format(name="李四", role="普通用户"))


# ============================================================
# 第三部分：% 格式化（旧式）
# ============================================================

print("\n" + "=" * 50)
print("第三部分：% 格式化（了解即可）")
print("=" * 50)

name = "张三"
age = 20
score = 95.5

print("我叫%s，今年%d岁，分数%.1f" % (name, age, score))
print("补零: %05d" % 42)
print("百分号: 完成了 %d%%" % 80)   # %% 输出 %


# ============================================================
# 第四部分：实际应用场景
# ============================================================

print("\n" + "=" * 50)
print("第四部分：实际应用场景")
print("=" * 50)

# 1. 日志输出
import datetime

print("--- 模拟日志输出 ---")
levels = ["INFO", "WARNING", "ERROR"]
messages = [
    "服务启动成功",
    "数据库连接池接近上限",
    "用户认证失败: token 过期"
]

timestamp = datetime.datetime.now()
for level, msg in zip(levels, messages):
    print(f"[{timestamp:%Y-%m-%d %H:%M:%S}] [{level:>7}] {msg}")

# 2. API 响应构造
print("\n--- 模拟 API 响应 ---")

def format_response(code, message, data=None):
    """构造统一的 API 响应"""
    return {
        "code": code,
        "message": message,
        "data": data
    }

# 成功响应
response = format_response(200, "查询成功", {"user_count": 42})
print(f"成功: {response}")

# 错误响应
user_id = 999
response = format_response(404, f"用户 {user_id} 不存在")
print(f"失败: {response}")

# 3. URL 构造
print("\n--- URL 构造 ---")
base_url = "https://api.example.com"
version = "v2"
resource = "users"
user_id = 42

url = f"{base_url}/{version}/{resource}/{user_id}"
print(f"完整 URL: {url}")

# 4. SQL 拼接的正确与错误方式
print("\n--- ⚠️ SQL 安全提醒 ---")
user_input = "admin"

# ❌ 危险！SQL 注入
bad_sql = f"SELECT * FROM users WHERE name = '{user_input}'"
print(f"❌ 危险 SQL: {bad_sql}")

# ✅ 安全！参数化查询（伪代码演示）
safe_sql = "SELECT * FROM users WHERE name = %s"
print(f"✅ 安全 SQL: {safe_sql}")
print(f"   参数: ({user_input},)")


# ============================================================
# 第五部分：三种方式对比
# ============================================================

print("\n" + "=" * 50)
print("第五部分：三种方式对比")
print("=" * 50)

print("""
┌──────────┬────────┬────────┬────────┬──────────┐
│ 方式     │ 可读性 │ 性能   │ 功能   │ 推荐度   │
├──────────┼────────┼────────┼────────┼──────────┤
│ f-string │ ⭐⭐⭐ │ ⭐⭐⭐ │ ⭐⭐⭐ │ 首选     │
│ format() │ ⭐⭐   │ ⭐⭐   │ ⭐⭐⭐ │ 模板场景 │
│ %        │ ⭐     │ ⭐⭐   │ ⭐⭐   │ 旧代码   │
└──────────┴────────┴────────┴────────┴──────────┘

结论：日常开发统一用 f-string！
""")


print("=" * 50)
print("✅ Demo 5 完成！")
print("=" * 50)
