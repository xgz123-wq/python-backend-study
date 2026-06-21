"""
电商 MVP 入口
"""
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import init_db, close_db
from app.routers.auth import router as auth_router
from app.routers.products import router as products_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield
    await close_db()


app = FastAPI(
    title="电商 MVP API",
    description="功能：用户注册登录 + 商品 CRUD 分页 + Redis 缓存",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(products_router)


@app.get("/", tags=["health"])
async def health_check():
    return {"status": "ok", "docs": "/docs"}
