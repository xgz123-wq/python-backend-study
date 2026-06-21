"""
Demo 3: 魔术方法
对应理论文档: 3.魔术方法.md

演示 __str__/__repr__、__len__/__bool__、__eq__/__lt__、
__getitem__/__contains__、__call__、__enter__/__exit__ 等核心魔术方法。
"""

# ============================================================
# 第一部分：__str__ 和 __repr__
# ============================================================

print("=" * 55)
print("第一部分：__str__ 和 __repr__")
print("=" * 55)


class Product:
    def __init__(self, name, price, stock):
        self.name = name
        self.price = price
        self.stock = stock

    def __str__(self):
        """给用户看：简洁友好"""
        return f"{self.name} - ¥{self.price:.2f}（库存 {self.stock}）"

    def __repr__(self):
        """给开发者看：能还原对象"""
        return f"Product(name='{self.name}', price={self.price}, stock={self.stock})"


p1 = Product("Python编程", 59.9, 100)
p2 = Product("FastAPI实战", 79.0, 50)

print(f"  str:  {p1}")              # 调用 __str__
print(f"  repr: {repr(p1)}")        # 调用 __repr__

products = [p1, p2]
print(f"  列表中显示: {products}")   # 列表中用 __repr__


# ============================================================
# 第二部分：__len__ 和 __bool__
# ============================================================

print("\n" + "=" * 55)
print("第二部分：__len__ 和 __bool__")
print("=" * 55)


class ShoppingCart:
    def __init__(self):
        self._items = []

    def add(self, product, qty=1):
        self._items.append({"product": product, "qty": qty})

    def __len__(self):
        """支持 len(cart)"""
        return len(self._items)

    def __bool__(self):
        """支持 if cart:（有商品为 True）"""
        return len(self._items) > 0

    def total(self):
        return sum(item["product"].price * item["qty"] for item in self._items)

    def __str__(self):
        if not self:
            return "购物车（空）"
        lines = [f"  购物车（{len(self)} 件商品）:"]
        for item in self._items:
            lines.append(f"    {item['product'].name} x{item['qty']}")
        lines.append(f"    合计: ¥{self.total():.2f}")
        return "\n".join(lines)


cart = ShoppingCart()

print(f"  len(cart) = {len(cart)}")
print(f"  bool(cart) = {bool(cart)}")
if not cart:
    print("  购物车是空的")

cart.add(p1, 2)
cart.add(p2, 1)
print(f"\n  len(cart) = {len(cart)}")
if cart:
    print("  购物车有商品")
print(cart)


# ============================================================
# 第三部分：__eq__ 和比较方法
# ============================================================

print("\n" + "=" * 55)
print("第三部分：比较方法 __eq__ / __lt__")
print("=" * 55)

from functools import total_ordering


@total_ordering  # 自动补全其他比较方法
class Student:
    def __init__(self, name, score):
        self.name = name
        self.score = score

    def __eq__(self, other):
        if not isinstance(other, Student):
            return NotImplemented
        return self.score == other.score

    def __lt__(self, other):
        if not isinstance(other, Student):
            return NotImplemented
        return self.score < other.score

    def __repr__(self):
        return f"Student({self.name}, {self.score})"


students = [
    Student("张三", 85),
    Student("李四", 92),
    Student("王五", 78),
    Student("赵六", 92),
]

s1, s2, s3, s4 = students
print(f"  s1={s1}, s2={s2}")
print(f"  s1 == s3? {s1 == s3}")   # False
print(f"  s2 == s4? {s2 == s4}")   # True（分数相同）
print(f"  s1 < s2?  {s1 < s2}")
print(f"  s2 > s1?  {s2 > s1}")    # total_ordering 自动生成

print(f"\n  排序:")
for s in sorted(students):
    print(f"    {s}")

print(f"\n  最高分: {max(students)}")
print(f"  最低分: {min(students)}")


# ============================================================
# 第四部分：__getitem__ / __setitem__ / __contains__
# ============================================================

print("\n" + "=" * 55)
print("第四部分：下标访问 __getitem__ / __setitem__ / __contains__")
print("=" * 55)


class Config:
    """支持字典式访问的配置类，带默认值和类型验证"""

    _DEFAULTS = {
        "host": "localhost",
        "port": 8000,
        "debug": False,
        "workers": 4,
    }

    def __init__(self, **kwargs):
        self._data = dict(self._DEFAULTS)
        self._data.update(kwargs)

    def __getitem__(self, key):
        if key not in self._data:
            raise KeyError(f"未知配置项: {key}")
        return self._data[key]

    def __setitem__(self, key, value):
        if key not in self._DEFAULTS:
            raise KeyError(f"不允许设置未知配置项: {key}")
        self._data[key] = value

    def __contains__(self, key):
        return key in self._data

    def __repr__(self):
        return f"Config({self._data})"


