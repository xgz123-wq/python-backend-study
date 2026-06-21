"""
HTTPS 与 CORS 演示
对应理论：5.HTTPS与CORS.md

演示内容：
1. 解释 HTTPS 保护的三个目标
2. 模拟浏览器跨域预检 OPTIONS 请求
3. 对比允许来源与不允许来源的 CORS 响应
"""

from http.client import HTTPConnection, HTTPResponse
from http.server import BaseHTTPRequestHandler, HTTPServer
from threading import Thread
from typing import Any
import json


ALLOWED_ORIGIN = "https://frontend.example.com"


class HttpsCorsHandler(BaseHTTPRequestHandler):
    def log_message(self, format: str, *args: Any) -> None:
        return

    def do_OPTIONS(self) -> None:
        origin = self.headers.get("Origin", "")
        requested_method = self.headers.get("Access-Control-Request-Method", "")
        requested_headers = self.headers.get("Access-Control-Request-Headers", "")

        print("\n[服务端] 收到 CORS 预检请求")
        print(f"  Origin: {origin}")
        print(f"  Access-Control-Request-Method: {requested_method}")
        print(f"  Access-Control-Request-Headers: {requested_headers}")

        if origin == ALLOWED_ORIGIN:
            self.send_response(204)
            self._send_cors_headers(origin)
            self.end_headers()
            return

        self.send_response(403)
        self.end_headers()

    def do_GET(self) -> None:
        origin = self.headers.get("Origin", "")
        response_body = {"message": "跨域请求成功", "origin": origin}
        response_bytes = json.dumps(response_body, ensure_ascii=False).encode("utf-8")

        self.send_response(200)
        if origin == ALLOWED_ORIGIN:
            self._send_cors_headers(origin)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(response_bytes)))
        self.end_headers()
        self.wfile.write(response_bytes)

    def _send_cors_headers(self, origin: str) -> None:
        self.send_header("Access-Control-Allow-Origin", origin)
        self.send_header("Access-Control-Allow-Methods", "GET, POST, PUT, PATCH, DELETE")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization")
        self.send_header("Access-Control-Allow-Credentials", "true")
        self.send_header("Access-Control-Max-Age", "600")


def start_server() -> HTTPServer:
    server = HTTPServer(("127.0.0.1", 0), HttpsCorsHandler)
    thread = Thread(target=server.serve_forever, daemon=True)
    thread.start()
    return server


def read_response(response: HTTPResponse) -> str:
    body = response.read().decode("utf-8")
    return body if body else "<无响应体>"


def options_preflight(host: str, port: int, origin: str) -> None:
    connection = HTTPConnection(host, port)
    connection.request(
        "OPTIONS",
        "/api/users",
        headers={
            "Origin": origin,
            "Access-Control-Request-Method": "POST",
            "Access-Control-Request-Headers": "Content-Type, Authorization",
        },
    )
    response = connection.getresponse()
    print(f"[客户端] Origin: {origin}")
    print(f"[客户端] 状态码: {response.status}")
    print(f"[客户端] Allow-Origin: {response.getheader('Access-Control-Allow-Origin')}")
    print(f"[客户端] 响应体: {read_response(response)}")
    connection.close()


def get_with_origin(host: str, port: int, origin: str) -> None:
    connection = HTTPConnection(host, port)
    connection.request("GET", "/api/data", headers={"Origin": origin})
    response = connection.getresponse()
    print(f"[客户端] Origin: {origin}")
    print(f"[客户端] 状态码: {response.status}")
    print(f"[客户端] Allow-Origin: {response.getheader('Access-Control-Allow-Origin')}")
    print(f"[客户端] 响应体: {read_response(response)}")
    connection.close()


print("=" * 60)
print("HTTPS 与 CORS 演示")
print("=" * 60)

print("\n1. HTTPS 解决的三个核心问题")
print("  - 加密：防止请求和响应内容被窃听")
print("  - 完整性：防止传输过程中被篡改")
print("  - 身份认证：通过证书确认服务器身份")

server = start_server()
host, port = server.server_address

try:
    print("\n" + "=" * 60)
    print("2. 允许来源的 CORS 预检请求")
    print("=" * 60)
    options_preflight(host, port, ALLOWED_ORIGIN)

    print("\n" + "=" * 60)
    print("3. 不允许来源的 CORS 预检请求")
    print("=" * 60)
    options_preflight(host, port, "https://evil.example.com")

    print("\n" + "=" * 60)
    print("4. 简单 GET 跨域请求：对比响应头")
    print("=" * 60)
    get_with_origin(host, port, ALLOWED_ORIGIN)
    get_with_origin(host, port, "https://evil.example.com")
finally:
    server.shutdown()
    server.server_close()

print("\n核心要点：")
print("1. HTTPS = HTTP + TLS，生产环境登录和隐私接口必须使用")
print("2. CORS 是浏览器安全策略，Postman 和后端服务间请求不受该限制")
print("3. 生产环境不要随意允许 *，尤其是需要携带 Cookie 的请求")
