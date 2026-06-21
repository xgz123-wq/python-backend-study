"""
Nginx 基础与反向代理 —— Python 概念演示脚本
==============================================

本脚本用纯 Python 演示 Nginx 的核心概念，帮助理解反向代理和负载均衡的底层原理。

演示内容：
  1. 正向代理 vs 反向代理的区别（概念图解）
  2. 用 Python 实现简单的反向代理（http.server + urllib）
  3. 模拟请求转发过程
  4. 演示负载均衡轮询逻辑

运行方式：
  python 1_nginx_basics.py

依赖：
  仅使用 Python 标准库，无需额外安装
"""

import http.server
import json
import socketserver
import threading
import time
import urllib.request
import urllib.error
from typing import Callable

# ===========================================================================
# 第一部分：正向代理 vs 反向代理 —— 概念图解
# ===========================================================================

def explain_proxy_concepts():
    """
    用文字图解的方式解释正向代理和反向代理的区别。
    这是面试高频考点，务必理解清楚。
    """
    print("=" * 70)
    print("第一部分：正向代理 vs 反向代理")
    print("=" * 70)

    print("""
【正向代理（Forward Proxy）】

  客户端 ──→ [正向代理] ──→ 目标服务器
              ↑
         代理代表「客户端」
         客户端知道目标服务器是谁
         服务器不知道真实客户端

  场景：VPN、公司内网代理、Python requests 的 proxies 参数

  代码示例：
    proxies = {"http": "http://proxy.company.com:8080"}
    requests.get("https://api.github.com", proxies=proxies)


【反向代理（Reverse Proxy）】

  客户端 ──→ [反向代理] ──→ 后端服务器
              ↑
         代理代表「服务端」
         客户端不知道后端服务器是谁
         后端知道真实请求内容

  场景：Nginx 作为 FastAPI 前置网关、CDN、API Gateway

  请求链路：
    浏览器 → Nginx (80/443) → FastAPI (127.0.0.1:8000)
""")

    # 对比表
    print("┌───────────┬──────────────────┬──────────────────┐")
    print("│   维度    │     正向代理     │     反向代理     │")
    print("├───────────┼──────────────────┼──────────────────┤")
    print("│  代理谁   │     客户端       │      服务端      │")
    print("│ 客户端知道│   知道目标       │   不知道后端     │")
    print("│ 部署位置  │   客户端侧       │    服务端侧      │")
    print("│ 典型工具  │  VPN, Squid      │  Nginx, HAProxy  │")
    print("│ 主要目的  │ 访问控制/翻墙    │ 负载均衡/安全    │")
    print("└───────────┴──────────────────┴──────────────────┘")
    print()


# ===========================================================================
# 第二部分：用 Python 实现简单的反向代理
# ===========================================================================

class SimpleBackendHandler(http.server.BaseHTTPRequestHandler):
    """
    模拟后端服务器：接收请求并返回 JSON 响应。
    相当于运行在 127.0.0.1:8000 的 FastAPI 应用。
    """

    def do_GET(self):
        """处理 GET 请求，返回请求路径和服务器信息。"""
        response = {
            "server": f"Backend-{self.server.server_port}",
            "path": self.path,
            "method": "GET",
            "message": "这是后端服务器的响应",
        }
        body = json.dumps(response, ensure_ascii=False, indent=2).encode("utf-8")

        self.send_response(200)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, format, *args):
        """自定义日志格式，显示是哪个后端实例在处理请求。"""
        port = self.server.server_port
        print(f"  [后端 :{port}] {args[0]}")


