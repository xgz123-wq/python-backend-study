"""
Demo 3: 密码哈希演示
对应理论文档: 3.密码哈希bcrypt与argon2.md

演示内容：
- MD5 明文存储的危险性（反面教材）
- bcrypt 加盐哈希演示
- argon2 高内存哈希演示
- 哈希速度对比（为什么慢是优点）
- passlib 统一接口使用

运行方式: python 3_password_hash.py
前置依赖: pip install bcrypt passlib
         (可选) pip install argon2-cffi passlib[argon2]
"""

import hashlib
import time
import bcrypt

print("=" * 60)
print("Demo 3: 密码哈希 — 安全存储用户密码")
print("=" * 60)

# ─────────────────────────────────────────────
# Part 1: MD5 的危险性（反面教材）
# ─────────────────────────────────────────────
print("\n【Part 1】❌ 错误做法：MD5 存储密码（反面教材）")
print("-" * 40)

# 演示 MD5 的确定性问题
common_passwords = ["123456", "password", "abc123", "qwerty", "123456789"]
print("MD5 是确定性函数：相同输入 → 相同输出")
print("攻击者可以预计算所有常见密码的 MD5（彩虹表）：")
print()

rainbow_table = {}
for pwd in common_passwords:
    md5_hash = hashlib.md5(pwd.encode()).hexdigest()
    rainbow_table[md5_hash] = pwd
    print(f"  MD5({pwd!r}) = {md5_hash}")

print("\n模拟数据库泄露攻击：")
# 假设数据库里存了这个 MD5
leaked_hash = hashlib.md5("123456".encode()).hexdigest()
print(f"  泄露的哈希: {leaked_hash}")
recovered = rainbow_table.get(leaked_hash)
if recovered:
    print(f"  ❌ 彩虹表攻击成功！原始密码: '{recovered}'")

print("\n演示 MD5 速度有多快（攻击者可以暴力穷举）：")
count = 100_000
start = time.perf_counter()
for i in range(count):
    hashlib.md5(f"password{i}".encode()).hexdigest()
elapsed = time.perf_counter() - start
rate = count / elapsed
print(f"  MD5: {count:,} 次哈希耗时 {elapsed:.3f}s → {rate:,.0f} 次/秒")
print(f"  → 攻击者用 GPU 可达每秒 数百亿次，暴力破解几乎无门槛")

# ─────────────────────────────────────────────
# Part 2: bcrypt 正确做法
# ─────────────────────────────────────────────
print("\n\n【Part 2】✅ 正确做法：bcrypt 加盐哈希")
print("-" * 40)

def hash_password_bcrypt(plain_password: str, rounds: int = 12) -> str:
    """用 bcrypt 生成密码哈希"""
    salt = bcrypt.gensalt(rounds=rounds)
    hashed = bcrypt.hashpw(plain_password.encode("utf-8"), salt)
    return hashed.decode("utf-8")

def verify_password_bcrypt(plain_password: str, hashed_password: str) -> bool:
    """验证密码"""
    return bcrypt.checkpw(
        plain_password.encode("utf-8"),
        hashed_password.encode("utf-8")
    )

# 演示加盐效果：同一密码，每次哈希结果不同
password = "my_secret_password"
print(f"对同一密码 '{password}' 哈希三次（盐不同，结果不同）：")
for i in range(3):
    hashed = hash_password_bcrypt(password, rounds=10)  # rounds=10 更快，演示用
    print(f"  哈希 {i+1}: {hashed}")

print("\n解析 bcrypt 哈希格式：")
sample_hash = hash_password_bcrypt(password, rounds=12)
print(f"  完整哈希: {sample_hash}")
parts = sample_hash.split("$")
print(f"  版本号:    ${parts[1]}$ (2b = bcrypt v2b)")
print(f"  cost:      ${parts[2]}$ (12 = 2^12 = 4096 轮迭代)")
print(f"  盐+哈希:   ${parts[3][:22]}...（前22字符=盐，后31字符=哈希）")

print("\n验证密码：")
test_cases = [
    ("my_secret_password", True),
    ("wrong_password", False),
    ("My_Secret_Password", False),  # 区分大小写
]
for test_pwd, expected in test_cases:
    result = verify_password_bcrypt(test_pwd, sample_hash)
    icon = "✅" if result == expected else "❌"
    print(f"  {icon} verify('{test_pwd}') = {result}")

