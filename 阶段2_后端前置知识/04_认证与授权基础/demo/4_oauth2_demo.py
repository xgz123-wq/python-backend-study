"""
Demo 4: OAuth2.0 授权流程模拟
对应理论文档: 4.OAuth2.0授权.md

演示内容：
- OAuth2.0 授权码模式完整流程模拟
- state 防 CSRF 攻击演示
- Scope 权限范围控制
- 客户端凭证模式（机器对机器）
- 手动解析 GitHub OAuth 流程

运行方式: python 4_oauth2_demo.py
前置依赖: 无（仅使用标准库）
注意: 本 Demo 模拟 OAuth2 流程，不真实调用 GitHub API
"""

import secrets
import time
import json
import hashlib
import hmac
from urllib.parse import urlencode, urlparse, parse_qs

print("=" * 60)
print("Demo 4: OAuth2.0 授权流程模拟")
print("=" * 60)

# ─────────────────────────────────────────────
# 模拟授权服务器（类似 GitHub 的授权系统）
# ─────────────────────────────────────────────

class MockAuthorizationServer:
    """
    模拟 OAuth2.0 授权服务器（类比 GitHub）
    真实场景中这是第三方平台（GitHub/Google/微信）的服务
    """
    
    def __init__(self):
        # 已注册的客户端应用
        self.registered_clients = {
            "my_app_client_id": {
                "client_secret": "super-secret-xyz-123",
                "name": "My Demo App",
                "redirect_uris": ["http://localhost:8000/auth/callback"],
                "allowed_scopes": ["read:user", "user:email", "repo"],
            }
        }
        # 已生成的授权码（临时，一次性）
        self._auth_codes = {}
        # 已签发的 Access Token
        self._access_tokens = {}
        # 模拟用户数据库
        self._users = {
            "alice": {
                "id": 1001,
                "username": "alice",
                "email": "alice@example.com",
                "avatar_url": "https://github.com/alice.png",
            }
        }
    
    def generate_auth_code(self, client_id: str, user_id: int,
                           scope: list[str], redirect_uri: str) -> str:
        """
        用户同意授权后，生成授权码（authorization_code）
        特点：一次性、短期有效（通常10分钟）
        """
        code = secrets.token_urlsafe(32)
        self._auth_codes[code] = {
            "client_id": client_id,
            "user_id": user_id,
            "scope": scope,
            "redirect_uri": redirect_uri,
            "expires_at": time.time() + 600,  # 10分钟有效
            "used": False,
        }
        return code
    
    def exchange_code_for_token(self, code: str, client_id: str,
                                 client_secret: str, redirect_uri: str) -> dict:
        """
        用授权码 + client_secret 换取 access_token
        这一步在服务端进行，client_secret 不会暴露给用户
        """
        code_data = self._auth_codes.get(code)
        
        # 验证授权码
        if not code_data:
            raise ValueError("无效的授权码")
        if code_data["used"]:
            raise ValueError("授权码已使用（一次性！）")
        if time.time() > code_data["expires_at"]:
            raise ValueError("授权码已过期")
        if code_data["client_id"] != client_id:
            raise ValueError("client_id 不匹配")
        if code_data["redirect_uri"] != redirect_uri:
            raise ValueError("redirect_uri 不匹配")
        
        # 验证 client_secret
        client = self.registered_clients.get(client_id)
        if not client or client["client_secret"] != client_secret:
            raise ValueError("client_secret 错误")
        
        # 授权码标记为已用（防重放）
        code_data["used"] = True
        
        # 生成 access_token
        access_token = secrets.token_urlsafe(40)
        self._access_tokens[access_token] = {
            "user_id": code_data["user_id"],
            "scope": code_data["scope"],
            "client_id": client_id,
            "expires_at": time.time() + 3600,  # 1小时有效
        }
        
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "expires_in": 3600,
            "scope": " ".join(code_data["scope"]),
        }
    
    def get_user_info(self, access_token: str, required_scope: str) -> dict:
        """
        用 access_token 获取用户信息（类似 GitHub API /user）
        会检查 token 是否包含所需的 scope
        """
        token_data = self._access_tokens.get(access_token)
        if not token_data:
            raise ValueError("无效的 access_token")
        if time.time() > token_data["expires_at"]:
            raise ValueError("access_token 已过期")
        if required_scope not in token_data["scope"]:
            raise PermissionError(f"token 没有 {required_scope} 权限")
        
        user = self._users.get("alice")  # 简化：直接返回 alice
        # 根据 scope 过滤返回的字段
        result = {"id": user["id"], "username": user["username"]}
        if "user:email" in token_data["scope"]:
            result["email"] = user["email"]
        return result


