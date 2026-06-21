# -*- coding: utf-8 -*-
"""
WSGI 与 ASGI 服务器概念演示

本脚本演示：
    1. WSGI 应用的标准接口（原生 Python）
    2. ASGI 应用的标准接口（异步 Python）
    3. 用 uvicorn 启动 ASGI 应用
    4. 单进程 vs 多进程处理并发的对比

运行方式：
    python 1_wsgi_asgi.py

前置要求：
    - Python 3.10+
    - 无额外依赖（全部使用标准库）

学习目标：
    - 理解 WSGI 和 ASGI 的接口规范
    - 理解为什么需要 Gunicorn/Uvicorn 等服务器
    - 理解多进程模型如何处理并发
"""

import os
import sys
import time
import multiprocessing
from http.server import HTTPServer, BaseHTTPRequestHandler
from concurrent.futures import ProcessPoolExecutor
import threading


# ============================================================
# 第一部分：WSGI 应用示例
# ============================================================

def wsgi_app(environ, start_response):
    """
    WSGI 应用的标准签名。

    WSGI（Web Server Gateway Interface）是 Python 的 Web 服务器
    与 Web 应用之间的标准接口（PEP 3333）。

    参数：
        environ: dict，包含 HTTP 请求信息（方法、路径、请求头等）
        start_response: callable，用于设置响应状态码和响应头

    返回：
        可迭代的字节串（响应体）
    """
    # 从 environ 中获取请求信息
    method = environ.get("REQUEST_METHOD", "GET")
    path = environ.get("PATH_INFO", "/")
    query = environ.get("QUERY_STRING", "")

    # 模拟业务处理（数据库查询、API 调用等）
    time.sleep(0.1)  # 模拟 100ms 的 I/O 操作

    # 构建响应
    status = "200 OK"
    response_headers = [
        ("Content-Type", "text/plain; charset=utf-8"),
        ("X-Powered-By", "WSGI"),
    ]

    # 调用 start_response 设置状态码和响应头
    start_response(status, response_headers)

    # 返回响应体（必须是可迭代的字节串）
    body = f"WSGI 响应: {method} {path}"
    if query:
        body += f"?{query}"
    body += f"\n进程 ID: {os.getpid()}"
    body += "\n线程 ID: " + str(threading.current_thread().ident)

    return [body.encode("utf-8")]


class WSGIServer:
    """
    简易 WSGI 服务器（用于演示，不要用于生产环境）。

    这个类展示了 WSGI 服务器的核心逻辑：
    1. 接收 HTTP 请求
    2. 构建 environ 字典
    3. 调用 WSGI 应用
    4. 发送响应
    """

    def __init__(self, app, host="127.0.0.1", port=8001):
        """
        初始化 WSGI 服务器。

        参数：
            app: WSGI 应用函数
            host: 监听地址
            port: 监听端口
        """
        self.app = app
        self.host = host
        self.port = port

    def serve(self):
        """启动服务器（阻塞）"""
        server = HTTPServer((self.host, self.port), self._make_handler())
        print(f"WSGI 服务器启动: http://{self.host}:{self.port}")
        print("按 Ctrl+C 停止")
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            print("\n服务器已停止")
            server.server_close()

    def _make_handler(self):
        """创建请求处理器"""
        app = self.app

        class Handler(BaseHTTPRequestHandler):
            def do_GET(self):
                """处理 GET 请求"""
                # 构建 WSGI environ
                environ = {
                    "REQUEST_METHOD": "GET",
                    "PATH_INFO": self.path.split("?")[0],
                    "QUERY_STRING": self.path.split("?")[1] if "?" in self.path else "",
                    "SERVER_NAME": self.server.server_name,
                    "SERVER_PORT": str(self.server.server_port),
                    "HTTP_HOST": self.headers.get("Host", ""),
                }

                # 收集响应
                response_started = []
                response_body = []

                def start_response(status, headers):
                    response_started.append((status, headers))

                # 调用 WSGI 应用
                result = app(environ, start_response)
                for chunk in result:
                    response_body.append(chunk)

                # 发送响应
                status, headers = response_started[0]
                status_code = int(status.split(" ")[0])
                self.send_response(status_code)
                for name, value in headers:
                    self.send_header(name, value)
                self.end_headers()
                self.wfile.write(b"".join(response_body))

            def log_message(self, format, *args):
                """自定义日志格式"""
                print(f"[WSGI] {self.client_address[0]} - {format % args}")

        return Handler


# ============================================================
# 第二部分：ASGI 应用示例
# ============================================================

