"""
Demo 2: 继承与多态
对应理论文档: 2.继承与多态.md

演示继承的基本语法、super() 调用、方法重写、多态、封装和实际的后端异常体系。
"""

# ============================================================
# 第一部分：基本继承
# ============================================================

print("=" * 55)
print("第一部分：基本继承")
print("=" * 55)


class Animal:
    """父类：动物基类"""

    def __init__(self, name, age):
        self.name = name
        self.age = age

    def eat(self):
        print(f"  {self.name} 在吃东西")

    def sleep(self):
        print(f"  {self.name} 在睡觉")

    def speak(self):
        print(f"  {self.name} 发出声音")

    def __str__(self):
        return f"{self.__class__.__name__}(name={self.name}, age={self.age})"


class Dog(Animal):
    """子类：继承 Animal，新增 bark 方法，重写 speak"""

    def __init__(self, name, age, breed):
        super().__init__(name, age)    # 调用父类 __init__
        self.breed = breed

    def bark(self):                    # 子类新增方法
        print(f"  {self.name} 说：汪汪！")

    def speak(self):                   # 重写父类方法
        self.bark()


class Cat(Animal):
    def __init__(self, name, age, indoor=True):
        super().__init__(name, age)
        self.indoor = indoor

    def meow(self):
        print(f"  {self.name} 说：喵喵！")

    def speak(self):
        self.meow()


class Duck(Animal):
    def speak(self):
        print(f"  {self.name} 说：嘎嘎！")


# 基本继承演示
dog = Dog("旺财", 3, "金毛")
cat = Cat("咪咪", 2)

print(dog)          # 使用父类 __str__（子类没有重写）
dog.eat()           # 继承自父类
dog.sleep()         # 继承自父类
dog.bark()          # 子类自己的方法


# ============================================================
# 第二部分：多态
# ============================================================

print("\n" + "=" * 55)
print("第二部分：多态")
print("=" * 55)

print("  让所有动物说话（多态）：")
animals = [Dog("旺财", 3, "金毛"), Cat("咪咪", 2), Duck("唐老鸭", 1)]
for animal in animals:
    animal.speak()    # 同一方法，不同对象，不同行为

# 图形面积多态演示
print()


class Shape:
    def area(self) -> float:
        raise NotImplementedError("子类必须实现 area()")

    def perimeter(self) -> float:
        raise NotImplementedError("子类必须实现 perimeter()")

    def describe(self):
        name = self.__class__.__name__
        print(f"  {name}: 面积={self.area():.2f}, 周长={self.perimeter():.2f}")


class Circle(Shape):
    def __init__(self, radius):
        self.radius = radius

    def area(self):
        return 3.14159 * self.radius ** 2

    def perimeter(self):
        return 2 * 3.14159 * self.radius


class Rectangle(Shape):
    def __init__(self, width, height):
        self.width = width
        self.height = height

    def area(self):
        return self.width * self.height

    def perimeter(self):
        return 2 * (self.width + self.height)


class Triangle(Shape):
    def __init__(self, a, b, c):
        self.a, self.b, self.c = a, b, c

    def area(self):
        s = (self.a + self.b + self.c) / 2
        return (s * (s - self.a) * (s - self.b) * (s - self.c)) ** 0.5

    def perimeter(self):
        return self.a + self.b + self.c


shapes = [Circle(5), Rectangle(4, 6), Triangle(3, 4, 5)]
for shape in shapes:
    shape.describe()

total_area = sum(s.area() for s in shapes)
print(f"\n  总面积: {total_area:.2f}")


# ============================================================
# 第三部分：封装
# ============================================================

print("\n" + "=" * 55)
print("第三部分：封装（访问控制）")
print("=" * 55)


