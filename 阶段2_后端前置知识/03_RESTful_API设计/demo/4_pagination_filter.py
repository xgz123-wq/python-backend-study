"""
Demo 4: 分页、过滤与排序
演示列表接口的三大核心能力

对应理论文档：4.分页过滤排序.md

演示内容：
- 页码分页（page + size）+ 分页元数据
- 游标分页（cursor-based pagination）
- 多条件过滤（等值、范围、模糊）
- 排序（单字段、多字段，白名单校验）
- 综合：分页 + 过滤 + 排序组合查询
"""

import json
import threading
import time
import base64
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse, parse_qs


# ─── 生成模拟数据 ──────────────────────────────────────────────────────────────
import random

random.seed(42)
PRODUCTS = [
    {
        "id": i,
        "name": f"商品{i:03d}",
        "category": random.choice(["electronics", "book", "clothing", "food"]),
        "price": round(random.uniform(9.9, 999.9), 2),
        "stock": random.randint(0, 500),
        "rating": round(random.uniform(3.0, 5.0), 1),
        "created_at": f"2024-{random.randint(1,12):02d}-{random.randint(1,28):02d}",
    }
    for i in range(1, 51)   # 50 个商品
]

# 排序字段白名单（防止 SQL 注入）
ALLOWED_SORT_FIELDS = {"id", "name", "price", "rating", "stock", "created_at"}


def apply_filters(items: list, query: dict) -> list:
    """根据查询参数过滤商品列表"""
    result = items[:]

    # 等值过滤
    if "category" in query:
        result = [p for p in result if p["category"] == query["category"][0]]

    # 范围过滤：price_gte / price_lte
    if "price_gte" in query:
        min_price = float(query["price_gte"][0])
        result = [p for p in result if p["price"] >= min_price]
    if "price_lte" in query:
        max_price = float(query["price_lte"][0])
        result = [p for p in result if p["price"] <= max_price]

    # 范围过滤：rating_gte
    if "rating_gte" in query:
        min_rating = float(query["rating_gte"][0])
        result = [p for p in result if p["rating"] >= min_rating]

    # 布尔过滤：in_stock=true（库存 > 0）
    if "in_stock" in query:
        in_stock = query["in_stock"][0].lower() == "true"
        result = [p for p in result if (p["stock"] > 0) == in_stock]

    # 模糊搜索：q=keyword（匹配 name）
    if "q" in query:
        keyword = query["q"][0].lower()
        result = [p for p in result if keyword in p["name"].lower()]

    return result


def apply_sort(items: list, sort_field: str, order: str) -> list:
    """排序，带白名单安全校验"""
    if sort_field not in ALLOWED_SORT_FIELDS:
        raise ValueError(f"不支持按 '{sort_field}' 排序，允许字段：{ALLOWED_SORT_FIELDS}")
    reverse = order.lower() == "desc"
    return sorted(items, key=lambda x: x.get(sort_field, 0), reverse=reverse)


def encode_cursor(item_id: int) -> str:
    """游标编码：将 ID 编码为 Base64"""
    return base64.b64encode(f"id:{item_id}".encode()).decode()


def decode_cursor(cursor: str) -> int:
    """游标解码：从 Base64 提取 ID"""
    raw = base64.b64decode(cursor.encode()).decode()
    return int(raw.split(":")[1])


class PaginationHandler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        pass

    def send_json(self, status: int, data: dict):
        body = json.dumps(data, ensure_ascii=False).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        parsed = urlparse(self.path)
        parts = [p for p in parsed.path.split("/") if p]
        query = parse_qs(parsed.query)

        # GET /products（页码分页 + 过滤 + 排序）
        if parts == ["products"]:
            try:
                page = int(query.get("page", [1])[0])
                size = min(int(query.get("size", [10])[0]), 50)  # 最大50
                sort = query.get("sort", ["id"])[0]
                order = query.get("order", ["asc"])[0]

                # 1. 过滤
                filtered = apply_filters(PRODUCTS, query)
                total = len(filtered)

                # 2. 排序
                sorted_items = apply_sort(filtered, sort, order)

                # 3. 分页
                offset = (page - 1) * size
                page_items = sorted_items[offset: offset + size]

                # 4. 分页元数据
                total_pages = (total + size - 1) // size if total > 0 else 1
                self.send_json(200, {
                    "code": 0,
                    "message": "success",
                    "data": {
                        "items": page_items,
                        "pagination": {
                            "page": page,
                            "size": size,
                            "total": total,
                            "totalPages": total_pages,
                            "hasNext": page < total_pages,
                            "hasPrev": page > 1,
                        }
                    }
                })
            except ValueError as e:
                self.send_json(400, {"code": 40001, "message": str(e), "data": None})

        # GET /products/cursor（游标分页）
        elif parts == ["products", "cursor"]:
            size = min(int(query.get("size", [5])[0]), 50)
            cursor = query.get("cursor", [None])[0]

            all_sorted = sorted(PRODUCTS, key=lambda x: x["id"])

            if cursor:
                last_id = decode_cursor(cursor)
                items = [p for p in all_sorted if p["id"] > last_id][:size]
            else:
                items = all_sorted[:size]

            last_item = items[-1] if items else None
            next_cursor = encode_cursor(last_item["id"]) if last_item else None
            has_next = len(items) == size and last_item is not None

            self.send_json(200, {
                "code": 0,
                "data": {
                    "items": items,
                    "pagination": {
                        "nextCursor": next_cursor if has_next else None,
                        "hasNext": has_next,
                        "size": len(items),
                    }
                }
            })

        else:
            self.send_json(404, {"code": 40400, "message": "接口不存在"})


