"""
认证路由（功能1：注册登录 JWT）

SOP 体现：
1. 需求：注册/登录
2. 数据建模：models/user.py
3. API 设计：POST /auth/register, POST /auth/login（本文件接口签名）
4. 分层实现：router → service（user_service.py）→ DB
5. 测试：见 README 的 curl 命令
"""
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.deps import get_db, get_current_user
from app.models.user import User
from app.schemas.user import UserRegister, UserLogin, UserResponse, TokenResponse
from app.services.user_service import register_user, login_user

router = APIRouter(prefix="/auth", tags=["认证"])


@router.post("/register", response_model=UserResponse, status_code=201)
async def register(data: UserRegister, db: AsyncSession = Depends(get_db)):
    user = await register_user(db, data)
    return user


@router.post("/login", response_model=TokenResponse)
async def login(data: UserLogin, db: AsyncSession = Depends(get_db)):
    token = await login_user(db, data.username, data.password)
    return TokenResponse(access_token=token)


@router.get("/me", response_model=UserResponse)
async def get_me(current_user: User = Depends(get_current_user)):
    """需要登录：把 JWT token 放到 Authorization: Bearer <token>"""
    return current_user
