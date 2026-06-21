"""
常见端口与协议演示
对应理论：3.常见端口与协议.md

演示内容：
1. 扫描本机常见端口的开放状态
2. 演示端口占用与冲突
3. 0.0.0.0 vs 127.0.0.1 的区别
4. 后端常用端口速查表
"""

import socket
import threading
import time


# ============================================================
# 1. 扫描本机常见端口
# ============================================================
print("=" * 60)
print("1. 扫描本机常见服务端口")
print("=" * 60)

common_ports = {
    80:    "HTTP（Web 服务）",
    443:   "HTTPS（加密 Web）",
    3306:  "MySQL 数据库",
    5432:  "PostgreSQL 数据库",
    6379:  "Redis 缓存",
    8000:  "FastAPI/Django 开发服务器",
    8080:  "备用 HTTP / Tomcat",
    22:    "SSH 远程登录",
    27017: "MongoDB",
    5672:  "RabbitMQ 消息队列",
}

print(f"  {'端口':<8} {'服务':<30} {'状态':<10}")
print("  " + "-" * 50)

for port, service in sorted(common_ports.items()):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(0.5)  # 超时 0.5 秒
    result = sock.connect_ex(("127.0.0.1", port))
    status = "✓ 开放" if result == 0 else "✗ 关闭"
    print(f"  {port:<8} {service:<30} {status}")
    sock.close()

print()
print("  说明：开放 = 有服务在监听该端口；关闭 = 没有服务使用该端口")
print("  提示：如果你安装了 MySQL/Redis 等，对应端口会显示「开放」")


# ============================================================
# 2. 端口占用与冲突演示
# ============================================================
print("\n" + "=" * 60)
print("2. 端口占用与冲突演示")
print("=" * 60)

test_port = 9100

# 第一个服务占用端口
server1 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server1.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server1.bind(("127.0.0.1", test_port))
server1.listen(1)
print(f"  [服务1] 成功绑定端口 {test_port}")

# 第二个服务尝试占用同一端口
server2 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
try:
    server2.bind(("127.0.0.1", test_port))
    print(f"  [服务2] 成功绑定端口 {test_port}")
except OSError as e:
    print(f"  [服务2] 绑定端口 {test_port} 失败: {e}")
    print(f"           → 这就是「端口已被占用」错误！")

server1.close()
server2.close()

print()
print("  解决端口冲突的方法：")
print("  1. 找到占用端口的进程并关闭")
print("     Windows: netstat -ano | findstr :端口号")
print("     Linux:   lsof -i :端口号")
print("  2. 换一个端口启动服务")


# ============================================================
# 3. 0.0.0.0 vs 127.0.0.1
# ============================================================
print("\n" + "=" * 60)
print("3. 0.0.0.0 vs 127.0.0.1 的区别")
print("=" * 60)

# 绑定 127.0.0.1 的服务
local_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
local_server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
local_server.bind(("127.0.0.1", 9101))
local_server.listen(1)
local_addr = local_server.getsockname()
print(f"  服务A 绑定地址: {local_addr[0]}:{local_addr[1]}")
print(f"         → 只接受来自本机的连接")

# 绑定 0.0.0.0 的服务
all_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
all_server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
all_server.bind(("0.0.0.0", 9102))
all_server.listen(1)
all_addr = all_server.getsockname()
print(f"  服务B 绑定地址: {all_addr[0]}:{all_addr[1]}")
print(f"         → 接受来自所有网络接口的连接（包括局域网）")

local_server.close()
all_server.close()

print()
print("  对比：")
print("  ┌──────────────┬───────────────────────────────────┐")
print("  │ 127.0.0.1    │ 只有本机能访问，安全但受限        │")
print("  │ 0.0.0.0      │ 任何网络都能访问，灵活但需注意安全│")
print("  ├──────────────┼───────────────────────────────────┤")
print("  │ 本地开发      │ 127.0.0.1 足够                   │")
print("  │ Docker 容器内 │ 必须用 0.0.0.0 才能外部访问      │")
print("  │ 生产部署      │ 通常 Nginx 监听 0.0.0.0          │")
print("  └──────────────┴───────────────────────────────────┘")


# ============================================================
# 4. 后端常用端口速查表
# ============================================================
print("\n" + "=" * 60)
print("4. 后端开发常用端口速查表")
print("=" * 60)

categories = {
    "Web 服务": [
        (80,   "HTTP",       "Nginx 默认"),
        (443,  "HTTPS",      "Nginx SSL"),
        (8000, "Dev Server", "FastAPI/Django/Uvicorn"),
        (8080, "Alt HTTP",   "Tomcat / 备用 Web"),
    ],
    "数据库": [
        (3306,  "MySQL",      "关系型数据库"),
        (5432,  "PostgreSQL", "关系型数据库（Django 常用）"),
        (27017, "MongoDB",    "文档型 NoSQL"),
    ],
    "缓存 & 队列": [
        (6379, "Redis",      "缓存/Session/消息队列"),
        (5672, "RabbitMQ",   "消息队列（AMQP 协议）"),
        (9200, "Elasticsearch", "全文搜索引擎"),
    ],
    "运维工具": [
        (22,   "SSH",        "远程登录服务器"),
        (53,   "DNS",        "域名解析"),
        (9090, "Prometheus", "监控系统"),
        (3000, "Grafana",    "监控仪表盘"),
    ],
}

for category, ports in categories.items():
    print(f"\n  【{category}】")
    print(f"  {'端口':<8} {'服务':<15} {'说明':<30}")
    print(f"  {'-'*53}")
    for port, service, desc in ports:
        print(f"  {port:<8} {service:<15} {desc}")


# ============================================================
# 5. 简单的端口连通性测试工具
# ============================================================
print("\n" + "=" * 60)
print("5. 端口连通性测试（模拟 telnet）")
print("=" * 60)

def check_port(host, port, timeout=2):
    """测试指定主机的端口是否可达"""
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(timeout)
    try:
        start = time.perf_counter()
        result = sock.connect_ex((host, port))
        elapsed = (time.perf_counter() - start) * 1000
        if result == 0:
            return True, f"{elapsed:.1f}ms"
        return False, "连接被拒绝"
    except socket.timeout:
        return False, "连接超时"
    except socket.gaierror:
        return False, "域名解析失败"
    finally:
        sock.close()

test_targets = [
    ("127.0.0.1", 80,   "本机 HTTP"),
    ("127.0.0.1", 3306, "本机 MySQL"),
    ("127.0.0.1", 6379, "本机 Redis"),
]

print(f"  {'目标':<30} {'状态':<10} {'延迟':<15}")
print(f"  {'-'*55}")
for host, port, desc in test_targets:
    reachable, detail = check_port(host, port)
    status = "✓ 可达" if reachable else "✗ 不可达"
    print(f"  {desc} ({host}:{port}){'':<5} {status:<10} {detail}")

print()
print("  说明：这个函数在排查后端服务连接问题时非常实用")
print("  场景：FastAPI 连不上 MySQL？先用这个测试端口是否通")


print("\n" + "=" * 60)
print("演示结束！")
print("=" * 60)
print("""
核心要点回顾：
1. 端口 = 服务器上的"门牌号"，区分不同服务
2. 后端必记端口：80(HTTP) / 443(HTTPS) / 3306(MySQL) / 6379(Redis) / 8000(开发)
3. 端口冲突是最常见的启动失败原因，用 netstat/lsof 排查
4. 127.0.0.1 只接受本机连接，0.0.0.0 接受所有网络连接
5. 排查连接问题的第一步：测试目标端口是否可达
""")