class ReverseProxyHandler(http.server.BaseHTTPRequestHandler):
    """
    简单的反向代理实现：
    接收客户端请求 → 转发到后端服务器 → 将响应返回给客户端。
    相当于 Nginx 的 proxy_pass 功能。
    """

    # 后端服务器地址（相当于 nginx.conf 中的 proxy_pass 目标）
    BACKEND_HOST = "127.0.0.1"
    BACKEND_PORT = 8001

    def do_GET(self):
        """
        反向代理核心逻辑：
        1. 接收客户端请求
        2. 构造对后端的请求（相当于 proxy_pass）
        3. 将后端响应返回给客户端
        """
        # 构造后端 URL（相当于 Nginx 的 proxy_pass）
        backend_url = (
            f"http://{self.BACKEND_HOST}:{self.BACKEND_PORT}{self.path}"
        )

        try:
            # 转发请求到后端（相当于 Nginx 向 FastAPI 发请求）
            req = urllib.request.Request(backend_url)

            # 传递客户端信息（相当于 proxy_set_header）
            req.add_header("X-Forwarded-For", self.client_address[0])
            req.add_header("X-Forwarded-Proto", "http")

            print(f"  [代理] 转发请求: {self.path} → 后端 :{self.BACKEND_PORT}")

            # 发送请求到后端并获取响应
            with urllib.request.urlopen(req, timeout=5) as resp:
                body = resp.read()
                status = resp.status
                content_type = resp.headers.get(
                    "Content-Type", "application/octet-stream"
                )

            # 将后端响应返回给客户端（相当于 Nginx 回传响应）
            self.send_response(status)
            self.send_header("Content-Type", content_type)
            self.send_header("Content-Length", str(len(body)))
            # 标记这是通过代理的响应（相当于 Nginx 添加的 header）
            self.send_header("X-Proxy-By", "PythonReverseProxy")
            self.end_headers()
            self.wfile.write(body)

        except urllib.error.URLError as e:
            # 后端不可达 → 返回 502 Bad Gateway
            # 这就是 Nginx 502 错误的原理
            error_body = json.dumps({
                "error": "502 Bad Gateway",
                "detail": f"无法连接后端服务器: {e}",
            }, ensure_ascii=False).encode("utf-8")

            self.send_response(502)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(error_body)))
            self.end_headers()
            self.wfile.write(error_body)

    def log_message(self, format, *args):
        """自定义日志格式。"""
        print(f"  [代理] {args[0]}")


def run_reverse_proxy_demo():
    """
    启动后端服务器和反向代理，演示请求转发过程。

    网络拓扑：
      客户端（本脚本）→ 代理 (:9000) → 后端 (:8001)
    """
    print("=" * 70)
    print("第二部分：Python 实现反向代理")
    print("=" * 70)
    print()
    print("网络拓扑：")
    print("  客户端 → 代理 (:9000) → 后端 (:8001)")
    print()

    # 启动后端服务器（模拟 FastAPI 应用）
    backend_server = http.server.HTTPServer(
        ("127.0.0.1", 8001), SimpleBackendHandler
    )
    backend_thread = threading.Thread(
        target=backend_server.serve_forever, daemon=True
    )
    backend_thread.start()
    print("  ✓ 后端服务器启动: 127.0.0.1:8001")

    # 启动反向代理（模拟 Nginx）
    proxy_server = http.server.HTTPServer(
        ("127.0.0.1", 9000), ReverseProxyHandler
    )
    proxy_thread = threading.Thread(
        target=proxy_server.serve_forever, daemon=True
    )
    proxy_thread.start()
    print("  ✓ 反向代理启动:   127.0.0.1:9000")
    print()

    # 等待服务器启动
    time.sleep(0.3)

    # 测试 1：通过代理访问后端
    print("--- 测试 1：通过反向代理访问后端 ---")
    try:
        resp = urllib.request.urlopen("http://127.0.0.1:9000/api/users", timeout=5)
        data = json.loads(resp.read().decode("utf-8"))
        print(f"  响应状态: {resp.status}")
        print(f"  代理标记: {resp.headers.get('X-Proxy-By', '无')}")
        print(f"  后端信息: {data['server']}")
        print(f"  请求路径: {data['path']}")
    except Exception as e:
        print(f"  请求失败: {e}")

    print()

    # 测试 2：模拟后端宕机 → 502 Bad Gateway
    print("--- 测试 2：后端不可达时返回 502 ---")
    # 将代理指向一个不存在的端口
    ReverseProxyHandler.BACKEND_PORT = 9999

    try:
        resp = urllib.request.urlopen("http://127.0.0.1:9000/api/users", timeout=5)
        print(f"  意外成功: {resp.status}")
    except urllib.error.HTTPError as e:
        data = json.loads(e.read().decode("utf-8"))
        print(f"  响应状态: {e.code}")
        print(f"  错误类型: {data['error']}")
        print(f"  这就是 Nginx 返回 502 Bad Gateway 的原理")

    # 恢复端口设置
    ReverseProxyHandler.BACKEND_PORT = 8001

    print()

    # 清理
    backend_server.shutdown()
    proxy_server.shutdown()
    print("  ✓ 服务器已关闭")
    print()


