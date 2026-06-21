# 面向对象编程（OOP）- Demo 学习指南

## 学习顺序

按编号顺序依次学习，每个 Demo 对应一个理论知识点。

---

### Demo 1: 类与对象（OOP 的基石）
**文件**: `1_class_and_object.py`

演示类定义、`__init__` 构造方法、实例属性与类属性的区别与陷阱，以及三种方法类型（实例方法/类方法/静态方法）的适用场景。结合后端用户服务类做实战演练。

**运行方式**: `python 1_class_and_object.py`
**前置依赖**: 无额外依赖

---

### Demo 2: 继承与多态（代码复用的核心）
**文件**: `2_inheritance_polymorphism.py`

演示父子类继承、`super()` 调用、方法重写（Override）、多态（同一接口不同实现）、封装（访问控制），以及实际的后端异常体系设计。重点关注 `isinstance` 和 `issubclass` 的使用。

**运行方式**: `python 2_inheritance_polymorphism.py`
**前置依赖**: 无额外依赖

---

### Demo 3: 魔术方法（融入 Python 语法）
**文件**: `3_magic_methods.py`

演示 `__str__`/`__repr__`、`__len__`/`__bool__`、`__eq__`/`__lt__`（配合 `@total_ordering`）、`__getitem__`/`__setitem__`/`__contains__`（下标操作）、`__call__`（可调用对象）、`__enter__`/`__exit__`（上下文管理器）。综合在 Vector 向量类中运用。

**运行方式**: `python 3_magic_methods.py`
**前置依赖**: 无额外依赖

---

### Demo 4: @property 装饰器（优雅的属性控制）
**文件**: `4_property.py`

演示 `@property` 的 getter/setter/deleter，重点场景：带验证的可读写属性、只读计算属性（面积/对角线）、双向换算属性（温度）、安全属性（密码只写不读）、懒加载属性。

**运行方式**: `python 4_property.py`
**前置依赖**: 无额外依赖

---

## 对应理论文档

| Demo | 文件 | 对应理论文档 |
|------|------|-------------|
| Demo 1 | `1_class_and_object.py` | `../1.类与对象.md` |
| Demo 2 | `2_inheritance_polymorphism.py` | `../2.继承与多态.md` |
| Demo 3 | `3_magic_methods.py` | `../3.魔术方法.md` |
| Demo 4 | `4_property.py` | `../4.property装饰器.md` |

---

## 核心要点

1. **OOP 核心思想**：数据 + 操作数据的方法 = 对象，比面向过程更清晰、更易复用
2. **类属性陷阱**：通过实例修改类属性实际上是创建了同名实例属性（遮蔽效果）
3. **super() 必不可少**：子类 `__init__` 中必须调用 `super().__init__()`，否则父类属性不会被初始化
4. **多态的价值**：不关心对象具体类型，只关心它能做什么，让代码更灵活
5. **魔术方法让类融入 Python**：实现 `__len__` 就能用 `len()`，实现 `__enter__` 就能用 `with`
6. **@property 的精髓**：外部看起来像属性访问，内部走验证和计算逻辑，两全其美

---

## 常见问题

| 问题 | 解决方案 |
|------|----------|
| `AttributeError: 'xxx' object has no attribute '_yyy'` | 忘记在 `__init__` 中初始化属性，或 setter 中属性名写错 |
| `TypeError: __init__() missing required argument` | 创建对象时缺少必传参数 |
| `RecursionError` | `@property` 的 getter 中访问了同名属性（如 `self.age = ...` ），应改用 `self._age` |
| 子类修改后父类属性不变 | 确认是否通过 `cls.xxx` 或 `ParentClass.xxx` 修改的类属性 |
| `@property` 无法赋值 | 只定义了 getter，没定义 `@xxx.setter` |
