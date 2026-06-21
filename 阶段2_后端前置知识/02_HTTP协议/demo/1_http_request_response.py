"""
HTTP 请求与响应结构演示
对应理论：1.HTTP请求与响应结构.md

演示内容：
1. 启动一个本地 HTTP 服务
2. 发送 GET 请求，观察路径、查询参数和 Header
3. 发送 POST 请求，观察请求体和响应体
"""

from http.client import HTTPConnection, HTTPResponse
from http.server import BaseHTTPRequestHandler, HTTPServer
from threading import Thread
from typing import Any
from urllib.parse import parse_qs, urlparse
import json


class RequestResponseHandler(BaseHTTPRequestHandler):
    """处理演示用 HTTP 请求。"""

    def log_message(self, format: str, *args: Any) -> None:
        # 禁用默认访问日志，让输出更聚焦于学习内容。
        return

    def do_GET(self) -> None:
        parsed_url = urlparse(self.path)
        query_params = parse_qs(parsed_url.query)

        print("\n[服务端] 收到 GET 请求")
        print(f"  请求路径: {parsed_url.path}")
        print(f"  查询参数: {query_params}")
        print(f"  User-Agent: {self.headers.get('User-Agent')}")

        response_body = {
            "method": "GET",
            "path": parsed_url.path,
            "query": query_params,
            "message": "这是服务端返回的 JSON 响应",
        }
        self._send_json_response(200, response_body)

    def do_POST(self) -> None:
        content_length = int(self.headers.get("Content-Length", "0"))
        raw_body = self.rfile.read(content_length).decode("utf-8")

        print("\n[服务端] 收到 POST 请求")
        print(f"  请求路径: {self.path}")
        print(f"  Content-Type: {self.headers.get('Content-Type')}")
        print(f"  请求体: {raw_body}")

        request_data = json.loads(raw_body)
        response_body = {
            "method": "POST",
            "received": request_data,
            "message": "用户创建成功",
        }
        self._send_json_response(201, response_body)

    def _send_json_response(self, status_code: int, body: dict[str, Any]) -> None:
        response_bytes = json.dumps(body, ensure_ascii=False).encode("utf-8")
        self.send_response(status_code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(response_bytes)))
        self.end_headers()
        self.wfile.write(response_bytes)


def start_server() -> HTTPServer:
    server = HTTPServer(("127.0.0.1", 0), RequestResponseHandler)
    thread = Thread(target=server.serve_forever, daemon=True)
    thread.start()
    return server


def read_response(response: HTTPResponse) -> str:
    return response.read().decode("utf-8")


print("=" * 60)
print("HTTP 请求与响应结构演示")
print("=" * 60)

server = start_server()
host, port = server.server_address
print(f"[服务端] 已启动: http://{host}:{port}")

try:
    print("\n" + "=" * 60)
    print("1. GET 请求：路径 + 查询参数 + Header")
    print("=" * 60)

    connection = HTTPConnection(host, port)
    connection.request(
        "GET",
        "/api/users?page=1&page_size=20",
        headers={"User-Agent": "Python-HTTP-Demo/1.0"},
    )
    response = connection.getresponse()
    print(f"[客户端] 状态行: HTTP/{response.version / 10:.1f} {response.status} {response.reason}")
    print(f"[客户端] Content-Type: {response.getheader('Content-Type')}")
    print(f"[客户端] 响应体: {read_response(response)}")
    connection.close()

    print("\n" + "=" * 60)
    print("2. POST 请求：Header + Body")
    print("=" * 60)

    request_body = json.dumps({"name": "Alice", "age": 20}, ensure_ascii=False)
    connection = HTTPConnection(host, port)
    connection.request(
        "POST",
        "/api/users",
        body=request_body.encode("utf-8"),
        headers={"Content-Type": "application/json"},
    )
    response = connection.getresponse()
    print(f"[客户端] 状态码: {response.status}")
    print(f"[客户端] 响应体: {read_response(response)}")
    connection.close()
finally:
    server.shutdown()
    server.server_close()

print("\n核心要点：")
print("1. 请求由请求行、请求头、空行、请求体组成")
print("2. 响应由状态行、响应头、空行、响应体组成")
print("3. 后端通过路径、查询参数、Header、Body 理解客户端意图")
