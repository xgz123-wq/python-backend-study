"""
Demo 1: 部署概念演示
=====================

对应理论：1.部署的定义与本质

本脚本演示部署的核心概念：
1. 启动本地 HTTP 服务器
2. 展示本机 IP 和公网 IP 的区别
3. 模拟"本地可访问但外部不可访问"的场景
4. 演示端口的概念

运行方式：
    python 1_deploy_concept.py

按 Ctrl+C 退出服务器。
"""

import socket
import threading
import time
import urllib.request
from http.server import HTTPServer, SimpleHTTPRequestHandler


# ============================================================
# 第 1 部分：获取本机网络信息
# ============================================================

def get_local_ip():
    """获取本机局域网 IP 地址。

    通过创建一个 UDP socket 连接外部地址来获取本机出口 IP。
    注意：UDP connect 不会真正发送数据，只是让系统选择出口网卡。
    """
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        # 连接一个外部地址（不会真正发送数据）
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "无法获取"


def get_public_ip():
    """尝试获取本机公网 IP 地址。

    通过访问外部服务来获取路由器/NAT 的公网 IP。
    如果网络不通则返回提示信息。
    """
    try:
        response = urllib.request.urlopen(
            "https://httpbin.org/ip", timeout=5
        )
        data = response.read().decode("utf-8")
        # 简单解析 JSON 获取 IP
        # 格式: {"origin": "x.x.x.x"}
        ip = data.split('"origin"')[1].split('"')[2].strip()
        return ip
    except Exception:
        return "无法获取（可能未联网或被防火墙阻止）"


def show_network_info():
    """展示本机的网络信息，帮助理解本地 vs 公网的区别。"""
    print("=" * 60)
    print("  部署概念演示：本机网络信息")
    print("=" * 60)

    # localhost 是回环地址，只有本机能访问
    print(f"\n  localhost（回环地址）:  127.0.0.1")

    # 局域网 IP，同一 Wi-Fi 下的设备可以访问
    local_ip = get_local_ip()
    print(f"  局域网 IP（内网地址）:  {local_ip}")

    # 公网 IP，全球可访问（实际上是路由器/NAT 的 IP）
    public_ip = get_public_ip()
    print(f"  公网 IP（外网地址）:    {public_ip}")

    print(f"\n  主机名:                 {socket.gethostname()}")

    print("\n" + "-" * 60)
    print("  关键理解：")
    print("  • 127.0.0.1 → 只有本机能访问")
    print("  • 局域网 IP → 同一网络下的设备能访问")
    print("  • 公网 IP  → 全球可访问（但需要端口映射）")
    print("  • 部署就是把服务暴露到公网 IP 上")
    print("-" * 60)


# ============================================================
# 第 2 部分：端口概念演示
# ============================================================

def demonstrate_ports():
    """演示端口的概念。

    端口是网络通信中的「门牌号」：
    - 一台服务器有 65535 个端口（0-65535）
    - 每个端口可以同时运行不同的服务
    - 常用端口：80（HTTP）、443（HTTPS）、22（SSH）
    """
    print("\n" + "=" * 60)
    print("  端口概念演示")
    print("=" * 60)

    # 常见端口说明
    common_ports = {
        22: "SSH（远程登录）",
        80: "HTTP（网页访问）",
        443: "HTTPS（加密网页）",
        3306: "MySQL 数据库",
        5432: "PostgreSQL 数据库",
        6379: "Redis 缓存",
        8000: "Python 开发服务器常用端口",
        8080: "备用 HTTP 端口",
    }

    print("\n  常见端口对照表：")
    print(f"  {'端口号':<8} {'用途':<30}")
    print(f"  {'------':<8} {'----':<30}")
    for port, desc in common_ports.items():
        print(f"  {port:<8} {desc}")

    # 检查本机的某些端口是否被占用
    print("\n  检查本机端口状态：")
    for port in [80, 443, 3306, 8000]:
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(1)
            result = s.connect_ex(("127.0.0.1", port))
            s.close()
            if result == 0:
                status = "✅ 已占用（有服务在监听）"
            else:
                status = "⬜ 空闲（可以使用）"
        except Exception:
            status = "❓ 无法检测"
        print(f"  端口 {port:<6} → {status}")

    print("\n  关键理解：")
    print("  • 部署时需要选择一个未被占用的端口")
    print("  • 生产环境通常使用 80（HTTP）或 443（HTTPS）")
    print("  • 开发环境通常使用 8000、8080 等非特权端口")


# ============================================================
# 第 3 部分：启动本地 HTTP 服务器
# ============================================================

