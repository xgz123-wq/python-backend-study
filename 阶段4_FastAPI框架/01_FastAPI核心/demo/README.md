# FastAPI 核心 Demo

> 累积式 Demo：6 个知识点共用一个 `app/` 项目，不是 6 个独立脚本。
> 每学一个知识点，`app/` 就新增或完善对应的文件。

---

## 快速启动

```bash
# 1. 安装依赖（建议在虚拟环境中）
pip install -r requirements.txt

# 2. 启动服务（在 demo/ 目录下运行）
uvicorn app.main:app --reload

# 3. 打开 API 文档
# 浏览器访问 http://localhost:8000/docs
```

---

## 知识点 → 文件对应关系

| 知识点 | 对应理论文档 | 对应代码文件 | 学完后能看到什么 |
|--------|-------------|-------------|-----------------|
| 1. 路由与请求参数 | `1.路由与请求参数.md` | `app/main.py`（路由注册）<br>`app/routers/items.py`（路由实现） | `/docs` 里出现 5 个接口 |
| 2. Pydantic 数据验证 | `2.Pydantic数据验证.md` | `app/schemas.py` | 传错误数据自动返回 422 |
| 3. 依赖注入 Depends | `3.依赖注入Depends.md` | `app/deps.py` | 路由自动拿到 db session |
| 4. async 异步 | `4.async异步.md` | `app/routers/items.py`（全路由 async） | 理解非阻塞执行 |
| 5. SQLAlchemy 异步集成 | `5.SQLAlchemy异步集成.md` | `app/database.py`<br>`app/models/item.py` | 数据真正落库（SQLite 文件） |
| 6. 中间件与异常处理 | `6.中间件与异常处理.md` | `app/main.py`（中间件部分） | 响应头有 `X-Process-Time` |

---

## Demo 目录结构

```
demo/
├── requirements.txt          # 依赖：fastapi/uvicorn/sqlalchemy/aiosqlite...
└── app/
    ├── main.py               # 入口：注册路由、中间件、异常处理（知识点1+6）
    ├── database.py           # 异步引擎 + Session 工厂 + 建表（知识点5）
    ├── schemas.py            # Pydantic Schema（知识点2）
    ├── deps.py               # 依赖函数：get_db（知识点3）
    ├── models/
    │   └── item.py           # SQLAlchemy 模型（知识点5）
    └── routers/
        └── items.py          # 商品 CRUD 路由（串联所有知识点）
```

---

## 用 curl 测试接口

```bash
# 创建商品
curl -X POST http://localhost:8000/items/ \
  -H "Content-Type: application/json" \
  -d '{"name":"苹果","price":5.5,"description":"新鲜红富士"}'

# 查询列表（分页）
curl "http://localhost:8000/items/?skip=0&limit=5"

# 查询单个
curl http://localhost:8000/items/1

# 部分更新（只改价格）
curl -X PATCH http://localhost:8000/items/1 \
  -H "Content-Type: application/json" \
  -d '{"price":6.0}'

# 删除
curl -X DELETE http://localhost:8000/items/1
```

---

## 常见问题

| 问题 | 原因 | 解决 |
|------|------|------|
| `ModuleNotFoundError: No module named 'app'` | 没在 `demo/` 目录下运行 | `cd demo/` 再执行 uvicorn |
| `aiosqlite` 找不到 | 依赖没装 | `pip install -r requirements.txt` |
| 启动后 `/docs` 打不开 | 端口被占用 | 换端口 `uvicorn app.main:app --port 8001` |
| `422 Unprocessable Entity` | 请求数据验证失败 | 看响应 body 里的 detail，检查字段类型/约束 |

---

## 核心要点

1. **路由三要素**：装饰器（方法+路径）、函数（接收参数）、返回值（自动转 JSON）
2. **Schema 分层**：Create/Update/Response 三类，不共用同一个
3. **Depends 的价值**：把重复逻辑（db/认证）抽出来，路由只关注业务
4. **async 禁忌**：异步路由里不能用同步数据库驱动
5. **累积式学习**：代码看不懂回查对应 .md，改完跑一遍看控制台输出
