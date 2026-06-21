"""
Demo 5: API 版本管理
演示 URL 路径版本管理的实现与迁移策略

对应理论文档：5.API版本管理.md

演示内容：
- v1 和 v2 并存（URL 路径版本）
- 破坏性变更：v1 → v2 字段命名变化、格式变化
- 弃用警告 Header（Deprecation / Sunset）
- 版本路由分发
- 对比四种版本管理方式
"""

import json
import threading
import time
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse, parse_qs


# ─── 模拟数据 ──────────────────────────────────────────────────────────────────
RAW_USERS = [
    {"id": 1, "name": "Alice",   "email": "alice@example.com",  "created_ts": 1704067200},
    {"id": 2, "name": "Bob",     "email": "bob@example.com",    "created_ts": 1704153600},
    {"id": 3, "name": "Charlie", "email": "charlie@example.com","created_ts": 1704240000},
]


def format_v1(user: dict) -> dict:
    """
    v1 响应格式（旧版本）：
    - 字段名：user_name, user_email, create_time（时间戳整数）
    - 无 role 字段
    """
    import datetime
    ts = user["created_ts"]
    create_time = datetime.datetime.utcfromtimestamp(ts).strftime("%Y-%m-%d %H:%M:%S")
    return {
        "user_id":    user["id"],
        "user_name":  user["name"],
        "user_email": user["email"],
        "create_time": create_time,   # 字符串，非 ISO 8601
    }


def format_v2(user: dict) -> dict:
    """
    v2 响应格式（新版本，破坏性变更）：
    - 字段名：id, username, email（命名更简洁）
    - created_at 使用 ISO 8601 格式（含时区）
    - 新增 avatar_url 字段
    """
    import datetime
    ts = user["created_ts"]
    created_at = datetime.datetime.utcfromtimestamp(ts).strftime("%Y-%m-%dT%H:%M:%SZ")
    return {
        "id":          user["id"],
        "username":    user["name"],           # ← 字段名变了（破坏性）
        "email":       user["email"],          # ← 字段名变了（破坏性）
        "created_at":  created_at,             # ← 格式变了（破坏性）
        "avatar_url":  None,                   # ← 新增字段（非破坏性）
    }


class VersionedAPIHandler(BaseHTTPRequestHandler):
    """
    支持以下路由：
      GET /api/v1/users         v1 用户列表
      GET /api/v1/users/{id}    v1 单个用户
      GET /api/v2/users         v2 用户列表
      GET /api/v2/users/{id}    v2 单个用户
      GET /api/users            未指定版本（默认最新版 v2）
    """

    def log_message(self, format, *args):
        pass

    def send_json(self, status: int, data: dict, extra_headers: dict = None):
        body = json.dumps(data, ensure_ascii=False).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        if extra_headers:
            for k, v in extra_headers.items():
                self.send_header(k, v)
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        parsed = urlparse(self.path)
        parts = [p for p in parsed.path.split("/") if p]

        # 路由结构: /api/{version}/users  或  /api/{version}/users/{id}
        if len(parts) >= 2 and parts[0] == "api":
            version = parts[1]          # v1 / v2 / users（无版本）
            resource_parts = parts[2:]  # 剩余路径

            # 无版本号（默认 v2）
            if version == "users":
                # /api/users 直接路由到 v2
                self._handle_users("v2", parts[1:], no_version=True)
                return

            # 有版本号
            if version in ("v1", "v2"):
                self._handle_users(version, resource_parts)
            else:
                self.send_json(400, {"code": 40001, "message": f"不支持的版本: {version}"})
        else:
            self.send_json(404, {"code": 40400, "message": "接口不存在"})

    def _handle_users(self, version: str, resource_parts: list, no_version: bool = False):
        formatter = format_v1 if version == "v1" else format_v2

        # v1 弃用警告 headers
        deprecation_headers = {}
        if version == "v1":
            deprecation_headers = {
                "Deprecation": "true",
                "Sunset": "Sun, 01 Jun 2025 00:00:00 GMT",
                "Link": '<http://localhost:8305/api/v2/users>; rel="successor-version"',
                "X-Warning": "API v1 将于 2025-06-01 下线，请迁移至 v2",
            }

        # GET /api/{v}/users
        if not resource_parts or resource_parts == ["users"]:
            items = [formatter(u) for u in RAW_USERS]
            resp = {"code": 0, "message": "success", "data": {"items": items, "total": len(items)}}
            if no_version:
                resp["_note"] = "未指定版本，默认返回 v2 格式"
            self.send_json(200, resp, deprecation_headers)

        # GET /api/{v}/users/{id}
        elif len(resource_parts) == 2 and resource_parts[0] == "users":
            uid = int(resource_parts[1])
            user = next((u for u in RAW_USERS if u["id"] == uid), None)
            if user:
                resp = {"code": 0, "message": "success", "data": formatter(user)}
                self.send_json(200, resp, deprecation_headers)
            else:
                self.send_json(404, {"code": 40401, "message": "用户不存在"}, deprecation_headers)
        else:
            self.send_json(404, {"code": 40400, "message": "接口不存在"})


