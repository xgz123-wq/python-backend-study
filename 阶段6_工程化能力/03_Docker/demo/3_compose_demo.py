"""
docker-compose 编排演示脚本
===========================

本脚本演示 docker-compose 的核心概念和操作方法：
1. 生成完整的 docker-compose.yml 配置文件
2. 解析 YAML 配置中每个服务的作用
3. 讲解服务间通信、依赖管理、数据持久化
4. 启动和停止编排服务（需要 Docker 已安装）

运行方式：
    python 3_compose_demo.py

注意：
- 生成文件和讲解部分不需要 Docker
- 实际启动/停止服务需要 Docker Desktop 已安装并运行
"""

import os
import subprocess
import sys
import textwrap


# ============================================================
# 工具函数
# ============================================================

def section(title: str):
    """打印章节标题分隔线。"""
    print(f"\n{'=' * 60}")
    print(f"  {title}")
    print(f"{'=' * 60}")


def run_cmd(cmd: str, check: bool = True, timeout: int = 120) -> subprocess.CompletedProcess:
    """
    执行 shell 命令并返回结果。

    参数:
        cmd: 要执行的命令字符串
        check: 是否在非零退出码时抛出异常
        timeout: 命令超时时间（秒）

    返回:
        subprocess.CompletedProcess 对象
    """
    print(f"\n>>> {cmd}")
    try:
        result = subprocess.run(
            cmd,
            shell=True,
            capture_output=True,
            text=True,
            check=check,
            timeout=timeout,
        )
        if result.stdout.strip():
            print(result.stdout.strip())
        return result
    except subprocess.CalledProcessError as e:
        print(f"[错误] 命令执行失败（退出码 {e.returncode}）")
        if e.stderr.strip():
            print(f"  错误信息: {e.stderr.strip()}")
        return e
    except subprocess.TimeoutExpired:
        print(f"[错误] 命令超时（{timeout}秒）")
        return None


def is_docker_available() -> bool:
    """
    检查 Docker 和 docker compose 是否可用。

    返回:
        True 表示可用，False 表示不可用
    """
    try:
        result = subprocess.run(
            "docker compose version",
            shell=True,
            capture_output=True,
            text=True,
            check=True,
            timeout=10,
        )
        return True
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired, FileNotFoundError):
        return False


# ============================================================
# 第一部分：生成 docker-compose.yml
# ============================================================

# 完整的 docker-compose.yml 配置
COMPOSE_YAML = '''\
# docker-compose.yml
# FastAPI + MySQL + Redis 全栈编排
#
# 使用方式：
#   docker compose up -d --build    # 构建并启动
#   docker compose down             # 停止并删除
#   docker compose logs -f web      # 查看 Web 日志

version: "3.9"

services:
  # ---- MySQL 数据库 ----
  db:
    image: mysql:8.0
    container_name: compose-demo-db
    restart: unless-stopped
    environment:
      MYSQL_ROOT_PASSWORD: root123
      MYSQL_DATABASE: demo_db
      MYSQL_USER: appuser
      MYSQL_PASSWORD: apppass123
    ports:
      - "3306:3306"
    volumes:
      - mysql-data:/var/lib/mysql
    networks:
      - app-network
    healthcheck:
      test: ["CMD", "mysqladmin", "ping", "-h", "localhost"]
      interval: 10s
      timeout: 5s
      retries: 5
      start_period: 30s

  # ---- Redis 缓存 ----
  redis:
    image: redis:7.2-alpine
    container_name: compose-demo-redis
    restart: unless-stopped
    ports:
      - "6379:6379"
    volumes:
      - redis-data:/data
    networks:
      - app-network
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5

  # ---- FastAPI Web 应用 ----
  web:
    build:
      context: .
      dockerfile: Dockerfile
    container_name: compose-demo-web
    restart: unless-stopped
    ports:
      - "8000:8000"
    volumes:
      - .:/app
    environment:
      - APP_ENV=development
      - DATABASE_URL=mysql+aiomysql://appuser:apppass123@db:3306/demo_db
      - REDIS_URL=redis://redis:6379/0
    depends_on:
      db:
        condition: service_healthy
      redis:
        condition: service_healthy
    networks:
      - app-network

volumes:
  mysql-data:
    driver: local
  redis-data:
    driver: local

networks:
  app-network:
    driver: bridge
'''

# 对应的 Dockerfile
DOCKERFILE = '''\
FROM python:3.12-slim
WORKDIR /app
RUN apt-get update && \\
    apt-get install -y --no-install-recommends curl && \\
    apt-get clean && rm -rf /var/lib/apt/lists/*
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
RUN useradd -m -r appuser && chown -R appuser:appuser /app
USER appuser
EXPOSE 8000
HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 \\
    CMD curl -f http://localhost:8000/health || exit 1
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
'''

