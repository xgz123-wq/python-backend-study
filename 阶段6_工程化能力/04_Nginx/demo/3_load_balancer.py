"""
负载均衡器 —— Python 概念演示脚本
==================================

本脚本模拟完整的负载均衡器，帮助深入理解 Nginx upstream 的工作原理。

演示内容：
  1. 启动多个后端服务器实例
  2. 实现轮询（Round Robin）算法
  3. 实现加权轮询（Weighted Round Robin）算法
  4. 实现最少连接（Least Connections）算法
  5. 模拟健康检查机制
  6. 展示请求分发效果

运行方式：
  python 3_load_balancer.py

依赖：
  仅使用 Python 标准库，无需额外安装
"""

import http.server
import json
import random
import socketserver
import threading
import time
import urllib.request
import urllib.error
from dataclasses import dataclass, field

# ===========================================================================
# 后端服务器模拟
# ===========================================================================

@dataclass
class BackendServer:
    """
    后端服务器数据结构。

    记录服务器的地址、权重、连接数、健康状态等信息，
    对应 Nginx upstream 中每个 server 指令的配置。
    """
    host: str               # 服务器地址
    port: int               # 服务器端口
    weight: int = 1         # 权重（对应 Nginx 的 weight 参数）
    max_fails: int = 3      # 最大失败次数（对应 Nginx 的 max_fails）
    fail_timeout: int = 30  # 失败超时窗口（秒，对应 Nginx 的 fail_timeout）

    # 运行时状态
    active_connections: int = 0     # 当前活跃连接数
    total_requests: int = 0         # 累计处理请求数
    fail_count: int = 0             # 当前失败计数
    is_available: bool = True       # 是否可用
    last_fail_time: float = 0.0     # 上次失败时间
    http_server: object = field(default=None, repr=False)  # HTTP 服务器实例


class BackendHandler(http.server.BaseHTTPRequestHandler):
    """
    后端服务器请求处理器。

    模拟 FastAPI 应用处理请求的过程。
    通过 server_name 和延迟来区分不同的后端实例。
    """

    # 类变量，所有实例共享
    server_name = "Unknown"
    process_delay = 0.0     # 模拟处理延迟（秒）
    should_fail = False     # 是否模拟故障

    def do_GET(self):
        """处理 GET 请求。"""
        # 增加活跃连接计数
        self.server.backend.active_connections += 1

        try:
            if self.should_fail:
                # 模拟后端故障（返回 502）
                self.send_response(502)
                self.end_headers()
                self.wfile.write(b"Internal Server Error")
                return

            # 模拟处理延迟
            if self.process_delay > 0:
                time.sleep(self.process_delay)

            # 构造响应
            response = {
                "server": self.server_name,
                "port": self.server.server_port,
                "path": self.path,
                "active_connections": self.server.backend.active_connections,
            }
            body = json.dumps(response, ensure_ascii=False).encode("utf-8")

            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        finally:
            # 减少活跃连接计数
            self.server.backend.active_connections -= 1
            self.server.backend.total_requests += 1

    def log_message(self, format, *args):
        """静默日志（避免干扰演示输出）。"""
        pass


def create_backend(server: BackendServer, delay: float = 0.0) -> http.server.HTTPServer:
    """
    创建并启动一个后端服务器实例。

    参数:
        server: 后端服务器配置
        delay: 模拟的处理延迟（秒）

    返回:
        HTTPServer 实例
    """
    # 为每个后端创建独立的 Handler 类（避免类变量冲突）
    handler_class = type(
        f"Handler_{server.port}",
        (BackendHandler,),
        {"server_name": f"Backend-{server.port}", "process_delay": delay},
    )

    http_server = http.server.HTTPServer((server.host, server.port), handler_class)
    http_server.backend = server   # 关联后端数据结构
    server.http_server = http_server

    # 在后台线程中运行
    thread = threading.Thread(target=http_server.serve_forever, daemon=True)
    thread.start()

    return http_server


# ===========================================================================
# 负载均衡算法实现
# ===========================================================================

