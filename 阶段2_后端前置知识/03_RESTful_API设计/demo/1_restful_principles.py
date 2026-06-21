"""
Demo 1: RESTful 设计原则
对比：动作导向 API vs 资源导向 RESTful API

对应理论文档：1.RESTful设计原则.md

演示内容：
- 用 http.server 模拟一个"动作导向"的旧风格 API
- 再模拟一个"资源导向"的 RESTful API
- 两者对比，理解 RESTful 设计的核心思想
"""

import json
import threading
import time
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse, parse_qs


# ─── 模拟数据库 ────────────────────────────────────────────────────────────────
USERS_DB = {
    1: {"id": 1, "name": "Alice", "email": "alice@example.com", "status": "active"},
    2: {"id": 2, "name": "Bob",   "email": "bob@example.com",   "status": "inactive"},
    3: {"id": 3, "name": "Carol", "email": "carol@example.com", "status": "active"},
}
next_id = 4


# ─── RESTful API 服务 ──────────────────────────────────────────────────────────
class RESTfulHandler(BaseHTTPRequestHandler):
    """
    实现标准 RESTful 路由：
      GET    /users        → 获取所有用户
      GET    /users/{id}   → 获取单个用户
      POST   /users        → 创建用户
      PATCH  /users/{id}   → 部分更新用户
      DELETE /users/{id}   → 删除用户
    """

    def log_message(self, format, *args):
        """关闭默认的访问日志，改为手动打印"""
        pass

    def send_json(self, status: int, data: dict):
        body = json.dumps(data, ensure_ascii=False).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        global USERS_DB
        parsed = urlparse(self.path)
        parts = [p for p in parsed.path.split("/") if p]

        # GET /users
        if parts == ["users"]:
            self.send_json(200, {
                "code": 0,
                "data": {"items": list(USERS_DB.values()), "total": len(USERS_DB)}
            })

        # GET /users/{id}
        elif len(parts) == 2 and parts[0] == "users":
            user_id = int(parts[1])
            user = USERS_DB.get(user_id)
            if user:
                self.send_json(200, {"code": 0, "data": user})
            else:
                self.send_json(404, {"code": 40401, "message": "用户不存在"})
        else:
            self.send_json(404, {"code": 40400, "message": "接口不存在"})

    def do_POST(self):
        global USERS_DB, next_id
        parsed = urlparse(self.path)
        parts = [p for p in parsed.path.split("/") if p]

        # POST /users
        if parts == ["users"]:
            length = int(self.headers.get("Content-Length", 0))
            body = json.loads(self.rfile.read(length))
            new_user = {"id": next_id, **body}
            USERS_DB[next_id] = new_user
            next_id += 1
            # 201 Created：创建成功用 201，不用 200
            self.send_json(201, {"code": 0, "message": "用户创建成功", "data": new_user})
        else:
            self.send_json(404, {"code": 40400, "message": "接口不存在"})

    def do_PATCH(self):
        global USERS_DB
        parsed = urlparse(self.path)
        parts = [p for p in parsed.path.split("/") if p]

        # PATCH /users/{id}
        if len(parts) == 2 and parts[0] == "users":
            user_id = int(parts[1])
            user = USERS_DB.get(user_id)
            if not user:
                self.send_json(404, {"code": 40401, "message": "用户不存在"})
                return
            length = int(self.headers.get("Content-Length", 0))
            updates = json.loads(self.rfile.read(length))
            user.update(updates)          # 只更新传入的字段（PATCH 语义）
            self.send_json(200, {"code": 0, "data": user})
        else:
            self.send_json(404, {"code": 40400, "message": "接口不存在"})

    def do_DELETE(self):
        global USERS_DB
        parsed = urlparse(self.path)
        parts = [p for p in parsed.path.split("/") if p]

        # DELETE /users/{id}
        if len(parts) == 2 and parts[0] == "users":
            user_id = int(parts[1])
            if user_id not in USERS_DB:
                self.send_json(404, {"code": 40401, "message": "用户不存在"})
                return
            del USERS_DB[user_id]
            # 204 No Content：删除成功通常不返回 body
            self.send_response(204)
            self.end_headers()
        else:
            self.send_json(404, {"code": 40400, "message": "接口不存在"})


# ─── 演示客户端 ────────────────────────────────────────────────────────────────
def demo_restful_client():
    """演示 RESTful API 的各种操作，对比动作导向的旧风格"""
    import http.client

    time.sleep(0.3)
    conn = http.client.HTTPConnection("localhost", 8301)

    def request(method, path, body=None):
        headers = {"Content-Type": "application/json"}
        data = json.dumps(body).encode() if body else b""
        conn.request(method, path, data, headers)
        resp = conn.getresponse()
        raw = resp.read().decode()
        return resp.status, json.loads(raw) if raw else None

    print("\n" + "=" * 60)
    print("     RESTful API 设计原则 Demo")
    print("=" * 60)

    print("\n【对比】动作导向 vs 资源导向")
    print("  动作导向（旧风格）:")
    print("    POST /getUser           ← 动词在 URL")
    print("    POST /createUser        ← 动词在 URL")
    print("    POST /deleteUser        ← 动词在 URL")
    print("  资源导向（RESTful）:")
    print("    GET    /users/{id}      ← 名词 URL + HTTP 方法表达动作")
    print("    POST   /users           ← 名词 URL + HTTP 方法表达动作")
    print("    DELETE /users/{id}      ← 名词 URL + HTTP 方法表达动作")

    print("\n─── 1. GET /users（获取所有用户）─────────────────")
    status, data = request("GET", "/users")
    print(f"  HTTP {status} → 共 {data['data']['total']} 个用户")
    for u in data["data"]["items"]:
        print(f"    - [{u['id']}] {u['name']} ({u['status']})")

    print("\n─── 2. GET /users/1（获取单个用户）───────────────")
    status, data = request("GET", "/users/1")
    print(f"  HTTP {status} → {data['data']}")

    print("\n─── 3. POST /users（创建用户，返回 201）──────────")
    status, data = request("POST", "/users", {"name": "Dave", "email": "dave@x.com", "status": "active"})
    print(f"  HTTP {status} → 创建成功：{data['data']}")

    print("\n─── 4. PATCH /users/2（部分更新，只改 status）───")
    status, data = request("PATCH", "/users/2", {"status": "active"})
    print(f"  HTTP {status} → 更新后：{data['data']}")

    print("\n─── 5. DELETE /users/3（删除用户，返回 204）─────")
    status, _ = request("DELETE", "/users/3")
    print(f"  HTTP {status} → 删除成功（204 No Content，无响应体）")

    print("\n─── 6. GET /users（确认删除后的列表）────────────")
    status, data = request("GET", "/users")
    print(f"  HTTP {status} → 现剩 {data['data']['total']} 个用户")

    print("\n─── 7. GET /users/999（不存在的资源）────────────")
    status, data = request("GET", "/users/999")
    print(f"  HTTP {status} → {data}")

    print("\n" + "=" * 60)
    print("  核心要点回顾：")
    print("  1. URL 只含名词（/users），HTTP 方法表达动词")
    print("  2. 集合用复数：/users，单个用：/users/{id}")
    print("  3. 创建成功返回 201，删除成功返回 204（无 body）")
    print("  4. 404 代表资源不存在，对应业务 code 细化原因")
    print("=" * 60)

    conn.close()


def main():
    server = HTTPServer(("localhost", 8301), RESTfulHandler)
    t = threading.Thread(target=server.serve_forever, daemon=True)
    t.start()

    demo_restful_client()


if __name__ == "__main__":
    main()
