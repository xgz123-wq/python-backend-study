"""
Demo 3: Alembic 迁移演示（配套脚本）
对应理论文档：3.Alembic数据库迁移.md

本脚本包含：
  - 定义演示用的 Model（初始版本 + 变更版本）
  - 展示完整的 Alembic 迁移工作流

Alembic 需要在命令行操作，本文件只提供 Model 定义和说明。
完整的迁移命令流程请参考下方注释和 README.md。

运行方式：
  1. 先运行 init_alembic.py 完成初始化（已自动执行）
  2. 按照 README.md 中的步骤操作 alembic 命令
"""

from datetime import datetime
from sqlalchemy import (
    create_engine, String, Integer, Text, DateTime, Boolean, ForeignKey
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship, sessionmaker

# ─────────────────────────────────────────────────
# 数据库连接（Alembic 从 alembic.ini 读取，这里供脚本使用）
# ─────────────────────────────────────────────────
DATABASE_URL = "sqlite:///./alembic_demo.db"
engine = create_engine(DATABASE_URL, echo=False,
                       connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)


class Base(DeclarativeBase):
    pass


# ─────────────────────────────────────────────────
# 版本1：初始 Model（两张表：users + posts）
# ─────────────────────────────────────────────────
class User(Base):
    """
    初始版本的 User Model
    对应第一次迁移：alembic revision --autogenerate -m "initial tables"
    """
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    email: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    posts: Mapped[list["Post"]] = relationship("Post", back_populates="author")


class Post(Base):
    __tablename__ = "posts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    content: Mapped[str | None] = mapped_column(Text, nullable=True)
    author_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    author: Mapped["User"] = relationship("User", back_populates="posts")


# ─────────────────────────────────────────────────
# 演示：直接用 SQLAlchemy 插入测试数据
# ─────────────────────────────────────────────────
def seed_data():
    """插入演示数据（模拟迁移后的状态）"""
    Base.metadata.create_all(bind=engine)  # 如果表不存在则创建

    with SessionLocal() as session:
        # 检查是否已有数据
        from sqlalchemy import select
        existing = session.execute(select(User)).scalars().first()
        if existing:
            print("  数据已存在，跳过初始化")
            return

        users = [
            User(username="admin", email="admin@example.com"),
            User(username="alice", email="alice@example.com"),
        ]
        session.add_all(users)
        session.commit()
        for u in users:
            session.refresh(u)

        posts = [
            Post(title="Alembic 入门", content="迁移工具详解", author_id=users[0].id),
            Post(title="数据库版本管理", content="如何管理 schema 变更", author_id=users[1].id),
        ]
        session.add_all(posts)
        session.commit()
        print(f"  插入测试数据：{len(users)} 个用户，{len(posts)} 篇文章")


# ─────────────────────────────────────────────────
# Alembic 迁移工作流说明（命令行操作，非代码）
# ─────────────────────────────────────────────────
MIGRATION_WORKFLOW = """
================================================================
Alembic 迁移工作流（在 demo/ 目录下执行）
================================================================

【第一步：初始化 Alembic（只需一次）】
  alembic init alembic

  修改 alembic.ini：
    sqlalchemy.url = sqlite:///./alembic_demo.db

  修改 alembic/env.py，找到 target_metadata = None，改为：
    from demo_3_alembic_models import Base
    target_metadata = Base.metadata

【第二步：生成初始迁移文件】
  alembic revision --autogenerate -m "initial tables"
  # 查看生成的文件：alembic/versions/xxxx_initial_tables.py

【第三步：执行迁移（建表）】
  alembic upgrade head
  # 验证：alembic current

【第四步：模拟 Model 变更（加字段）】
  # 在 User 类中添加：
  avatar: Mapped[str | None] = mapped_column(String(255), nullable=True)

  alembic revision --autogenerate -m "add avatar to users"
  # 查看生成的迁移文件内容
  alembic upgrade head

【第五步：查看迁移历史】
  alembic history
  alembic current

【第六步：回滚演示】
  alembic downgrade -1        # 回滚最近一次（删除 avatar 列）
  alembic upgrade head        # 重新升级
  alembic downgrade base      # 回滚到最初（删除所有表）

================================================================
"""


if __name__ == "__main__":
    print("=" * 50)
    print("【Alembic 迁移演示 - 初始化数据】")
    seed_data()
    print("\n" + MIGRATION_WORKFLOW)