config = Config(port=3000, debug=True)

print(f"  config['host'] = {config['host']}")
print(f"  config['port'] = {config['port']}")

config['port'] = 5000
print(f"  修改后 port = {config['port']}")

print(f"  'debug' in config? {'debug' in config}")
print(f"  'secret' in config? {'secret' in config}")

try:
    config['unknown'] = "value"
except KeyError as e:
    print(f"  ❌ {e}")


# ============================================================
# 第五部分：__call__（可调用对象）
# ============================================================

print("\n" + "=" * 55)
print("第五部分：__call__（让对象像函数一样调用）")
print("=" * 55)


class RateLimiter:
    """速率限制器：限制函数调用频率"""

    def __init__(self, max_calls, period=60):
        self.max_calls = max_calls
        self.period = period
        self.calls = []

    def __call__(self, func_name="操作"):
        """每次调用时检查是否超限"""
        import time
        now = time.time()
        # 移除超出时间窗口的调用记录
        self.calls = [t for t in self.calls if now - t < self.period]

        if len(self.calls) >= self.max_calls:
            remaining = self.period - (now - self.calls[0])
            print(f"  ❌ 速率限制：{func_name} 请求过于频繁，请 {remaining:.0f}s 后重试")
            return False

        self.calls.append(now)
        print(f"  ✅ {func_name} 允许（已用 {len(self.calls)}/{self.max_calls}）")
        return True


limiter = RateLimiter(max_calls=3, period=60)

for i in range(5):
    limiter(f"请求#{i+1}")   # 像函数一样调用对象

# __call__ 的另一个常见用法：带状态的转换器
class Formatter:
    def __init__(self, prefix="", suffix=""):
        self.prefix = prefix
        self.suffix = suffix

    def __call__(self, text):
        return f"{self.prefix}{text}{self.suffix}"

warn = Formatter("⚠️ ", "")
error = Formatter("❌ ", "！")
print(f"\n  {warn('磁盘空间不足')}")
print(f"  {error('服务器错误')}")


# ============================================================
# 第六部分：__enter__ / __exit__（上下文管理器）
# ============================================================

print("\n" + "=" * 55)
print("第六部分：上下文管理器 __enter__ / __exit__")
print("=" * 55)


class Timer:
    """计时器上下文管理器"""

    def __init__(self, name="操作"):
        self.name = name

    def __enter__(self):
        import time
        self._start = time.time()
        print(f"  ⏱ 开始计时: {self.name}")
        return self    # as 后面的变量拿到的是这个返回值

    def __exit__(self, exc_type, exc_val, exc_tb):
        import time
        elapsed = time.time() - self._start
        if exc_type:
            print(f"  ❌ {self.name} 发生异常: {exc_val}")
        else:
            print(f"  ✅ {self.name} 完成，耗时: {elapsed*1000:.2f}ms")
        return False    # 不压制异常


# 正常使用
with Timer("数据处理") as t:
    result = sum(range(100000))
    print(f"    计算结果: {result}")

# 发生异常时 __exit__ 仍然执行
print()
try:
    with Timer("危险操作"):
        x = 1 / 0    # 会触发异常
except ZeroDivisionError:
    print("  已捕获除零异常")


# ============================================================
# 第七部分：Vector 类综合演示
# ============================================================

print("\n" + "=" * 55)
print("第七部分：Vector 向量类（综合魔术方法）")
print("=" * 55)


class Vector:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __repr__(self):
        return f"Vector({self.x}, {self.y})"

    def __add__(self, other):
        return Vector(self.x + other.x, self.y + other.y)

    def __sub__(self, other):
        return Vector(self.x - other.x, self.y - other.y)

    def __mul__(self, scalar):
        return Vector(self.x * scalar, self.y * scalar)

    def __rmul__(self, scalar):   # 支持 3 * v（scalar 在左边）
        return self.__mul__(scalar)

    def __abs__(self):
        return (self.x ** 2 + self.y ** 2) ** 0.5

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y

    def __bool__(self):
        return abs(self) != 0   # 零向量为 False


v1 = Vector(1, 2)
v2 = Vector(3, 4)

print(f"  v1 = {v1}")
print(f"  v2 = {v2}")
print(f"  v1 + v2 = {v1 + v2}")
print(f"  v2 - v1 = {v2 - v1}")
print(f"  v1 * 3  = {v1 * 3}")
print(f"  3 * v1  = {3 * v1}")      # __rmul__
print(f"  |v2|    = {abs(v2)}")
print(f"  v1 == v1? {v1 == v1}")


print("\n" + "=" * 55)
print("✅ Demo 3 完成！")
print("=" * 55)