def demo_versioning_client():
    import http.client

    time.sleep(0.3)
    conn = http.client.HTTPConnection("localhost", 8305)

    def get(path):
        conn.request("GET", path)
        resp = conn.getresponse()
        # 读取响应头中的弃用警告
        headers = dict(resp.getheaders())
        body = json.loads(resp.read().decode())
        return resp.status, body, headers

    print("\n" + "=" * 60)
    print("        API 版本管理 Demo")
    print("=" * 60)

    print("\n【四种版本管理方式对比】")
    print("  ✅ URL 路径版本（推荐）: GET /api/v1/users")
    print("  ⭐ 请求头版本:           GET /api/users  Headers: API-Version: 2")
    print("  ⚠  查询参数版本（不推荐）: GET /api/users?version=2")
    print("  🏢 子域名版本:           GET https://v2.api.example.com/users")

    print("\n─── 1. v1 API（旧格式）──────────────────────────")
    status, data, headers = get("/api/v1/users")
    print(f"  HTTP {status}")
    for u in data["data"]["items"]:
        print(f"    v1字段：{list(u.keys())} → {u}")

    print("\n─── 2. v1 包含弃用警告 Headers ──────────────────")
    for h in ["Deprecation", "Sunset", "X-Warning"]:
        val = headers.get(h, headers.get(h.lower(), "（未设置）"))
        print(f"    {h}: {val}")

    print("\n─── 3. v2 API（新格式，破坏性变更）─────────────")
    status, data, _ = get("/api/v2/users")
    print(f"  HTTP {status}")
    for u in data["data"]["items"]:
        print(f"    v2字段：{list(u.keys())} → {u}")

    print("\n─── 4. v1 vs v2 字段对比（同一用户）────────────")
    _, v1_data, _ = get("/api/v1/users/1")
    _, v2_data, _ = get("/api/v2/users/1")
    v1_user = v1_data["data"]
    v2_user = v2_data["data"]
    print(f"  v1: {v1_user}")
    print(f"  v2: {v2_user}")

    print("\n  破坏性变更（必须升版本）：")
    v1_fields = set(v1_user.keys())
    v2_fields = set(v2_user.keys())
    renamed = {
        "user_id → id": ("user_id" in v1_fields and "id" in v2_fields),
        "user_name → username": ("user_name" in v1_fields and "username" in v2_fields),
        "user_email → email": ("user_email" in v1_fields and "email" in v2_fields),
        "create_time → created_at (ISO格式)": ("create_time" in v1_fields and "created_at" in v2_fields),
    }
    for change, exists in renamed.items():
        print(f"    {'✅' if exists else '❌'} {change}")

    print("\n  非破坏性变更（不需要升版本）：")
    new_fields = v2_fields - v1_fields
    print(f"    ✅ 新增字段: {new_fields}")

    print("\n─── 5. 未指定版本（默认 v2）─────────────────────")
    status, data, _ = get("/api/users")
    print(f"  HTTP {status} → {data.get('_note', '')}")
    print(f"  格式：{list(data['data']['items'][0].keys())}")

    print("\n─── 6. 不支持的版本号 ────────────────────────────")
    status, data, _ = get("/api/v3/users")
    print(f"  HTTP {status} → code={data['code']}: {data['message']}")

    print("\n" + "=" * 60)
    print("  版本管理核心要点：")
    print("  1. 只有破坏性变更（删字段、改字段名/类型）才需要新版本")
    print("  2. URL 路径版本（/v1/、/v2/）最直观，首选方案")
    print("  3. 旧版本弃用时：返回 Deprecation/Sunset 响应头")
    print("  4. 旧版本给足迁移时间（移动端至少3-6个月）后再下线")
    print("  5. API 文档中明确标注 deprecated 状态")
    print("=" * 60)

    conn.close()


def main():
    server = HTTPServer(("localhost", 8305), VersionedAPIHandler)
    t = threading.Thread(target=server.serve_forever, daemon=True)
    t.start()
    demo_versioning_client()


if __name__ == "__main__":
    main()