# FastAPI 应用源码
FASTAPI_APP = '''\
from fastapi import FastAPI
from datetime import datetime
import os

app = FastAPI(title="Compose Demo")

@app.get("/")
async def root():
    return {"message": "Hello from docker-compose!"}

@app.get("/health")
async def health():
    return {"status": "healthy", "time": datetime.now().isoformat()}
'''


def demo_generate_compose():
    """
    生成 docker-compose.yml 及相关文件。

    展示一个完整的三服务编排配置，
    包含 Web 应用、数据库和缓存。
    """
    section("第一部分：生成 docker-compose.yml")

    print("\n我们要编排三个服务：")
    print("  1. db     — MySQL 8.0 数据库")
    print("  2. redis  — Redis 7.2 缓存")
    print("  3. web    — FastAPI Web 应用\n")

    print("以下是完整的 docker-compose.yml 配置：")
    print("-" * 40)
    print(COMPOSE_YAML.strip())
    print("-" * 40)


# ============================================================
# 第二部分：解析 YAML 配置
# ============================================================

def demo_explain_services():
    """
    逐个解析 docker-compose.yml 中每个服务的配置项，
    解释每项配置的作用和原理。
    """
    section("第二部分：解析每个服务的配置")

    print("\n" + "=" * 40)
    print("  服务 1: db（MySQL 数据库）")
    print("=" * 40)
    print("""
  image: mysql:8.0
    → 使用官方 MySQL 8.0 镜像，无需手动安装

  environment:
    MYSQL_ROOT_PASSWORD: root123
    MYSQL_DATABASE: demo_db
    MYSQL_USER: appuser
    MYSQL_PASSWORD: apppass123
    → MySQL 镜像通过这些环境变量自动初始化：
      - 设置 root 密码
      - 创建名为 demo_db 的数据库
      - 创建应用专用用户 appuser

  volumes:
    - mysql-data:/var/lib/mysql
    → 将 MySQL 数据目录挂载到命名卷 mysql-data
    → 容器删除后，数据库数据不会丢失

  healthcheck:
    test: ["CMD", "mysqladmin", "ping", "-h", "localhost"]
    → 每 10 秒检查 MySQL 是否就绪
    → start_period: 30s 给 MySQL 充足的初始化时间
    → web 服务的 depends_on: service_healthy 依赖此检查
""")

    print("=" * 40)
    print("  服务 2: redis（Redis 缓存）")
    print("=" * 40)
    print("""
  image: redis:7.2-alpine
    → 使用 Alpine 版本的 Redis，体积更小（约 30MB）

  volumes:
    - redis-data:/data
    → 持久化 Redis 数据（RDB/AOF 文件）

  healthcheck:
    test: ["CMD", "redis-cli", "ping"]
    → 用 redis-cli ping 检查 Redis 是否就绪
    → 返回 PONG 表示健康
""")

    print("=" * 40)
    print("  服务 3: web（FastAPI 应用）")
    print("=" * 40)
    print("""
  build:
    context: .
    dockerfile: Dockerfile
    → 从当前目录的 Dockerfile 构建镜像
    → context 是构建上下文（发送给 Docker daemon 的文件目录）

  ports:
    - "8000:8000"
    → 将容器的 8000 端口映射到宿主机的 8000 端口
    → 浏览器访问 http://localhost:8000 即可

  volumes:
    - .:/app
    → 绑定挂载：将当前目录映射到容器的 /app
    → 开发模式下，修改源码后容器内实时更新（配合 --reload）

  environment:
    DATABASE_URL: mysql+aiomysql://appuser:apppass123@db:3306/demo_db
    REDIS_URL: redis://redis:6379/0
    → 关键！连接字符串中的主机名是服务名（db、redis）
    → 不是 localhost，不是 IP 地址，而是 docker-compose 的服务名
    → 同一网络下的容器可以通过服务名互相访问

  depends_on:
    db:
      condition: service_healthy
    redis:
      condition: service_healthy
    → web 会在 db 和 redis 都健康后才启动
    → condition: service_healthy 依赖对方的 healthcheck
    → 避免 web 启动时数据库还没准备好
""")


# ============================================================
# 第三部分：讲解核心概念
# ============================================================

