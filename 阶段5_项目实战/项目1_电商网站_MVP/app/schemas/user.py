"""
用户 Schema（功能1：注册登录 JWT）
"""
from pydantic import BaseModel, EmailStr, Field


class UserRegister(BaseModel):
    """注册请求"""
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(..., min_length=6)


class UserLogin(BaseModel):
    """登录请求"""
    username: str
    password: str


class UserResponse(BaseModel):
    """返回给客户端（不含密码）"""
    id: int
    username: str
    email: str
    is_active: bool

    model_config = {"from_attributes": True}


class TokenResponse(BaseModel):
    """登录成功返回 JWT"""
    access_token: str
    token_type: str = "bearer"
