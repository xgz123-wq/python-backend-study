"""
Demo 3: re 正则表达式
对应理论文档: 3.re正则表达式.md

演示匹配、提取、替换、分组和常见后端文本处理场景。
"""

import re


print("=" * 55)
print("第一部分：match 与 search")
print("=" * 55)

print(re.match(r"abc", "abcdef"))
print(re.match(r"abc", "zabcdef"))
print(re.search(r"abc", "zabcdef"))


print("\n" + "=" * 55)
print("第二部分：findall")
print("=" * 55)

text = "订单123，金额456，库存789"
nums = re.findall(r"\d+", text)
print(f"提取数字 = {nums}")


print("\n" + "=" * 55)
print("第三部分：sub 替换")
print("=" * 55)

masked_phone = re.sub(r"(\d{3})\d{4}(\d{4})", r"\1****\2", "联系方式：13812345678")
print(masked_phone)


print("\n" + "=" * 55)
print("第四部分：分组提取")
print("=" * 55)

log_line = "user:alice, age:20"
match = re.search(r"user:(\w+), age:(\d+)", log_line)
if match:
    print(f"用户名 = {match.group(1)}")
    print(f"年龄 = {match.group(2)}")


print("\n" + "=" * 55)
print("第五部分：后端场景模拟")
print("=" * 55)

username_pattern = r"^[a-zA-Z0-9_]{4,16}$"
status_pattern = r"\b(\d{3})\b"

usernames = ["user_01", "ab", "hello-world", "backend007"]
for username in usernames:
    ok = bool(re.match(username_pattern, username))
    print(f"{username:12s} -> {'合法' if ok else '不合法'}")

api_log = "GET /api/users 200 15ms"
status_match = re.search(status_pattern, api_log)
print(f"日志状态码 = {status_match.group(1) if status_match else '未找到'}")


print("\n" + "=" * 55)
print("Demo 3 完成!")
print("=" * 55)