class LoadBalancer:
    """
    负载均衡器基类。

    所有负载均衡算法的公共接口和共享功能。
    """

    def __init__(self, servers: list[BackendServer]):
        """
        初始化负载均衡器。

        参数:
            servers: 后端服务器列表
        """
        self.servers = servers
        self.request_count = 0

    def next_server(self) -> BackendServer:
        """
        选择下一个后端服务器（子类实现具体算法）。

        返回:
            被选中的后端服务器
        """
        raise NotImplementedError

    def get_available_servers(self) -> list[BackendServer]:
        """
        获取当前可用的后端服务器列表。
        过滤掉不可用（down 或健康检查失败）的服务器。
        """
        now = time.time()
        available = []
        for server in self.servers:
            if server.is_available:
                available.append(server)
            elif server.fail_timeout > 0:
                # 检查是否已经过了 fail_timeout 恢复时间
                if now - server.last_fail_time > server.fail_timeout:
                    server.is_available = True
                    server.fail_count = 0
                    available.append(server)
        return available

    def record_success(self, server: BackendServer):
        """记录请求成功，重置失败计数。"""
        server.fail_count = 0

    def record_failure(self, server: BackendServer):
        """
        记录请求失败。
        当失败次数达到 max_fails 时，标记服务器为不可用。
        """
        server.fail_count += 1
        server.last_fail_time = time.time()
        if server.fail_count >= server.max_fails:
            server.is_available = False
            print(f"    ⚠ 后端 {server.port} 连续失败 {server.fail_count} 次，标记为不可用")


class RoundRobinBalancer(LoadBalancer):
    """
    轮询负载均衡器。

    按顺序依次将请求分配到各个后端服务器。
    对应 Nginx 默认的 upstream 行为（不加任何算法关键字）。

    Nginx 配置等价：
        upstream backend {
            server 127.0.0.1:8001;
            server 127.0.0.1:8002;
            server 127.0.0.1:8003;
        }
    """

    def __init__(self, servers: list[BackendServer]):
        super().__init__(servers)
        self.current_index = 0

    def next_server(self) -> BackendServer:
        """轮询选择下一个可用的后端服务器。"""
        available = self.get_available_servers()
        if not available:
            raise RuntimeError("没有可用的后端服务器")

        # 在可用服务器中轮询
        idx = self.current_index % len(available)
        server = available[idx]
        self.current_index += 1
        self.request_count += 1
        return server


class WeightedRoundRobinBalancer(LoadBalancer):
    """
    加权轮询负载均衡器。

    根据权重比例分配请求，权重越高的服务器处理越多请求。

    Nginx 配置等价：
        upstream backend {
            server 127.0.0.1:8001 weight=5;
            server 127.0.0.1:8002 weight=3;
            server 127.0.0.1:8003 weight=2;
        }
    """

    def __init__(self, servers: list[BackendServer]):
        super().__init__(servers)
        # 按权重展开服务器列表
        self.expanded: list[BackendServer] = []
        for s in servers:
            self.expanded.extend([s] * s.weight)
        self.current_index = 0

    def next_server(self) -> BackendServer:
        """按加权轮询选择下一个后端服务器。"""
        available = self.get_available_servers()
        if not available:
            raise RuntimeError("没有可用的后端服务器")

        # 从展开列表中轮询
        server = self.expanded[self.current_index % len(self.expanded)]
        self.current_index += 1
        self.request_count += 1

        # 如果选中的服务器不可用，跳到下一个
        if not server.is_available:
            for s in available:
                return s

        return server


class LeastConnectionsBalancer(LoadBalancer):
    """
    最少连接负载均衡器。

    将请求分配给当前活跃连接数最少的后端服务器。
    适合后端请求处理时间差异较大的场景。

    Nginx 配置等价：
        upstream backend {
            least_conn;
            server 127.0.0.1:8001;
            server 127.0.0.1:8002;
            server 127.0.0.1:8003;
        }
    """

    def next_server(self) -> BackendServer:
        """选择当前活跃连接数最少的可用后端服务器。"""
        available = self.get_available_servers()
        if not available:
            raise RuntimeError("没有可用的后端服务器")

        # 选择 active_connections 最小的服务器
        server = min(available, key=lambda s: s.active_connections)
        self.request_count += 1
        return server


