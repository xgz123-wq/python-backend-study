"""
Demo 3: 三个部署层次
=====================

对应理论：3.部署的三个层次

本脚本演示部署的三个层次：
1. 静态部署：生成 HTML 文件，用 Python HTTP 服务器托管
2. 应用部署：启动带 API 路由的后端服务
3. 容器化部署：展示 Dockerfile 模板（仅打印，不执行）

运行方式：
    python 3_deploy_levels.py
"""

import json
import os
import tempfile
import threading
import time
from http.server import HTTPServer, BaseHTTPRequestHandler


# ============================================================
# 第 1 部分：静态部署演示
# ============================================================

def demo_static_deploy():
    """演示静态部署：生成 HTML 文件并用 HTTP 服务器托管。

    静态部署是最简单的部署方式，只需要托管预先生成的文件。
    典型场景：个人博客、文档站点、前端 SPA 应用。
    """
    print("\n" + "=" * 60)
    print("  第 1 部分：静态部署演示")
    print("=" * 60)

    # 创建临时目录来存放静态文件
    static_dir = tempfile.mkdtemp(prefix="static_deploy_")
    print(f"\n  创建静态文件目录: {static_dir}")

    # 生成一个示例 HTML 文件
    html_content = """<!DOCTYPE html>
<html lang="zh">
<head>
    <meta charset="utf-8">
    <title>我的静态网站</title>
    <style>
        body {
            font-family: -apple-system, sans-serif;
            max-width: 600px;
            margin: 50px auto;
            padding: 0 20px;
            background: #f5f5f5;
        }
        .card {
            background: white;
            padding: 30px;
            border-radius: 12px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        h1 { color: #2c3e50; }
        .badge {
            display: inline-block;
            background: #27ae60;
            color: white;
            padding: 4px 12px;
            border-radius: 20px;
            font-size: 14px;
        }
    </style>
</head>
<body>
    <div class="card">
        <h1>Hello from Static Site!</h1>
        <p><span class="badge">静态部署</span></p>
        <p>这是一个纯静态网页，不需要任何后端逻辑。</p>
        <p>服务器只需要找到这个文件并原样返回。</p>
        <hr>
        <p><strong>静态部署的特点：</strong></p>
        <ul>
            <li>零计算开销 — 只返回文件</li>
            <li>极快的响应速度</li>
            <li>天然支持高并发</li>
            <li>可以免费托管（GitHub Pages、Vercel）</li>
        </ul>
        <p style="color: #999; font-size: 12px;">
            生成时间: """ + time.strftime("%Y-%m-%d %H:%M:%S") + """
        </p>
    </div>
</body>
</html>"""

    # 写入 index.html
    index_path = os.path.join(static_dir, "index.html")
    with open(index_path, "w", encoding="utf-8") as f:
        f.write(html_content)

    # 生成一个 about.html
    about_html = """<!DOCTYPE html>
<html lang="zh">
<head><meta charset="utf-8"><title>关于</title></head>
<body>
    <h1>关于页面</h1>
    <p>这是静态网站的第二个页面。</p>
    <p><a href="/">返回首页</a></p>
</body>
</html>"""
    about_path = os.path.join(static_dir, "about.html")
    with open(about_path, "w", encoding="utf-8") as f:
        f.write(about_html)

    print(f"  ✅ 生成 index.html ({len(html_content)} bytes)")
    print(f"  ✅ 生成 about.html ({len(about_html)} bytes)")

    # 列出目录内容
    print(f"\n  静态文件目录结构：")
    print(f"  {static_dir}/")
    for f in os.listdir(static_dir):
        size = os.path.getsize(os.path.join(static_dir, f))
        print(f"  ├── {f}  ({size} bytes)")

    print(f"\n  📋 静态部署流程：")
    print(f"  1. 编写/生成 HTML 文件 ✅（已完成）")
    print(f"  2. 上传到托管平台")
    print(f"     - GitHub Pages: git push 到仓库")
    print(f"     - Vercel: vercel 命令部署")
    print(f"     - 本地模拟: python -m http.server")
    print(f"  3. 用户通过 URL 访问")

    # 启动简单的静态服务器
    print(f"\n  启动本地静态文件服务器...")

    os.chdir(static_dir)
    server = HTTPServer(("127.0.0.1", 0), StaticFileHandler)
    port = server.server_address[1]

    server_thread = threading.Thread(target=server.handle_request)
    server_thread.daemon = True
    server_thread.start()

    print(f"  ✅ 静态服务器运行在 http://127.0.0.1:{port}")
    print(f"  💡 实际部署时，这些文件会托管在 CDN 上")

    # 模拟请求
    try:
        import urllib.request
        response = urllib.request.urlopen(f"http://127.0.0.1:{port}/index.html", timeout=3)
        print(f"  ✅ 模拟请求成功: 状态码 {response.status}, 响应 {len(response.read())} bytes")
    except Exception as e:
        print(f"  ⚠️ 模拟请求: {e}")

    server.server_close()

    print(f"\n  常见静态部署平台：")
    print(f"  ┌──────────────────┬──────────┬──────────────────┐")
    print(f"  │ 平台             │ 费用     │ 特点             │")
    print(f"  ├──────────────────┼──────────┼──────────────────┤")
    print(f"  │ GitHub Pages     │ 免费     │ 与 Git 集成      │")
    print(f"  │ Vercel           │ 免费     │ 自动构建+CDN     │")
    print(f"  │ Netlify          │ 免费     │ 表单+函数        │")
    print(f"  │ Cloudflare Pages │ 免费     │ 无限带宽         │")
    print(f"  └──────────────────┴──────────┴──────────────────┘")