class MockClientApp:
    """
    模拟第三方客户端应用（类比"用 GitHub 登录"的那个网站）
    """
    
    def __init__(self, client_id: str, client_secret: str, redirect_uri: str):
        self.client_id = client_id
        self.client_secret = client_secret  # 只在服务端！绝不暴露给前端！
        self.redirect_uri = redirect_uri
        self._state_store = {}  # 存储待验证的 state
    
    def step1_build_authorization_url(self, scope: list[str],
                                       auth_server_url: str) -> str:
        """
        步骤1：构建授权 URL，引导用户跳转到授权服务器
        生成随机 state 防 CSRF 攻击
        """
        state = secrets.token_urlsafe(32)
        self._state_store[state] = {"created_at": time.time(), "scope": scope}
        
        params = {
            "client_id": self.client_id,
            "redirect_uri": self.redirect_uri,
            "scope": " ".join(scope),
            "state": state,
            "response_type": "code",
        }
        return f"{auth_server_url}/oauth/authorize?{urlencode(params)}"
    
    def step3_handle_callback(self, callback_url: str,
                               auth_server: MockAuthorizationServer) -> dict:
        """
        步骤3：处理授权回调
        - 验证 state 防 CSRF
        - 用 code 换 access_token（服务端操作）
        - 用 access_token 获取用户信息
        """
        # 解析回调 URL 中的参数
        parsed = urlparse(callback_url)
        params = parse_qs(parsed.query)
        
        code = params.get("code", [None])[0]
        state = params.get("state", [None])[0]
        error = params.get("error", [None])[0]
        
        if error:
            raise ValueError(f"授权被拒绝: {error}")
        
        # 验证 state（防 CSRF 攻击！）
        if state not in self._state_store:
            raise ValueError("❌ state 不匹配，可能是 CSRF 攻击！拒绝处理！")
        del self._state_store[state]  # 使用后删除
        
        # 用 code 换 access_token（服务端操作，使用 client_secret）
        token_data = auth_server.exchange_code_for_token(
            code=code,
            client_id=self.client_id,
            client_secret=self.client_secret,  # 服务端才有！
            redirect_uri=self.redirect_uri,
        )
        
        # 用 access_token 获取用户信息
        user_info = auth_server.get_user_info(
            token_data["access_token"],
            required_scope="read:user"
        )
        
        return {
            "token_data": token_data,
            "user_info": user_info,
        }


# ─────────────────────────────────────────────
# Part 1: 完整授权码模式演示
# ─────────────────────────────────────────────
print("\n【Part 1】OAuth2.0 授权码模式完整流程")
print("-" * 40)

auth_server = MockAuthorizationServer()
client_app = MockClientApp(
    client_id="my_app_client_id",
    client_secret="super-secret-xyz-123",  # 只有服务端知道！
    redirect_uri="http://localhost:8000/auth/callback",
)

print("\n═══ 步骤 1：构建授权 URL ═══")
auth_url = client_app.step1_build_authorization_url(
    scope=["read:user", "user:email"],
    auth_server_url="https://github.com"
)
print(f"重定向用户到：")
print(f"  {auth_url[:80]}...")