# ASGI 应用的标准签名
# 注意：这里用同步方式模拟，真正的 ASGI 应用使用 async def
ASGI_APP_INFO = """
ASGI 应用的标准签名：

    async def application(scope, receive, send):
        # scope: dict，包含连接信息（类型、路径、请求头等）
        # receive: async callable，接收客户端消息
        # send: async callable，发送响应消息

        # 接收 HTTP 请求
        message = await receive()

        # 发送响应头
        await send({
            'type': 'http.response.start',
            'status': 200,
            'headers': [[b'content-type', b'text/plain']],
        })

        # 发送响应体
        await send({
            'type': 'http.response.body',
            'body': b'Hello from ASGI!',
        })

ASGI 相比 WSGI 的优势：
    1. 原生异步：使用 async/await，不阻塞线程
    2. WebSocket 支持：双向通信
    3. 长连接支持：SSE、长轮询
    4. 后台任务：不阻塞响应
"""


def show_asgi_example():
    """展示 ASGI 应用示例代码"""
    print("\n" + "=" * 60)
    print("ASGI 应用示例")
    print("=" * 60)
    print(ASGI_APP_INFO)

    print("\n用 uvicorn 启动 ASGI 应用的命令：")
    print("  uvicorn app.main:app --host 0.0.0.0 --port 8000")
    print("  uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4")
    print("  uvicorn app.main:app --reload  # 仅开发环境！")

    print("\n用 Gunicorn + Uvicorn Worker 启动（生产推荐）：")
    print("  gunicorn app.main:app \\")
    print("    --workers 4 \\")
    print("    --worker-class uvicorn.workers.UvicornWorker \\")
    print("    --bind 0.0.0.0:8000")


# ============================================================
# 第三部分：单进程 vs 多进程对比
# ============================================================

def handle_request(request_id):
    """
    模拟处理一个请求。

    参数：
        request_id: 请求 ID

    返回：
        处理结果字符串
    """
    pid = os.getpid()
    start = time.time()

    # 模拟 I/O 操作（数据库查询、API 调用）
    time.sleep(0.5)

    elapsed = time.time() - start
    return f"请求 #{request_id} 由进程 {pid} 处理，耗时 {elapsed:.2f}s"


def demo_single_process(num_requests=5):
    """
    演示单进程处理请求。

    单进程模式下，请求依次处理，总耗时 = 请求数 * 单个请求耗时。
    """
    print(f"\n{'=' * 60}")
    print(f"单进程模式：处理 {num_requests} 个请求")
    print(f"{'=' * 60}")

    start = time.time()

    for i in range(num_requests):
        result = handle_request(i + 1)
        print(f"  {result}")

    total = time.time() - start
    print(f"\n总耗时: {total:.2f}s")
    print(f"进程数: 1")
    print(f"吞吐量: {num_requests / total:.1f} 请求/秒")

    return total


def demo_multi_process(num_requests=5, num_workers=3):
    """
    演示多进程处理请求。

    多进程模式下，请求并行处理，总耗时大幅减少。
    这就是 Gunicorn 多 worker 的核心原理。
    """
    print(f"\n{'=' * 60}")
    print(f"多进程模式：{num_workers} 个 worker 处理 {num_requests} 个请求")
    print(f"{'=' * 60}")

    start = time.time()

    # 使用进程池模拟 Gunicorn 的多 worker
    with ProcessPoolExecutor(max_workers=num_workers) as executor:
        futures = [
            executor.submit(handle_request, i + 1)
            for i in range(num_requests)
        ]
        for future in futures:
            result = future.result()
            print(f"  {result}")

    total = time.time() - start
    print(f"\n总耗时: {total:.2f}s")
    print(f"进程数: {num_workers}")
    print(f"吞吐量: {num_requests / total:.1f} 请求/秒")

    return total


def compare_performance():
    """
    对比单进程和多进程的性能差异。

    这是 Gunicorn 多 worker 模型的核心价值：
    - 单进程：请求依次处理，I/O 等待时 CPU 空闲
    - 多进程：请求并行处理，充分利用多核 CPU
    """
    num_requests = 6
    num_workers = 3

    print("\n" + "=" * 60)
    print("性能对比：单进程 vs 多进程")
    print("=" * 60)
    print(f"请求数: {num_requests}")
    print(f"每个请求模拟 0.5s I/O 操作")
    print(f"多进程 worker 数: {num_workers}")

    # 单进程
    single_time = demo_single_process(num_requests)

    # 多进程
    multi_time = demo_multi_process(num_requests, num_workers)

    # 对比结果
    print(f"\n{'=' * 60}")
    print("性能对比结果")
    print(f"{'=' * 60}")
    print(f"单进程耗时: {single_time:.2f}s")
    print(f"多进程耗时: {multi_time:.2f}s")
    print(f"性能提升: {single_time / multi_time:.1f}x")
    print(f"\n结论：多进程可以显著提升并发处理能力")
    print(f"这就是为什么生产环境需要 Gunicorn 等进程管理器")