class DemoHandler(SimpleHTTPRequestHandler):
    """自定义 HTTP 请求处理器。

    继承自 SimpleHTTPRequestHandler，重写部分方法以展示部署相关概念。
    """

    def do_GET(self):
        """处理 GET 请求，返回部署相关的演示信息。"""
        if self.path == "/" or self.path == "":
            # 首页：展示部署概念信息
            response = f"""<!DOCTYPE html>
<html lang="zh">
<head>
    <meta charset="utf-8">
    <title>部署概念演示</title>
    <style>
        body {{ font-family: sans-serif; max-width: 800px; margin: 50px auto; padding: 0 20px; }}
        h1 {{ color: #2c3e50; }}
        .info {{ background: #f0f0f0; padding: 15px; border-radius: 8px; margin: 10px 0; }}
        .highlight {{ background: #fff3cd; padding: 10px; border-left: 4px solid #ffc107; margin: 15px 0; }}
        code {{ background: #e8e8e8; padding: 2px 6px; border-radius: 3px; }}
    </style>
</head>
<body>
    <h1>🚀 本地 HTTP 服务器运行中</h1>

    <div class="info">
        <h3>服务器信息</h3>
        <p>服务器地址: <code>{self.server.server_address[0]}:{self.server.server_address[1]}</code></p>
        <p>请求路径: <code>{self.path}</code></p>
        <p>客户端地址: <code>{self.client_address[0]}:{self.client_address[1]}</code></p>
        <p>请求时间: <code>{time.strftime('%Y-%m-%d %H:%M:%S')}</code></p>
    </div>

    <div class="highlight">
        <h3>💡 这就是"部署"的核心</h3>
        <p>你现在看到的内容，就是一个运行中的 HTTP 服务器返回的。</p>
        <p>如果这台服务器有公网 IP，并且 24 小时运行，</p>
        <p>那么全球任何人都可以通过 <code>http://公网IP:{self.server.server_address[1]}</code> 访问这个页面。</p>
        <p><strong>这就是部署的本质。</strong></p>
    </div>

    <div class="info">
        <h3>试试这些路径</h3>
        <p><a href="/api/info">/api/info</a> - 查看服务器信息（模拟 API）</p>
        <p><a href="/api/time">/api/time</a> - 获取服务器当前时间</p>
    </div>
</body>
</html>"""
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(response.encode("utf-8"))

        elif self.path == "/api/info":
            # 模拟 API 接口
            import json
            info = {
                "server": "Python HTTP Server",
                "address": f"{self.server.server_address[0]}:{self.server.server_address[1]}",
                "message": "这是一个模拟的 API 接口，部署后会变成真正的后端服务",
            }
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.end_headers()
            self.wfile.write(json.dumps(info, ensure_ascii=False, indent=2).encode("utf-8"))

        elif self.path == "/api/time":
            # 模拟时间接口
            import json
            data = {
                "server_time": time.strftime("%Y-%m-%d %H:%M:%S"),
                "timestamp": time.time(),
                "note": "生产环境中，这个接口可能用于同步时间、验证服务存活等",
            }
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.end_headers()
            self.wfile.write(json.dumps(data, ensure_ascii=False, indent=2).encode("utf-8"))

        else:
            self.send_response(404)
            self.send_header("Content-Type", "text/plain; charset=utf-8")
            self.end_headers()
            self.wfile.write(f"404 - 路径 {self.path} 不存在".encode("utf-8"))

    def log_message(self, format, *args):
        """自定义日志格式，展示请求信息。"""
        print(f"  [请求] {self.client_address[0]} - {format % args}")


def start_server(host="127.0.0.1", port=8000):
    """启动本地 HTTP 服务器。

    Args:
        host: 监听地址，127.0.0.1 表示只接受本机连接
        port: 监听端口
    """
    server = HTTPServer((host, port), DemoHandler)
    print(f"\n  ✅ 服务器已启动！")
    print(f"  📍 访问地址: http://{host}:{port}")
    print(f"  🛑 按 Ctrl+C 停止服务器\n")
    print(f"  等待请求中...")
    print(f"  {'─' * 50}")

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print(f"\n  {'─' * 50}")
        print(f"  ⏹️  服务器已停止")
        server.server_close()


# ============================================================
# 第 4 部分：演示"本地可访问 vs 外部不可访问"
# ============================================================

def demonstrate_accessibility():
    """演示本地可访问但外部不可访问的概念。"""
    print("\n" + "=" * 60)
    print("  本地 vs 外部访问演示")
    print("=" * 60)

    print("\n  场景：你在本地启动了一个 HTTP 服务器")
    print("  问：谁可以访问？\n")

    local_ip = get_local_ip()

    access_table = [
        ("你自己（本机）", "http://127.0.0.1:8000", "✅ 可以访问"),
        ("同 Wi-Fi 的手机", f"http://{local_ip}:8000", "⚠️ 可能可以（取决于防火墙）"),
        ("隔壁城市的朋友", f"http://{get_public_ip()}:8000", "❌ 无法访问（需要端口映射）"),
        ("全球用户", "http://yourdomain.com", "❌ 无法访问（需要部署到服务器）"),
    ]

    print(f"  {'访问者':<20} {'尝试访问的地址':<35} {'结果':<25}")
    print(f"  {'------':<20} {'----------':<35} {'----':<25}")
    for who, addr, result in access_table:
        print(f"  {who:<20} {addr:<35} {result}")

    print("\n  关键理解：")
    print("  • 本地开发的服务默认只有自己能访问")
    print("  • 要让外部访问，需要：")
    print("    1. 部署到有公网 IP 的服务器")
    print("    2. 或者配置路由器的端口映射（不推荐）")
    print("    3. 或者使用内网穿透工具（ngrok、frp 等）")


# ============================================================
# 主程序
# ============================================================

def main():
    """主程序入口，依次运行各个演示部分。"""
    print("\n" + "█" * 60)
    print("  部署概览 Demo 1：部署的定义与本质")
    print("█" * 60)

    # 第 1 部分：网络信息
    show_network_info()

    # 第 2 部分：端口概念
    demonstrate_ports()

    # 第 3 部分：本地 vs 外部访问
    demonstrate_accessibility()

    # 第 4 部分：启动本地服务器
    print("\n" + "=" * 60)
    print("  接下来将启动一个本地 HTTP 服务器")
    print("  请在浏览器中打开 http://127.0.0.1:8000")
    print("=" * 60)

    input("\n  按 Enter 启动服务器（Ctrl+C 退出）...")

    start_server(host="127.0.0.1", port=8000)


if __name__ == "__main__":
    main()