class StaticFileHandler(BaseHTTPRequestHandler):
    """简单的静态文件处理器。"""

    def do_GET(self):
        """处理 GET 请求，返回对应的静态文件。"""
        # 默认返回 index.html
        if self.path == "/":
            self.path = "/index.html"

        file_path = os.path.join(os.getcwd(), self.path.lstrip("/"))

        if os.path.isfile(file_path):
            with open(file_path, "rb") as f:
                content = f.read()
            self.send_response(200)
            # 根据扩展名设置 Content-Type
            if file_path.endswith(".html"):
                self.send_header("Content-Type", "text/html; charset=utf-8")
            elif file_path.endswith(".css"):
                self.send_header("Content-Type", "text/css")
            elif file_path.endswith(".js"):
                self.send_header("Content-Type", "application/javascript")
            else:
                self.send_header("Content-Type", "application/octet-stream")
            self.send_header("Content-Length", str(len(content)))
            self.end_headers()
            self.wfile.write(content)
        else:
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b"404 Not Found")

    def log_message(self, format, *args):
        """静默日志。"""
        pass


# ============================================================
# 第 2 部分：应用部署演示
# ============================================================

def demo_app_deploy():
    """演示应用部署：启动一个带 API 路由的后端服务。

    应用部署是最常见的后端部署方式，需要运行服务器端代码，
    处理业务逻辑、数据库查询等。
    """
    print("\n" + "=" * 60)
    print("  第 2 部分：应用部署演示")
    print("=" * 60)

    print(f"\n  启动一个模拟的后端 API 服务...")

    # 启动 API 服务器
    server = HTTPServer(("127.0.0.1", 0), APIHandler)
    port = server.server_address[1]

    # 在后台线程运行服务器
    server_thread = threading.Thread(target=lambda: [server.handle_request() for _ in range(5)])
    server_thread.daemon = True
    server_thread.start()

    print(f"  ✅ API 服务器运行在 http://127.0.0.1:{port}")
    print(f"\n  应用部署 vs 静态部署的区别：")
    print(f"  • 静态部署：返回固定文件")
    print(f"  • 应用部署：执行代码后动态生成响应\n")

    # 模拟 API 请求
    import urllib.request

    endpoints = [
        ("/api/users", "GET", "获取用户列表"),
        ("/api/status", "GET", "服务状态检查"),
        ("/api/time", "GET", "服务器时间"),
    ]

    print(f"  模拟 API 请求：")
    print(f"  {'端点':<20} {'说明':<15} {'状态':<8} {'响应':<50}")
    print(f"  {'----':<20} {'----':<15} {'----':<8} {'----':<50}")

    for path, method, desc in endpoints:
        try:
            start = time.perf_counter()
            req = urllib.request.Request(f"http://127.0.0.1:{port}{path}")
            response = urllib.request.urlopen(req, timeout=3)
            data = json.loads(response.read().decode("utf-8"))
            elapsed = (time.perf_counter() - start) * 1000

            # 截取响应摘要
            summary = json.dumps(data, ensure_ascii=False)[:45]
            print(f"  {path:<20} {desc:<15} {response.status:<8} {summary}")
        except Exception as e:
            print(f"  {path:<20} {desc:<15} {'失败':<8} {str(e)[:50]}")

    server.server_close()

    print(f"\n  📋 应用部署流程：")
    print(f"  1. 购买云服务器（阿里云 ECS、腾讯云 CVM）")
    print(f"  2. 安装 Python 和依赖")
    print(f"  3. 上传代码（Git clone 或 SCP）")
    print(f"  4. 配置 Nginx 反向代理")
    print(f"  5. 使用 Gunicorn 启动应用")
    print(f"  6. 配置 systemd 保持服务运行")
    print(f"  7. 配置防火墙和 HTTPS")

    print(f"\n  📋 生产环境启动命令示例：")
    print(f"  gunicorn -w 4 -b 0.0.0.0:8000 app:app")
    print(f"  │         │   │              │")
    print(f"  │         │   │              └── 应用入口（模块:变量）")
    print(f"  │         │   └── 监听地址和端口")
    print(f"  │         └── 4 个 worker 进程")
    print(f"  └── WSGI HTTP 服务器")