# ===========================================================================
# 健康检查模拟
# ===========================================================================

class HealthChecker:
    """
    健康检查器。

    模拟 Nginx 的被动健康检查机制：
    - 通过实际请求检测后端是否可用
    - 连续失败 max_fails 次后标记为不可用
    - fail_timeout 秒后自动恢复

    Nginx 配置等价：
        upstream backend {
            server 127.0.0.1:8001 max_fails=3 fail_timeout=30s;
        }
        proxy_next_upstream error timeout http_502;
    """

    def __init__(self, servers: list[BackendServer]):
        """
        初始化健康检查器。

        参数:
            servers: 要检查的后端服务器列表
        """
        self.servers = servers

    def check_server(self, server: BackendServer) -> bool:
        """
        检查单个后端服务器是否健康。

        参数:
            server: 要检查的后端服务器

        返回:
            True 表示健康，False 表示故障
        """
        try:
            url = f"http://{server.host}:{server.port}/health"
            resp = urllib.request.urlopen(url, timeout=2)
            if resp.status == 200:
                return True
        except Exception:
            pass
        return False

    def check_all(self) -> dict[int, bool]:
        """
        检查所有后端服务器的健康状态。

        返回:
            {端口号: 是否健康} 的字典
        """
        results = {}
        for server in self.servers:
            healthy = self.check_server(server)
            results[server.port] = healthy

            if not healthy:
                server.fail_count += 1
                server.last_fail_time = time.time()
                if server.fail_count >= server.max_fails:
                    server.is_available = False
            else:
                server.fail_count = 0
                server.is_available = True

        return results

    def print_status(self):
        """打印所有后端服务器的状态。"""
        for server in self.servers:
            status = "✓ 可用" if server.is_available else "✗ 不可用"
            print(
                f"    后端 :{server.port} | {status} | "
                f"请求数: {server.total_requests:>3} | "
                f"活跃连接: {server.active_connections} | "
                f"失败计数: {server.fail_count}"
            )


# ===========================================================================
# 演示函数
# ===========================================================================

def demo_round_robin():
    """演示轮询负载均衡算法。"""
    print("=" * 70)
    print("演示 1：轮询负载均衡（Round Robin）")
    print("=" * 70)
    print()
    print("  相当于 Nginx 配置:")
    print("    upstream backend {")
    print("        server 127.0.0.1:10001;")
    print("        server 127.0.0.1:10002;")
    print("        server 127.0.0.1:10003;")
    print("    }")
    print()

    # 创建后端服务器
    servers = [
        BackendServer("127.0.0.1", 10001),
        BackendServer("127.0.0.1", 10002),
        BackendServer("127.0.0.1", 10003),
    ]

    for s in servers:
        create_backend(s)

    time.sleep(0.3)

    # 创建轮询负载均衡器
    balancer = RoundRobinBalancer(servers)

    # 模拟 12 个请求
    print("  发送 12 个请求：")
    for i in range(12):
        server = balancer.next_server()
        try:
            url = f"http://{server.host}:{server.port}/test"
            resp = urllib.request.urlopen(url, timeout=3)
            data = json.loads(resp.read().decode("utf-8"))
            print(f"    请求 #{i + 1:>2} → 后端 :{server.port} ({data['server']})")
            balancer.record_success(server)
        except Exception as e:
            print(f"    请求 #{i + 1:>2} → 后端 :{server.port} 失败: {e}")
            balancer.record_failure(server)

    print()
    print("  请求分布（轮询结果）：")
    for s in servers:
        bar = "█" * s.total_requests
        print(f"    后端 :{s.port}: {bar} ({s.total_requests} 次)")

    print()
    print("  结论：每个后端各处理 4 个请求，完全均匀")
    print()

    # 清理
    for s in servers:
        s.http_server.shutdown()


