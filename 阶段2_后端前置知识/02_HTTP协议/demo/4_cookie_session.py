"""
Cookie 与 Session 演示
对应理论：4.Cookie与Session.md

演示内容：
1. 登录后服务端通过 Set-Cookie 下发 session_id
2. 客户端后续请求自动或手动携带 Cookie
3. 服务端通过 session_id 找到对应用户状态
"""

from http.client import HTTPConnection, HTTPResponse
from http.server import BaseHTTPRequestHandler, HTTPServer
from http.cookies import SimpleCookie
from threading import Thread
from typing import Any
import json
import uuid


SESSIONS: dict[str, dict[str, str]] = {}


class CookieSessionHandler(BaseHTTPRequestHandler):
    def log_message(self, format: str, *args: Any) -> None:
        return

    def do_POST(self) -> None:
        if self.path != "/login":
            self._send_json(404, {"error": "接口不存在"})
            return

        session_id = uuid.uuid4().hex
        SESSIONS[session_id] = {"user_id": "1", "username": "alice"}

        response_body = {"message": "登录成功", "session_id": session_id}
        response_bytes = json.dumps(response_body, ensure_ascii=False).encode("utf-8")

        self.send_response(200)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(response_bytes)))
        self.send_header(
            "Set-Cookie",
            f"session_id={session_id}; HttpOnly; SameSite=Lax; Path=/",
        )
        self.end_headers()
        self.wfile.write(response_bytes)

        print("[服务端] 登录成功，已创建 Session")
        print(f"  session_id: {session_id}")
        print("  Set-Cookie: session_id=...; HttpOnly; SameSite=Lax; Path=/")

    def do_GET(self) -> None:
        if self.path != "/profile":
            self._send_json(404, {"error": "接口不存在"})
            return

        session_id = self._get_session_id_from_cookie()
        if session_id is None or session_id not in SESSIONS:
            self._send_json(401, {"error": "未登录或 Session 已失效"})
            return

        self._send_json(200, {"message": "已登录", "user": SESSIONS[session_id]})

    def _get_session_id_from_cookie(self) -> str | None:
        cookie_header = self.headers.get("Cookie", "")
        cookie = SimpleCookie(cookie_header)
        morsel = cookie.get("session_id")
        if morsel is None:
            return None
        return morsel.value

    def _send_json(self, status_code: int, body: dict[str, Any]) -> None:
        response_bytes = json.dumps(body, ensure_ascii=False).encode("utf-8")
        self.send_response(status_code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(response_bytes)))
        self.end_headers()
        self.wfile.write(response_bytes)


def start_server() -> HTTPServer:
    server = HTTPServer(("127.0.0.1", 0), CookieSessionHandler)
    thread = Thread(target=server.serve_forever, daemon=True)
    thread.start()
    return server


def read_response(response: HTTPResponse) -> str:
    return response.read().decode("utf-8")


print("=" * 60)
print("Cookie 与 Session 演示")
print("=" * 60)

server = start_server()
host, port = server.server_address

try:
    print("\n1. 未登录直接访问个人中心")
    connection = HTTPConnection(host, port)
    connection.request("GET", "/profile")
    response = connection.getresponse()
    print(f"[客户端] 状态码: {response.status}")
    print(f"[客户端] 响应体: {read_response(response)}")
    connection.close()

    print("\n2. 登录并接收 Set-Cookie")
    connection = HTTPConnection(host, port)
    connection.request("POST", "/login")
    response = connection.getresponse()
    set_cookie = response.getheader("Set-Cookie") or ""
    print(f"[客户端] 状态码: {response.status}")
    print(f"[客户端] Set-Cookie: {set_cookie}")
    print(f"[客户端] 响应体: {read_response(response)}")
    connection.close()

    print("\n3. 携带 Cookie 访问个人中心")
    cookie_value = set_cookie.split(";", maxsplit=1)[0]
    connection = HTTPConnection(host, port)
    connection.request("GET", "/profile", headers={"Cookie": cookie_value})
    response = connection.getresponse()
    print(f"[客户端] 请求头 Cookie: {cookie_value}")
    print(f"[客户端] 状态码: {response.status}")
    print(f"[客户端] 响应体: {read_response(response)}")
    connection.close()
finally:
    server.shutdown()
    server.server_close()

print("\n核心要点：")
print("1. Cookie 保存在客户端，Session 保存在服务端")
print("2. 浏览器通过 Cookie 携带 session_id，服务端据此查 Session")
print("3. 登录态 Cookie 应设置 HttpOnly、Secure、SameSite 等安全属性")
