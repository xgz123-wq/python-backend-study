"""
Demo 2: Tortoise ORM 异步操作演示
对应理论文档：2.Tortoise_ORM异步.md

演示内容：
  - 异步 Model 定义（User + Post）
  - 初始化连接与建表
  - 完整异步 CRUD 操作
  - 关联预加载（prefetch_related / select_related）
  - 事务处理
  - Q 对象复杂查询

运行前提：
  - 已安装依赖：pip install -r requirements.txt
  （使用 SQLite，无需启动 MySQL，方便直接运行）

运行方式：
  python 2_tortoise_orm_demo.py
"""

import asyncio
from tortoise import fields, Tortoise
from tortoise.models import Model
from tortoise.expressions import Q
from tortoise.transactions import in_transaction


# ─────────────────────────────────────────────────
# Model 定义
# ─────────────────────────────────────────────────
class User(Model):
    class Meta:
        table = "users"
        ordering = ["-created_at"]

    id = fields.IntField(primary_key=True)
    username = fields.CharField(max_length=50, unique=True)
    email = fields.CharField(max_length=100, unique=True)
    is_active = fields.BooleanField(default=True)
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    # 反向关联（由 Post.author 的 related_name 定义）
    posts: fields.ReverseRelation["Post"]

    def __str__(self) -> str:
        return f"User(id={self.id}, username={self.username})"


class Post(Model):
    class Meta:
        table = "posts"
        ordering = ["-created_at"]

    id = fields.IntField(primary_key=True)
    title = fields.CharField(max_length=200)
    content = fields.TextField(null=True)
    author = fields.ForeignKeyField(
        "models.User",
        related_name="posts",
        on_delete=fields.CASCADE,
    )
    created_at = fields.DatetimeField(auto_now_add=True)

    def __str__(self) -> str:
        return f"Post(id={self.id}, title={self.title!r})"


# ─────────────────────────────────────────────────
# 初始化 Tortoise ORM（连接数据库、建表）
# ─────────────────────────────────────────────────
async def init_db():
    await Tortoise.init(
        db_url="sqlite://./tortoise_demo.db",  # SQLite，无需 MySQL
        # db_url="mysql://root:123456@localhost:3306/orm_demo",  # MySQL
        modules={"models": ["__main__"]},      # Model 定义在当前文件（__main__）
    )
    await Tortoise.generate_schemas(safe=True)  # safe=True：表已存在时不报错
    print("【数据库初始化完成】")


# ─────────────────────────────────────────────────
# 1. Create（创建）
# ─────────────────────────────────────────────────
async def demo_create():
    print("\n" + "=" * 50)
    print("【1. Create 异步创建】")

    # create()：一步完成
    u1 = await User.create(username="zhangsan", email="zs@example.com")
    u2 = await User.create(username="lisi", email="ls@example.com")
    u3 = await User.create(username="wangwu", email="ww@example.com", is_active=False)
    print(f"  创建用户: {[str(u) for u in [u1, u2, u3]]}")

    # 为用户创建文章（通过外键 author 关联）
    p1 = await Post.create(title="Tortoise ORM 入门", content="异步 ORM 真香", author=u1)
    p2 = await Post.create(title="FastAPI 实战", content="性能极强", author=u1)
    p3 = await Post.create(title="Python 协程", content="async/await 详解", author=u2)
    print(f"  创建文章: {[str(p) for p in [p1, p2, p3]]}")


# ─────────────────────────────────────────────────
# 2. Read（查询）
# ─────────────────────────────────────────────────
async def demo_read():
    print("\n" + "=" * 50)
    print("【2. Read 异步查询】")

    # get()：精确查找，不存在抛异常
    user = await User.get(username="zhangsan")
    print(f"  get: {user}")

    # get_or_none()：更安全，不存在返回 None
    not_found = await User.get_or_none(username="不存在的用户")
    print(f"  get_or_none（不存在）: {not_found}")

    # filter().all()：条件查询
    active_users = await User.filter(is_active=True).all()
    print(f"  活跃用户 ({len(active_users)}个): {[u.username for u in active_users]}")

    # 字段查找语法（__后缀）
    users = await User.filter(email__endswith="@example.com").all()
    print(f"  email 以 @example.com 结尾的用户: {len(users)} 个")

    # Q 对象：复杂 OR/AND 组合条件
    users = await User.filter(
        Q(username="zhangsan") | Q(username="lisi")  # OR 条件
    ).all()
    print(f"  Q 对象 OR 查询 (zhangsan OR lisi): {[u.username for u in users]}")

    # 排序 + 分页
    users = await User.all().order_by("username").offset(0).limit(2)
    print(f"  分页（按 username 升序，前2条）: {[u.username for u in users]}")

    # 统计
    count = await User.filter(is_active=True).count()
    print(f"  活跃用户数: {count}")

    # exists()
    exists = await User.filter(username="zhangsan").exists()
    print(f"  zhangsan 是否存在: {exists}")

    # values()：只返回指定字段（减少数据传输）
    data = await User.all().values("id", "username")
    print(f"  values() 只返回 id, username: {data}")

    # values_list()：返回扁平列表
    ids = await User.all().values_list("id", flat=True)
    print(f"  所有用户 ID: {ids}")