class APIHandler(BaseHTTPRequestHandler):
    """模拟后端 API 处理器。

    展示一个真实的后端应用如何处理不同类型的请求。
    """

    def do_GET(self):
        """处理 GET 请求，模拟不同的 API 端点。"""
        # 模拟路由匹配
        routes = {
            "/api/users": self._handle_users,
            "/api/status": self._handle_status,
            "/api/time": self._handle_time,
        }

        handler = routes.get(self.path)
        if handler:
            handler()
        else:
            self._send_json(404, {"error": "Not Found", "path": self.path})

    def _handle_users(self):
        """模拟用户列表 API（实际项目中会查询数据库）。"""
        # 模拟数据库查询结果
        users = [
            {"id": 1, "name": "张三", "role": "admin"},
            {"id": 2, "name": "李四", "role": "user"},
            {"id": 3, "name": "王五", "role": "user"},
        ]
        self._send_json(200, {
            "data": users,
            "total": len(users),
            "source": "模拟数据库查询（实际项目中这里是 MySQL/PostgreSQL）",
        })

    def _handle_status(self):
        """服务健康检查端点（部署后用于监控）。"""
        self._send_json(200, {
            "status": "healthy",
            "version": "1.0.0",
            "uptime": "running",
            "note": "生产环境中，负载均衡器会定期检查此端点",
        })

    def _handle_time(self):
        """服务器时间 API。"""
        self._send_json(200, {
            "server_time": time.strftime("%Y-%m-%d %H:%M:%S"),
            "timestamp": time.time(),
            "timezone": time.strftime("%Z"),
        })

    def _send_json(self, status_code, data):
        """发送 JSON 响应。"""
        body = json.dumps(data, ensure_ascii=False, indent=2).encode("utf-8")
        self.send_response(status_code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, format, *args):
        """静默日志。"""
        pass


# ============================================================
# 第 3 部分：容器化部署概念演示
# ============================================================

