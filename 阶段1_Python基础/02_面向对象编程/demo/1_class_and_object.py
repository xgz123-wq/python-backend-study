"""
Demo 1: 类与对象
对应理论文档: 1.类与对象.md

演示类的定义、__init__ 构造方法、实例属性与类属性、
三种方法类型（实例方法/类方法/静态方法）。
"""

# ============================================================
# 第一部分：定义类和创建对象
# ============================================================

print("=" * 55)
print("第一部分：定义类和创建对象")
print("=" * 55)


class Dog:
    """狗类，演示基本的类定义"""

    # 类属性：所有对象共享
    species = "Canis familiaris"
    count = 0    # 统计创建了多少只狗

    def __init__(self, name, age, breed):
        # 实例属性：每个对象独有
        self.name = name
        self.age = age
        self.breed = breed
        Dog.count += 1    # 每创建一只狗，计数 +1

    # 实例方法：操作实例数据，第一个参数是 self
    def bark(self):
        print(f"{self.name} 说：汪汪！")

    def info(self):
        return f"{self.name}（{self.breed}），{self.age}岁"

    def birthday(self):
        """生日，年龄 +1"""
        self.age += 1
        print(f"{self.name} 过生日了！现在 {self.age} 岁")

    # 类方法：操作类数据，第一个参数是 cls
    @classmethod
    def get_count(cls):
        return f"目前共有 {cls.count} 只狗"

    # 静态方法：工具函数，不操作实例或类数据
    @staticmethod
    def is_adult(age):
        return age >= 2

    def __str__(self):
        return f"Dog({self.name}, {self.age}岁, {self.breed})"

    def __repr__(self):
        return f"Dog(name='{self.name}', age={self.age}, breed='{self.breed}')"


# 创建对象（实例化）
dog1 = Dog("旺财", 3, "金毛")
dog2 = Dog("小白", 1, "柯基")
dog3 = Dog("黑豹", 5, "拉布拉多")

print(f"dog1: {dog1}")
print(f"dog2: {dog2}")
print(f"repr: {repr(dog1)}")

# 调用实例方法
dog1.bark()
print(dog1.info())
dog2.birthday()

# 访问类属性（通过实例和类都可以）
print(f"\n物种: {dog1.species}")          # 通过实例访问类属性
print(f"物种: {Dog.species}")            # 通过类访问类属性

# 调用类方法
print(Dog.get_count())

# 调用静态方法
print(f"\n{dog1.name} 成年了吗? {Dog.is_adult(dog1.age)}")
print(f"{dog2.name} 成年了吗? {Dog.is_adult(dog2.age)}")


# ============================================================
# 第二部分：类属性 vs 实例属性 - 陷阱演示
# ============================================================

print("\n" + "=" * 55)
print("第二部分：类属性 vs 实例属性（注意陷阱！）")
print("=" * 55)


class Counter:
    total = 0    # 类属性


c1 = Counter()
c2 = Counter()

# 通过类修改类属性：所有实例都受影响
Counter.total = 100
print(f"修改类属性后: c1.total={c1.total}, c2.total={c2.total}")    # 都是 100

# ⚠️ 陷阱：通过实例"修改"类属性，实际上是创建了实例属性
c1.total = 999    # 给 c1 创建了一个实例属性，遮蔽了类属性
print(f"c1.total={c1.total}")    # 999（实例属性）
print(f"c2.total={c2.total}")    # 100（类属性，没变）
print(f"Counter.total={Counter.total}")    # 100（类属性，没变）


# ============================================================
# 第三部分：工厂类方法 - 提供多种创建方式
# ============================================================

print("\n" + "=" * 55)
print("第三部分：工厂类方法")
print("=" * 55)


class Date:
    def __init__(self, year, month, day):
        self.year = year
        self.month = month
        self.day = day

    @classmethod
    def from_string(cls, date_str):
        """从 'YYYY-MM-DD' 字符串创建"""
        year, month, day = map(int, date_str.split("-"))
        return cls(year, month, day)

    @classmethod
    def today(cls):
        """创建今天的日期"""
        import datetime
        t = datetime.date.today()
        return cls(t.year, t.month, t.day)

    def __str__(self):
        return f"{self.year}-{self.month:02d}-{self.day:02d}"

    def __repr__(self):
        return f"Date({self.year}, {self.month}, {self.day})"


d1 = Date(2024, 1, 15)                 # 普通方式
d2 = Date.from_string("2024-03-20")   # 工厂方法：从字符串
d3 = Date.today()                      # 工厂方法：今天

print(f"普通: {d1}")
print(f"从字符串: {d2}")
print(f"今天: {d3}")


# ============================================================
# 第四部分：后端场景模拟 - 用户服务
# ============================================================

print("\n" + "=" * 55)
print("第四部分：后端场景 - 用户服务类")
print("=" * 55)


class UserService:
    """模拟后端用户服务层"""

    _users = {}       # 类属性：模拟数据库
    _next_id = 1

    def __init__(self):
        pass

    def create(self, name, email):
        """创建用户"""
        user_id = UserService._next_id
        UserService._users[user_id] = {
            "id": user_id,
            "name": name,
            "email": email,
            "active": True
        }
        UserService._next_id += 1
        print(f"  创建用户: id={user_id}, name={name}")
        return user_id

    def get(self, user_id):
        """查询用户"""
        return UserService._users.get(user_id)

    def delete(self, user_id):
        """软删除（标记为非活跃）"""
        if user_id in UserService._users:
            UserService._users[user_id]["active"] = False
            print(f"  删除用户 id={user_id}")

    @classmethod
    def count(cls):
        """活跃用户数量"""
        return sum(1 for u in cls._users.values() if u["active"])

    @staticmethod
    def is_valid_email(email):
        """验证邮箱格式"""
        return "@" in email and "." in email.split("@")[-1]


# 使用
svc = UserService()
id1 = svc.create("张三", "zhangsan@qq.com")
id2 = svc.create("李四", "lisi@163.com")
id3 = svc.create("王五", "wangwu_invalid")  # 邮箱无效，但还是存了（演示用）

print(f"\n  查询 id={id1}: {svc.get(id1)}")
print(f"  活跃用户数: {UserService.count()}")

svc.delete(id3)
print(f"  删除后活跃用户数: {UserService.count()}")

print(f"\n  邮箱验证:")
print(f"    zhangsan@qq.com: {UserService.is_valid_email('zhangsan@qq.com')}")
print(f"    invalid_email:   {UserService.is_valid_email('invalid_email')}")


print("\n" + "=" * 55)
print("✅ Demo 1 完成！")
print("=" * 55)