class BankAccount:
    def __init__(self, owner, balance=0):
        self.owner = owner          # 公开属性
        self._balance = balance     # 受保护（约定不直接访问）
        self.__pin = "1234"         # 私有（名称改写）

    def deposit(self, amount):
        if amount <= 0:
            print("  ❌ 存款金额必须大于 0")
            return
        self._balance += amount
        print(f"  存入 ¥{amount}，余额: ¥{self._balance}")

    def withdraw(self, amount, pin):
        if pin != self.__pin:
            print("  ❌ PIN 错误")
            return
        if amount > self._balance:
            print("  ❌ 余额不足")
            return
        self._balance -= amount
        print(f"  取出 ¥{amount}，余额: ¥{self._balance}")

    def get_balance(self):
        return self._balance

    def __str__(self):
        return f"BankAccount({self.owner}, ¥{self._balance})"


account = BankAccount("张三", 1000)
account.deposit(500)
account.withdraw(200, "1234")    # 正确 PIN
account.withdraw(200, "0000")    # 错误 PIN
account.withdraw(5000, "1234")   # 余额不足
print(f"  当前余额: ¥{account.get_balance()}")

# 私有属性的名称改写机制
print(f"\n  直接访问 _balance（约定保护，实际可以）: {account._balance}")
# print(account.__pin)    # ← 取消注释: AttributeError
print(f"  绕过改写访问 __pin: {account._BankAccount__pin}")    # 能访问但很麻烦


# ============================================================
# 第四部分：后端异常体系（继承实战）
# ============================================================

print("\n" + "=" * 55)
print("第四部分：后端异常体系（继承实战）")
print("=" * 55)


class AppException(Exception):
    """所有应用异常的基类"""
    def __init__(self, message: str, code: int = 400):
        super().__init__(message)
        self.message = message
        self.code = code

    def to_response(self):
        return {"code": self.code, "message": self.message}


class AuthException(AppException):
    def __init__(self, message="认证失败，请重新登录"):
        super().__init__(message, code=401)


class PermissionException(AppException):
    def __init__(self, message="权限不足"):
        super().__init__(message, code=403)


class NotFoundException(AppException):
    def __init__(self, resource="资源"):
        super().__init__(f"{resource}不存在", code=404)


class ValidationException(AppException):
    def __init__(self, field, reason):
        super().__init__(f"字段 '{field}' 验证失败: {reason}", code=422)


def handle_request(action):
    """模拟请求处理，统一捕获所有应用异常"""
    try:
        action()
    except AppException as e:
        # 统一的错误响应格式
        print(f"  ❌ HTTP {e.code}: {e.message}")


print("  模拟各种异常场景：")
handle_request(lambda: (_ for _ in ()).throw(AuthException()))
handle_request(lambda: (_ for _ in ()).throw(PermissionException("需要管理员权限")))
handle_request(lambda: (_ for _ in ()).throw(NotFoundException("用户")))
handle_request(lambda: (_ for _ in ()).throw(ValidationException("email", "格式不正确")))


# ============================================================
# 第五部分：isinstance / issubclass
# ============================================================

print("\n" + "=" * 55)
print("第五部分：isinstance / issubclass")
print("=" * 55)

dog = Dog("旺财", 3, "金毛")

print(f"  isinstance(dog, Dog)    = {isinstance(dog, Dog)}")
print(f"  isinstance(dog, Animal) = {isinstance(dog, Animal)}")   # True！继承关系
print(f"  isinstance(dog, Cat)    = {isinstance(dog, Cat)}")

print(f"\n  issubclass(Dog, Animal) = {issubclass(Dog, Animal)}")
print(f"  issubclass(Cat, Dog)    = {issubclass(Cat, Dog)}")

# 多态中常用 isinstance 做类型检查
def process_animal(animal):
    if isinstance(animal, Dog):
        animal.bark()
    elif isinstance(animal, Cat):
        animal.meow()
    else:
        animal.speak()

print("\n  类型检查处理：")
for a in [Dog("旺财", 3, "金毛"), Cat("咪咪", 2), Duck("唐老鸭", 1)]:
    process_animal(a)


print("\n" + "=" * 55)
print("✅ Demo 2 完成！")
print("=" * 55)