def demo_container_deploy():
    """演示容器化部署的概念。

    容器化部署将应用及其所有依赖打包成标准化的镜像，
    在任何支持 Docker 的环境中都能以相同方式运行。

    注意：本 Demo 只展示 Dockerfile 模板，不执行 Docker 命令。
    """
    print("\n" + "=" * 60)
    print("  第 3 部分：容器化部署概念演示")
    print("=" * 60)

    # 展示 Dockerfile 模板
    dockerfile = '''# =============================================================
# Python 后端应用的 Dockerfile 模板
# =============================================================

# 第 1 步：选择基础镜像
# slim 版本体积小（约 120MB），适合生产环境
FROM python:3.12-slim

# 第 2 步：设置工作目录
WORKDIR /app

# 第 3 步：安装系统依赖（如果有）
# RUN apt-get update && apt-get install -y \\
#     gcc \\
#     && rm -rf /var/lib/apt/lists/*

# 第 4 步：复制依赖文件（利用 Docker 层缓存）
# 先只复制 requirements.txt，这样依赖不变时不会重新安装
COPY requirements.txt .

# 第 5 步：安装 Python 依赖
# --no-cache-dir 减少镜像体积
RUN pip install --no-cache-dir -r requirements.txt

# 第 6 步：复制应用代码
COPY . .

# 第 7 步：创建非 root 用户（安全最佳实践）
RUN useradd -m appuser && chown -R appuser:appuser /app
USER appuser

# 第 8 步：暴露端口（仅文档作用，不真正映射）
EXPOSE 8000

# 第 9 步：健康检查
HEALTHCHECK --interval=30s --timeout=3s \\
    CMD curl -f http://localhost:8000/api/status || exit 1

# 第 10 步：启动命令
# 使用 Gunicorn 作为生产级 WSGI 服务器
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:8000", "app:app"]
'''

    print(f"\n  📄 Dockerfile 模板：")
    print(f"  {'─' * 50}")
    for line in dockerfile.strip().split("\n"):
        print(f"  {line}")
    print(f"  {'─' * 50}")

    # 展示 docker-compose.yml 模板
    compose = '''version: "3.8"

services:
  # Web 应用
  web:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://user:pass@db:5432/myapp
      - REDIS_URL=redis://cache:6379
    depends_on:
      - db
      - cache

  # 数据库
  db:
    image: postgres:16-alpine
    environment:
      POSTGRES_DB: myapp
      POSTGRES_USER: user
      POSTGRES_PASSWORD: pass
    volumes:
      - pgdata:/var/lib/postgresql/data

  # 缓存
  cache:
    image: redis:7-alpine

  # Nginx 反向代理
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
    depends_on:
      - web

volumes:
  pgdata:
'''

    print(f"\n  📄 Docker Compose 模板（多服务编排）：")
    print(f"  {'─' * 50}")
    for line in compose.strip().split("\n"):
        print(f"  {line}")
    print(f"  {'─' * 50}")

    # 展示常用 Docker 命令
    print(f"\n  📋 Docker 常用命令：")
    commands = [
        ("docker build -t myapp:v1 .", "构建镜像"),
        ("docker run -d -p 8000:8000 myapp:v1", "运行容器"),
        ("docker ps", "查看运行中的容器"),
        ("docker logs <container_id>", "查看容器日志"),
        ("docker stop <container_id>", "停止容器"),
        ("docker-compose up -d", "启动所有服务"),
        ("docker-compose down", "停止所有服务"),
    ]

    print(f"\n  {'命令':<40} {'说明':<20}")
    print(f"  {'----':<40} {'----':<20}")
    for cmd, desc in commands:
        print(f"  {cmd:<40} {desc}")

    print(f"\n  📋 三个部署层次对比：")
    print(f"  ┌──────────┬────────────────┬──────────────────┬──────────────────┐")
    print(f"  │ 维度     │ 静态部署       │ 应用部署         │ 容器化部署       │")
    print(f"  ├──────────┼────────────────┼──────────────────┼──────────────────┤")
    print(f"  │ 复杂度   │ ⭐             │ ⭐⭐⭐           │ ⭐⭐⭐⭐⭐       │")
    print(f"  │ 成本     │ 免费           │ 月付 ¥50+        │ 月付 ¥200+       │")
    print(f"  │ 适用     │ 前端/文档      │ 后端 API         │ 微服务/大型应用  │")
    print(f"  │ 运维     │ 零运维         │ 需要 Linux 基础  │ 需要 DevOps 知识 │")
    print(f"  │ 扩展性   │ 天然高         │ 手动扩展         │ 自动扩展         │")
    print(f"  └──────────┴────────────────┴──────────────────┴──────────────────┘")


# ============================================================
# 主程序
# ============================================================

def main():
    """主程序入口，依次演示三个部署层次。"""
    print("\n" + "█" * 60)
    print("  部署概览 Demo 3：部署的三个层次")
    print("█" * 60)
    print("\n  本 Demo 将演示静态部署、应用部署和容器化部署的概念。\n")

    # 第 1 部分：静态部署
    demo_static_deploy()

    # 第 2 部分：应用部署
    demo_app_deploy()

    # 第 3 部分：容器化部署
    demo_container_deploy()

    # 总结
    print("\n" + "=" * 60)
    print("  Demo 3 总结")
    print("=" * 60)
    print("""
  部署的三个层次（由简到复杂）：

  1️⃣ 静态部署
     └── 只托管文件，无需服务器端计算
     └── 适合：个人博客、文档、前端应用
     └── 工具：GitHub Pages、Vercel

  2️⃣ 应用部署
     └── 运行后端代码，处理业务逻辑
     └── 适合：API 服务、Web 应用、小程序后端
     └── 工具：云服务器 + Nginx + Gunicorn

  3️⃣ 容器化部署
     └── 打包为标准化容器，在任何环境运行
     └── 适合：微服务、大型应用、需要弹性扩展的项目
     └── 工具：Docker + Kubernetes

  选择建议：
  • 个人项目 / 学习 → 从静态部署或简单应用部署开始
  • 公司项目 → 应用部署 + CI/CD
  • 大型系统 → 容器化部署 + K8s
""")


if __name__ == "__main__":
    main()
