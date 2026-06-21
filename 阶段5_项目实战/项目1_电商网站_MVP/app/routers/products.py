"""
商品路由（功能2：CRUD 分页；功能3：Redis 缓存）
"""
from typing import Optional
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
import redis.asyncio as aioredis

from app.deps import get_db, get_current_user
from app.database import get_redis
from app.models.user import User
from app.schemas.product import ProductCreate, ProductUpdate, ProductResponse, ProductListResponse
from app.services import product_service

router = APIRouter(prefix="/products", tags=["商品"])


@router.get("/", response_model=ProductListResponse)
async def list_products(
    skip: int = 0,
    limit: int = 10,
    category: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    redis: aioredis.Redis = Depends(get_redis),
):
    """获取商品列表（带 Redis 缓存，同一查询条件首次查库，后续命中缓存）"""
    return await product_service.get_product_list(db, redis, skip, limit, category)


@router.get("/{product_id}", response_model=ProductResponse)
async def get_product(
    product_id: int,
    db: AsyncSession = Depends(get_db),
    redis: aioredis.Redis = Depends(get_redis),
):
    result = await product_service.get_product(db, redis, product_id)
    # 如果从缓存拿到的是 dict，直接返回（Pydantic 会自动转换）
    return result


@router.post("/", response_model=ProductResponse, status_code=201)
async def create_product(
    data: ProductCreate,
    db: AsyncSession = Depends(get_db),
    redis: aioredis.Redis = Depends(get_redis),
    _: User = Depends(get_current_user),   # 要求登录（_表示不使用该变量）
):
    return await product_service.create_product(db, redis, data)


@router.patch("/{product_id}", response_model=ProductResponse)
async def update_product(
    product_id: int,
    data: ProductUpdate,
    db: AsyncSession = Depends(get_db),
    redis: aioredis.Redis = Depends(get_redis),
    _: User = Depends(get_current_user),
):
    return await product_service.update_product(db, redis, product_id, data)


@router.delete("/{product_id}", status_code=204)
async def delete_product(
    product_id: int,
    db: AsyncSession = Depends(get_db),
    redis: aioredis.Redis = Depends(get_redis),
    _: User = Depends(get_current_user),
):
    await product_service.delete_product(db, redis, product_id)
