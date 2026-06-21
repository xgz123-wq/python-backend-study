"""
Demo 4: @property 装饰器
对应理论文档: 4.property装饰器.md

演示 @property 的 getter/setter/deleter、计算属性、数据验证、
懒加载等实际使用场景。
"""

# ============================================================
# 第一部分：基本 @property
# ============================================================

print("=" * 55)
print("第一部分：基本 @property（getter + setter）")
print("=" * 55)


class User:
    def __init__(self, name, age, email):
        self.name = name     # 触发 setter
        self.age = age       # 触发 setter
        self.email = email   # 触发 setter

    @property
    def age(self):
        return self._age

    @age.setter
    def age(self, value):
        if not isinstance(value, int):
            raise TypeError(f"年龄必须是整数，得到: {type(value).__name__}")
        if value < 0 or value > 150:
            raise ValueError(f"年龄超出合理范围: {value}")
        self._age = value

    @property
    def email(self):
        return self._email

    @email.setter
    def email(self, value):
        if not isinstance(value, str) or "@" not in value:
            raise ValueError(f"邮箱格式无效: {value}")
        self._email = value.lower().strip()   # 自动规范化：转小写、去空格

    def __repr__(self):
        return f"User(name={self.name!r}, age={self.age}, email={self.email!r})"


# 正常创建
user = User("张三", 25, "  ZhangSan@QQ.com  ")
print(f"  创建成功: {user}")
print(f"  邮箱已规范化: '{user.email}'")   # 自动变小写、去空格

# 修改属性（走 setter 验证）
user.age = 26
print(f"  修改年龄: {user.age}")

# 验证失败
print("\n  验证失败场景：")
for bad_age, desc in [(-1, "负数"), (200, "超大"), ("20", "字符串")]:
    try:
        user.age = bad_age
    except (ValueError, TypeError) as e:
        print(f"    ❌ age={bad_age!r}（{desc}）: {e}")

for bad_email in ["not-email", 123]:
    try:
        user.email = bad_email
    except (ValueError, TypeError) as e:
        print(f"    ❌ email={bad_email!r}: {e}")


# ============================================================
# 第二部分：计算属性（只读 @property）
# ============================================================

print("\n" + "=" * 55)
print("第二部分：计算属性（只读，始终与其他属性同步）")
print("=" * 55)


class Rectangle:
    def __init__(self, width, height):
        self.width = width       # 触发 setter
        self.height = height     # 触发 setter

    @property
    def width(self):
        return self._width

    @width.setter
    def width(self, value):
        if value <= 0:
            raise ValueError(f"宽度必须大于 0: {value}")
        self._width = value

    @property
    def height(self):
        return self._height

    @height.setter
    def height(self, value):
        if value <= 0:
            raise ValueError(f"高度必须大于 0: {value}")
        self._height = value

    @property
    def area(self):
        """计算属性：面积，自动由 width/height 推导"""
        return self._width * self._height

    @property
    def perimeter(self):
        """计算属性：周长"""
        return 2 * (self._width + self._height)

    @property
    def diagonal(self):
        """计算属性：对角线长度"""
        return (self._width ** 2 + self._height ** 2) ** 0.5

    def __repr__(self):
        return f"Rectangle({self._width} x {self._height})"


r = Rectangle(4, 6)
print(f"  矩形: {r}")
print(f"  面积: {r.area}")
print(f"  周长: {r.perimeter}")
print(f"  对角线: {r.diagonal:.2f}")

# 修改尺寸后，计算属性自动更新
r.width = 10
print(f"\n  修改宽度为 10 后:")
print(f"  面积: {r.area}")        # 自动更新，不需要重新计算
print(f"  周长: {r.perimeter}")


# ============================================================
# 第三部分：温度转换（双向 setter）
# ============================================================

print("\n" + "=" * 55)
print("第三部分：双向 property - 温度转换")
print("=" * 55)


