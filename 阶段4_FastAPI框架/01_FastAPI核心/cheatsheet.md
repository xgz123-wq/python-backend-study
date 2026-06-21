# FastAPI Cheatsheet（最小可用片段）

> 卡住时先查这里，不用翻大段文档。

---

## 路由装饰器

```python
@app.get("/items/")          # 查询列表
@app.get("/items/{id}")      # 查询单个
@app.post("/items/")         # 创建
@app.put("/items/{id}")      # 全量更新
@app.patch("/items/{id}")    # 部分更新
@app.delete("/items/{id}")   # 删除
```

---

## Pydantic Schema 模板

```python
from pydantic import BaseModel, Field
from typing import Optional

class ItemBase(BaseModel):
    name: str = Field(..., min_length=1)
    price: float = Field(..., gt=0)

class ItemCreate(ItemBase):
    pass

class ItemUpdate(BaseModel):
    name: Optional[str] = None
    price: Optional[float] = None

class ItemResponse(ItemBase):
    id: int
    model_config = {"from_attributes": True}
```

---

## 异步数据库 Session（SQLAlchemy）

```python
# database.py
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker

engine = create_async_engine("sqlite+aiosqlite:///./app.db")
AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False)

# deps.py
async def get_db():
    async with AsyncSessionLocal() as session:
        yield session
```

---

## 常用 SQLAlchemy 操作

```python
from sqlalchemy import select

# 查全部
result = await db.execute(select(Item))
items = result.scalars().all()

# 查单个（按主键）
item = await db.get(Item, item_id)

# 查单个（按条件）
result = await db.execute(select(Item).where(Item.name == name))
item = result.scalar_one_or_none()

# 创建
db_item = Item(**data.model_dump())
db.add(db_item)
await db.commit()
await db.refresh(db_item)

# 更新
item.name = "new name"
await db.commit()

# 删除
await db.delete(item)
await db.commit()

# 分页
result = await db.execute(select(Item).offset(skip).limit(limit))
```

---

## JWT 工具（配合 python-jose）

```python
from jose import jwt
from datetime import datetime, timedelta

SECRET_KEY = "your-secret"
ALGORITHM = "HS256"

def create_access_token(data: dict, expires_delta: int = 30) -> str:
    payload = data.copy()
    payload["exp"] = datetime.utcnow() + timedelta(minutes=expires_delta)
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

def decode_token(token: str) -> dict:
    return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
```

---

## 密码哈希（passlib）

```python
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"])

def hash_password(plain: str) -> str:
    return pwd_context.hash(plain)

def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)
```

---

## Redis 缓存模板（aioredis）

```python
import json, redis.asyncio as aioredis

redis_client = aioredis.from_url("redis://localhost:6379")

async def get_with_cache(key: str, fetch_fn, ttl: int = 300):
    cached = await redis_client.get(key)
    if cached:
        return json.loads(cached)
    data = await fetch_fn()
    await redis_client.setex(key, ttl, json.dumps(data))
    return data
```

---

## 统一响应格式

```python
from fastapi.responses import JSONResponse

def ok(data=None, message="success"):
    return {"code": 200, "message": message, "data": data}

def fail(code: int, message: str):
    return JSONResponse(status_code=code, content={"code": code, "message": message})
```

---

## CORS 配置

```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # 生产改为实际域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

---

## 启动命令

```bash
uvicorn app.main:app --reload          # 开发
uvicorn app.main:app --host 0.0.0.0 --port 8000  # 生产
```

API 文档：`http://localhost:8000/docs`
