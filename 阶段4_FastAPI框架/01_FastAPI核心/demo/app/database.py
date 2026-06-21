"""
数据库配置（知识点5：SQLAlchemy 异步集成）

学习每个知识点时，这个文件会逐步完善：
- 知识点1：此文件不存在，路由直接返回假数据
- 知识点5：加入异步引擎 + Session 工厂
"""
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase

# 开发用 SQLite（无需安装 MySQL）
# 切换 MySQL：mysql+aiomysql://root:password@localhost:3306/fastapi_demo
DATABASE_URL = "sqlite+aiosqlite:///./fastapi_demo.db"

engine = create_async_engine(
    DATABASE_URL,
    echo=True,   # 打印 SQL，学习阶段保留，生产改 False
)

# expire_on_commit=False：避免 commit 后访问属性触发新查询（异步环境必须）
AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False)


class Base(DeclarativeBase):
    pass


async def init_db():
    """建表（main.py startup 事件调用）"""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