# 解析 URL 中的参数
parsed_url = urlparse(auth_url)
url_params = parse_qs(parsed_url.query)
print(f"\n参数解析：")
print(f"  client_id:    {url_params['client_id'][0]}")
print(f"  scope:        {url_params['scope'][0]}（只申请需要的权限！）")
print(f"  state:        {url_params['state'][0][:20]}...（随机，防CSRF）")
print(f"  redirect_uri: {url_params['redirect_uri'][0]}")

print("\n═══ 步骤 2：用户在 GitHub 页面登录并同意授权 ═══")
print("  [模拟] 用户 alice 点击同意，授权 read:user 和 user:email 权限")
# 模拟授权服务器生成授权码
auth_code = auth_server.generate_auth_code(
    client_id="my_app_client_id",
    user_id=1001,
    scope=["read:user", "user:email"],
    redirect_uri="http://localhost:8000/auth/callback",
)
print(f"  GitHub 生成授权码: {auth_code[:20]}...（一次性、10分钟有效）")

# 模拟回调 URL
state_value = url_params['state'][0]
callback_url = f"http://localhost:8000/auth/callback?code={auth_code}&state={state_value}"
print(f"\n  GitHub 重定向回调: {callback_url[:70]}...")

print("\n═══ 步骤 3：服务端处理回调 ═══")
result = client_app.step3_handle_callback(callback_url, auth_server)
token_data = result["token_data"]
user_info = result["user_info"]

print(f"  ✅ state 验证通过（防CSRF检查通过）")
print(f"  ✅ 授权码换取 Access Token 成功")
print(f"  Access Token: {token_data['access_token'][:20]}...")
print(f"  过期时间:     {token_data['expires_in']}秒")
print(f"  权限范围:     {token_data['scope']}")
print(f"\n  ✅ 获取用户信息成功:")
print(f"  用户信息: {json.dumps(user_info, ensure_ascii=False, indent=6)}")

print("\n  ✅ 登录完成！为用户创建本地会话（颁发我们自己的 JWT）")

# ─────────────────────────────────────────────
# Part 2: state 防 CSRF 攻击演示
# ─────────────────────────────────────────────
print("\n\n【Part 2】state 参数防御 CSRF 攻击")
print("-" * 40)

print("场景：攻击者伪造一个回调 URL，state 不匹配")
fake_callback = f"http://localhost:8000/auth/callback?code=FAKE_CODE&state=ATTACKER_STATE"
print(f"伪造的回调 URL: {fake_callback}")

try:
    client_app.step3_handle_callback(fake_callback, auth_server)
except ValueError as e:
    print(f"🛡️  防御成功: {e}")

print("\nstate 工作原理：")
print("  1. 发起授权前，服务端生成随机 state 并存入 session")
print("  2. 回调时，对比 URL 中的 state 与 session 中存的是否一致")
print("  3. 攻击者无法伪造正确的 state（因为不知道 session 里存的值）")

# ─────────────────────────────────────────────
# Part 3: Scope 权限范围控制
# ─────────────────────────────────────────────
print("\n\n【Part 3】Scope 权限范围控制（最小权限原则）")
print("-" * 40)

# 生成只有 read:user 权限的 token（没有 user:email）
limited_code = auth_server.generate_auth_code(
    client_id="my_app_client_id",
    user_id=1001,
    scope=["read:user"],  # 只有 read:user，没有 user:email
    redirect_uri="http://localhost:8000/auth/callback",
)
limited_token_data = auth_server.exchange_code_for_token(
    code=limited_code,
    client_id="my_app_client_id",
    client_secret="super-secret-xyz-123",
    redirect_uri="http://localhost:8000/auth/callback",
)
limited_token = limited_token_data["access_token"]

print(f"Token 权限范围: {limited_token_data['scope']}")

print("\n测试不同 scope 的访问：")
try:
    info = auth_server.get_user_info(limited_token, "read:user")
    print(f"✅ 访问基本信息（read:user）: 用户名={info['username']}")
