"""
Header 与 Content-Type 演示
对应理论：3.Header与Content-Type.md

演示内容：
1. Content-Type 决定服务端如何解析请求体
2. Accept 表示客户端希望接收什么响应格式
3. Authorization 放在 Header 中，不放在 URL 中
"""

from http.client import HTTPConnection, HTTPResponse
from http.server import BaseHTTPRequestHandler, HTTPServer
from threading import Thread
from typing import Any
from urllib.parse import parse_qs
import json


class HeaderContentTypeHandler(BaseHTTPRequestHandler):
    def log_message(self, format: str, *args: Any) -> None:
        return

    def do_POST(self) -> None:
        content_length = int(self.headers.get("Content-Length", "0"))
        content_type = self.headers.get("Content-Type", "")
        accept = self.headers.get("Accept", "*/*")
        authorization = self.headers.get("Authorization", "")
        raw_body = self.rfile.read(content_length).decode("utf-8")

        print("\n[服务端] 收到请求")
        print(f"  Content-Type: {content_type}")
        print(f"  Accept: {accept}")
        print(f"  Authorization: {mask_token(authorization)}")
        print(f"  Raw Body: {raw_body}")

        if "application/json" in content_type:
            parsed_body: Any = json.loads(raw_body)
        elif "application/x-www-form-urlencoded" in content_type:
            parsed_body = parse_qs(raw_body)
        elif "text/plain" in content_type:
            parsed_body = raw_body
        else:
            self._send_json(415, {"error": "不支持的 Content-Type"})
            return

        if "application/json" not in accept and "*/*" not in accept:
            self._send_json(406, {"error": "客户端不接受 JSON 响应"})
            return

        self._send_json(
            200,
            {
                "content_type": content_type,
                "parsed_body": parsed_body,
                "message": "服务端已按 Content-Type 正确解析请求体",
            },
        )

    def _send_json(self, status_code: int, body: dict[str, Any]) -> None:
        response_bytes = json.dumps(body, ensure_ascii=False).encode("utf-8")
        self.send_response(status_code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(response_bytes)))
        self.end_headers()
        self.wfile.write(response_bytes)


def mask_token(value: str) -> str:
    if not value:
        return "<未提供>"
    if len(value) <= 12:
        return "***"
    return f"{value[:10]}...***"


def start_server() -> HTTPServer:
    server = HTTPServer(("127.0.0.1", 0), HeaderContentTypeHandler)
    thread = Thread(target=server.serve_forever, daemon=True)
    thread.start()
    return server


def read_response(response: HTTPResponse) -> str:
    return response.read().decode("utf-8")


def post(host: str, port: int, title: str, body: str, headers: dict[str, str]) -> None:
    print("\n" + "=" * 60)
    print(title)
    print("=" * 60)
    connection = HTTPConnection(host, port)
    connection.request("POST", "/submit", body=body.encode("utf-8"), headers=headers)
    response = connection.getresponse()
    print(f"[客户端] 状态码: {response.status}")
    print(f"[客户端] 响应体: {read_response(response)}")
    connection.close()


print("=" * 60)
print("Header 与 Content-Type 演示")
print("=" * 60)

server = start_server()
host, port = server.server_address

try:
    post(
        host,
        port,
        "1. JSON 请求：Content-Type = application/json",
        json.dumps({"name": "Alice", "age": 20}, ensure_ascii=False),
        {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "Authorization": "Bearer demo-token-123456",
        },
    )
    post(
        host,
        port,
        "2. 表单请求：Content-Type = application/x-www-form-urlencoded",
        "username=alice&password=secret",
        {
            "Content-Type": "application/x-www-form-urlencoded",
            "Accept": "application/json",
        },
    )
    post(
        host,
        port,
        "3. Accept 不匹配：客户端不接受 JSON",
        "hello",
        {
            "Content-Type": "text/plain",
            "Accept": "text/html",
        },
    )
finally:
    server.shutdown()
    server.server_close()

print("\n核心要点：")
print("1. Content-Type 描述自己发送的 Body 格式")
print("2. Accept 描述客户端希望接收的响应格式")
print("3. Token 应放在 Authorization Header 中，避免出现在 URL 和日志里")
