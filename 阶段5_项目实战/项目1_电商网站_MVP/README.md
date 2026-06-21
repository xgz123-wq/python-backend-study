# 电商 MVP 项目

> 阶段5实战核心：用一个完整项目把前4个阶段的知识全部激活。
> 不追求功能多，追求**每个功能走完整的项目流程SOP**。

## 功能清单（3 个核心功能）

| 功能 | 接口 | 激活的前置知识 |
|------|------|---------------|
| 用户注册/登录/JWT | `POST /auth/register`<br>`POST /auth/login`<br>`GET /auth/me` | 阶段2认证授权、密码哈希；阶段4 Pydantic |
| 商品 CRUD + 分页 | `GET /products/`<br>`GET /products/{id}`<br>`POST /products/`<br>`PATCH /products/{id}`<br>`DELETE /products/{id}` | 阶段3 SQLAlchemy；阶段2 RESTful 分页；阶段4 Depends |
| 商品列表 Redis 缓存 | 同上（列表接口透明缓存） | 阶段3 Redis、缓存穿透处理 |

---

## 项目流程 SOP（每新增功能都走一遍）

```
1. 需求拆解    → 明确：这个功能需要哪些接口？数据有哪些字段？
2. 数据建模    → 写 app/models/xxx.py（SQLAlchemy 模型）
3. API 设计    → 先写 app/schemas/xxx.py + 路由签名（不实现），看 /docs 是否符合预期
4. 分层实现    → router 调 service，service 调 DB/Redis
5. Postman测试 → 按下方 curl 命令逐一测试每个接口
6. 写 pytest   → tests/ 里写 1-2 个关键路径测试
```

---

## 启动方式

### 第一步：启动中间件

```bash
# 在项目根目录（有 docker-compose.yml 的目录）
docker-compose up -d

# 确认服务正常
docker-compose ps      # mysql/redis 都是 healthy/running
```

### 第二步：安装依赖

```bash
pip install -r requirements.txt
```

### 第三步：启动 API 服务

```bash
# 在项目根目录（有 app/ 目录的那层）
uvicorn app.main:app --reload

# 打开 API 文档
# http://localhost:8000/docs
```

---

## curl 测试命令（项目 SOP 第5步）

### 功能1：用户注册登录

```bash
# 注册
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{"username":"testuser","email":"test@example.com","password":"123456"}'

# 登录（拿到 access_token）
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"testuser","password":"123456"}'

# 查看当前用户（需要 token，替换 YOUR_TOKEN）
curl http://localhost:8000/auth/me \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### 功能2：商品 CRUD + 分页

```bash
# 创建商品（需要登录）
curl -X POST http://localhost:8000/products/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{"name":"苹果","price":5.5,"stock":100,"category":"水果"}'

# 商品列表（分页）
curl "http://localhost:8000/products/?skip=0&limit=10"

# 按分类筛选
curl "http://localhost:8000/products/?category=水果"

# 商品详情
curl http://localhost:8000/products/1

# 更新价格
curl -X PATCH http://localhost:8000/products/1 \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{"price":6.0}'

# 删除（软删除）
curl -X DELETE http://localhost:8000/products/1 \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### 功能3：验证 Redis 缓存

```bash
# 第1次请求（查数据库，控制台会打印 SQL）
curl "http://localhost:8000/products/?skip=0&limit=10"

# 第2次请求（命中缓存，控制台不再打印 SQL）
curl "http://localhost:8000/products/?skip=0&limit=10"

# 查看 Redis 里的缓存（需要 Redis 客户端）
# redis-cli -a redis123
# KEYS products:*
# GET products:list:0:10:all
```

---

## 运行测试

```bash
pytest tests/ -v
```

---

## 目录结构

```
项目1_电商网站_MVP/
├── README.md
├── requirements.txt
├── docker-compose.yml
└── app/
    ├── main.py            # 入口
    ├── config.py          # 配置（读环境变量）
    ├── database.py        # DB引擎 + Redis连接
    ├── deps.py            # Depends：get_db, get_current_user
    ├── models/
    │   ├── user.py        # 用户表
    │   └── product.py     # 商品表
    ├── schemas/
    │   ├── user.py        # 用户 Schema
    │   └── product.py     # 商品 Schema
    ├── routers/
    │   ├── auth.py        # 认证路由
    │   └── products.py    # 商品路由
    ├── services/
    │   ├── user_service.py    # 用户业务逻辑
    │   └── product_service.py # 商品业务逻辑（含Redis缓存）
    └── utils/
        └── security.py    # 密码哈希 + JWT
```

---

## 常见问题

| 问题 | 原因 | 解决 |
|------|------|------|
| `Can't connect to MySQL` | MySQL 容器未启动或未就绪 | `docker-compose up -d && docker-compose ps` 确认 healthy |
| `Authentication required` | JWT token 过期或格式错误 | 重新登录拿新 token，格式：`Bearer <token>` |
| `422 Unprocessable Entity` | 请求体字段类型/约束不对 | 查看响应 body 的 detail 字段 |
| 列表缓存不更新 | 写操作没有清缓存 | 检查 product_service.py 的 `_clear_list_cache` 是否被调用 |

---

## 停止服务

```bash
docker-compose down          # 停止（数据保留）
docker-compose down -v       # 停止并清除数据
```
