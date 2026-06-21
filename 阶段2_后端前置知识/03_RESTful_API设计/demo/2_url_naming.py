"""
Demo 2: URL 命名规范
演示 RESTful URL 设计的七条核心规范

对应理论文档：2.URL命名规范.md

演示内容：
- 规范 vs 不规范的 URL 对比
- 嵌套资源路由（用户 → 订单）
- 路径参数 vs 查询参数的正确使用
- 特殊操作（支付/取消）的子路径设计
"""

import json
import threading
import time
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse, parse_qs


# ─── 模拟数据 ──────────────────────────────────────────────────────────────────
USERS = {
    1: {"id": 1, "name": "Alice", "role": "admin"},
    2: {"id": 2, "name": "Bob",   "role": "user"},
}

ORDERS = {
    101: {"id": 101, "user_id": 1, "amount": 299, "status": "pending"},
    102: {"id": 102, "user_id": 1, "amount": 59,  "status": "paid"},
    103: {"id": 103, "user_id": 2, "amount": 199, "status": "pending"},
}


class URLDemoHandler(BaseHTTPRequestHandler):
    """
    演示以下 URL 结构：
      GET  /users                          集合：获取所有用户
      GET  /users/{id}                     单体：获取指定用户
      GET  /users/{id}/orders              嵌套：用户的订单列表
      GET  /users/{id}/orders/{orderId}    嵌套：用户的指定订单
      POST /orders/{id}/pay                特殊操作：支付订单
      POST /orders/{id}/cancel             特殊操作：取消订单
    """

    def log_message(self, format, *args):
        pass

    def send_json(self, status: int, data: dict):
        body = json.dumps(data, ensure_ascii=False).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.end_headers()
        self.wfile.write(body)

    def route(self):
        """解析路由，返回 (parts, query_params)"""
        parsed = urlparse(self.path)
        parts = [p for p in parsed.path.split("/") if p]
        query = parse_qs(parsed.query)
        return parts, query

    def do_GET(self):
        parts, query = self.route()

        # GET /users
        if parts == ["users"]:
            role_filter = query.get("role", [None])[0]
            users = list(USERS.values())
            if role_filter:
                users = [u for u in users if u["role"] == role_filter]
            self.send_json(200, {"code": 0, "data": users})

        # GET /users/{id}
        elif len(parts) == 2 and parts[0] == "users":
            uid = int(parts[1])
            user = USERS.get(uid)
            if user:
                self.send_json(200, {"code": 0, "data": user})
            else:
                self.send_json(404, {"code": 40401, "message": "用户不存在"})

        # GET /users/{id}/orders
        elif len(parts) == 3 and parts[0] == "users" and parts[2] == "orders":
            uid = int(parts[1])
            if uid not in USERS:
                self.send_json(404, {"code": 40401, "message": "用户不存在"})
                return
            user_orders = [o for o in ORDERS.values() if o["user_id"] == uid]
            self.send_json(200, {"code": 0, "data": user_orders})

        # GET /users/{id}/orders/{orderId}
        elif len(parts) == 4 and parts[0] == "users" and parts[2] == "orders":
            uid = int(parts[1])
            oid = int(parts[3])
            order = ORDERS.get(oid)
            if order and order["user_id"] == uid:
                self.send_json(200, {"code": 0, "data": order})
            else:
                self.send_json(404, {"code": 40402, "message": "订单不存在"})

        else:
            self.send_json(404, {"code": 40400, "message": "接口不存在"})

    def do_POST(self):
        parts, _ = self.route()

        # POST /orders/{id}/pay（特殊操作：子路径用动名词）
        if len(parts) == 3 and parts[0] == "orders" and parts[2] == "pay":
            oid = int(parts[1])
            order = ORDERS.get(oid)
            if not order:
                self.send_json(404, {"code": 40402, "message": "订单不存在"})
                return
            if order["status"] == "paid":
                self.send_json(400, {"code": 40001, "message": "订单已支付"})
                return
            order["status"] = "paid"
            self.send_json(200, {"code": 0, "message": "支付成功", "data": order})

        # POST /orders/{id}/cancel（特殊操作：子路径用动名词）
        elif len(parts) == 3 and parts[0] == "orders" and parts[2] == "cancel":
            oid = int(parts[1])
            order = ORDERS.get(oid)
            if not order:
                self.send_json(404, {"code": 40402, "message": "订单不存在"})
                return
            if order["status"] == "cancelled":
                self.send_json(400, {"code": 40002, "message": "订单已取消"})
                return
            order["status"] = "cancelled"
            self.send_json(200, {"code": 0, "message": "取消成功", "data": order})

        else:
            self.send_json(404, {"code": 40400, "message": "接口不存在"})


