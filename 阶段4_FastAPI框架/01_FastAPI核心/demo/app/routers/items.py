"""
商品路由（知识点1+2+3+4+5）

这个文件把所有知识点串起来：
- 知识点1：路由装饰器、路径参数、查询参数
- 知识点2：Pydantic schema 做请求验证 + 响应序列化
- 知识点3：Depends(get_db) 注入数据库 session
- 知识点4：async/await 异步路由
- 知识点5：SQLAlchemy 异步 CRUD
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.deps import get_db
from app.models.item import Item
from app.schemas import ItemCreate, ItemUpdate, ItemResponse

router = APIRouter(prefix="/items", tags=["商品"])


# ---- 查询列表（知识点1：查询参数；知识点5：分页查询）----
@router.get("/", response_model=list[ItemResponse])
async def list_items(
    skip: int = 0,
    limit: int = 10,
    db: AsyncSession = Depends(get_db),   # 知识点3：依赖注入
):
    result = await db.execute(
        select(Item).offset(skip).limit(limit)   # 知识点4：await 异步查询
    )
    return result.scalars().all()


# ---- 查询单个（知识点1：路径参数）----
@router.get("/{item_id}", response_model=ItemResponse)
async def get_item(item_id: int, db: AsyncSession = Depends(get_db)):
    item = await db.get(Item, item_id)
    if not item:
        raise HTTPException(status_code=404, detail=f"Item {item_id} not found")
    return item


# ---- 创建（知识点2：请求体验证）----
@router.post("/", response_model=ItemResponse, status_code=201)
async def create_item(
    data: ItemCreate,                        # 知识点2：Pydantic 自动验证
    db: AsyncSession = Depends(get_db),
):
    db_item = Item(**data.model_dump())
    db.add(db_item)
    await db.commit()
    await db.refresh(db_item)   # 刷新拿到数据库生成的 id
    return db_item


# ---- 更新（部分更新：只改传入的字段）----
@router.patch("/{item_id}", response_model=ItemResponse)
async def update_item(item_id: int, data: ItemUpdate, db: AsyncSession = Depends(get_db)):
    item = await db.get(Item, item_id)
    if not item:
        raise HTTPException(status_code=404, detail=f"Item {item_id} not found")

    # exclude_unset=True：只更新请求里实际传了值的字段
    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(item, field, value)

    await db.commit()
    await db.refresh(item)
    return item


# ---- 删除 ----
@router.delete("/{item_id}", status_code=204)
async def delete_item(item_id: int, db: AsyncSession = Depends(get_db)):
    item = await db.get(Item, item_id)
    if not item:
        raise HTTPException(status_code=404, detail=f"Item {item_id} not found")
    await db.delete(item)
    await db.commit()