class Temperature:
    """内部以摄氏度存储，对外提供三种温标"""

    def __init__(self, celsius=0):
        self.celsius = celsius   # 触发 setter，包含下限验证

    @property
    def celsius(self):
        return self._celsius

    @celsius.setter
    def celsius(self, value):
        if value < -273.15:
            raise ValueError(f"低于绝对零度: {value}°C")
        self._celsius = round(value, 4)

    @property
    def fahrenheit(self):
        return self._celsius * 9 / 5 + 32

    @fahrenheit.setter
    def fahrenheit(self, value):
        """设置华氏度时，自动换算为摄氏度存储"""
        self.celsius = (value - 32) * 5 / 9

    @property
    def kelvin(self):
        return self._celsius + 273.15

    @kelvin.setter
    def kelvin(self, value):
        self.celsius = value - 273.15

    def __repr__(self):
        return f"{self._celsius:.2f}°C / {self.fahrenheit:.2f}°F / {self.kelvin:.2f}K"


t = Temperature(100)
print(f"  沸点: {t}")

t.fahrenheit = 32   # 通过华氏度设置
print(f"  冰点: {t}")

t.kelvin = 0        # 通过开氏度设置（绝对零度）
print(f"  绝对零度: {t}")

try:
    t.celsius = -300
except ValueError as e:
    print(f"  ❌ {e}")


# ============================================================
# 第四部分：密码属性（安全场景）
# ============================================================

print("\n" + "=" * 55)
print("第四部分：密码属性（安全：只写不读）")
print("=" * 55)

import hashlib


class SecureUser:
    def __init__(self, username, password):
        self.username = username
        self.password = password    # 触发 setter，立即哈希

    @property
    def password(self):
        """永远不返回真实密码"""
        raise AttributeError("密码不可读取！请使用 verify_password() 方法")

    @password.setter
    def password(self, value):
        if len(value) < 8:
            raise ValueError("密码至少 8 位")
        # 存储哈希值，而非明文
        self._password_hash = hashlib.sha256(value.encode()).hexdigest()
        print(f"  密码已哈希存储（前 16 位）: {self._password_hash[:16]}...")

    def verify_password(self, password):
        """验证密码"""
        return hashlib.sha256(password.encode()).hexdigest() == self._password_hash

    def __repr__(self):
        return f"SecureUser(username={self.username!r})"


user = SecureUser("张三", "mypassword123")
print(f"  用户: {user}")
print(f"  验证 'mypassword123': {user.verify_password('mypassword123')}")
print(f"  验证 'wrongpassword': {user.verify_password('wrongpassword')}")

try:
    print(user.password)   # 尝试读取密码
except AttributeError as e:
    print(f"  ❌ {e}")


# ============================================================
# 第五部分：懒加载（延迟计算）
# ============================================================

print("\n" + "=" * 55)
print("第五部分：懒加载（第一次访问才计算）")
print("=" * 55)


class ArticleAnalyzer:
    """文章分析器，统计信息懒加载"""

    def __init__(self, text):
        self.text = text
        self._word_count = None
        self._word_freq = None

    @property
    def word_count(self):
        if self._word_count is None:
            print("  [计算中] 统计词数...")
            words = self.text.lower().split()
            self._word_count = len(words)
        return self._word_count

    @property
    def word_freq(self):
        if self._word_freq is None:
            print("  [计算中] 统计词频...")
            from collections import Counter
            words = self.text.lower().split()
            self._word_freq = Counter(words)
        return self._word_freq

    @property
    def top_words(self):
        """由 word_freq 推导，不需要单独缓存"""
        return self.word_freq.most_common(3)


text = "python is great python is fast python is fun and python is popular"
analyzer = ArticleAnalyzer(text)

print(f"  文章: {text[:40]}...")
print(f"\n  第一次访问 word_count:")
print(f"  词数 = {analyzer.word_count}")    # 触发计算
print(f"\n  第二次访问 word_count:")
print(f"  词数 = {analyzer.word_count}")    # 直接返回缓存

print(f"\n  第一次访问 word_freq:")
print(f"  高频词 = {analyzer.top_words}")   # 触发计算


print("\n" + "=" * 55)
print("✅ Demo 4 完成！")
print("=" * 55)