# ============================================================
# 第四部分：Gunicorn 架构说明
# ============================================================

def show_gunicorn_architecture():
    """展示 Gunicorn 的架构和工作原理"""
    print("\n" + "=" * 60)
    print("Gunicorn 架构")
    print("=" * 60)

    architecture = """
    ┌─────────────────────────────────────────────────────────┐
    │                    Nginx（反向代理）                       │
    │              处理 HTTPS、静态文件、负载均衡                   │
    └─────────────────────────┬───────────────────────────────┘
                              │ HTTP 请求
                              ▼
    ┌─────────────────────────────────────────────────────────┐
    │                Gunicorn Master Process                    │
    │                  （进程管理器）                             │
    │                                                          │
    │  职责：                                                   │
    │  - 启动/停止 worker                                       │
    │  - 监控 worker 健康状态                                    │
    │  - worker 崩溃时自动重启                                   │
    │  - 优雅重启（零停机部署）                                   │
    └──────────┬──────────────┬──────────────┬────────────────┘
               │              │              │
        ┌──────▼──────┐ ┌─────▼───────┐ ┌────▼──────────┐
        │  Worker 1   │ │  Worker 2   │ │  Worker 3     │
        │  (Uvicorn)  │ │  (Uvicorn)  │ │  (Uvicorn)    │
        │             │ │             │ │               │
        │  异步事件    │ │  异步事件    │ │  异步事件      │
        │  循环处理    │ │  循环处理    │ │  循环处理      │
        │  请求       │ │  请求       │ │  请求         │
        └─────────────┘ └─────────────┘ └───────────────┘
    """
    print(architecture)

    print("\n关键概念：")
    print("  - Master 进程：不处理请求，只负责管理 worker")
    print("  - Worker 进程：实际处理请求的进程")
    print("  - Worker 崩溃：Master 会自动重启新的 worker")
    print("  - 优雅重启：发送 HUP 信号，worker 完成当前请求后重启")

    print("\nWorker 数量计算公式：")
    print("  workers = 2 * CPU_核数 + 1")
    print("  例如：4 核 CPU → 9 个 worker")

    print("\n为什么不能直接用 uvicorn --reload？")
    print("  1. --reload 只启动单进程，无法利用多核")
    print("  2. --reload 监控文件变化，消耗性能")
    print("  3. --reload 文件变更导致频繁重启，不稳定")
    print("  4. 生产环境应使用 Gunicorn 管理进程")


# ============================================================
# 主函数
# ============================================================

def main():
    """主函数：运行所有演示"""
    print("=" * 60)
    print("WSGI 与 ASGI 服务器概念演示")
    print("=" * 60)

    # 1. WSGI 应用演示
    print("\n" + "=" * 60)
    print("第一部分：WSGI 应用接口")
    print("=" * 60)
    print("\nWSGI 应用的标准签名：")
    print("  def application(environ, start_response):")
    print("      start_response('200 OK', [('Content-Type', 'text/plain')])")
    print("      return [b'Hello World']")

    print("\nWSGI 应用的特性：")
    print("  - 同步接口：每个请求占用一个线程/进程")
    print("  - 不支持 WebSocket")
    print("  - 适合 Flask、Django（同步模式）")
    print("  - 典型服务器：Gunicorn（sync worker）")

    # 模拟 WSGI 请求处理
    print("\n模拟 WSGI 请求处理：")

    def mock_start_response(status, headers):
        print(f"  状态码: {status}")
        print(f"  响应头: {headers}")

    environ = {
        "REQUEST_METHOD": "GET",
        "PATH_INFO": "/api/users",
        "QUERY_STRING": "page=1&size=10",
    }

    print(f"  请求: {environ['REQUEST_METHOD']} {environ['PATH_INFO']}?{environ['QUERY_STRING']}")
    result = wsgi_app(environ, mock_start_response)
    print(f"  响应体: {result[0].decode('utf-8')}")

    # 2. ASGI 应用演示
    show_asgi_example()

    # 3. 性能对比
    compare_performance()

    # 4. Gunicorn 架构
    show_gunicorn_architecture()

    # 总结
    print("\n" + "=" * 60)
    print("本章总结")
    print("=" * 60)
    print("""
    1. WSGI 是同步接口，ASGI 是异步接口
    2. 生产环境需要专用服务器（Gunicorn/Uvicorn）
    3. Gunicorn 负责进程管理，Uvicorn 负责异步处理
    4. 最佳组合：Gunicorn + UvicornWorker
    5. Worker 数量：2 * CPU 核数 + 1
    6. 生产环境禁止使用 --reload
    """)


if __name__ == "__main__":
    main()
