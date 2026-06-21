# 04_认证与授权基础 - Demo 说明

> 本章 Demo 演示 Web 后端认证与授权的核心机制，绝大多数使用标准库，无需外部依赖。

---

## 学习顺序

建议按以下顺序运行和阅读，每个 Demo 与一篇理论文档 1:1 对应：

| 顺序 | Demo 文件 | 对应理论 | 说明 |
|------|-----------|----------|------|
| 1 | `1_auth_concepts.py` | `1.认证与授权概念.md` | AuthN vs AuthZ、Session 机制、401 vs 403、RBAC |
| 2 | `2_jwt_demo.py` | `2.JWT详解.md` | JWT 结构解析、签名原理、双 Token 机制 |
| 3 | `3_password_hash.py` | `3.密码哈希bcrypt与argon2.md` | MD5 危险性、bcrypt/argon2 加盐哈希 |
| 4 | `4_oauth2_demo.py` | `4.OAuth2.0授权.md` | 授权码模式完整流程、state 防 CSRF、scope 控制 |

---

## 运行方式

### Demo 1（无依赖，直接运行）
```bash
python 1_auth_concepts.py
```

### Demo 2（需要 PyJWT）
```bash
pip install PyJWT
python 2_jwt_demo.py
```
> Part 1 和 Part 2 使用纯标准库，无需 PyJWT，可以先运行观察 JWT 结构

### Demo 3（需要 bcrypt 和 passlib）
```bash
pip install bcrypt "passlib[bcrypt]"
# 可选（argon2 支持）
pip install "argon2-cffi" "passlib[argon2]"
python 3_password_hash.py
```
> 即使不安装依赖也可以运行，会跳过对应 Part 并提示安装命令

### Demo 4（无依赖，直接运行）
```bash
python 4_oauth2_demo.py
```

---

## Demo 详细说明

### Demo 1: 认证与授权基础概念（理解 AuthN vs AuthZ）

**文件**: `1_auth_concepts.py`

演示认证（Authentication）和授权（Authorization）的本质区别，通过一个简化的用户系统模拟 RBAC（基于角色的权限控制），以及 Session 机制的完整工作原理。直观演示 HTTP 401 和 403 的触发场景。

**运行方式**: `python 1_auth_concepts.py`  
**前置依赖**: 无（仅标准库）  
**测试方式**: 观察控制台输出，理解每个场景对应的 HTTP 状态码

---

### Demo 2: JWT 结构与生成验证（理解 Token 的本质）

**文件**: `2_jwt_demo.py`

分三部分：①手动 Base64URL 解码真实 JWT，证明 Payload 任何人都能读取；②用纯标准库实现 HS256 签名和验证，理解签名防篡改原理；③用 PyJWT 库实现 Access Token + Refresh Token 双 Token 机制。

**运行方式**: `python 2_jwt_demo.py`  
**前置依赖**: `pip install PyJWT`（Part 3 需要，Part 1/2 不需要）  
**测试方式**: 观察控制台输出，注意 Payload 解码和签名篡改检测的结果

---

### Demo 3: 密码哈希（为什么慢是优点）

**文件**: `3_password_hash.py`

通过数据对比直观理解密码安全存储：①演示 MD5 的速度和彩虹表攻击；②演示 bcrypt 的加盐效果（同密码不同结果）和速度控制；③演示 argon2 的高内存特性；④演示 passlib 的统一接口（生产环境推荐方式）。

**运行方式**: `python 3_password_hash.py`  
**前置依赖**: `pip install bcrypt "passlib[bcrypt]"`  
**测试方式**: 观察 MD5 vs bcrypt 的速度对比数字，理解"慢"为什么是安全优势

---

### Demo 4: OAuth2.0 授权流程（完整模拟）

**文件**: `4_oauth2_demo.py`

完整模拟 OAuth2.0 授权码模式（类比"用 GitHub 登录"），包含：授权 URL 构建与参数解析、用户同意授权后的 code 生成、服务端用 code + client_secret 换取 token、state 防 CSRF 攻击演示、scope 权限范围控制、以及机器对机器的客户端凭证模式。

**运行方式**: `python 4_oauth2_demo.py`  
**前置依赖**: 无（仅标准库）  
**测试方式**: 观察控制台输出，特别注意 state 防 CSRF 的演示部分

---

## 对应理论文档

| Demo 文件 | 理论文档 | 核心概念 |
|-----------|----------|----------|
| `1_auth_concepts.py` | `1.认证与授权概念.md` | AuthN/AuthZ 区别、Session、RBAC、401 vs 403 |
| `2_jwt_demo.py` | `2.JWT详解.md` | JWT 结构、签名防篡改、双 Token 机制 |
| `3_password_hash.py` | `3.密码哈希bcrypt与argon2.md` | 彩虹表攻击、加盐哈希、慢哈希原理 |
| `4_oauth2_demo.py` | `4.OAuth2.0授权.md` | 授权码流程、state、scope、客户端凭证 |

---

## 核心要点

1. **认证（AuthN）≠ 授权（AuthZ）**：认证=验证身份（失败→401），授权=验证权限（失败→403）
2. **JWT 不是加密**：Payload 是 Base64URL 编码，任何人都能读取，不要存敏感信息
3. **密码哈希要用专门的算法**：bcrypt/argon2，不能用 MD5/SHA1（太快，可被彩虹表/暴力破解）
4. **双 Token 机制**：Access Token 短期（2h）用于 API 访问，Refresh Token 长期（30d）无感刷新
5. **OAuth2 = 授权框架**：解决"第三方访问用户数据"的问题，全程无需用户提供密码给第三方
6. **state 参数是必须的**：防止 CSRF 攻击，每次 OAuth 授权都要验证 state

---

## 常见问题

| 问题 | 解决方案 |
|------|---------|
| `ModuleNotFoundError: No module named 'jwt'` | `pip install PyJWT`（注意是 PyJWT 不是 jwt） |
| `ModuleNotFoundError: No module named 'bcrypt'` | `pip install bcrypt` |
| `ModuleNotFoundError: No module named 'passlib'` | `pip install "passlib[bcrypt]"` |
| `ModuleNotFoundError: No module named 'argon2'` | `pip install "argon2-cffi"` |
| Demo 3 运行很慢（bcrypt 部分）| 正常现象！bcrypt 故意设计得慢，rounds=12 约 300ms |
| JWT 部分 Part 1/2 报错 | Part 1/2 不需要 PyJWT，检查 Python 版本（需要 3.10+）|

---

## 本章与后续章节的关系

```
本章学习的概念            → 在哪里深入使用
─────────────────────────────────────────────
JWT 生成与验证           → 第四阶段 FastAPI 中实现完整的 JWT 认证中间件
bcrypt 密码哈希          → 第四阶段 FastAPI 用户注册/登录接口
OAuth2 PasswordBearer   → 第四阶段 FastAPI 的 Depends(oauth2_scheme) 依赖注入
完整登录系统             → 第五阶段 项目实战（用户模块）
```
