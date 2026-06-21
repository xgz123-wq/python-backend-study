"""
Demo 1: SQLAlchemy 核心用法演示
对应理论文档：1.SQLAlchemy核心用法.md

演示内容：
  - Model 定义（User + Post，一对多关系）
  - 建表
  - 完整 CRUD 操作
  - 关联查询（joinedload 预加载）
  - 事务处理
  - 分页查询

运行前提：
  - 已启动 MySQL（docker-compose up -d）
  - 已安装依赖：pip install -r requirements.txt

运行方式：
  python 1_sqlalchemy_demo.py
"""

from datetime import datetime
from sqlalchemy import (
    create_engine, String, Integer, Text, DateTime, Boolean,
    ForeignKey, select, update, delete, func, and_
)
from sqlalchemy.orm import (
    sessionmaker, DeclarativeBase, Mapped, mapped_column,
    relationship, joinedload
)

# ─────────────────────────────────────────────────
# 数据库连接配置（使用 SQLite，无需额外服务，方便直接运行）
# 切换 MySQL 只需修改这里的 DATABASE_URL
# ─────────────────────────────────────────────────
DATABASE_URL = "sqlite:///./orm_demo.db"   # SQLite 文件数据库
# DATABASE_URL = "mysql+pymysql://root:123456@localhost:3306/orm_demo"  # MySQL

engine = create_engine(
    DATABASE_URL,
    echo=False,       # True 时打印所有 SQL，调试时可开启
    connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {},
)

SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)