def demo_pagination_client():
    import http.client

    time.sleep(0.3)
    conn = http.client.HTTPConnection("localhost", 8304)

    def get(path):
        conn.request("GET", path)
        resp = conn.getresponse()
        return resp.status, json.loads(resp.read().decode())

    def show_pagination(pg: dict):
        print(f"    分页: page={pg['page']}, size={pg['size']}, "
              f"total={pg['total']}, totalPages={pg['totalPages']}, "
              f"hasNext={pg['hasNext']}, hasPrev={pg['hasPrev']}")

    print("\n" + "=" * 60)
    print("     分页、过滤与排序 Demo（共50条商品数据）")
    print("=" * 60)

    print("\n─── 1. 基础分页：GET /products?page=1&size=5 ─────")
    status, data = get("/products?page=1&size=5")
    show_pagination(data["data"]["pagination"])
    print(f"    第1页商品：{[p['name'] for p in data['data']['items']]}")

    print("\n─── 2. 第2页：GET /products?page=2&size=5 ────────")
    status, data = get("/products?page=2&size=5")
    show_pagination(data["data"]["pagination"])
    print(f"    第2页商品：{[p['name'] for p in data['data']['items']]}")

    print("\n─── 3. 过滤（等值）：?category=book ─────────────")
    status, data = get("/products?category=book&size=5")
    pg = data["data"]["pagination"]
    print(f"    book 类共 {pg['total']} 条，本页：{[p['name'] for p in data['data']['items']]}")

    print("\n─── 4. 过滤（范围）：?price_gte=100&price_lte=300 ")
    status, data = get("/products?price_gte=100&price_lte=300&size=5")
    pg = data["data"]["pagination"]
    items = data["data"]["items"]
    print(f"    100~300 元共 {pg['total']} 条，价格范围：{min(p['price'] for p in items)} ~ {max(p['price'] for p in items)}")

    print("\n─── 5. 过滤（布尔）：?in_stock=true ─────────────")
    status, data = get("/products?in_stock=true&size=5")
    print(f"    有库存商品共 {data['data']['pagination']['total']} 条")

    print("\n─── 6. 过滤（模糊搜索）：?q=001 ─────────────────")
    status, data = get("/products?q=001")
    items = data["data"]["items"]
    print(f"    名称含 '001' 的商品：{[p['name'] for p in items]}")

    print("\n─── 7. 排序：?sort=price&order=desc&size=5 ───────")
    status, data = get("/products?sort=price&order=desc&size=5")
    items = data["data"]["items"]
    print(f"    价格降序前5：{[(p['name'], p['price']) for p in items]}")

    print("\n─── 8. 排序：?sort=rating&order=asc&size=5 ───────")
    status, data = get("/products?sort=rating&order=asc&size=5")
    items = data["data"]["items"]
    print(f"    评分升序前5：{[(p['name'], p['rating']) for p in items]}")

    print("\n─── 9. 综合查询（过滤+排序+分页）────────────────")
    status, data = get("/products?category=electronics&price_gte=100&sort=rating&order=desc&page=1&size=3")
    pg = data["data"]["pagination"]
    items = data["data"]["items"]
    print(f"    电子产品 ≥100元，按评分降序，第1页（共{pg['total']}条）：")
    for p in items:
        print(f"      {p['name']} | ¥{p['price']} | ★{p['rating']}")

    print("\n─── 10. 排序字段安全校验（非法字段）──────────────")
    status, data = get("/products?sort=password")
    print(f"    HTTP {status} → code={data['code']}: {data['message']}")

    print("\n─── 11. 游标分页演示（无限滚动风格）──────────────")
    status, data = get("/products/cursor?size=5")
    pg = data["data"]["pagination"]
    print(f"    第1批：{[p['name'] for p in data['data']['items']]}，hasNext={pg['hasNext']}")
    if pg["nextCursor"]:
        status2, data2 = get(f"/products/cursor?size=5&cursor={pg['nextCursor']}")
        pg2 = data2["data"]["pagination"]
        print(f"    第2批：{[p['name'] for p in data2['data']['items']]}，hasNext={pg2['hasNext']}")

    print("\n" + "=" * 60)
    print("  核心要点：")
    print("  1. 分页：page/size 参数，total 需 COUNT 全量（非当前页数量）")
    print("  2. 游标分页：适合 Feed 流，性能稳定，不支持跳页")
    print("  3. 过滤：等值/?category=x  范围/?price_gte=x  模糊/?q=kw")
    print("  4. 排序：sort + order 参数，必须白名单校验防 SQL 注入")
    print("=" * 60)

    conn.close()


def main():
    server = HTTPServer(("localhost", 8304), PaginationHandler)
    t = threading.Thread(target=server.serve_forever, daemon=True)
    t.start()
    demo_pagination_client()


if __name__ == "__main__":
    main()
