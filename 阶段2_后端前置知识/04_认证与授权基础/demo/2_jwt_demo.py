"""
Demo 2: JWT 生成与验证演示
对应理论文档: 2.JWT详解.md

演示内容：
- 手动解析 JWT 三部分结构
- 用 PyJWT 生成和验证 JWT
- Access Token + Refresh Token 双 Token 机制
- Token 过期与篡改检测

运行方式: python 2_jwt_demo.py
前置依赖: pip install PyJWT
"""

import base64
import json
import time
import hashlib
import hmac
import secrets
from datetime import datetime, timedelta, timezone

print("=" * 60)
print("Demo 2: JWT 结构解析与生成验证")
print("=" * 60)

# ─────────────────────────────────────────────
# Part 1: 手动解析 JWT（理解结构）
# ─────────────────────────────────────────────
print("\n【Part 1】手动解析 JWT 结构（不依赖第三方库）")
print("-" * 40)

# 一个真实的 JWT 示例（HS256 算法）
sample_jwt = (
    "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9"
    ".eyJzdWIiOiIxMjM0NTYiLCJ1c2VybmFtZSI6ImFsaWNlIiwicm9sZSI6InVzZXIiLCJleHAiOjk5OTk5OTk5OTl9"
    ".placeholder_signature"
)

print(f"JWT 示例（截取前50字符）: {sample_jwt[:50]}...")
print()

# JWT 的三部分用 "." 分隔
parts = sample_jwt.split(".")
print(f"分割后共 {len(parts)} 部分：")
print(f"  Part 1 (Header):    {parts[0]}")
print(f"  Part 2 (Payload):   {parts[1]}")
print(f"  Part 3 (Signature): {parts[2]}")

def b64_decode(data: str) -> dict:
    """Base64URL 解码 → JSON（JWT 的 Header 和 Payload 是 Base64URL 编码）"""
    # Base64URL 与标准 Base64 的区别：用 - 代替 +，用 _ 代替 /
    # 补齐到 4 的倍数
    padding = 4 - len(data) % 4
    if padding != 4:
        data += "=" * padding
    decoded_bytes = base64.urlsafe_b64decode(data)
    return json.loads(decoded_bytes)

print("\n解码 Header：")
header = b64_decode(parts[0])
print(f"  {json.dumps(header, indent=4)}")
print(f"  → alg: {header['alg']} 表示使用 HMAC-SHA256 签名算法")

print("\n解码 Payload（任何人都能读取！）：")
payload = b64_decode(parts[1])
print(f"  {json.dumps(payload, indent=4)}")
print(f"  → sub: 用户ID, username: 用户名, role: 角色")
if "exp" in payload:
    exp_dt = datetime.fromtimestamp(payload["exp"])
    print(f"  → exp: 过期时间 = {exp_dt.strftime('%Y-%m-%d %H:%M:%S')}")

print("\n⚠️  重要提醒：Payload 只是 Base64URL 编码，不是加密！")
print("   任何人拿到 JWT 都能解码读取 Payload 内容！")
print("   → 不要在 Payload 里放密码、身份证等敏感信息！")

# ─────────────────────────────────────────────
# Part 2: 手动实现 HS256 JWT（理解签名原理）
# ─────────────────────────────────────────────
print("\n\n【Part 2】手动实现 HS256 JWT 签名（理解原理）")
print("-" * 40)

def base64url_encode(data: bytes) -> str:
    """Base64URL 编码（去掉末尾 = 号）"""
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode()

def create_jwt_manually(payload: dict, secret: str) -> str:
    """手动创建 JWT（演示用，生产环境用 PyJWT）"""
    # 1. Header
    header = {"alg": "HS256", "typ": "JWT"}
    header_encoded = base64url_encode(json.dumps(header, separators=(",", ":")).encode())
    
    # 2. Payload
    payload_encoded = base64url_encode(json.dumps(payload, separators=(",", ":")).encode())
    
    # 3. 签名 = HMACSHA256(header.payload, secret)
    signing_input = f"{header_encoded}.{payload_encoded}"
    signature = hmac.new(
        secret.encode(),
        signing_input.encode(),
        hashlib.sha256
    ).digest()
    signature_encoded = base64url_encode(signature)
    
    return f"{header_encoded}.{payload_encoded}.{signature_encoded}"

def verify_jwt_manually(token: str, secret: str) -> dict | None:
    """手动验证 JWT 签名（演示用）"""
    parts = token.split(".")
    if len(parts) != 3:
        return None
    
    # 重新计算签名
    signing_input = f"{parts[0]}.{parts[1]}"
    expected_sig = hmac.new(
        secret.encode(),
        signing_input.encode(),
        hashlib.sha256
    ).digest()
    expected_sig_encoded = base64url_encode(expected_sig)
    
    # 使用 hmac.compare_digest 防时序攻击
    if not hmac.compare_digest(expected_sig_encoded, parts[2]):
        return None  # 签名不匹配，Token 被篡改！
    
    # 解码 Payload
    payload = b64_decode(parts[1])
    
    # 检查过期时间
    if "exp" in payload and time.time() > payload["exp"]:
        return None  # Token 已过期
    
    return payload