# ===========================================================================
# 第三部分：模拟请求转发过程
# ===========================================================================

def simulate_request_flow():
    """
    模拟一个请求从客户端经过 Nginx 到 FastAPI 的完整链路。
    展示每一步发生了什么，帮助理解整个请求生命周期。
    """
    print("=" * 70)
    print("第三部分：请求转发全链路模拟")
    print("=" * 70)
    print()

    steps = [
        ("1. 客户端发起请求", [
            "浏览器构造 HTTP 请求:",
            "  GET /api/users HTTP/1.1",
            "  Host: api.example.com",
            "  User-Agent: Mozilla/5.0",
            "",
            "DNS 解析 api.example.com → 服务器 IP 203.0.113.10",
            "TCP 三次握手建立连接到 203.0.113.10:443 (HTTPS)",
        ]),
        ("2. Nginx 接收请求", [
            "Nginx worker 进程接收 TCP 连接",
            "解析 HTTP 请求头和请求体",
            "匹配 server_name: api.example.com → 找到对应的 server 块",
            "匹配 location: /api/ → 找到代理规则",
        ]),
        ("3. Nginx 转发到后端（proxy_pass）", [
            "从 upstream fastapi_backend 选择一个后端实例",
            "  例如选择 127.0.0.1:8001（按负载均衡算法）",
            "构造新的 HTTP 请求:",
            "  GET /api/users HTTP/1.0",
            "  Host: api.example.com          ← proxy_set_header Host",
            "  X-Real-IP: 198.51.100.1       ← proxy_set_header X-Real-IP",
            "  X-Forwarded-For: 198.51.100.1  ← proxy_set_header X-Forwarded-For",
            "  X-Forwarded-Proto: https       ← proxy_set_header X-Forwarded-Proto",
        ]),
        ("4. FastAPI 处理请求", [
            "uvicorn 接收请求",
            "FastAPI 路由匹配: /api/users → users_handler()",
            "执行业务逻辑（查询数据库等）",
            "构造 JSON 响应:",
            '  {"users": [{"id": 1, "name": "张三"}]}',
        ]),
        ("5. Nginx 返回响应给客户端", [
            "Nginx 接收后端的 HTTP 响应",
            "可能执行 gzip 压缩（如果客户端支持且响应类型匹配）",
            "添加 Nginx 层的响应头",
            "将响应返回给客户端",
            "记录访问日志 (access.log)",
        ]),
    ]

    for title, details in steps:
        print(f"  {title}")
        for detail in details:
            print(f"    {detail}")
        print()

    print("  总耗时 = DNS + TCP握手 + TLS握手 + Nginx处理 + 后端处理 + 网络传输")
    print("  Nginx 本身的处理延迟通常 < 1ms")
    print()


# ===========================================================================
# 第四部分：负载均衡轮询逻辑演示
# ===========================================================================

class RoundRobinBalancer:
    """
    轮询负载均衡器。

    按顺序依次将请求分配到各个后端服务器，
    当所有服务器都轮过一遍后，从头开始。
    这与 Nginx 默认的 upstream 行为一致。
    """

    def __init__(self, servers: list[str]):
        """
        初始化负载均衡器。

        参数:
            servers: 后端服务器地址列表，如 ["127.0.0.1:8001", "127.0.0.1:8002"]
        """
        self.servers = servers
        self.current_index = 0       # 当前轮询到的服务器索引
        self.request_count = 0       # 总请求计数

    def next_server(self) -> str:
        """
        选择下一个后端服务器（轮询算法）。

        返回:
            被选中的服务器地址
        """
        server = self.servers[self.current_index]
        # 移动到下一个服务器，到末尾则回到开头
        self.current_index = (self.current_index + 1) % len(self.servers)
        self.request_count += 1
        return server

    def get_stats(self) -> dict:
        """返回各服务器的请求分布统计。"""
        return {
            "total_requests": self.request_count,
            "servers": self.servers,
            "current_index": self.current_index,
        }


