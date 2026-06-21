"""
商品业务逻辑（功能2：CRUD 分页；功能3：Redis 缓存）

Redis 缓存策略：
- 商品列表：缓存 5 分钟，key = "products:list:{skip}:{limit}"
- 商品详情：缓存 10 分钟，key = "products:detail:{id}"
- 写操作（创建/更新/删除）后清除相关缓存
"""
import json
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from fastapi import HTTPException
import redis.asyncio as aioredis

from app.models.product import Product
from app.schemas.product import ProductCreate, ProductUpdate, ProductListResponse


async def get_product_list(
    db: AsyncSession,
    redis: aioredis.Redis,
    skip: int = 0,
    limit: int = 10,
    category: str | None = None,
) -> ProductListResponse:
    """获取商品列表（带 Redis 缓存）"""
    cache_key = f"products:list:{skip}:{limit}:{category or 'all'}"

    # 先查缓存
    cached = await redis.get(cache_key)
    if cached:
        data = json.loads(cached)
        return ProductListResponse(**data)

    # 缓存未命中，查数据库
    query = select(Product).where(Product.is_active == True)
    if category:
        query = query.where(Product.category == category)

    count_result = await db.execute(select(func.count()).select_from(query.subquery()))
    total = count_result.scalar()

    result = await db.execute(query.offset(skip).limit(limit))
    items = result.scalars().all()

    response = ProductListResponse(
        total=total,
        items=items,
        skip=skip,
        limit=limit,
    )

    # 写入缓存，TTL 300 秒
    await redis.setex(cache_key, 300, response.model_dump_json())
    return response


async def get_product(db: AsyncSession, redis: aioredis.Redis, product_id: int) -> Product:
    """获取商品详情（带 Redis 缓存）"""
    cache_key = f"products:detail:{product_id}"
    cached = await redis.get(cache_key)
    if cached:
        # 从缓存拿到数据后，构造一个"像ORM对象"的字典直接返回
        return json.loads(cached)

    product = await db.get(Product, product_id)
    if not product or not product.is_active:
        raise HTTPException(status_code=404, detail="商品不存在")

    # 缓存 10 分钟
    from app.schemas.product import ProductResponse
    await redis.setex(cache_key, 600, ProductResponse.model_validate(product).model_dump_json())
    return product


async def create_product(db: AsyncSession, redis: aioredis.Redis, data: ProductCreate) -> Product:
    product = Product(**data.model_dump())
    db.add(product)
    await db.commit()
    await db.refresh(product)

    # 清除列表缓存（新增商品后旧缓存失效）
    await _clear_list_cache(redis)
    return product


async def update_product(
    db: AsyncSession, redis: aioredis.Redis, product_id: int, data: ProductUpdate
) -> Product:
    product = await db.get(Product, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="商品不存在")

    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(product, field, value)

    await db.commit()
    await db.refresh(product)

    # 清除该商品详情缓存 + 列表缓存
    await redis.delete(f"products:detail:{product_id}")
    await _clear_list_cache(redis)
    return product


async def delete_product(db: AsyncSession, redis: aioredis.Redis, product_id: int):
    product = await db.get(Product, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="商品不存在")

    product.is_active = False   # 软删除，不真正删除数据
    await db.commit()

    await redis.delete(f"products:detail:{product_id}")
    await _clear_list_cache(redis)


async def _clear_list_cache(redis: aioredis.Redis):
    """清除所有商品列表缓存（使用 pattern 删除）"""
    keys = await redis.keys("products:list:*")
    if keys:
        await redis.delete(*keys)
