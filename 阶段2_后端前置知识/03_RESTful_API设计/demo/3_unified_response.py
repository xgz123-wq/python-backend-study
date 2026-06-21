"""
Demo 3: 统一响应格式
演示统一响应格式的设计与实现

对应理论文档：3.统一响应格式.md

演示内容：
- 统一响应格式封装（code / message / data）
- HTTP 状态码 + 业务 code 双层设计
- 成功响应 vs 错误响应的不同格式
- 分页响应格式
- 业务错误码体系
"""

import json
import threading
import time
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse, parse_qs
from typing import Any, Optional


# ─── 统一响应格式封装 ──────────────────────────────────────────────────────────
class APIResponse:
    """
    统一响应格式：
    {
        "code": 0,          # 业务状态码，0 = 成功
        "message": "...",   # 人类可读的状态描述
        "data": ...         # 业务数据（失败时为 null）
    }
    """

    # 业务错误码常量
    SUCCESS = 0
    ERR_PARAM = 40001       # 参数错误
    ERR_DUPLICATE = 40002   # 重复/已存在
    ERR_UNAUTHORIZED = 40101  # 未认证
    ERR_FORBIDDEN = 40301   # 无权限
    ERR_USER_NOT_FOUND = 40401  # 用户不存在
    ERR_ORDER_NOT_FOUND = 40402  # 订单不存在
    ERR_SERVER = 50001       # 服务器内部错误

    @staticmethod
    def ok(data: Any = None, message: str = "success") -> dict:
        return {"code": APIResponse.SUCCESS, "message": message, "data": data}

    @staticmethod
    def created(data: Any = None, message: str = "创建成功") -> dict:
        return {"code": APIResponse.SUCCESS, "message": message, "data": data}

    @staticmethod
    def error(code: int, message: str) -> dict:
        return {"code": code, "message": message, "data": None}

    @staticmethod
    def paginate(items: list, page: int, size: int, total: int) -> dict:
        """分页响应格式"""
        total_pages = (total + size - 1) // size
        return {
            "code": APIResponse.SUCCESS,
            "message": "success",
            "data": {
                "items": items,
                "pagination": {
                    "page": page,
                    "size": size,
                    "total": total,
                    "totalPages": total_pages,
                    "hasNext": page < total_pages,
                    "hasPrev": page > 1,
                }
            }
        }


# ─── 业务错误码映射 ────────────────────────────────────────────────────────────
ERROR_CODE_MAP = {
    APIResponse.SUCCESS:           (200, "成功"),
    APIResponse.ERR_PARAM:         (400, "请求参数错误"),
    APIResponse.ERR_DUPLICATE:     (400, "数据已存在"),
    APIResponse.ERR_UNAUTHORIZED:  (401, "未登录或 Token 已过期"),
    APIResponse.ERR_FORBIDDEN:     (403, "无访问权限"),
    APIResponse.ERR_USER_NOT_FOUND:(404, "用户不存在"),
    APIResponse.ERR_ORDER_NOT_FOUND:(404, "订单不存在"),
    APIResponse.ERR_SERVER:        (500, "服务器内部错误"),
}


# ─── 模拟数据 ──────────────────────────────────────────────────────────────────
USERS = [
    {"id": i, "name": f"User{i}", "email": f"user{i}@example.com", "role": "admin" if i <= 2 else "user"}
    for i in range(1, 26)
]