def demo_weighted_round_robin():
    """演示加权轮询负载均衡算法。"""
    print("=" * 70)
    print("演示 2：加权轮询负载均衡（Weighted Round Robin）")
    print("=" * 70)
    print()
    print("  相当于 Nginx 配置:")
    print("    upstream backend {")
    print("        server 127.0.0.1:10011 weight=5;  # 高性能服务器")
    print("        server 127.0.0.1:10012 weight=3;  # 中等性能")
    print("        server 127.0.0.1:10013 weight=2;  # 低性能")
    print("    }")
    print()

    servers = [
        BackendServer("127.0.0.1", 10011, weight=5),
        BackendServer("127.0.0.1", 10012, weight=3),
        BackendServer("127.0.0.1", 10013, weight=2),
    ]

    for s in servers:
        create_backend(s)

    time.sleep(0.3)

    balancer = WeightedRoundRobinBalancer(servers)

    # 模拟 30 个请求
    total_requests = 30
    print(f"  发送 {total_requests} 个请求：")

    for i in range(total_requests):
        server = balancer.next_server()
        try:
            url = f"http://{server.host}:{server.port}/test"
            urllib.request.urlopen(url, timeout=3)
            balancer.record_success(server)
        except Exception:
            balancer.record_failure(server)

    print()
    print("  请求分布（加权轮询结果）：")
    total = sum(s.total_requests for s in servers)
    for s in servers:
        bar = "█" * s.total_requests
        pct = s.total_requests / total * 100 if total > 0 else 0
        print(f"    后端 :{s.port} (权重{s.weight}): {bar} ({s.total_requests} 次, {pct:.0f}%)")

    print()
    print("  结论：请求按 5:3:2 的比例分配")
    print("  权重为 5 的服务器处理了约 50% 的请求")
    print()

    for s in servers:
        s.http_server.shutdown()


def demo_least_connections():
    """演示最少连接负载均衡算法。"""
    print("=" * 70)
    print("演示 3：最少连接负载均衡（Least Connections）")
    print("=" * 70)
    print()
    print("  相当于 Nginx 配置:")
    print("    upstream backend {")
    print("        least_conn;")
    print("        server 127.0.0.1:10021;")
    print("        server 127.0.0.1:10022;")
    print("        server 127.0.0.1:10023;")
    print("    }")
    print()

    # 创建后端，每个有不同的处理延迟
    servers = [
        BackendServer("127.0.0.1", 10021),
        BackendServer("127.0.0.1", 10022),
        BackendServer("127.0.0.1", 10023),
    ]

    # 后端 :10021 处理慢（模拟复杂请求），其他两个快
    create_backend(servers[0], delay=0.5)
    create_backend(servers[1], delay=0.01)
    create_backend(servers[2], delay=0.01)

    time.sleep(0.3)

    balancer = LeastConnectionsBalancer(servers)

    print("  场景：后端 :10021 处理慢（0.5s/请求），:10022 和 :10023 处理快（0.01s/请求）")
    print("  用多线程并发发送 15 个请求：")
    print()

    results: list[str] = []
    results_lock = threading.Lock()

    def send_request(request_id: int):
        """发送一个请求（在独立线程中运行）。"""
        server = balancer.next_server()
        start = time.time()
        try:
            url = f"http://{server.host}:{server.port}/test"
            resp = urllib.request.urlopen(url, timeout=5)
            data = json.loads(resp.read().decode("utf-8"))
            elapsed = time.time() - start
            with results_lock:
                results.append(
                    f"    请求 #{request_id:>2} → 后端 :{server.port} "
                    f"(耗时 {elapsed:.2f}s)"
                )
            balancer.record_success(server)
        except Exception as e:
            with results_lock:
                results.append(f"    请求 #{request_id:>2} → 后端 :{server.port} 失败: {e}")
            balancer.record_failure(server)

    # 并发发送请求
    threads = []
    for i in range(15):
        t = threading.Thread(target=send_request, args=(i + 1,))
        threads.append(t)
        t.start()
        time.sleep(0.05)  # 稍微错开启动时间

    # 等待所有请求完成
    for t in threads:
        t.join(timeout=10)

    # 打印结果
    for r in sorted(results):
        print(r)

    print()
    print("  请求分布：")
    for s in servers:
        bar = "█" * s.total_requests
        print(f"    后端 :{s.port}: {bar} ({s.total_requests} 次)")

    print()
    print("  结论：处理快的后端（:10022, :10023）处理了更多请求")
    print("  因为它们的连接更快释放，被选中的概率更高")
    print("  这就是 least_conn 算法的智能之处")
    print()

    for s in servers:
        s.http_server.shutdown()