# ─────────────────────────────────────────────────
# 3. 关联查询（预加载，避免 N+1）
# ─────────────────────────────────────────────────
async def demo_prefetch():
    print("\n" + "=" * 50)
    print("【3. 关联预加载（避免 N+1 问题）】")

    # ❌ 错误示范：N+1 问题（每个 post 访问 .author 都会额外查询一次）
    print("  [N+1 问题演示：不使用预加载]")
    posts = await Post.all()
    for post in posts:
        # 注意：访问外键关联对象必须先 await fetch_related
        await post.fetch_related("author")
        print(f"    文章 '{post.title}' - 作者: {post.author.username}")

    # ✅ 正确做法：select_related 一次 JOIN 查询
    print("\n  [正确做法：select_related 一次加载]")
    posts = await Post.all().select_related("author")
    for post in posts:
        print(f"    文章 '{post.title}' - 作者: {post.author.username}")

    # 一对多：查询用户及其所有文章
    print("\n  [prefetch_related：用户及其文章]")
    users = await User.filter(is_active=True).prefetch_related("posts")
    for user in users:
        print(f"  用户: {user.username} - 文章数: {len(user.posts)}")
        for post in user.posts:
            print(f"      - {post.title}")


# ─────────────────────────────────────────────────
# 4. Update（更新）
# ─────────────────────────────────────────────────
async def demo_update():
    print("\n" + "=" * 50)
    print("【4. Update 异步更新】")

    # 方式1：查出来改属性再 save()
    user = await User.get(username="lisi")
    old_email = user.email
    user.email = "lisi_new@example.com"
    await user.save()
    print(f"  单条更新: {old_email} → {user.email}")

    # 方式2：filter().update() 批量更新（高效，不加载对象）
    count = await User.filter(is_active=False).update(is_active=True)
    print(f"  批量激活用户: 更新 {count} 条")


# ─────────────────────────────────────────────────
# 5. Delete（删除）
# ─────────────────────────────────────────────────
async def demo_delete():
    print("\n" + "=" * 50)
    print("【5. Delete 异步删除】")

    # 单条删除
    user = await User.get_or_none(username="wangwu")
    if user:
        await user.delete()
        print("  删除用户 wangwu")

    # 批量删除
    deleted = await Post.filter(title__contains="协程").delete()
    print(f"  批量删除包含'协程'的文章: {deleted} 条")

    remaining = await Post.all().count()
    print(f"  剩余文章数: {remaining}")


# ─────────────────────────────────────────────────
# 6. 事务
# ─────────────────────────────────────────────────
async def demo_transaction():
    print("\n" + "=" * 50)
    print("【6. 事务演示】")

    try:
        async with in_transaction():
            # 步骤1：更新用户
            await User.filter(username="zhangsan").update(email="tx@example.com")
            print("  步骤1 完成")

            # 步骤2：模拟失败，抛异常
            raise ValueError("模拟业务异常，事务应自动回滚")

    except ValueError as e:
        print(f"  事务已回滚: {e}")

    # 验证回滚：email 应该没有变化
    user = await User.get(username="zhangsan")
    print(f"  回滚后 email 仍为: {user.email}")  # 应为 zs@example.com


# ─────────────────────────────────────────────────
# 主流程
# ─────────────────────────────────────────────────
async def main():
    await init_db()
    # 清空旧数据（演示用）
    await Post.all().delete()
    await User.all().delete()

    await demo_create()
    await demo_read()
    await demo_prefetch()
    await demo_update()
    await demo_delete()
    await demo_transaction()

    await Tortoise.close_connections()
    print("\n" + "=" * 50)
    print("Tortoise ORM Demo 运行完成！")
    print("提示：tortoise_demo.db 是 SQLite 数据库文件")


if __name__ == "__main__":
    asyncio.run(main())