class WeightedRoundRobinBalancer:
    """
    加权轮询负载均衡器。

    根据权重比例分配请求，权重越高的服务器处理越多请求。
    例如权重 5:3:2 表示分配比例约为 50%:30%:20%。
    """

    def __init__(self, servers_with_weights: list[tuple[str, int]]):
        """
        初始化加权轮询负载均衡器。

        参数:
            servers_with_weights: [(服务器地址, 权重), ...] 列表
        """
        # 按权重展开服务器列表
        # 例如 [("A", 3), ("B", 1)] → ["A", "A", "A", "B"]
        self.expanded_servers = []
        for server, weight in servers_with_weights:
            self.expanded_servers.extend([server] * weight)

        self.current_index = 0
        self.request_count = 0
        self.server_counts: dict[str, int] = {
            s: 0 for s, _ in servers_with_weights
        }

    def next_server(self) -> str:
        """按加权轮询选择下一个服务器。"""
        server = self.expanded_servers[self.current_index]
        self.current_index = (
            (self.current_index + 1) % len(self.expanded_servers)
        )
        self.request_count += 1
        self.server_counts[server] += 1
        return server


def run_load_balancing_demo():
    """演示轮询和加权轮询负载均衡算法。"""
    print("=" * 70)
    print("第四部分：负载均衡轮询逻辑")
    print("=" * 70)
    print()

    # --- 轮询演示 ---
    print("--- 普通轮询（Round Robin）---")
    print("后端服务器: A(:8001), B(:8002), C(:8003)")
    print()

    balancer = RoundRobinBalancer([
        "127.0.0.1:8001 (A)",
        "127.0.0.1:8002 (B)",
        "127.0.0.1:8003 (C)",
    ])

    # 模拟 9 个请求
    distribution: dict[str, int] = {}
    for i in range(9):
        server = balancer.next_server()
        distribution[server] = distribution.get(server, 0) + 1
        print(f"  请求 #{i + 1} → {server}")

    print()
    print("请求分布：")
    for server, count in distribution.items():
        bar = "█" * count
        print(f"  {server}: {bar} ({count} 次)")

    print()

    # --- 加权轮询演示 ---
    print("--- 加权轮询（Weighted Round Robin）---")
    print("后端服务器: A(权重5), B(权重3), C(权重2)")
    print()

    weighted_balancer = WeightedRoundRobinBalancer([
        ("A(:8001)", 5),
        ("B(:8002)", 3),
        ("C(:8003)", 2),
    ])

    # 模拟 20 个请求
    for i in range(20):
        weighted_balancer.next_server()

    print("请求分布（20 个请求）：")
    total = sum(weighted_balancer.server_counts.values())
    for server, count in weighted_balancer.server_counts.items():
        bar = "█" * count
        pct = count / total * 100
        print(f"  {server}: {bar} ({count} 次, {pct:.0f}%)")

    print()
    print("  可以看到 A 处理了约 50% 的请求，B 约 30%，C 约 20%")
    print("  这与 Nginx upstream weight 参数的效果一致")
    print()


# ===========================================================================
# 主程序
# ===========================================================================

def main():
    """运行所有演示。"""
    print()
    print("╔══════════════════════════════════════════════════════════════════╗")
    print("║          Nginx 基础与反向代理 —— Python 概念演示              ║")
    print("╚══════════════════════════════════════════════════════════════════╝")
    print()

    # 第一部分：概念图解
    explain_proxy_concepts()

    # 第二部分：反向代理实战
    run_reverse_proxy_demo()

    # 第三部分：请求转发链路
    simulate_request_flow()

    # 第四部分：负载均衡轮询
    run_load_balancing_demo()

    print("=" * 70)
    print("演示结束！")
    print()
    print("核心收获：")
    print("  1. 正向代理代表客户端，反向代理代表服务端")
    print("  2. 反向代理的核心是「接收请求 → 转发到后端 → 返回响应」")
    print("  3. 502 Bad Gateway = 代理无法连接后端服务器")
    print("  4. 轮询算法按顺序均匀分配请求")
    print("  5. 加权轮询可以让性能更好的服务器处理更多请求")
    print("=" * 70)


if __name__ == "__main__":
    main()
