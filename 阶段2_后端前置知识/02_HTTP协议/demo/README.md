# 02_HTTP协议 - Demo 说明

> 本章 Demo 使用 Python 标准库（`http.server`、`http.client`），无需安装第三方依赖。

---

## 学习顺序

建议按以下顺序运行和阅读，每个 Demo 与一篇理论文档 1:1 对应：

| 顺序 | Demo 文件 | 对应理论 | 说明 |
|------|-----------|----------|------|
| 1 | `1_http_request_response.py` | `1.HTTP请求与响应结构.md` | 观察请求行、Header、Body 与响应结构 |
| 2 | `2_methods_status_codes.py` | `2.HTTP方法与状态码.md` | 体验 HTTP 方法语义和常见状态码 |
| 3 | `3_headers_content_type.py` | `3.Header与Content-Type.md` | 理解 Header、Content-Type、Accept、Authorization |
| 4 | `4_cookie_session.py` | `4.Cookie与Session.md` | 模拟登录态、Cookie、Session 的配合 |
| 5 | `5_https_cors.py` | `5.HTTPS与CORS.md` | 理解 HTTPS 目标与 CORS 预检流程 |

---

## 运行方式

所有 Demo 均为独立脚本，直接运行即可：

```bash
python 1_http_request_response.py
python 2_methods_status_codes.py
python 3_headers_content_type.py
python 4_cookie_session.py
python 5_https_cors.py
```

**前置依赖**：无额外依赖，仅使用 Python 标准库。

---

## Demo 详细说明

### Demo 1: HTTP 请求与响应结构

**文件**: `1_http_request_response.py`

启动一个本地 HTTP 服务，并用客户端发送 `GET` 和 `POST` 请求。观察路径、查询参数、请求头、请求体、状态码、响应头、响应体如何组成一次完整 HTTP 交互。

**运行方式**: `python 1_http_request_response.py`  
**前置依赖**: 无额外依赖  
**测试方式**: 观察控制台输出中的客户端请求与服务端解析结果

### Demo 2: HTTP 方法与状态码

**文件**: `2_methods_status_codes.py`

演示 `GET`、`POST`、`PUT`、`PATCH`、`DELETE` 的语义，并返回 `200`、`201`、`204`、`400`、`404`、`500` 等状态码。

**运行方式**: `python 2_methods_status_codes.py`  
**前置依赖**: 无额外依赖  
**测试方式**: 观察不同请求对应的状态码和响应体

### Demo 3: Header 与 Content-Type

**文件**: `3_headers_content_type.py`

分别发送 JSON、表单、纯文本请求，观察服务端如何根据 `Content-Type` 解析请求体，并理解 `Accept` 与 `Authorization` 的作用。

**运行方式**: `python 3_headers_content_type.py`  
**前置依赖**: 无额外依赖  
**测试方式**: 对比不同 `Content-Type` 下的解析结果

### Demo 4: Cookie 与 Session

**文件**: `4_cookie_session.py`

模拟登录流程：服务端创建 Session，通过 `Set-Cookie` 返回 `session_id`，客户端后续携带 Cookie 访问个人中心。

**运行方式**: `python 4_cookie_session.py`  
**前置依赖**: 无额外依赖  
**测试方式**: 观察未登录访问、登录后拿到 Cookie、携带 Cookie 访问的结果差异

### Demo 5: HTTPS 与 CORS

**文件**: `5_https_cors.py`

解释 HTTPS 的加密、完整性、身份认证目标，并模拟浏览器跨域预检 `OPTIONS` 请求，观察允许来源与不允许来源的 CORS 响应头差异。

**运行方式**: `python 5_https_cors.py`  
**前置依赖**: 无额外依赖  
**测试方式**: 观察 `Access-Control-Allow-*` 响应头

---

## 对应理论文档

| Demo 文件 | 理论文档 | 核心概念 |
|-----------|----------|----------|
| `1_http_request_response.py` | `1.HTTP请求与响应结构.md` | 请求行、请求头、请求体、状态行、响应头、响应体 |
| `2_methods_status_codes.py` | `2.HTTP方法与状态码.md` | GET/POST/PUT/PATCH/DELETE、2xx/4xx/5xx |
| `3_headers_content_type.py` | `3.Header与Content-Type.md` | Header、Content-Type、Accept、Authorization |
| `4_cookie_session.py` | `4.Cookie与Session.md` | 无状态、Cookie、Session、Set-Cookie |
| `5_https_cors.py` | `5.HTTPS与CORS.md` | HTTPS、同源策略、CORS、预检请求 |

---

## 核心要点

1. **HTTP 是请求-响应模型**：客户端发请求，服务端回响应。
2. **方法表达动作**：`GET` 查、`POST` 建、`PUT` 全量改、`PATCH` 局部改、`DELETE` 删。
3. **状态码表达结果**：`2xx` 成功、`4xx` 客户端错误、`5xx` 服务端错误。
4. **Header 是元数据**：决定认证、格式、缓存、跨域等行为。
5. **Cookie/Session 解决无状态问题**：Cookie 存客户端，Session 存服务端。
6. **HTTPS 与 CORS 是 Web 安全基础**：HTTPS 保护传输，CORS 限制浏览器跨域访问。

---

## 常见问题

| 问题 | 解决方案 |
|------|----------|
| `Address already in use` | Demo 使用系统随机端口，正常不应冲突；如遇到，重新运行即可 |
| `ConnectionRefusedError` | 服务端可能未启动完成，重新运行脚本 |
| 中文响应显示乱码 | 确保终端使用 UTF-8；Demo 已设置 `charset=utf-8` |
| 浏览器和 Postman 跨域表现不同 | CORS 是浏览器安全策略，Postman 不受同源策略限制 |