def demo_explain_concepts():
    """
    讲解 docker-compose 的三个核心概念：
    1. 服务间通信（网络）
    2. 数据持久化（卷）
    3. 环境变量管理
    """
    section("第三部分：核心概念讲解")

    print("\n" + "─" * 40)
    print("  概念 1：服务间通信")
    print("─" * 40)
    print("""
docker-compose 自动创建一个专用网络（app-network），
所有服务都连接到这个网络。

网络内的 DNS 解析：
  服务名 "db"    → db 容器的 IP 地址
  服务名 "redis" → redis 容器的 IP 地址
  服务名 "web"   → web 容器的 IP 地址

所以 web 容器连接数据库时：
  mysql://appuser:apppass123@db:3306/demo_db
                                    ^^
                              服务名，不是 localhost！

如果写成 localhost，连接的是 web 容器自己，不是 db 容器。
""")

    print("─" * 40)
    print("  概念 2：数据持久化")
    print("─" * 40)
    print("""
docker-compose 中的 volumes 有两种形式：

1. 命名卷（Named Volume）— 由 Docker 管理
   volumes:
     - mysql-data:/var/lib/mysql
   → mysql-data 在顶层 volumes 部分声明
   → Docker 自动在宿主机分配存储位置
   → 适合数据库、缓存等需要持久化的数据

2. 绑定挂载（Bind Mount）— 直接映射宿主机目录
   volumes:
     - .:/app
   → 将当前目录映射到容器的 /app
   → 适合开发时代码热更新
   → 注意：容器内的修改也会影响宿主机文件
""")

    print("─" * 40)
    print("  概念 3：环境变量管理")
    print("─" * 40)
    print("""
docker-compose 支持三种方式管理环境变量：

1. 直接写在 compose 文件中（environment）
   environment:
     - APP_ENV=development

2. 从 .env 文件加载（env_file）
   env_file:
     - .env

3. 变量替换（在 compose 文件中引用变量）
   image: myapp:${APP_VERSION:-latest}

优先级（从高到低）：
  命令行 -e → environment → env_file → 宿主机变量 → .env 文件

安全建议：
  - 敏感信息（密码、密钥）放在 .env 文件中
  - .env 文件加入 .gitignore，不要提交到 Git
  - 提供 .env.example 作为模板
""")


# ============================================================
# 第四部分：常用命令讲解
# ============================================================

def demo_explain_commands():
    """
    讲解 docker compose 的常用命令，
    包括启动、停止、查看日志、执行命令等。
    """
    section("第四部分：docker compose 常用命令")

    commands = [
        ("docker compose up -d",
         "后台启动所有服务。-d 表示 detached（后台运行）。"
         "首次运行会自动构建镜像。"),

        ("docker compose up -d --build",
         "强制重新构建镜像后启动。修改了 Dockerfile 后使用。"),

        ("docker compose up -d web",
         "只启动 web 服务（及其依赖的服务）。"),

        ("docker compose ps",
         "查看所有服务的状态、端口映射和健康检查状态。"),

        ("docker compose logs -f web",
         "实时查看 web 服务的日志。-f 表示 follow（跟踪）。"
         "类似 tail -f。"),

        ("docker compose exec web /bin/sh",
         "进入 web 容器的 shell。用于调试、查看文件、执行命令。"),

        ("docker compose restart web",
         "重启 web 服务（不影响 db 和 redis）。"),

        ("docker compose down",
         "停止并删除所有容器和网络。数据卷不会被删除。"),

        ("docker compose down -v",
         "停止并删除所有容器、网络和数据卷。"
         "警告：-v 会删除数据库数据！"),

        ("docker compose build web",
         "只构建 web 服务的镜像，不启动。"),
    ]

    for cmd, desc in commands:
        print(f"\n  $ {cmd}")
        print(f"    {desc}")


# ============================================================
# 第五部分：实际操作（需要 Docker）
# ============================================================

