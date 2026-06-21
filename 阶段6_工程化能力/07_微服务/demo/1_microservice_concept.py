"""
演示脚本：微服务架构概念

本脚本用 Python 模拟微服务架构的核心概念，包括：
1. 两个微服务：用户服务 + 订单服务
2. 服务注册与发现机制
3. API 网关的角色
4. 服务间调用链追踪

⚠️ 这是概念演示，不是生产级实现。
    实际微服务使用 Flask/FastAPI + 注册中心（Consul/Nacos）等工具。

运行方式：
    python 1_microservice_concept.py
"""

import json
import time
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse
from urllib.request import urlopen, Request
from urllib.error import URLError


# ============================================================
# 第一部分：模拟服务注册中心
# ============================================================

class ServiceRegistry:
    """
    模拟服务注册中心（类似 Consul、Eureka、Nacos）

    在真实的微服务架构中：
    - 每个服务启动时向注册中心注册自己的地址
    - 其他服务通过注册中心查询目标服务的地址
    - 注册中心还会做健康检查，剔除不健康的服务实例
    """

    def __init__(self):
        # 存储格式：{服务名: [{地址、端口、状态、注册时间}, ...]}
        self._services = {}
        self._lock = threading.Lock()

    def register(self, service_name, host, port):
        """服务注册：服务启动时调用"""
        with self._lock:
            if service_name not in self._services:
                self._services[service_name] = []

            instance = {
                "host": host,
                "port": port,
                "status": "UP",
                "registered_at": time.time(),
            }
            self._services[service_name].append(instance)
            print(f"  [注册中心] 服务已注册: {service_name} @ {host}:{port}")

    def discover(self, service_name):
        """
        服务发现：获取某个服务的所有可用实例地址

        真实场景中，这里还会做负载均衡（轮询、随机、加权等）
        """
        with self._lock:
            instances = self._services.get(service_name, [])
            # 只返回状态为 UP 的实例
            available = [
                inst for inst in instances if inst["status"] == "UP"
            ]
            if not available:
                return None
            # 简单策略：返回第一个可用实例
            return available[0]

    def deregister(self, service_name, host, port):
        """服务注销：服务关闭时调用"""
        with self._lock:
            if service_name in self._services:
                self._services[service_name] = [
                    inst for inst in self._services[service_name]
                    if not (inst["host"] == host and inst["port"] == port)
                ]
                print(f"  [注册中心] 服务已注销: {service_name} @ {host}:{port}")

    def list_all(self):
        """列出所有已注册的服务"""
        with self._lock:
            return {
                name: [
                    f"{inst['host']}:{inst['port']} ({inst['status']})"
                    for inst in instances
                ]
                for name, instances in self._services.items()
            }


# 全局注册中心实例（真实场景中是独立的分布式服务）
registry = ServiceRegistry()


# ============================================================
# 第二部分：模拟用户服务（User Service）
# ============================================================

# 模拟用户数据库
USER_DB = {
    1: {"id": 1, "name": "张三", "email": "zhangsan@example.com", "age": 28},
    2: {"id": 2, "name": "李四", "email": "lisi@example.com", "age": 32},
    3: {"id": 3, "name": "王五", "email": "wangwu@example.com", "age": 25},
}


