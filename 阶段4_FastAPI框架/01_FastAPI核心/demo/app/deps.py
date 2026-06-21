"""
依赖注入（知识点3：Depends）

这里集中放所有可复用的依赖函数：
- get_db：获取异步数据库 session
- 后续可加：get_current_user（JWT 校验）
"""
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import AsyncSessionLocal


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    数据库 session 依赖

    用 yield（不是 return）= 请求结束后自动执行 finally，关闭 session。
    路由里写 db: AsyncSession = Depends(get_db) 就能拿到已经初始化好的 session。
    """
    async with AsyncSessionLocal() as session:
        yield session
