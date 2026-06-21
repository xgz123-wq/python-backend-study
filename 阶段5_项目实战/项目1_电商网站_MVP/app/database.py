"""
数据库 + Redis 连接管理
"""
import redis.asyncio as aioredis
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase

from app.config import settings

# MySQL 异步引擎
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=False,        # 生产改 False；调试 SQL 时改 True
    pool_size=10,
    max_overflow=20,
)
AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False)


class Base(DeclarativeBase):
    pass


# Redis 连接（全局单例）
redis_client: aioredis.Redis | None = None


async def get_redis() -> aioredis.Redis:
    global redis_client
    if redis_client is None:
        redis_client = aioredis.from_url(
            settings.REDIS_URL,
            encoding="utf-8",
            decode_responses=True,
        )
    return redis_client


async def init_db():
    """启动时建表"""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def close_db():
    """关闭时释放连接"""
    await engine.dispose()
    global redis_client
    if redis_client:
        await redis_client.aclose()