class UnifiedResponseHandler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        pass

    def send_response_json(self, resp_data: dict, business_code: int = 0):
        """根据业务 code 自动映射 HTTP 状态码"""
        http_status, _ = ERROR_CODE_MAP.get(business_code, (200, ""))
        body = json.dumps(resp_data, ensure_ascii=False).encode()
        self.send_response(http_status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        parsed = urlparse(self.path)
        parts = [p for p in parsed.path.split("/") if p]
        query = parse_qs(parsed.query)

        # GET /users（带分页）
        if parts == ["users"]:
            page = int(query.get("page", [1])[0])
            size = int(query.get("size", [10])[0])

            # 参数校验
            if size > 100:
                err = APIResponse.error(APIResponse.ERR_PARAM, "size 不能超过 100")
                self.send_response_json(err, APIResponse.ERR_PARAM)
                return

            total = len(USERS)
            offset = (page - 1) * size
            items = USERS[offset: offset + size]
            resp = APIResponse.paginate(items, page, size, total)
            self.send_response_json(resp)

        # GET /users/{id}
        elif len(parts) == 2 and parts[0] == "users":
            uid = int(parts[1])
            user = next((u for u in USERS if u["id"] == uid), None)
            if user:
                resp = APIResponse.ok(user)
                self.send_response_json(resp)
            else:
                err = APIResponse.error(APIResponse.ERR_USER_NOT_FOUND, "用户不存在")
                self.send_response_json(err, APIResponse.ERR_USER_NOT_FOUND)

        # GET /error-demo（演示各种错误响应）
        elif parts == ["error-demo"]:
            error_type = query.get("type", ["user_not_found"])[0]
            if error_type == "user_not_found":
                resp = APIResponse.error(APIResponse.ERR_USER_NOT_FOUND, "用户不存在")
                self.send_response_json(resp, APIResponse.ERR_USER_NOT_FOUND)
            elif error_type == "forbidden":
                resp = APIResponse.error(APIResponse.ERR_FORBIDDEN, "无访问权限")
                self.send_response_json(resp, APIResponse.ERR_FORBIDDEN)
            elif error_type == "server_error":
                resp = APIResponse.error(APIResponse.ERR_SERVER, "服务器内部错误")
                self.send_response_json(resp, APIResponse.ERR_SERVER)
            else:
                resp = APIResponse.error(APIResponse.ERR_PARAM, f"未知的错误类型: {error_type}")
                self.send_response_json(resp, APIResponse.ERR_PARAM)

        else:
            resp = APIResponse.error(40400, "接口不存在")
            self.send_response_json(resp, 40400)

    def do_POST(self):
        parts = [p for p in urlparse(self.path).path.split("/") if p]

        # POST /users（创建用户）
        if parts == ["users"]:
            length = int(self.headers.get("Content-Length", 0))
            body = json.loads(self.rfile.read(length))

            # 参数校验
            if "name" not in body or "email" not in body:
                err = APIResponse.error(APIResponse.ERR_PARAM, "name 和 email 为必填字段")
                self.send_response_json(err, APIResponse.ERR_PARAM)
                return

            # 重复校验
            if any(u["email"] == body["email"] for u in USERS):
                err = APIResponse.error(APIResponse.ERR_DUPLICATE, f"邮箱 {body['email']} 已被注册")
                self.send_response_json(err, APIResponse.ERR_DUPLICATE)
                return

            new_user = {"id": len(USERS) + 1, **body}
            USERS.append(new_user)
            # 201 通过 HTTP 状态码直接发送（创建成功特殊处理）
            resp = APIResponse.created(new_user)
            body_bytes = json.dumps(resp, ensure_ascii=False).encode()
            self.send_response(201)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.end_headers()
            self.wfile.write(body_bytes)
        else:
            resp = APIResponse.error(40400, "接口不存在")
            self.send_response_json(resp, 40400)


def demo_unified_response_client():
    import http.client

    time.sleep(0.3)
    conn = http.client.HTTPConnection("localhost", 8303)

    def get(path):
        conn.request("GET", path)
        resp = conn.getresponse()
        return resp.status, json.loads(resp.read().decode())

    def post(path, body):
        data = json.dumps(body).encode()
        conn.request("POST", path, data, {"Content-Type": "application/json"})
        resp = conn.getresponse()
        return resp.status, json.loads(resp.read().decode())

    print("\n" + "=" * 60)
    print("       统一响应格式 Demo")
    print("=" * 60)

    print("\n【统一响应格式结构】")
    print('  成功: {"code": 0, "message": "success", "data": {...}}')
    print('  失败: {"code": 40401, "message": "用户不存在", "data": null}')

    print("\n─── 1. GET /users（分页响应）─────────────────────")
    status, data = get("/users?page=1&size=5")
    pg = data["data"]["pagination"]
    print(f"  HTTP {status} → code={data['code']}")
    print(f"  分页元数据：page={pg['page']}, size={pg['size']}, total={pg['total']}, "
          f"totalPages={pg['totalPages']}, hasNext={pg['hasNext']}")
    print(f"  本页 {len(data['data']['items'])} 条，首条：{data['data']['items'][0]['name']}")

    print("\n─── 2. GET /users（第3页）────────────────────────")
    status, data = get("/users?page=3&size=5")
    pg = data["data"]["pagination"]
    print(f"  HTTP {status} → hasPrev={pg['hasPrev']}, hasNext={pg['hasNext']}")
    print(f"  当前页用户：{[u['name'] for u in data['data']['items']]}")

    print("\n─── 3. GET /users?size=200（参数校验）────────────")
    status, data = get("/users?size=200")
    print(f"  HTTP {status} → code={data['code']}: {data['message']}")

    print("\n─── 4. GET /users/5（单个用户成功）──────────────")
    status, data = get("/users/5")
    print(f"  HTTP {status} → code={data['code']}, data={data['data']}")

    print("\n─── 5. GET /users/999（用户不存在）──────────────")
    status, data = get("/users/999")
    print(f"  HTTP {status} → code={data['code']}: {data['message']}, data={data['data']}")

    print("\n─── 6. POST /users（创建成功，HTTP 201）─────────")
    status, data = post("/users", {"name": "NewUser", "email": "new@example.com"})
    print(f"  HTTP {status} → code={data['code']}: {data['message']}, data={data['data']}")

    print("\n─── 7. POST /users（重复邮箱，业务 code 40002）──")
    status, data = post("/users", {"name": "NewUser2", "email": "new@example.com"})
    print(f"  HTTP {status} → code={data['code']}: {data['message']}")

    print("\n─── 8. POST /users（缺少必填字段，HTTP 400）─────")
    status, data = post("/users", {"name": "MissingEmail"})
    print(f"  HTTP {status} → code={data['code']}: {data['message']}")

    print("\n─── 9. 各种错误类型演示 ──────────────────────────")
    for err_type in ["forbidden", "server_error"]:
        status, data = get(f"/error-demo?type={err_type}")
        print(f"  {err_type}: HTTP {status} → code={data['code']}: {data['message']}")

    print("\n" + "=" * 60)
    print("  业务错误码设计规范：")
    print("  0      → 成功")
    print("  400xx  → 参数/请求错误（对应 HTTP 4xx）")
    print("  401xx  → 认证失败")
    print("  403xx  → 权限不足")
    print("  404xx  → 资源不存在")
    print("  500xx  → 服务器内部错误")
    print("=" * 60)

    conn.close()


def main():
    server = HTTPServer(("localhost", 8303), UnifiedResponseHandler)
    t = threading.Thread(target=server.serve_forever, daemon=True)
    t.start()
    demo_unified_response_client()


if __name__ == "__main__":
    main()