# ─────────────────────────────────────────────────
# Model 定义
# ─────────────────────────────────────────────────
class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    email: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # 一对多关系（一个用户有多篇文章）
    posts: Mapped[list["Post"]] = relationship("Post", back_populates="author", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<User id={self.id} username={self.username}>"


class Post(Base):
    __tablename__ = "posts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    content: Mapped[str | None] = mapped_column(Text, nullable=True)
    author_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # 多对一关系（每篇文章属于一个用户）
    author: Mapped["User"] = relationship("User", back_populates="posts")

    def __repr__(self) -> str:
        return f"<Post id={self.id} title={self.title!r}>"


# ─────────────────────────────────────────────────
# 1. 建表
# ─────────────────────────────────────────────────
def setup_db():
    print("=" * 50)
    print("【0. 建表】")
    Base.metadata.drop_all(bind=engine)    # 清理旧表（演示用）
    Base.metadata.create_all(bind=engine)  # 建表
    print("  表已创建：users, posts")


# ─────────────────────────────────────────────────
# 2. Create（创建）
# ─────────────────────────────────────────────────
def demo_create():
    print("\n" + "=" * 50)
    print("【1. Create 创建】")

    with SessionLocal() as session:
        # 创建用户
        users = [
            User(username="zhangsan", email="zs@example.com"),
            User(username="lisi",     email="ls@example.com"),
            User(username="wangwu",   email="ww@example.com", is_active=False),
        ]
        session.add_all(users)
        session.commit()

        # 刷新后才能拿到自动生成的 id
        for u in users:
            session.refresh(u)
        print(f"  创建用户: {[u.username for u in users]}")
        print(f"  ID 分别为: {[u.id for u in users]}")

        # 为 zhangsan 创建两篇文章
        posts = [
            Post(title="SQLAlchemy 入门", content="ORM 真的很方便", author_id=users[0].id),
            Post(title="Python 类型提示", content="类型提示提升代码可读性", author_id=users[0].id),
            Post(title="异步编程笔记", content="async/await 详解", author_id=users[1].id),
        ]
        session.add_all(posts)
        session.commit()
        print(f"  创建文章: {[p.title for p in posts]}")


# ─────────────────────────────────────────────────
# 3. Read（查询）
# ─────────────────────────────────────────────────
def demo_read():
    print("\n" + "=" * 50)
    print("【2. Read 查询】")

    with SessionLocal() as session:
        # 按主键查询
        user = session.get(User, 1)
        print(f"  按 ID 查询: {user}")

        # WHERE 条件查询
        stmt = select(User).where(User.username == "lisi")
        user = session.execute(stmt).scalar_one_or_none()
        print(f"  条件查询 username=lisi: {user}")

        # 查询所有活跃用户
        stmt = select(User).where(User.is_active == True).order_by(User.created_at.desc())
        users = session.execute(stmt).scalars().all()
        print(f"  活跃用户 ({len(users)}个): {[u.username for u in users]}")

        # 统计数量
        stmt = select(func.count()).select_from(User)
        total = session.execute(stmt).scalar()
        print(f"  用户总数: {total}")

        # 分页查询（第1页，每页2条）
        page, page_size = 1, 2
        stmt = select(User).offset((page - 1) * page_size).limit(page_size)
        page_users = session.execute(stmt).scalars().all()
        print(f"  分页查询（第{page}页，每页{page_size}条）: {[u.username for u in page_users]}")


# ─────────────────────────────────────────────────
# 4. 关联查询（joinedload 预加载，避免 N+1）
# ─────────────────────────────────────────────────
def demo_join():
    print("\n" + "=" * 50)
    print("【3. 关联查询（预加载）】")

    with SessionLocal() as session:
        # 查询用户及其文章（joinedload 一次性加载，不产生 N+1）
        stmt = (
            select(User)
            .options(joinedload(User.posts))
            .where(User.username == "zhangsan")
        )
        user = session.execute(stmt).unique().scalar_one_or_none()
        if user:
            print(f"  用户: {user.username}，共 {len(user.posts)} 篇文章")
            for post in user.posts:
                print(f"    - {post.title}")

        # 查询所有文章及其作者
        stmt = select(Post).options(joinedload(Post.author))
        posts = session.execute(stmt).unique().scalars().all()
        print(f"\n  所有文章及作者:")
        for post in posts:
            print(f"    [{post.author.username}] {post.title}")


# ─────────────────────────────────────────────────
# 5. Update（更新）
# ─────────────────────────────────────────────────
def demo_update():
    print("\n" + "=" * 50)
    print("【4. Update 更新】")

    with SessionLocal() as session:
        # 方式1：查出来改属性
        user = session.get(User, 1)
        old_email = user.email
        user.email = "zhangsan_new@example.com"
        session.commit()
        print(f"  单条更新: {old_email} → {user.email}")

        # 方式2：批量 UPDATE（不加载对象，直接 SQL）
        stmt = update(User).where(User.is_active == False).values(is_active=True)
        result = session.execute(stmt)
        session.commit()
        print(f"  批量激活禁用用户: 影响 {result.rowcount} 行")


# ─────────────────────────────────────────────────
# 6. Delete（删除）
# ─────────────────────────────────────────────────
def demo_delete():
    print("\n" + "=" * 50)
    print("【5. Delete 删除】")

    with SessionLocal() as session:
        # 查出来再删（cascade 会自动删除关联的 posts）
        user = session.get(User, 3)  # wangwu
        if user:
            session.delete(user)
            session.commit()
            print(f"  删除用户 wangwu（及其关联文章）")

        # 验证删除
        remaining = session.execute(select(func.count()).select_from(User)).scalar()
        print(f"  剩余用户数: {remaining}")


# ─────────────────────────────────────────────────
# 7. 事务演示
# ─────────────────────────────────────────────────
def demo_transaction():
    print("\n" + "=" * 50)
    print("【6. 事务演示】")

    with SessionLocal() as session:
        try:
            # 模拟转账：这里故意在第二步抛异常
            user1 = session.get(User, 1)
            user1.email = "tx_test@example.com"  # 步骤1：修改

            # 步骤2：模拟失败（抛出异常）
            raise ValueError("模拟业务异常，事务应回滚")

            session.commit()   # 永远不会执行到这里

        except ValueError as e:
            session.rollback()  # 回滚，步骤1的修改被撤销
            print(f"  事务回滚成功: {e}")

        # 验证回滚：email 应该没有变化
        user1 = session.get(User, 1)
        print(f"  回滚后 email 仍为: {user1.email}")  # 应为原来的值


if __name__ == "__main__":
    setup_db()
    demo_create()
    demo_read()
    demo_join()
    demo_update()
    demo_delete()
    demo_transaction()
    print("\n" + "=" * 50)
    print("SQLAlchemy Demo 运行完成！")
    print("提示：orm_demo.db 文件是 SQLite 数据库，可用 DB Browser for SQLite 查看")