def demo_health_check():
    """演示健康检查机制。"""
    print("=" * 70)
    print("演示 4：健康检查与故障恢复")
    print("=" * 70)
    print()
    print("  相当于 Nginx 配置:")
    print("    upstream backend {")
    print("        server 127.0.0.1:10031 max_fails=3 fail_timeout=5s;")
    print("        server 127.0.0.1:10032 max_fails=3 fail_timeout=5s;")
    print("        server 127.0.0.1:10033 max_fails=3 fail_timeout=5s;")
    print("    }")
    print("    proxy_next_upstream error timeout http_502;")
    print()
    print("  注：这里 fail_timeout 设为 5 秒以加速演示")
    print()

    servers = [
        BackendServer("127.0.0.1", 10031, max_fails=3, fail_timeout=5),
        BackendServer("127.0.0.1", 10032, max_fails=3, fail_timeout=5),
        BackendServer("127.0.0.1", 10033, max_fails=3, fail_timeout=5),
    ]

    for s in servers:
        create_backend(s)

    time.sleep(0.3)

    checker = HealthChecker(servers)
    balancer = RoundRobinBalancer(servers)

    # 阶段 1：所有后端正常
    print("--- 阶段 1：所有后端正常运行 ---")
    for i in range(6):
        server = balancer.next_server()
        try:
            url = f"http://{server.host}:{server.port}/test"
            urllib.request.urlopen(url, timeout=3)
            balancer.record_success(server)
        except Exception:
            balancer.record_failure(server)

    checker.print_status()
    print()

    # 阶段 2：模拟后端 :10032 故障
    print("--- 阶段 2：后端 :10032 发生故障 ---")

    # 让 :10032 的 Handler 返回 502
    for s in servers:
        if s.port == 10032:
            # 找到对应的 Handler 类并设置故障标志
            handler_class = s.http_server.RequestHandlerClass
            handler_class.should_fail = True

    # 发送请求，触发故障检测
    for i in range(9):
        server = balancer.next_server()
        try:
            url = f"http://{server.host}:{server.port}/test"
            resp = urllib.request.urlopen(url, timeout=3)
            if resp.status == 502:
                balancer.record_failure(server)
            else:
                balancer.record_success(server)
        except urllib.error.HTTPError:
            balancer.record_failure(server)
        except Exception:
            balancer.record_failure(server)

    print()
    checker.print_status()
    print()

    # 阶段 3：流量只分配到健康的后端
    print("--- 阶段 3：故障后端被移除，流量只到 :10031 和 :10033 ---")

    # 重置请求计数以便观察
    for s in servers:
        s.total_requests = 0

    for i in range(6):
        server = balancer.next_server()
        try:
            url = f"http://{server.host}:{server.port}/test"
            resp = urllib.request.urlopen(url, timeout=3)
            balancer.record_success(server)
        except Exception:
            balancer.record_failure(server)

    print("  发送 6 个请求后的分布：")
    for s in servers:
        if s.is_available:
            bar = "█" * s.total_requests
            print(f"    后端 :{s.port}: {bar} ({s.total_requests} 次)")
        else:
            print(f"    后端 :{s.port}: [不可用，未接收请求]")

    print()

    # 阶段 4：故障后端恢复
    print("--- 阶段 4：后端 :10032 恢复，等待 fail_timeout（5秒）后重新加入 ---")

    # 修复 :10032
    for s in servers:
        if s.port == 10032:
            handler_class = s.http_server.RequestHandlerClass
            handler_class.should_fail = False

    # 等待 fail_timeout
    print("  等待 6 秒...")
    time.sleep(6)

    # 重置计数
    for s in servers:
        s.total_requests = 0

    for i in range(9):
        server = balancer.next_server()
        try:
            url = f"http://{server.host}:{server.port}/test"
            urllib.request.urlopen(url, timeout=3)
            balancer.record_success(server)
        except Exception:
            balancer.record_failure(server)

    print()
    print("  恢复后发送 9 个请求的分布：")
    for s in servers:
        bar = "█" * s.total_requests
        status = "可用" if s.is_available else "不可用"
        print(f"    后端 :{s.port} [{status}]: {bar} ({s.total_requests} 次)")

    print()
    print("  结论：")
    print("  1. 故障后端被自动检测并移除")
    print("  2. 流量自动分配到健康的后端")
    print("  3. fail_timeout 过后，故障后端自动恢复接收请求")
    print("  4. 这就是 Nginx 被动健康检查的完整流程")
    print()

    for s in servers:
        s.http_server.shutdown()