def demo_url_client():
    import http.client

    time.sleep(0.3)
    conn = http.client.HTTPConnection("localhost", 8302)

    def get(path):
        conn.request("GET", path)
        resp = conn.getresponse()
        return resp.status, json.loads(resp.read().decode())

    def post(path):
        conn.request("POST", path, b"", {})
        resp = conn.getresponse()
        return resp.status, json.loads(resp.read().decode())

    print("\n" + "=" * 60)
    print("        URL 命名规范 Demo")
    print("=" * 60)

    print("\n【规范对照表】")
    rules = [
        ("用名词，不用动词", "GET /users", "POST /getUsers"),
        ("复数表示集合", "GET /users", "GET /user"),
        ("小写+连字符", "GET /product-categories", "GET /productCategories"),
        ("层级表资源关系", "GET /users/1/orders", "GET /getOrdersByUserId?uid=1"),
        ("查询参数做过滤", "GET /users?role=admin", "GET /users/admin"),
        ("特殊操作用子路径", "POST /orders/101/pay", "POST /payOrder"),
    ]
    for desc, good, bad in rules:
        print(f"  ✅ {good:<35} ❌ {bad}  ({desc})")

    print("\n─── 1. GET /users（集合）─────────────────────────")
    status, data = get("/users")
    print(f"  HTTP {status} → {data['data']}")

    print("\n─── 2. GET /users?role=admin（查询参数过滤）─────")
    status, data = get("/users?role=admin")
    print(f"  HTTP {status} → role=admin 的用户：{data['data']}")

    print("\n─── 3. GET /users/1（路径参数获取单体）──────────")
    status, data = get("/users/1")
    print(f"  HTTP {status} → {data['data']}")

    print("\n─── 4. GET /users/1/orders（嵌套资源）───────────")
    status, data = get("/users/1/orders")
    print(f"  HTTP {status} → 用户1的订单：")
    for o in data["data"]:
        print(f"    - 订单#{o['id']}: ¥{o['amount']} ({o['status']})")

    print("\n─── 5. GET /users/1/orders/102（嵌套单体）───────")
    status, data = get("/users/1/orders/102")
    print(f"  HTTP {status} → {data['data']}")

    print("\n─── 6. POST /orders/101/pay（特殊操作：支付）────")
    status, data = post("/orders/101/pay")
    print(f"  HTTP {status} → {data['message']}，状态：{data['data']['status']}")

    print("\n─── 7. POST /orders/101/pay（重复支付，应报错）──")
    status, data = post("/orders/101/pay")
    print(f"  HTTP {status} → code={data['code']}: {data['message']}")

    print("\n─── 8. POST /orders/103/cancel（取消订单）───────")
    status, data = post("/orders/103/cancel")
    print(f"  HTTP {status} → {data['message']}，状态：{data['data']['status']}")

    print("\n" + "=" * 60)
    print("  URL 命名规范七条总结：")
    print("  1. 名词（复数）不含动词")
    print("  2. 小写字母 + 连字符（kebab-case）")
    print("  3. 层级嵌套不超过 2 层")
    print("  4. 路径参数 = 标识资源，查询参数 = 过滤/搜索")
    print("  5. 特殊操作用子路径动名词（pay/cancel/publish）")
    print("  6. 统一 /api 前缀")
    print("  7. 不含文件扩展名（.json/.xml）")
    print("=" * 60)

    conn.close()


def main():
    server = HTTPServer(("localhost", 8302), URLDemoHandler)
    t = threading.Thread(target=server.serve_forever, daemon=True)
    t.start()
    demo_url_client()


if __name__ == "__main__":
    main()
