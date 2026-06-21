"""
Demo 2: 迭代器与生成器
对应理论文档: 2.迭代器与生成器.md

演示可迭代对象与迭代器的区别、自定义迭代器、
yield 生成器、生成器表达式、yield from、
以及后端场景中的管道处理。
"""

import sys

# ============================================================
# 第一部分：可迭代对象 vs 迭代器
# ============================================================

print("=" * 55)
print("第一部分：可迭代对象 vs 迭代器")
print("=" * 55)

# list 是可迭代对象，但不是迭代器
nums = [10, 20, 30]
print(f"  nums 有 __iter__: {hasattr(nums, '__iter__')}")     # True
print(f"  nums 有 __next__: {hasattr(nums, '__next__')}")     # False

# 用 iter() 转成迭代器
it = iter(nums)
print(f"\n  迭代器 it 有 __iter__: {hasattr(it, '__iter__')}")  # True
print(f"  迭代器 it 有 __next__: {hasattr(it, '__next__')}")  # True

# 手动调用 next() 逐个取值
print(f"\n  next(it) = {next(it)}")   # 10
print(f"  next(it) = {next(it)}")     # 20
print(f"  next(it) = {next(it)}")     # 30
# next(it)  # 再调用会抛出 StopIteration


# for 循环的本质
print(f"\n  for 循环的本质演示：")
it2 = iter([100, 200, 300])
while True:
    try:
        item = next(it2)
        print(f"    取到: {item}")
    except StopIteration:
        print(f"    StopIteration → 循环结束")
        break


# ============================================================
# 第二部分：自定义迭代器
# ============================================================

print("\n" + "=" * 55)
print("第二部分：自定义迭代器")
print("=" * 55)


class Countdown:
    """倒计时迭代器"""
    def __init__(self, start):
        self.current = start

    def __iter__(self):
        return self

    def __next__(self):
        if self.current <= 0:
            raise StopIteration
        value = self.current
        self.current -= 1
        return value


print("  倒计时: ", end="")
for num in Countdown(5):
    print(num, end=" ")
print()


class Range:
    """模拟 range()，理解迭代器工作原理"""
    def __init__(self, start, stop, step=1):
        self.start = start
        self.stop = stop
        self.step = step

    def __iter__(self):
        current = self.start
        while current < self.stop:
            yield current    # 用 yield 简化 __next__ 的实现
            current += self.step


print("  自定义 Range(0, 10, 3): ", end="")
for num in Range(0, 10, 3):
    print(num, end=" ")
print()


# ============================================================
# 第三部分：生成器函数（yield）
# ============================================================

print("\n" + "=" * 55)
print("第三部分：生成器函数（yield）")
print("=" * 55)


def countdown_gen(n):
    """生成器版倒计时：比自定义迭代器简洁得多"""
    while n > 0:
        yield n
        n -= 1


gen = countdown_gen(5)
print(f"  类型: {type(gen)}")   # <class 'generator'>

print(f"  next: {next(gen)}")   # 5
print(f"  next: {next(gen)}")   # 4

print("  剩余: ", end="")
for num in gen:                  # 从上次暂停处继续
    print(num, end=" ")
print()


# yield 的暂停与恢复
print(f"\n  yield 执行流程:")

def step_by_step():
    print("    → 第一步")
    yield 1
    print("    → 第二步")
    yield 2
    print("    → 第三步")
    yield 3
    print("    → 结束")

gen2 = step_by_step()
print(f"  取值: {next(gen2)}")    # 打印"第一步"，返回 1
print(f"  取值: {next(gen2)}")    # 打印"第二步"，返回 2
print(f"  取值: {next(gen2)}")    # 打印"第三步"，返回 3


# ============================================================
# 第四部分：生成器表达式 vs 列表推导式
# ============================================================

print("\n" + "=" * 55)
print("第四部分：生成器表达式 vs 列表推导式（内存对比）")
print("=" * 55)

# 列表推导式：立即生成所有数据
list_comp = [x ** 2 for x in range(100000)]

# 生成器表达式：按需生成
gen_expr = (x ** 2 for x in range(100000))

