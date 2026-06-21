"""
商品 Schema（功能2+3）
"""
from pydantic import BaseModel, Field
from typing import Optional


class ProductCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    price: float = Field(..., gt=0)
    stock: int = Field(0, ge=0)
    description: Optional[str] = None
    category: Optional[str] = None


class ProductUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    price: Optional[float] = Field(None, gt=0)
    stock: Optional[int] = Field(None, ge=0)
    description: Optional[str] = None
    category: Optional[str] = None


class ProductResponse(BaseModel):
    id: int
    name: str
    price: float
    stock: int
    description: Optional[str]
    category: Optional[str]
    is_active: bool

    model_config = {"from_attributes": True}


class ProductListResponse(BaseModel):
    """分页列表响应"""
    total: int
    items: list[ProductResponse]
    skip: int
    limit: int
