"""
HTTP 方法与状态码演示
对应理论：2.HTTP方法与状态码.md

演示内容：
1. GET / POST / PUT / PATCH / DELETE 的语义
2. 200 / 201 / 204 / 400 / 404 / 500 等状态码
3. 幂等与非幂等的直观对比
"""

from http.client import HTTPConnection, HTTPResponse
from http.server import BaseHTTPRequestHandler, HTTPServer
from threading import Thread
from typing import Any
import json


class MethodStatusHandler(BaseHTTPRequestHandler):
    users: dict[int, dict[str, str]] = {1: {"id": "1", "name": "Alice"}}
    next_id: int = 2

    def log_message(self, format: str, *args: Any) -> None:
        return

    def do_GET(self) -> None:
        if self.path == "/users/1":
            self._send_json(200, self.users[1])
            return
        if self.path == "/users/999":
            self._send_json(404, {"error": "用户不存在"})
            return
        if self.path == "/error":
            self._send_json(500, {"error": "服务端内部错误示例"})
            return
        self._send_json(400, {"error": "不支持的查询路径"})

    def do_POST(self) -> None:
        user_id = self.next_id
        self.next_id += 1
        self.users[user_id] = {"id": str(user_id), "name": f"User{user_id}"}
        self._send_json(201, {"message": "创建成功", "user": self.users[user_id]})

    def do_PUT(self) -> None:
        if self.path != "/users/1":
            self._send_json(404, {"error": "用户不存在"})
            return
        self.users[1] = {"id": "1", "name": "Alice Updated"}
        self._send_json(200, {"message": "全量更新成功", "user": self.users[1]})

    def do_PATCH(self) -> None:
        if self.path != "/users/1":
            self._send_json(404, {"error": "用户不存在"})
            return
        self.users[1]["name"] = "Alice Patched"
        self._send_json(200, {"message": "局部更新成功", "user": self.users[1]})

    def do_DELETE(self) -> None:
        if self.path != "/users/1":
            self._send_json(404, {"error": "用户不存在"})
            return
        self.send_response(204)
        self.end_headers()

    def _send_json(self, status_code: int, body: dict[str, Any]) -> None:
        response_bytes = json.dumps(body, ensure_ascii=False).encode("utf-8")
        self.send_response(status_code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(response_bytes)))
        self.end_headers()
        self.wfile.write(response_bytes)


def start_server() -> HTTPServer:
    server = HTTPServer(("127.0.0.1", 0), MethodStatusHandler)
    thread = Thread(target=server.serve_forever, daemon=True)
    thread.start()
    return server


def read_response(response: HTTPResponse) -> str:
    body = response.read().decode("utf-8")
    return body if body else "<无响应体>"


def request(host: str, port: int, method: str, path: str) -> None:
    connection = HTTPConnection(host, port)
    connection.request(method, path)
    response = connection.getresponse()
    print(f"  {method:<6} {path:<12} → {response.status:<3} {response.reason:<22} {read_response(response)}")
    connection.close()


print("=" * 60)
print("HTTP 方法与状态码演示")
print("=" * 60)

server = start_server()
host, port = server.server_address

try:
    print("\n1. 常见方法与状态码")
    print("  方法   路径          状态码 状态文本               响应体")
    print("  " + "-" * 90)
    request(host, port, "GET", "/users/1")
    request(host, port, "GET", "/users/999")
    request(host, port, "POST", "/users")
    request(host, port, "PUT", "/users/1")
    request(host, port, "PATCH", "/users/1")
    request(host, port, "DELETE", "/users/1")
    request(host, port, "GET", "/error")

    print("\n2. 幂等理解")
    print("  GET /users/1 多次查询不会改变资源 → 幂等")
    print("  PUT /users/1 多次全量更新为同一结果 → 幂等")
    print("  POST /users 多次请求会创建多个用户 → 通常非幂等")
finally:
    server.shutdown()
    server.server_close()

print("\n核心要点：")
print("1. 方法表达动作：GET 查、POST 建、PUT 全量改、PATCH 局部改、DELETE 删")
print("2. 状态码表达结果：2xx 成功，4xx 客户端错误，5xx 服务端错误")
print("3. 401 是未认证，403 是无权限，404 是资源不存在")
