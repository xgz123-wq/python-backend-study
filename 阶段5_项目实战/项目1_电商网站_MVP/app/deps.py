"""
依赖注入（Depends）

集中管理所有路由可复用的依赖：
- get_db：异步数据库 session
- get_current_user：JWT 校验 + 拿到当前用户
"""
from typing import AsyncGenerator
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import AsyncSessionLocal
from app.utils.security import decode_access_token

# OAuth2 密码模式：从 Authorization: Bearer <token> 提取 token
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        yield session


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db),
):
    """
    JWT 校验依赖：解码 token → 查用户 → 返回 User 对象
    路由里加 user: User = Depends(get_current_user) 即可要求登录
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid or expired token",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = decode_access_token(token)
        user_id: int = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    # 避免循环导入，在函数内 import
    from app.models.user import User
    user = await db.get(User, int(user_id))
    if not user or not user.is_active:
        raise credentials_exception
    return user