def demo_algorithm_comparison():
    """对比展示三种算法的请求分布。"""
    print("=" * 70)
    print("演示 5：三种算法对比总结")
    print("=" * 70)
    print()

    print("  ┌──────────────┬────────────────┬─────────────────┬───────────────────┐")
    print("  │    算法      │   Nginx 配置   │    分配策略     │    适用场景       │")
    print("  ├──────────────┼────────────────┼─────────────────┼───────────────────┤")
    print("  │ 轮询         │ （默认）       │ 均匀轮流分配    │ 后端配置相同      │")
    print("  │              │                │                 │                   │")
    print("  │ 加权轮询     │ weight=N       │ 按权重比例分配  │ 后端性能不同      │")
    print("  │              │                │                 │                   │")
    print("  │ IP Hash      │ ip_hash        │ 按客户端IP哈希  │ 需Session粘性     │")
    print("  │              │                │                 │                   │")
    print("  │ 最少连接     │ least_conn     │ 发给连接最少的  │ 请求处理时间差异大│")
    print("  └──────────────┴────────────────┴─────────────────┴───────────────────┘")
    print()

    print("  选择建议：")
    print("  - 大多数场景：默认轮询即可")
    print("  - 服务器配置不同：用 weight 加权")
    print("  - 用内存 Session 且无法共享：用 ip_hash")
    print("  - 请求处理时间差异大（有长有短）：用 least_conn")
    print("  - 最佳实践：后端无状态化 + Redis Session + 轮询/加权")
    print()


# ===========================================================================
# 主程序
# ===========================================================================

def main():
    """运行所有演示。"""
    print()
    print("╔══════════════════════════════════════════════════════════════════╗")
    print("║         负载均衡器 —— Python 概念演示                          ║")
    print("╚══════════════════════════════════════════════════════════════════╝")
    print()
    print("  本脚本模拟 Nginx upstream 的负载均衡机制：")
    print("  - 启动真实的 HTTP 后端服务器")
    print("  - 实现三种负载均衡算法")
    print("  - 演示健康检查和故障恢复")
    print()

    # 演示 1：轮询
    demo_round_robin()

    # 演示 2：加权轮询
    demo_weighted_round_robin()

    # 演示 3：最少连接
    demo_least_connections()

    # 演示 4：健康检查
    demo_health_check()

    # 演示 5：算法对比
    demo_algorithm_comparison()

    print("=" * 70)
    print("演示结束！")
    print()
    print("核心收获：")
    print("  1. 轮询算法简单公平，适合后端配置相同的场景")
    print("  2. 加权轮询让高性能服务器处理更多请求")
    print("  3. 最少连接算法智能地将请求分配给空闲的后端")
    print("  4. 被动健康检查通过实际请求发现故障，自动移除和恢复")
    print("  5. 生产环境推荐：后端无状态化 + Redis Session + 加权轮询")
    print("=" * 70)


if __name__ == "__main__":
    main()
