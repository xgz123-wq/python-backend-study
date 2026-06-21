"""
Demo 2: datetime
对应理论文档: 2.datetime.md

演示时间获取、格式化、解析、加减和后端常见时间场景。
"""

from datetime import date, datetime, timedelta


print("=" * 55)
print("第一部分：当前时间")
print("=" * 55)

now = datetime.now()
today = date.today()

print(f"datetime.now() = {now}")
print(f"date.today() = {today}")


print("\n" + "=" * 55)
print("第二部分：时间格式化与解析")
print("=" * 55)

formatted = now.strftime("%Y-%m-%d %H:%M:%S")
parsed = datetime.strptime("2026-05-07 20:30:00", "%Y-%m-%d %H:%M:%S")

print(f"格式化结果 = {formatted}")
print(f"解析结果 = {parsed}")


print("\n" + "=" * 55)
print("第三部分：时间加减")
print("=" * 55)

after_7_days = now + timedelta(days=7)
before_30_minutes = now - timedelta(minutes=30)

print(f"7 天后 = {after_7_days}")
print(f"30 分钟前 = {before_30_minutes}")


print("\n" + "=" * 55)
print("第四部分：时间差")
print("=" * 55)

register_time = datetime(2026, 5, 1, 8, 0, 0)
login_time = datetime(2026, 5, 7, 10, 30, 0)
delta = login_time - register_time

print(f"相差天数 = {delta.days}")
print(f"总秒数 = {delta.total_seconds()}")


print("\n" + "=" * 55)
print("第五部分：后端场景模拟")
print("=" * 55)

created_at = datetime.now()
token_expire_at = created_at + timedelta(hours=2)
log_time = created_at.strftime("%Y-%m-%d %H:%M:%S")

print(f"用户创建时间 = {created_at}")
print(f"令牌过期时间 = {token_expire_at}")
print(f"日志时间戳 = {log_time}")


print("\n" + "=" * 55)
print("Demo 2 完成!")
print("=" * 55)
