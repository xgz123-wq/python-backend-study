"""
Pydantic Schema（知识点2：数据验证）

职责：
- XxxCreate：接收创建请求（无 id）
- XxxUpdate：接收更新请求（字段全 Optional）
- XxxResponse：返回给客户端（有 id，过滤敏感字段）
"""
from pydantic import BaseModel, Field
from typing import Optional


class ItemBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100, description="商品名称")
    price: float = Field(..., gt=0, description="价格，必须大于0")
    description: Optional[str] = Field(None, max_length=500)


class ItemCreate(ItemBase):
    """创建商品的请求体"""
    pass


class ItemUpdate(BaseModel):
    """更新商品的请求体（全部可选，只改传入的字段）"""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    price: Optional[float] = Field(None, gt=0)
    description: Optional[str] = None


class ItemResponse(ItemBase):
    """返回给客户端的格式"""
    id: int

    # from_attributes=True：允许从 SQLAlchemy ORM 对象直接转换
    model_config = {"from_attributes": True}
