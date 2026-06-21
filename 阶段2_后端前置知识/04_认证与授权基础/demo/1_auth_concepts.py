"""
Demo 1: 认证与授权基础概念演示
对应理论文档: 1.认证与授权概念.md

演示内容：
- Session 登录机制模拟
- Token 登录机制模拟
- 401 vs 403 的区别
- RBAC 权限控制

运行方式: python 1_auth_concepts.py
前置依赖: 无（仅使用标准库）
"""

import hashlib
import time
import json
import secrets

print("=" * 60)
print("Demo 1: 认证（AuthN）与授权（AuthZ）基础概念")
print("=" * 60)

# ─────────────────────────────────────────────
# Part 1: 认证 vs 授权的直观对比
# ─────────────────────────────────────────────
print("\n【Part 1】认证 vs 授权")
print("-" * 40)

class SimpleAuthSystem:
    """
    简化版认证与授权系统，用于演示概念
    （生产环境请用 bcrypt + JWT，不要用这个！）
    """
    
    def __init__(self):
        # 用户数据库：用户名 → {密码哈希, 角色}
        self.users = {
            "alice": {"password_hash": hashlib.sha256("alice123".encode()).hexdigest(), "role": "user"},
            "bob":   {"password_hash": hashlib.sha256("bob456".encode()).hexdigest(),   "role": "admin"},
            "root":  {"password_hash": hashlib.sha256("root999".encode()).hexdigest(),  "role": "super_admin"},
        }
        # 权限表：角色 → 可执行操作
        self.permissions = {
            "user":        ["read_own_profile", "read_public_posts", "create_comment"],
            "admin":       ["read_own_profile", "read_public_posts", "create_comment",
                            "manage_users", "delete_comments"],
            "super_admin": ["read_own_profile", "read_public_posts", "create_comment",
                            "manage_users", "delete_comments", "system_config", "delete_users"],
        }

    def authenticate(self, username: str, password: str) -> dict | None:
        """
        认证（Authentication）：验证用户身份
        返回 None 表示认证失败 → HTTP 401 Unauthorized
        """
        user = self.users.get(username)
        if not user:
            return None  # 用户不存在
        
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        if password_hash != user["password_hash"]:
            return None  # 密码错误
        
        return {"username": username, "role": user["role"]}

    def authorize(self, user: dict, action: str) -> bool:
        """
        授权（Authorization）：验证用户是否有权执行某操作
        返回 False 表示无权限 → HTTP 403 Forbidden
        """
        allowed_actions = self.permissions.get(user["role"], [])
        return action in allowed_actions

auth = SimpleAuthSystem()

# 演示：认证阶段
print("\n--- 认证（Authentication）演示 ---")
test_cases = [
    ("alice", "alice123"),  # 正确
    ("alice", "wrong"),     # 密码错误
    ("nobody", "xxx"),      # 用户不存在
]

for username, password in test_cases:
    user = auth.authenticate(username, password)
    if user:
        print(f"✅ 认证成功: {username} → 角色: {user['role']}")
    else:
        print(f"❌ 认证失败: {username} → HTTP 401 Unauthorized（未认证）")

# 演示：授权阶段
print("\n--- 授权（Authorization）演示 ---")
alice = auth.authenticate("alice", "alice123")
bob   = auth.authenticate("bob", "bob456")

test_actions = [
    (alice, "read_public_posts"),   # 普通用户可以
    (alice, "manage_users"),        # 普通用户不能
    (bob,   "manage_users"),        # 管理员可以
    (bob,   "system_config"),       # 管理员不能（需要 super_admin）
]

for user, action in test_actions:
    if auth.authorize(user, action):
        print(f"✅ 授权成功: {user['username']}({user['role']}) → 允许 [{action}]")
    else:
        print(f"❌ 授权失败: {user['username']}({user['role']}) → 拒绝 [{action}] HTTP 403 Forbidden（无权限）")

# ─────────────────────────────────────────────
# Part 2: Session 机制模拟
# ─────────────────────────────────────────────
print("\n\n【Part 2】Session 机制模拟")
print("-" * 40)

