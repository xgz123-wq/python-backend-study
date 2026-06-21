"""
DNS 解析演示
对应理论：2.DNS解析.md

演示内容：
1. 用 Python 进行 DNS 查询
2. 查看域名的 IP 地址（A 记录）
3. 理解 DNS 缓存与解析耗时
4. hosts 文件的作用
"""

import socket
import time
import platform


# ============================================================
# 1. 基础 DNS 查询：域名 → IP
# ============================================================
print("=" * 60)
print("1. 基础 DNS 查询：域名 → IP 地址")
print("=" * 60)

domains = [
    "www.baidu.com",
    "www.google.com",
    "github.com",
    "localhost",
]

for domain in domains:
    try:
        ip = socket.gethostbyname(domain)
        print(f"  {domain:<25} → {ip}")
    except socket.gaierror as e:
        print(f"  {domain:<25} → 解析失败: {e}")

print()
print("说明：gethostbyname() 是最简单的 DNS 查询，返回域名对应的 IPv4 地址")
print("      localhost 总是解析为 127.0.0.1（在 hosts 文件中定义）")


# ============================================================
# 2. 获取域名的所有 IP（一个域名可以有多个 IP）
# ============================================================
print("\n" + "=" * 60)
print("2. 获取域名的所有 IP 地址")
print("=" * 60)

domain = "www.baidu.com"
try:
    # getaddrinfo 返回更完整的信息
    results = socket.getaddrinfo(domain, 80, socket.AF_INET, socket.SOCK_STREAM)
    ips = set()
    for result in results:
        ip = result[4][0]
        ips.add(ip)
    print(f"  {domain} 的所有 IP 地址：")
    for ip in sorted(ips):
        print(f"    - {ip}")
    print()
    print("  说明：大型网站通常有多个 IP，用于负载均衡和就近访问（CDN）")
except socket.gaierror as e:
    print(f"  查询失败: {e}")


# ============================================================
# 3. DNS 解析耗时测量
# ============================================================
print("\n" + "=" * 60)
print("3. DNS 解析耗时测量")
print("=" * 60)

test_domains = ["www.baidu.com", "github.com", "www.python.org"]

for domain in test_domains:
    times = []
    for i in range(3):
        start = time.perf_counter()
        try:
            socket.gethostbyname(domain)
        except socket.gaierror:
            pass
        elapsed = (time.perf_counter() - start) * 1000  # 转为毫秒
        times.append(elapsed)

    print(f"  {domain:<25} 三次查询耗时: "
          f"{times[0]:.2f}ms, {times[1]:.2f}ms, {times[2]:.2f}ms")

print()
print("  观察：第一次查询通常较慢（需要完整解析流程），")
print("        后续查询明显更快（命中了操作系统 DNS 缓存）")
print("        这就是 DNS 缓存的作用！")


# ============================================================
# 4. 反向 DNS 查询：IP → 域名
# ============================================================
print("\n" + "=" * 60)
print("4. 反向 DNS 查询：IP → 域名")
print("=" * 60)

test_ips = ["8.8.8.8", "1.1.1.1", "127.0.0.1"]

for ip in test_ips:
    try:
        hostname, aliases, addresses = socket.gethostbyaddr(ip)
        print(f"  {ip:<20} → 主机名: {hostname}")
        if aliases:
            print(f"  {'':20}   别名: {', '.join(aliases)}")
    except socket.herror as e:
        print(f"  {ip:<20} → 反向查询失败: {e}")

print()
print("  说明：反向 DNS 不一定能查到结果，取决于 IP 是否配置了 PTR 记录")


# ============================================================
# 5. 获取本机网络信息
# ============================================================
print("\n" + "=" * 60)
print("5. 本机网络信息")
print("=" * 60)

hostname = socket.gethostname()
print(f"  主机名:     {hostname}")

try:
    local_ip = socket.gethostbyname(hostname)
    print(f"  本机 IP:    {local_ip}")
except socket.gaierror:
    print("  本机 IP:    获取失败")

print(f"  操作系统:   {platform.system()} {platform.release()}")

# hosts 文件位置
if platform.system() == "Windows":
    hosts_path = r"C:\Windows\System32\drivers\etc\hosts"
else:
    hosts_path = "/etc/hosts"
print(f"  hosts 文件: {hosts_path}")


# ============================================================
# 6. DNS 解析流程模拟（用打印说明）
# ============================================================
print("\n" + "=" * 60)
print("6. DNS 解析流程（概念演示）")
print("=" * 60)

def simulate_dns_resolution(domain):
    """模拟 DNS 解析流程的步骤（概念性，非真实实现）"""
    print(f"\n  查询: {domain}")
    print(f"  ─────────────────────────────────────")

    steps = [
        ("① 浏览器缓存",        "检查浏览器是否缓存了该域名的 IP"),
        ("② 操作系统缓存",      "检查 OS 的 DNS 缓存 + hosts 文件"),
        ("③ 本地 DNS 服务器",   "向运营商/公共 DNS（如 8.8.8.8）查询"),
        ("④ 根域名服务器",      "全球 13 组根服务器，返回 .com 服务器地址"),
        ("⑤ 顶级域名服务器",    f".com 服务器返回 {domain.split('.')[-2]}.com 的 NS 记录"),
        ("⑥ 权威域名服务器",    f"返回 {domain} 的 A 记录（最终 IP）"),
    ]

    for step_name, description in steps:
        print(f"  {step_name:<18} → {description}")

    # 实际查询
    try:
        ip = socket.gethostbyname(domain)
        print(f"\n  ✓ 最终结果: {domain} → {ip}")
    except socket.gaierror:
        print(f"\n  ✗ 解析失败")

simulate_dns_resolution("www.baidu.com")

print("\n" + "=" * 60)
print("演示结束！")
print("=" * 60)
print("""
核心要点回顾：
1. DNS 的作用是把域名翻译成 IP 地址
2. 一个域名可以对应多个 IP（负载均衡/CDN）
3. DNS 有多级缓存，首次查询慢、后续查询快
4. DNS 解析流程：浏览器缓存 → OS 缓存 → 本地 DNS → 根 → 顶级 → 权威
5. 后端开发中，DNS 影响部署配置、问题排查、CDN 加速
""")