print("\nbcrypt 速度测试（慢=安全）：")
for rounds in [10, 12]:
    start = time.perf_counter()
    hash_password_bcrypt(password, rounds=rounds)
    elapsed = time.perf_counter() - start
    print(f"  rounds={rounds}: {elapsed*1000:.1f}ms → 攻击者每秒最多 {int(1/elapsed)} 次尝试")

print("\n📌 bcrypt 核心优势：")
print("  ① 自动加盐：每次哈希不同，彩虹表失效")
print("  ② 故意慢：攻击者暴力破解代价极高")
print("  ③ cost 可调：随 CPU 性能提升可增大 rounds")

# ─────────────────────────────────────────────
# Part 3: argon2（更现代的选择）
# ─────────────────────────────────────────────
print("\n\n【Part 3】argon2（新项目推荐）")
print("-" * 40)

try:
    from argon2 import PasswordHasher
    from argon2.exceptions import VerifyMismatchError

    ph = PasswordHasher(
        time_cost=2,        # 迭代次数
        memory_cost=65536,  # 64MB 内存（抗 GPU 攻击关键！）
        parallelism=2,      # 并行线程
    )

    hashed_argon2 = ph.hash(password)
    print(f"argon2 哈希: {hashed_argon2[:60]}...")
    print(f"\n解析 argon2 哈希格式：")
    print(f"  完整: {hashed_argon2}")
    print(f"  → $argon2id = 算法版本")
    print(f"  → v=19 = argon2 协议版本")
    print(f"  → m=65536 = 内存占用 64MB")
    print(f"  → t=2 = 时间成本（迭代次数）")
    print(f"  → p=2 = 并行度")

    print("\n验证 argon2 密码：")
    try:
        ph.verify(hashed_argon2, password)
        print(f"  ✅ 正确密码验证通过")
    except VerifyMismatchError:
        print(f"  ❌ 密码不匹配")

    try:
        ph.verify(hashed_argon2, "wrong_password")
        print(f"  ✅ 错误密码验证通过（这不应该发生！）")
    except VerifyMismatchError:
        print(f"  ❌ 错误密码验证失败（正常）")

    print("\n⚡ 为什么 argon2 比 bcrypt 更强？")
    print(f"  bcrypt: 内存占用固定（很小）→ GPU 可以大量并行")
    print(f"  argon2: 内存占用 {ph.memory_cost // 1024}MB → GPU 内存有限，无法大量并行")
    print(f"  → 相同安全等级下，argon2 让 GPU 暴力破解更难")

except ImportError:
    print("⚠️  argon2-cffi 未安装，跳过此部分")
    print("   安装命令: pip install argon2-cffi")

# ─────────────────────────────────────────────
# Part 4: passlib 统一接口（生产推荐）
# ─────────────────────────────────────────────
print("\n\n【Part 4】passlib 统一接口（推荐的生产方式）")
print("-" * 40)

try:
    from passlib.context import CryptContext

    # 推荐配置：bcrypt 作为主算法
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

    print("注册场景：哈希并存储密码")
    hashed = pwd_context.hash("user_password_123")
    print(f"  存入数据库: {hashed[:50]}...")

    print("\n登录场景：验证密码")
    print(f"  正确密码: {pwd_context.verify('user_password_123', hashed)}")
    print(f"  错误密码: {pwd_context.verify('wrong', hashed)}")

    print("\n升级场景：检查是否需要重新哈希（cost 参数升级时）")
    print(f"  需要重新哈希: {pwd_context.needs_update(hashed)}")
    print("  → 如果升级了 rounds，旧哈希下次登录时自动重新哈希")

    print("\n📌 passlib 的优势：")
    print("  ① 统一接口：轻松切换 bcrypt/argon2 等算法")
    print("  ② 自动迁移：旧算法的哈希在验证后自动升级")
    print("  ③ FastAPI/Django 广泛使用")

except ImportError:
    print("⚠️  passlib 未安装，跳过此部分")
    print("   安装命令: pip install passlib[bcrypt]")

print("\n" + "=" * 60)
print("✅ Demo 3 完成！核心要点：")
print("  • MD5/SHA1 存密码 = 危险！可被彩虹表秒破")
print("  • bcrypt = 加盐 + 慢哈希，生产环境基础选择")
print("  • argon2 = 高内存 + 慢哈希，新项目推荐")
print("  • passlib = Python 最佳实践封装库")
print("  • 哈希慢 = 设计使然，让攻击者暴力破解不可行")
print("=" * 60)
