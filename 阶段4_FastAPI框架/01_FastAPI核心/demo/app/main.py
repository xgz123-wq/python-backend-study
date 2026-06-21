"""
FastAPI 入口（知识点1+6：路由注册、中间件、异常处理）

累积式学习说明：
- 知识点1 后：能看到路由，文档 /docs 可以调用接口
- 知识点2 后：schemas.py 完善，请求验证生效
- 知识点3 后：deps.py 完善，Depends 注入生效
- 知识点4 后：全路由 async，理解非阻塞
- 知识点5 后：database.py 完善，数据真正落库
- 知识点6 后：中间件+异常处理加上，本文件最终形态
"""
import time
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.database import init_db
from app.routers.items import router as items_router


# 生命周期管理（替代已废弃的 on_event）
@asynccontextmanager
async def lifespan(app: FastAPI):
    # 启动时建表
    await init_db()
    yield
    # 关闭时可做清理


app = FastAPI(
    title="FastAPI 学习 Demo",
    description="累积式 Demo：每学一个知识点，这个 app 就更完整",
    version="1.0.0",
    lifespan=lifespan,
)

# ---- 知识点6：CORS 中间件（必须最先 add）----
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # 开发用 *，生产改为实际前端域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---- 知识点6：自定义中间件（记录请求耗时）----
@app.middleware("http")
async def log_process_time(request: Request, call_next):
    start = time.time()
    response = await call_next(request)
    duration = round((time.time() - start) * 1000, 2)
    response.headers["X-Process-Time"] = f"{duration}ms"
    print(f"{request.method} {request.url.path} → {response.status_code} ({duration}ms)")
    return response

# ---- 知识点6：全局异常处理（把未捕获异常转为统一 JSON）----
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={"code": 500, "message": "Internal Server Error", "detail": str(exc)},
    )

# ---- 注册路由 ----
app.include_router(items_router)


@app.get("/", tags=["health"])
async def health_check():
    return {"status": "ok", "docs": "/docs"}
