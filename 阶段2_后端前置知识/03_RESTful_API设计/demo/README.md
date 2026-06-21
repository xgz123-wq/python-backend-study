# RESTful API 设计 - Demo 运行指南

## 学习顺序

按以下顺序运行，每个 Demo 独立可执行：

| 顺序 | 文件 | 对应理论 | 核心内容 |
|------|------|---------|---------|
| 1 | `1_restful_principles.py` | `1.RESTful设计原则.md` | 资源导向 vs 动作导向，HTTP 方法与 CRUD 映射 |
| 2 | `2_url_naming.py` | `2.URL命名规范.md` | 嵌套资源路由，特殊操作子路径，路径参数 vs 查询参数 |
| 3 | `3_unified_response.py` | `3.统一响应格式.md` | 统一响应结构，业务错误码体系，分页元数据格式 |
| 4 | `4_pagination_filter.py` | `4.分页过滤排序.md` | 页码分页、游标分页、多条件过滤、排序白名单校验 |
| 5 | `5_api_versioning.py` | `5.API版本管理.md` | v1/v2 并存，破坏性变更演示，弃用警告 Header |

## 运行方式

每个 Demo 直接运行即可，无需安装额外依赖（仅用 Python 标准库）：

```bash
# 在项目根目录执行
python "阶段2_后端前置知识/03_RESTful_API设计/demo/1_restful_principles.py"
python "阶段2_后端前置知识/03_RESTful_API设计/demo/2_url_naming.py"
python "阶段2_后端前置知识/03_RESTful_API设计/demo/3_unified_response.py"
python "阶段2_后端前置知识/03_RESTful_API设计/demo/4_pagination_filter.py"
python "阶段2_后端前置知识/03_RESTful_API设计/demo/5_api_versioning.py"
```

## 各 Demo 详细说明

### Demo 1：RESTful 设计原则（端口 8301）

**演示要点：**
- `GET /users` 获取所有用户（集合）
- `GET /users/{id}` 获取单个用户
- `POST /users` 创建用户，返回 **201**（不是 200）
- `PATCH /users/{id}` 部分更新（只改传入字段）
- `DELETE /users/{id}` 删除用户，返回 **204**（无响应体）

**关键对比：**
```
动作导向（旧）              资源导向（RESTful）
POST /getUser         →    GET /users/{id}
POST /createUser      →    POST /users
POST /deleteUser      →    DELETE /users/{id}
```

---

### Demo 2：URL 命名规范（端口 8302）

**演示要点：**
- 名词复数：`/users`、`/orders`
- 嵌套资源：`/users/{id}/orders`（不超过 2 层）
- 查询参数过滤：`/users?role=admin`
- 特殊操作子路径：`/orders/{id}/pay`、`/orders/{id}/cancel`

**命名规范七条：**
1. 名词，不用动词
2. 复数表示集合
3. 小写 + 连字符（kebab-case）
4. 层级路径表资源关系
5. 查询参数做过滤/分页/排序
6. 特殊操作用子路径动名词
7. 统一 `/api` 前缀

---

### Demo 3：统一响应格式（端口 8303）

**统一结构：**
```json
成功: {"code": 0, "message": "success", "data": {...}}
失败: {"code": 40401, "message": "用户不存在", "data": null}
```

**业务错误码体系：**
```
0       → 成功
40001   → 参数错误（对应 HTTP 400）
40002   → 数据重复（对应 HTTP 400）
40101   → 未认证（对应 HTTP 401）
40301   → 无权限（对应 HTTP 403）
40401   → 用户不存在（对应 HTTP 404）
50001   → 服务器错误（对应 HTTP 500）
```

**分页响应结构：**
```json
{
  "data": {
    "items": [...],
    "pagination": {
      "page": 1, "size": 10, "total": 100,
      "totalPages": 10, "hasNext": true, "hasPrev": false
    }
  }
}
```

---

### Demo 4：分页、过滤与排序（端口 8304）

**数据集：** 50 个商品（随机分类、价格、评分）

**分页方式：**
- 页码分页：`GET /products?page=2&size=10`
- 游标分页：`GET /products/cursor?size=5&cursor=<base64>`

**过滤参数：**
```
?category=electronics       等值过滤
?price_gte=100&price_lte=500  范围过滤
?rating_gte=4.0             评分过滤
?in_stock=true              布尔过滤
?q=001                      模糊搜索
```

**排序参数：**
```
?sort=price&order=desc      单字段降序
?sort=rating&order=asc      单字段升序
```

**安全特性：** sort 字段白名单校验，非法字段返回 400。

---

### Demo 5：API 版本管理（端口 8305）

**v1 vs v2 破坏性变更对比：**

| 字段 | v1 格式 | v2 格式 | 变更类型 |
|------|---------|---------|---------|
| 用户ID | `user_id` | `id` | 字段重命名（破坏性）|
| 用户名 | `user_name` | `username` | 字段重命名（破坏性）|
| 邮箱 | `user_email` | `email` | 字段重命名（破坏性）|
| 创建时间 | `"2024-01-01 00:00:00"` | `"2024-01-01T00:00:00Z"` | 格式变更（破坏性）|
| 头像 | 无 | `avatar_url: null` | 新增字段（非破坏性）|

**弃用警告响应头：**
```
Deprecation: true
Sunset: Sun, 01 Jun 2025 00:00:00 GMT
X-Warning: API v1 将于 2025-06-01 下线，请迁移至 v2
```

---

## 核心概念速查

| 概念 | 关键点 |
|------|--------|
| RESTful | 资源导向 + HTTP 方法表达动作 + 无状态 |
| URL 规范 | 名词复数 + 小写连字符 + 层级嵌套 ≤ 2 层 |
| 响应格式 | `{code, message, data}` 三字段统一 |
| 分页 | 页码分页（适合跳页） vs 游标分页（适合Feed流） |
| 过滤 | 查询参数：等值/范围/_gte/_lte/布尔/模糊 |
| 排序 | sort + order 参数，**必须白名单校验** |
| 版本管理 | URL 路径版本（/v1/）最推荐，破坏性变更时必须升版本 |

## 常见问题

**Q: Demo 运行报端口占用错误？**
> 各 Demo 使用不同端口（8301~8305），确保没有其他进程占用。

**Q: Demo 4 每次运行数据一样吗？**
> 是的，使用 `random.seed(42)` 固定随机种子，保证每次运行结果一致。

**Q: Demo 中的服务器什么时候停止？**
> Demo 以守护线程运行服务器，主线程执行完客户端演示后程序自动退出。