def demo_actual_operations():
    """
    实际启动和停止 docker-compose 服务。

    如果 Docker 不可用，则跳过此部分并给出提示。
    """
    section("第五部分：实际操作（启动/停止服务）")

    if not is_docker_available():
        print("\n[跳过] Docker 或 docker compose 不可用。")
        print("如果需要实际操作，请先安装 Docker Desktop。")
        print("\n以下是你可以手动执行的命令：")
        print("  cd demo/")
        print("  docker compose up -d --build")
        print("  docker compose ps")
        print("  docker compose logs -f web")
        print("  docker compose down")
        return

    # 获取当前脚本所在目录作为工作目录
    demo_dir = os.path.dirname(os.path.abspath(__file__))

    print(f"\n工作目录: {demo_dir}")
    print("注意：实际操作需要 demo 目录下有完整的 Dockerfile 和应用代码。")
    print("这里只演示命令格式，不实际执行（避免在当前目录创建不必要的容器）。\n")

    print("实际操作步骤：")
    print(f"""
  1. 进入 demo 目录
     cd "{demo_dir}"

  2. 确保以下文件存在：
     - Dockerfile
     - docker-compose.yml
     - requirements.txt
     - main.py（FastAPI 应用）

  3. 启动所有服务
     docker compose up -d --build

  4. 查看服务状态
     docker compose ps

     预期输出：
     NAME              STATUS                   PORTS
     compose-demo-db   Up (healthy)             3306->3306
     compose-demo-redis Up (healthy)            6379->6379
     compose-demo-web  Up                       8000->8000

  5. 访问应用
     http://localhost:8000         — 应用主页
     http://localhost:8000/health  — 健康检查

  6. 查看日志
     docker compose logs -f web

  7. 进入容器调试
     docker compose exec web /bin/sh

  8. 停止并清理
     docker compose down
""")


# ============================================================
# 第六部分：常见问题排查
# ============================================================

def demo_troubleshooting():
    """
    讲解 docker-compose 使用中的常见问题和排查方法。
    """
    section("第六部分：常见问题排查")

    problems = [
        {
            "problem": "web 服务启动后立即退出",
            "cause": "应用代码有错误（如 import 失败、端口冲突）",
            "fix": "docker compose logs web 查看详细错误日志",
        },
        {
            "problem": "web 无法连接数据库",
            "cause": "使用了 localhost 而不是服务名 db",
            "fix": "DATABASE_URL 中的主机名改为 db（服务名）",
        },
        {
            "problem": "depends_on 没有等待服务就绪",
            "cause": "没有配置 condition: service_healthy",
            "fix": "在被依赖的服务中添加 healthcheck，depends_on 使用 service_healthy",
        },
        {
            "problem": "修改了代码但容器没有更新",
            "cause": "没有挂载源码目录，或没有重启容器",
            "fix": "确保 volumes 中有 .:/app 绑定挂载，或 docker compose restart web",
        },
        {
            "problem": "端口 3306 被占用",
            "cause": "宿主机上已有 MySQL 在运行",
            "fix": "修改 compose 文件中的端口映射，如 13306:3306",
        },
        {
            "problem": "docker compose down 后数据丢失",
            "cause": "使用了 -v 参数删除了数据卷",
            "fix": "去掉 -v 参数。docker compose down 不加 -v 会保留数据卷",
        },
    ]

    for i, p in enumerate(problems, 1):
        print(f"\n  问题 {i}: {p['problem']}")
        print(f"    原因: {p['cause']}")
        print(f"    解决: {p['fix']}")


# ============================================================
# 主流程
# ============================================================

def main():
    """
    主函数：按顺序执行所有演示。

    流程：
    1. 生成 docker-compose.yml 配置文件
    2. 解析每个服务的配置项
    3. 讲解核心概念（网络、卷、环境变量）
    4. 讲解常用命令
    5. 实际操作演示（需要 Docker）
    6. 常见问题排查
    """
    print("=" * 60)
    print("  docker-compose 编排演示")
    print("  本脚本讲解如何用一个命令启动多容器应用")
    print("=" * 60)

    demo_generate_compose()
    demo_explain_services()
    demo_explain_concepts()
    demo_explain_commands()
    demo_actual_operations()
    demo_troubleshooting()

    # 总结
    section("演示完毕")
    print("""
本章核心知识点：

1. docker-compose 是什么
   一个 YAML 配置文件 + 一条命令 = 启动所有服务
   告别手动 docker run 逐个启动容器

2. 核心配置
   services  — 定义每个容器（Web、DB、Redis 等）
   volumes   — 数据持久化（数据库数据不会丢）
   networks  — 服务间通信（用服务名当主机名）

3. 服务编排要点
   depends_on + healthcheck 保证启动顺序
   服务名即主机名（db、redis，不是 localhost）
   命名卷持久化数据，绑定挂载方便开发

4. 常用命令
   docker compose up -d          — 启动
   docker compose down           — 停止
   docker compose logs -f web    — 看日志
   docker compose exec web sh    — 进容器
   docker compose up -d --build  — 重新构建

Docker 四章学习完毕！

建议的练习路径：
  1. 把本章 demo 目录下的文件实际运行一遍
  2. 在你自己的 FastAPI 项目中添加 Dockerfile
  3. 编写 docker-compose.yml 加入数据库和 Redis
  4. 尝试多环境配置（开发 vs 生产）
  5. 探索 Docker Hub 上的更多镜像
""")


if __name__ == "__main__":
    main()