except PermissionError as e:
    print(f"❌ {e}")

try:
    info = auth_server.get_user_info(limited_token, "user:email")
    print(f"✅ 访问邮箱（user:email）: {info.get('email')}")
except PermissionError as e:
    print(f"🚫 访问邮箱被拒绝: {e}")

print("\n📌 最小权限原则：只申请你真正需要的 scope！")
print("  ❌ 申请 admin:org repo delete_repo → 用户不信任，拒绝授权")
print("  ✅ 申请 read:user user:email → 用户更愿意同意")

# ─────────────────────────────────────────────
# Part 4: 客户端凭证模式（机器对机器）
# ─────────────────────────────────────────────
print("\n\n【Part 4】客户端凭证模式（无用户参与，机器对机器）")
print("-" * 40)

class ClientCredentialsFlow:
    """
    OAuth2.0 客户端凭证模式
    用途：服务A需要访问服务B的API，无需用户参与
    例如：定时任务服务、微服务间调用、CI/CD 流程
    """
    
    def __init__(self):
        self.registered_services = {
            "service_a": {
                "secret": "service-a-secret-key",
                "allowed_scopes": ["read:data", "write:data"],
            },
            "service_b": {
                "secret": "service-b-secret-key",
                "allowed_scopes": ["read:data"],  # 只读权限
            },
        }
        self._tokens = {}
    
    def get_token(self, client_id: str, client_secret: str,
                  scope: list[str]) -> dict:
        """
        服务用 client_id + client_secret 直接换取 token
        无需用户授权步骤
        """
        service = self.registered_services.get(client_id)
        if not service or service["secret"] != client_secret:
            raise ValueError("客户端认证失败")
        
        # 检查请求的 scope 是否在允许范围内
        for s in scope:
            if s not in service["allowed_scopes"]:
                raise PermissionError(f"服务 {client_id} 没有 {s} 权限")
        
        token = secrets.token_urlsafe(32)
        self._tokens[token] = {
            "client_id": client_id,
            "scope": scope,
            "expires_at": time.time() + 3600,
        }
        return {"access_token": token, "token_type": "bearer", "expires_in": 3600}

cc_flow = ClientCredentialsFlow()

print("场景：数据分析服务（service_a）定期从数据API获取数据")
print()

# 服务A 获取 token
try:
    token_a = cc_flow.get_token("service_a", "service-a-secret-key", ["read:data"])
    print(f"✅ service_a 获取 Token 成功: {token_a['access_token'][:20]}...")
    print(f"   权限: read:data, 有效期: {token_a['expires_in']}s")
except Exception as e:
    print(f"❌ {e}")

# 服务B 尝试获取 write 权限（被拒绝）
try:
    token_b = cc_flow.get_token("service_b", "service-b-secret-key", ["write:data"])
    print(f"✅ service_b 获取 write 权限成功")
except PermissionError as e:
    print(f"🚫 service_b 申请 write:data 被拒绝: {e}")

# 错误凭证
try:
    cc_flow.get_token("service_a", "wrong-secret", ["read:data"])
except ValueError as e:
    print(f"❌ 错误凭证被拒绝: {e}")

print("\n📌 客户端凭证模式 vs 授权码模式：")
print("  授权码模式：有用户参与（用户授权第三方访问）")
print("  客户端凭证模式：无用户参与（服务间调用，用 ID+Secret 换 Token）")

print("\n" + "=" * 60)
print("✅ Demo 4 完成！OAuth2.0 核心要点：")
print("  • 授权码模式：用户参与，安全性最高，最常用")
print("  • authorization_code：一次性、短期，防止重放攻击")
print("  • client_secret：只在服务端使用，绝不暴露给前端")
print("  • state：防 CSRF 攻击，每次授权必须验证")
print("  • scope：最小权限原则，只申请必要权限")
print("  • OAuth2 = 授权框架，JWT 常作为其 Token 格式")
print("=" * 60)