SECRET_KEY = "super-secret-key-at-least-32-chars-long"
my_payload = {
    "sub": "user_123",
    "username": "alice",
    "role": "user",
    "exp": int(time.time()) + 3600,  # 1小时后过期
    "iat": int(time.time()),
}

token = create_jwt_manually(my_payload, SECRET_KEY)
print(f"生成的 JWT：{token[:60]}...")

# 验证正确的 Token
result = verify_jwt_manually(token, SECRET_KEY)
print(f"\n验证结果：{result}")
print(f"✅ 签名验证通过！用户: {result['username']}, 角色: {result['role']}")

# 验证篡改后的 Token
tampered = token[:-5] + "XXXXX"  # 篡改签名
result_tampered = verify_jwt_manually(tampered, SECRET_KEY)
print(f"\n篡改 Token 后验证：{result_tampered}")
print(f"❌ 签名不匹配，Token 已被篡改！")

# ─────────────────────────────────────────────
# Part 3: 使用 PyJWT 库（生产环境推荐方式）
# ─────────────────────────────────────────────
print("\n\n【Part 3】使用 PyJWT 库（推荐方式）")
print("-" * 40)

try:
    import jwt

    SECRET = "your-production-secret-key-use-env-variable"

    def create_access_token(user_id: int, username: str, role: str) -> str:
        """生成 Access Token（短期，2小时）"""
        payload = {
            "sub": str(user_id),
            "username": username,
            "role": role,
            "type": "access",
            "exp": datetime.now(timezone.utc) + timedelta(hours=2),
            "iat": datetime.now(timezone.utc),
        }
        return jwt.encode(payload, SECRET, algorithm="HS256")

    def create_refresh_token(user_id: int) -> str:
        """生成 Refresh Token（长期，30天）"""
        payload = {
            "sub": str(user_id),
            "type": "refresh",
            "jti": secrets.token_urlsafe(16),  # 唯一 ID，防重放
            "exp": datetime.now(timezone.utc) + timedelta(days=30),
            "iat": datetime.now(timezone.utc),
        }
        return jwt.encode(payload, SECRET, algorithm="HS256")

    def verify_token(token: str, expected_type: str = "access") -> dict:
        """验证 Token，返回 Payload 或抛出异常"""
        try:
            payload = jwt.decode(token, SECRET, algorithms=["HS256"])
            if payload.get("type") != expected_type:
                raise ValueError(f"Token 类型错误: 期望 {expected_type}")
            return payload
        except jwt.ExpiredSignatureError:
            raise ValueError("Token 已过期")
        except jwt.InvalidTokenError as e:
            raise ValueError(f"Token 无效: {e}")

    # 演示双 Token 机制
    print("模拟用户登录，发放双 Token：")
    access_token = create_access_token(user_id=1, username="alice", role="user")
    refresh_token = create_refresh_token(user_id=1)

    print(f"  Access Token  (前50字符): {access_token[:50]}...")
    print(f"  Refresh Token (前50字符): {refresh_token[:50]}...")

    print("\n验证 Access Token：")
    payload = verify_token(access_token, "access")
    print(f"  ✅ 验证成功: 用户={payload['username']}, 角色={payload['role']}")

    print("\n用 Refresh Token 换新 Access Token：")
    refresh_payload = verify_token(refresh_token, "refresh")
    new_access_token = create_access_token(
        user_id=int(refresh_payload["sub"]),
        username="alice",  # 实际从数据库查
        role="user"
    )
    print(f"  ✅ 刷新成功，新 Access Token: {new_access_token[:50]}...")

    print("\n测试过期 Token（故意生成一个已过期的 token）：")
    expired_payload = {
        "sub": "1",
        "username": "alice",
        "type": "access",
        "exp": datetime.now(timezone.utc) - timedelta(hours=1),  # 已过期
    }
    expired_token = jwt.encode(expired_payload, SECRET, algorithm="HS256")
    try:
        verify_token(expired_token)
    except ValueError as e:
        print(f"  ❌ {e}")

except ImportError:
    print("⚠️  PyJWT 未安装，跳过此部分")
    print("   安装命令: pip install PyJWT")

print("\n" + "=" * 60)
print("✅ Demo 2 完成！核心要点：")
print("  • JWT = Header.Payload.Signature，三部分 Base64URL 编码")
print("  • Payload 不是加密，任何人都能读取！")
print("  • Signature 防篡改（需要 secret_key 才能生成/验证）")
print("  • Access Token 短期（2h）+ Refresh Token 长期（30d）")
print("  • 生产环境用 PyJWT，不要手动实现签名逻辑")
print("=" * 60)
