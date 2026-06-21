"""
用户业务逻辑（功能1：注册登录）

SOP：router → service → DB
service 层只管业务逻辑，不直接操作 HTTP（不用 HTTPException 以外的 fastapi 对象）
"""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import HTTPException, status

from app.models.user import User
from app.schemas.user import UserRegister
from app.utils.security import hash_password, verify_password, create_access_token


async def register_user(db: AsyncSession, data: UserRegister) -> User:
    """注册：检查用户名/邮箱唯一性 → 哈希密码 → 存库"""
    # 检查用户名是否已存在
    existing = await db.execute(select(User).where(User.username == data.username))
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="用户名已存在")

    # 检查邮箱是否已存在
    existing = await db.execute(select(User).where(User.email == data.email))
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="邮箱已被注册")

    user = User(
        username=data.username,
        email=data.email,
        hashed_password=hash_password(data.password),
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


async def login_user(db: AsyncSession, username: str, password: str) -> str:
    """登录：查用户 → 校验密码 → 生成 JWT"""
    result = await db.execute(select(User).where(User.username == username))
    user = result.scalar_one_or_none()

    if not user or not verify_password(password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误",
        )

    # JWT payload 里存 user_id（sub 字段是标准 JWT 约定）
    token = create_access_token({"sub": str(user.id)})
    return token