print(f"  列表推导式内存: {sys.getsizeof(list_comp):>10,} 字节")
print(f"  生成器表达式内存: {sys.getsizeof(gen_expr):>8,} 字节")
print(f"  差距: {sys.getsizeof(list_comp) / sys.getsizeof(gen_expr):.0f} 倍")

# 生成器表达式也可以直接传给函数
total = sum(x ** 2 for x in range(100))
print(f"\n  前 100 个整数的平方和: {total}")


# ============================================================
# 第五部分：yield from — 委托生成器
# ============================================================

print("\n" + "=" * 55)
print("第五部分：yield from")
print("=" * 55)


def flatten(nested_list):
    """展平嵌套列表"""
    for item in nested_list:
        if isinstance(item, list):
            yield from flatten(item)    # 递归展平
        else:
            yield item


nested = [1, [2, 3], [4, [5, 6]], 7]
print(f"  原始: {nested}")
print(f"  展平: {list(flatten(nested))}")


def chain(*iterables):
    """串联多个可迭代对象"""
    for it in iterables:
        yield from it

result = list(chain([1, 2], "AB", (10, 20)))
print(f"  串联: {result}")


# ============================================================
# 第六部分：send() — 向生成器发送值
# ============================================================

print("\n" + "=" * 55)
print("第六部分：send()（了解即可）")
print("=" * 55)


def accumulator():
    """累加器：接收值并返回累计总和"""
    total = 0
    while True:
        value = yield total
        if value is None:
            break
        total += value


gen3 = accumulator()
next(gen3)              # 启动生成器
print(f"  send(10) → {gen3.send(10)}")    # 10
print(f"  send(20) → {gen3.send(20)}")    # 30
print(f"  send(30) → {gen3.send(30)}")    # 60
print(f"  send(5)  → {gen3.send(5)}")     # 65


# ============================================================
# 第七部分：后端场景 — 生成器管道
# ============================================================

print("\n" + "=" * 55)
print("第七部分：后端场景 — 日志分析管道")
print("=" * 55)

# 模拟日志数据（实际场景从文件读取）
FAKE_LOGS = [
    "2024-01-15 10:00:00 INFO  用户登录成功 user=zhangsan",
    "2024-01-15 10:00:01 ERROR 数据库连接超时 db=mysql",
    "2024-01-15 10:00:02 INFO  查询商品列表 count=50",
    "2024-01-15 10:00:03 ERROR 支付接口异常 code=500",
    "2024-01-15 10:00:04 WARN  缓存未命中 key=user:1001",
    "2024-01-15 10:00:05 ERROR 文件上传失败 size=10MB",
    "2024-01-15 10:00:06 INFO  订单创建成功 order_id=10086",
]


def read_logs(logs):
    """第一步：读取日志（模拟从文件/数据库读取）"""
    yield from logs


def filter_level(lines, level):
    """第二步：过滤指定级别"""
    for line in lines:
        if f" {level} " in line:
            yield line


def extract_message(lines):
    """第三步：提取消息内容"""
    for line in lines:
        parts = line.split(maxsplit=3)
        if len(parts) >= 4:
            yield parts[3]


# 管道串联：读取 → 过滤 ERROR → 提取消息
logs = read_logs(FAKE_LOGS)
errors = filter_level(logs, "ERROR")
messages = extract_message(errors)

print("  ERROR 日志消息：")
for msg in messages:
    print(f"    - {msg}")


# ============================================================
# 第八部分：坑 — 生成器只能遍历一次
# ============================================================

print("\n" + "=" * 55)
print("第八部分：坑 — 生成器只能遍历一次")
print("=" * 55)

gen4 = (x for x in range(5))
first_pass = list(gen4)
second_pass = list(gen4)

print(f"  第一次遍历: {first_pass}")    # [0, 1, 2, 3, 4]
print(f"  第二次遍历: {second_pass}")   # []（空了！）
print(f"  ⚠️ 生成器耗尽后不能重复使用，需要重新创建")


print("\n" + "=" * 55)
print("✅ Demo 2 完成！")
print("=" * 55)