class UserServiceHandler(BaseHTTPRequestHandler):
    """
    用户服务的 HTTP 处理器

    提供两个接口：
    - GET /users         → 获取所有用户
    - GET /users/<id>    → 获取单个用户
    """

    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path

        if path == "/users":
            # 获取所有用户
            self._send_json(200, list(USER_DB.values()))
        elif path.startswith("/users/"):
            # 获取单个用户
            try:
                user_id = int(path.split("/")[-1])
                user = USER_DB.get(user_id)
                if user:
                    self._send_json(200, user)
                else:
                    self._send_json(404, {"error": f"用户 {user_id} 不存在"})
            except ValueError:
                self._send_json(400, {"error": "无效的用户 ID"})
        elif path == "/health":
            # 健康检查接口（注册中心用）
            self._send_json(200, {"status": "UP", "service": "user-service"})
        else:
            self._send_json(404, {"error": "路径不存在"})

    def _send_json(self, status_code, data):
        """发送 JSON 响应"""
        self.send_response(status_code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.end_headers()
        self.wfile.write(json.dumps(data, ensure_ascii=False).encode("utf-8"))

    def log_message(self, format, *args):
        """自定义日志格式"""
        print(f"  [用户服务] {args[0]}")


# ============================================================
# 第三部分：模拟订单服务（Order Service）
# ============================================================

# 模拟订单数据库
ORDER_DB = {
    101: {"id": 101, "user_id": 1, "product": "Python 编程书", "amount": 59.9},
    102: {"id": 102, "user_id": 2, "product": "机械键盘", "amount": 399.0},
    103: {"id": 103, "user_id": 1, "product": "显示器", "amount": 1299.0},
}


class OrderServiceHandler(BaseHTTPRequestHandler):
    """
    订单服务的 HTTP 处理器

    提供两个接口：
    - GET /orders           → 获取所有订单
    - GET /orders/<id>/full → 获取订单详情（包含用户信息，需要调用用户服务）

    重点：/orders/<id>/full 展示了服务间的调用链
    """

    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path

        if path == "/orders":
            self._send_json(200, list(ORDER_DB.values()))

        elif path.endswith("/full"):
            # 获取订单详情 — 需要调用用户服务获取用户信息
            # 这里展示了服务间调用的核心概念
            try:
                order_id = int(path.split("/")[-2])
                order = ORDER_DB.get(order_id)
                if not order:
                    self._send_json(404, {"error": f"订单 {order_id} 不存在"})
                    return

                # ★ 关键步骤：通过注册中心发现用户服务的地址
                user_service = registry.discover("user-service")
                if not user_service:
                    self._send_json(503, {"error": "用户服务不可用"})
                    return

                # ★ 调用用户服务获取用户信息
                user_url = (
                    f"http://{user_service['host']}:{user_service['port']}"
                    f"/users/{order['user_id']}"
                )
                try:
                    req = Request(user_url)
                    with urlopen(req, timeout=3) as resp:
                        user_data = json.loads(resp.read().decode("utf-8"))
                except URLError:
                    self._send_json(503, {"error": "调用用户服务失败"})
                    return

                # 组合订单 + 用户信息返回
                full_order = {
                    **order,
                    "user": user_data,
                }
                self._send_json(200, full_order)

            except (ValueError, IndexError):
                self._send_json(400, {"error": "无效的请求"})
        else:
            self._send_json(404, {"error": "路径不存在"})

    def _send_json(self, status_code, data):
        self.send_response(status_code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.end_headers()
        self.wfile.write(json.dumps(data, ensure_ascii=False).encode("utf-8"))

    def log_message(self, format, *args):
        print(f"  [订单服务] {args[0]}")


# ============================================================
# 第四部分：模拟 API 网关
# ============================================================

class APIGatewayHandler(BaseHTTPRequestHandler):
    """
    API 网关处理器

    职责：
    1. 路由：将请求转发到对应的微服务
    2. 认证：验证请求是否合法（这里简化为检查 API Key）
    3. 日志：记录所有请求
    4. 聚合：将多个服务的数据组合后返回
    """

    # 路由规则：URL 前缀 → 服务名
    ROUTES = {
        "/api/users": "user-service",
        "/api/orders": "order-service",
    }

    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path

        # ★ 认证检查（模拟）
        api_key = self.headers.get("X-API-Key", "")
        if path != "/api/health" and api_key != "demo-key-123":
            self._send_json(401, {"error": "认证失败：无效的 API Key"})
            return

        # ★ 路由匹配
        target_service = None
        for prefix, service_name in self.ROUTES.items():
            if path.startswith(prefix):
                target_service = service_name
                # 去掉 /api 前缀，转发给目标服务
                # 例如：/api/users/1 → /users/1
                forward_path = path[len("/api"):]
                break

        if not target_service:
            # 特殊路由：/api/dashboard 聚合多个服务的数据
            if path == "/api/dashboard":
                self._handle_dashboard()
                return
            self._send_json(404, {"error": "路由不存在"})
            return

        # ★ 通过注册中心发现服务地址
        service = registry.discover(target_service)
        if not service:
            self._send_json(503, {"error": f"服务 {target_service} 不可用"})
            return

        # ★ 转发请求到目标服务
        target_url = f"http://{service['host']}:{service['port']}{forward_path}"
        try:
            req = Request(target_url)
            with urlopen(req, timeout=3) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                self._send_json(200, data)
        except URLError:
            self._send_json(502, {"error": f"调用 {target_service} 失败"})

    def _handle_dashboard(self):
        """
        聚合接口：从多个服务获取数据并组合

        这是 API 网关的典型用途之一 —— 数据聚合
        客户端一次请求就能获取仪表盘所需的全部数据
        """
        result = {}

        # 从用户服务获取用户列表
        user_service = registry.discover("user-service")
        if user_service:
            try:
                url = f"http://{user_service['host']}:{user_service['port']}/users"
                with urlopen(url, timeout=3) as resp:
                    result["users"] = json.loads(resp.read().decode("utf-8"))
            except URLError:
                result["users"] = []
        else:
            result["users"] = []

        # 从订单服务获取订单列表
        order_service = registry.discover("order-service")
        if order_service:
            try:
                url = f"http://{order_service['host']}:{order_service['port']}/orders"
                with urlopen(url, timeout=3) as resp:
                    result["orders"] = json.loads(resp.read().decode("utf-8"))
            except URLError:
                result["orders"] = []
        else:
            result["orders"] = []

        result["total_users"] = len(result["users"])
        result["total_orders"] = len(result["orders"])

        self._send_json(200, result)

    def _send_json(self, status_code, data):
        self.send_response(status_code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.end_headers()
        self.wfile.write(json.dumps(data, ensure_ascii=False).encode("utf-8"))

    def log_message(self, format, *args):
        print(f"  [API网关]  {args[0]}")


# ============================================================
# 第五部分：启动服务并演示
# ============================================================

def start_service(name, handler_class, port):
    """在后台线程启动一个 HTTP 服务"""
    server = HTTPServer(("127.0.0.1", port), handler_class)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    # 向注册中心注册
    registry.register(name, "127.0.0.1", port)
    return server


def http_get(url, headers=None):
    """发送 HTTP GET 请求并返回 JSON"""
    req = Request(url)
    if headers:
        for key, value in headers.items():
            req.add_header(key, value)
    try:
        with urlopen(req, timeout=3) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except Exception as e:
        return {"error": str(e)}


def print_separator(title):
    """打印分隔线和标题"""
    print(f"\n{'=' * 60}")
    print(f"  {title}")
    print(f"{'=' * 60}")


def demo():
    """主演示流程"""
    print_separator("微服务架构概念演示")
    print()
    print("本演示模拟了一个简化的微服务系统，包含：")
    print("  - 用户服务 (端口 8001)")
    print("  - 订单服务 (端口 8002)")
    print("  - API 网关 (端口 8080)")
    print("  - 服务注册中心 (内存)")

    # ── 步骤 1：启动微服务 ──
    print_separator("步骤 1：启动微服务并注册")
    print()

    user_server = start_service("user-service", UserServiceHandler, 8001)
    order_server = start_service("order-service", OrderServiceHandler, 8002)
    gateway_server = start_service("api-gateway", APIGatewayHandler, 8080)

    time.sleep(0.5)  # 等待服务启动

    print()
    print("当前注册的服务：")
    for name, instances in registry.list_all().items():
        for inst in instances:
            print(f"  - {name}: {inst}")

    # ── 步骤 2：直接调用微服务（绕过网关）──
    print_separator("步骤 2：直接调用微服务（不经过网关）")
    print()

    print("→ 直接调用用户服务 GET /users：")
    users = http_get("http://127.0.0.1:8001/users")
    print(f"  结果: {json.dumps(users, ensure_ascii=False, indent=4)}")

    print()
    print("→ 直接调用订单服务 GET /orders：")
    orders = http_get("http://127.0.0.1:8002/orders")
    print(f"  结果: {json.dumps(orders, ensure_ascii=False, indent=4)}")

    # ── 步骤 3：通过 API 网关调用 ──
    print_separator("步骤 3：通过 API 网关调用（带认证）")
    print()

    # 不带 API Key 的请求会被拒绝
    print("→ 不带 API Key 请求网关（应该被拒绝）：")
    result = http_get("http://127.0.0.1:8080/api/users")
    print(f"  结果: {result}")

    print()
    print("→ 带 API Key 请求网关 GET /api/users：")
    result = http_get(
        "http://127.0.0.1:8080/api/users",
        headers={"X-API-Key": "demo-key-123"},
    )
    print(f"  结果: {json.dumps(result, ensure_ascii=False, indent=4)}")

    # ── 步骤 4：服务间调用链演示 ──
    print_separator("步骤 4：服务间调用链（订单服务 → 用户服务）")
    print()
    print("当请求订单详情时，订单服务需要调用用户服务获取用户信息：")
    print("  客户端 → 订单服务 → 用户服务")
    print()

    print("→ 直接调用订单服务 GET /orders/101/full：")
    result = http_get("http://127.0.0.1:8002/orders/101/full")
    print(f"  结果: {json.dumps(result, ensure_ascii=False, indent=4)}")
    print()
    print("  ↑ 注意：订单信息中包含了从用户服务获取的用户详情")
    print("    这就是微服务之间的调用链！")

    # ── 步骤 5：API 网关的数据聚合 ──
    print_separator("步骤 5：API 网关数据聚合")
    print()
    print("网关可以同时从多个服务获取数据，组合后返回给客户端：")
    print()

    result = http_get(
        "http://127.0.0.1:8080/api/dashboard",
        headers={"X-API-Key": "demo-key-123"},
    )
    print(f"→ GET /api/dashboard 结果：")
    print(f"  用户数: {result.get('total_users', 0)}")
    print(f"  订单数: {result.get('total_orders', 0)}")
    print(f"  完整数据: {json.dumps(result, ensure_ascii=False, indent=4)}")

    # ── 步骤 6：服务发现演示 ──
    print_separator("步骤 6：服务发现机制")
    print()
    print("服务发现的核心流程：")
    print("  1. 服务启动时，向注册中心注册自己的地址")
    print("  2. 调用方通过注册中心查询目标服务的地址")
    print("  3. 注册中心可以做健康检查，剔除故障服务")
    print()
    print("模拟服务注销（如用户服务下线）：")

    registry.deregister("user-service", "127.0.0.1", 8001)
    print()
    print("当前注册的服务：")
    for name, instances in registry.list_all().items():
        for inst in instances:
            print(f"  - {name}: {inst}")

    print()
    print("→ 用户服务下线后，再请求订单详情（应该失败）：")
    result = http_get("http://127.0.0.1:8002/orders/101/full")
    print(f"  结果: {result}")
    print()
    print("  ↑ 订单服务调用用户服务失败，返回 503 错误")
    print("    这就是为什么需要熔断机制来优雅处理这种故障！")

    # ── 关闭服务 ──
    print_separator("清理：关闭所有服务")
    user_server.shutdown()
    order_server.shutdown()
    gateway_server.shutdown()
    print("  所有服务已关闭")

    # ── 总结 ──
    print_separator("总结：微服务架构核心概念")
    print("""
本演示展示了以下核心概念：

1. 微服务拆分
   - 用户服务和订单服务是独立的的服务，各有自己的数据库
   - 每个服务可以独立部署和扩展

2. 服务注册与发现
   - 服务启动时注册到注册中心
   - 调用方通过注册中心获取目标服务的地址
   - 服务下线后注册中心会更新状态

3. API 网关
   - 统一入口，处理路由、认证、日志
   - 可以聚合多个服务的数据

4. 服务间调用
   - 订单服务调用用户服务获取用户信息
   - 调用链路：客户端 → 网关 → 订单服务 → 用户服务

5. 故障场景
   - 用户服务下线后，依赖它的订单服务也会受影响
   - 这就是为什么需要熔断、重试、降级等容错机制

实际生产环境中，还需要：
  - 注册中心：Consul、Eureka、Nacos
  - API 网关：Kong、Nginx、Traefik
  - 链路追踪：Jaeger、Zipkin
  - 熔断限流：Hystrix、Sentinel
  - 配置中心：Apollo、Nacos
""")


if __name__ == "__main__":
    demo()