class SessionStore:
    """模拟服务端 Session 存储（真实场景用 Redis）"""
    
    def __init__(self):
        self._sessions = {}  # session_id → {user_data, expires_at}
    
    def create_session(self, user_data: dict, ttl_seconds: int = 3600) -> str:
        """创建 Session，返回 Session ID（存在 Cookie 里）"""
        session_id = secrets.token_urlsafe(32)  # 随机安全的 Session ID
        self._sessions[session_id] = {
            "user": user_data,
            "expires_at": time.time() + ttl_seconds,
            "created_at": time.time(),
        }
        return session_id
    
    def get_session(self, session_id: str) -> dict | None:
        """用 Session ID 查找用户信息（模拟 Cookie 请求）"""
        session = self._sessions.get(session_id)
        if not session:
            return None  # Session 不存在
        if time.time() > session["expires_at"]:
            del self._sessions[session_id]
            return None  # Session 已过期
        return session["user"]
    
    def delete_session(self, session_id: str):
        """删除 Session（登出）"""
        self._sessions.pop(session_id, None)

session_store = SessionStore()

# 模拟用户登录（Session 方式）
print("场景：用户 Alice 用 Session 方式登录")
alice_user = auth.authenticate("alice", "alice123")
session_id = session_store.create_session(alice_user)
print(f"  登录成功，服务器创建 Session")
print(f"  Session ID: {session_id[:20]}...（存入 Cookie，自动携带）")

# 模拟后续请求（服务器从 Cookie 中取 session_id）
print("\n模拟第 2 次请求（浏览器自动携带 Cookie）：")
user_from_session = session_store.get_session(session_id)
if user_from_session:
    print(f"  服务器查 Session → 找到用户: {user_from_session['username']}")

# 模拟登出
session_store.delete_session(session_id)
print("\n模拟登出：服务器删除 Session")
user_after_logout = session_store.get_session(session_id)
print(f"  再次携带旧 Session ID → 结果: {'找到（未登出？）' if user_after_logout else '找不到，Session 已删除 ✅'}")

print("\n📌 Session 核心特点：")
print("  - 状态存在服务端（内存/Redis）")
print("  - 浏览器只存一个 Session ID（Cookie）")
print("  - 登出直接删除服务端 Session，立即生效")
print("  - 多服务器部署需要共享 Session（如 Redis）")

# ─────────────────────────────────────────────
# Part 3: HTTP 状态码 401 vs 403 演示
# ─────────────────────────────────────────────
print("\n\n【Part 3】HTTP 状态码：401 vs 403")
print("-" * 40)

def simulate_api_request(session_id: str | None, action: str, user_session_store: SessionStore):
    """模拟 API 请求处理流程"""
    
    # Step 1: 认证（你是谁？）
    if not session_id:
        return 401, "未提供认证凭证（请先登录）"
    
    current_user = user_session_store.get_session(session_id)
    if not current_user:
        return 401, "Session 无效或已过期（请重新登录）"
    
    # Step 2: 授权（你能做什么？）
    if not auth.authorize(current_user, action):
        return 403, f"权限不足，{current_user['role']} 角色无法执行 [{action}]"
    
    return 200, f"操作成功！{current_user['username']} 执行了 [{action}]"

# 重新创建 Alice 的 Session
alice_session = session_store.create_session(alice_user)

print("模拟不同请求场景：")
scenarios = [
    (None,          "manage_users"),   # 未登录
    (alice_session, "read_public_posts"),  # 有权限
    (alice_session, "manage_users"),   # 无权限
    ("invalid_id",  "read_public_posts"),  # 无效 Session
]

for sid, action in scenarios:
    status, message = simulate_api_request(sid, action, session_store)
    icon = "✅" if status == 200 else ("🔐" if status == 401 else "🚫")
    print(f"  {icon} HTTP {status}: {message}")

print("\n📌 关键区分：")
print("  401 Unauthorized = 未认证（没登录 / Token 过期 / 无效）")
print("  403 Forbidden    = 未授权（已登录，但没有这个权限）")

print("\n" + "=" * 60)
print("✅ Demo 1 完成！核心概念：")
print("  • 认证（AuthN）= 验证身份，失败返回 401")
print("  • 授权（AuthZ）= 验证权限，失败返回 403")
print("  • RBAC = 用户→角色→权限，最常用的权限模型")
print("  • Session = 服务端存状态，Cookie 传 ID")
print("=" * 60)
