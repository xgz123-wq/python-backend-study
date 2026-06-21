"""
Dockerfile 生成与讲解演示脚本
============================

本脚本通过代码生成一个完整的 FastAPI 应用及其对应的 Dockerfile，
并逐行讲解每条 Dockerfile 指令的作用、原理和最佳实践。

主要功能：
1. 生成一个 FastAPI 应用的 main.py 源码
2. 生成生产级 Dockerfile（多阶段构建 + 非 root 用户 + 健康检查）
3. 逐行解析 Dockerfile 每条指令的含义
4. 模拟构建流程，展示层缓存的原理

运行方式：
    python 2_dockerfile_demo.py

注意：本脚本不需要 Docker 已安装，它只是生成文件并讲解。
     如果要实际构建镜像，需要安装 Docker 后运行 docker build 命令。
"""

import os
import textwrap


# ============================================================
# 工具函数
# ============================================================

def section(title: str):
    """打印章节标题分隔线。"""
    print(f"\n{'=' * 60}")
    print(f"  {title}")
    print(f"{'=' * 60}")


def print_code_block(title: str, code: str):
    """格式化打印代码块。"""
    print(f"\n--- {title} ---")
    print("-" * 40)
    print(code.strip())
    print("-" * 40)


# ============================================================
# 第一部分：生成 FastAPI 应用代码
# ============================================================

# FastAPI 应用源码
FASTAPI_APP_CODE = '''\
"""
FastAPI 示例应用
==============
一个简洁的 FastAPI Web 应用，包含健康检查、基本路由和中间件。
用于演示 Docker 容器化部署。
"""

from fastapi import FastAPI
from datetime import datetime
import os

app = FastAPI(title="Docker Demo App", version="1.0.0")


@app.get("/")
async def root():
    """根路由：返回欢迎信息。"""
    return {
        "message": "Hello from Docker!",
        "app_env": os.getenv("APP_ENV", "unknown"),
        "hostname": os.getenv("HOSTNAME", "unknown"),
    }


@app.get("/health")
async def health_check():
    """
    健康检查端点。
    Docker HEALTHCHECK 指令会定期请求此接口，
    返回 200 表示服务健康，否则表示服务异常。
    """
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
    }


@app.get("/info")
async def app_info():
    """应用信息：展示环境变量，验证 Docker 环境配置是否生效。"""
    return {
        "python_version": os.sys.version,
        "app_env": os.getenv("APP_ENV", "not set"),
        "database_url": os.getenv("DATABASE_URL", "not set"),
        "redis_url": os.getenv("REDIS_URL", "not set"),
    }
'''

# requirements.txt 内容
REQUIREMENTS_TXT = '''\
fastapi>=0.104.0
uvicorn[standard]>=0.24.0
'''


def demo_generate_app():
    """
    演示生成 FastAPI 应用代码。

    在真实项目中，这些文件是你手写的源码。
    这里用脚本生成，方便演示完整流程。
    """
    section("第一部分：生成 FastAPI 应用代码")

    print("\n我们先准备一个简单的 FastAPI 应用，包含三个端点：")
    print("  GET /        — 欢迎信息")
    print("  GET /health  — 健康检查（Docker HEALTHCHECK 用）")
    print("  GET /info    — 应用信息（展示环境变量）")

    print_code_block("main.py", FASTAPI_APP_CODE)
    print_code_block("requirements.txt", REQUIREMENTS_TXT)

    print("\n这个应用非常简单，但足以演示 Docker 容器化的完整流程。")
    print("注意 /health 端点——它是 Docker HEALTHCHECK 的检查目标。")


# ============================================================
# 第二部分：生成 Dockerfile
# ============================================================

# 多阶段构建的 Dockerfile
DOCKERFILE_CONTENT = '''\
# ===== 阶段 1：依赖安装（构建阶段）=====
FROM python:3.12-slim AS builder
WORKDIR /build
COPY requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt

# ===== 阶段 2：运行环境（最终镜像）=====
FROM python:3.12-slim AS runtime
WORKDIR /app
RUN apt-get update && \\
    apt-get install -y --no-install-recommends curl && \\
    apt-get clean && \\
    rm -rf /var/lib/apt/lists/*
COPY --from=builder /root/.local /root/.local
ENV PATH=/root/.local/bin:$PATH
COPY . .
RUN useradd -m -r appuser && chown -R appuser:appuser /app
USER appuser
EXPOSE 8000
HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 \\
    CMD curl -f http://localhost:8000/health || exit 1
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
'''

# .dockerignore 内容
DOCKERIGNORE_CONTENT = '''\
# 版本控制
.git
.gitignore

# Python 缓存
__pycache__
*.pyc
*.pyo
.pytest_cache
venv/
.venv/

# IDE
.vscode/
.idea/

# Docker 自身
Dockerfile
docker-compose*.yml
.dockerignore

# 文档
*.md
tests/
docs/

# 系统文件
.DS_Store
.env
'''


def demo_generate_dockerfile():
    """
    演示生成 Dockerfile 和 .dockerignore。

    Dockerfile 是构建 Docker 镜像的"配方"，
    每条指令对应镜像中的一个层（Layer）。
    """
    section("第二部分：生成 Dockerfile")

    print("\nDockerfile 是 Docker 镜像的构建脚本。")
    print("Docker 读取 Dockerfile 中的指令，一层一层地构建出镜像。\n")

    print_code_block("Dockerfile（多阶段构建）", DOCKERFILE_CONTENT)
    print_code_block(".dockerignore", DOCKERIGNORE_CONTENT)

    print("\n.dockerignore 的作用：")
    print("  告诉 Docker 在构建时忽略哪些文件。")
    print("  类似 .gitignore，但用于 docker build 的构建上下文。")
    print("  避免把 __pycache__、.git、.env 等无关文件打入镜像。")


# ============================================================
# 第三部分：逐行解析 Dockerfile
# ============================================================

def demo_explain_dockerfile():
    """
    逐行解析 Dockerfile 中每条指令的作用。

    理解每条指令的原理，才能写出高效、安全、可维护的 Dockerfile。
    """
    section("第三部分：逐行解析 Dockerfile")

    instructions = [
        {
            "line": "FROM python:3.12-slim AS builder",
            "explain": (
                "FROM — 指定基础镜像。这是一切的起点。\n"
                "  python:3.12-slim 表示使用 Python 3.12 的精简版镜像（约 125MB）。\n"
                "  AS builder 给这个阶段起别名 'builder'，后续阶段可以用\n"
                "  COPY --from=builder 从这个阶段复制文件。\n"
                "  这就是「多阶段构建」的核心：构建阶段和运行阶段分离。"
            ),
        },
        {
            "line": "WORKDIR /build",
            "explain": (
                "WORKDIR — 设置工作目录。\n"
                "  后续的 COPY、RUN 等指令都在 /build 目录下执行。\n"
                "  如果目录不存在，Docker 会自动创建。\n"
                "  最佳实践：始终使用绝对路径。"
            ),
        },
        {
            "line": "COPY requirements.txt .",
            "explain": (
                "COPY — 从构建上下文复制文件到镜像中。\n"
                "  这里只复制 requirements.txt，不复制其他源码文件。\n"
                "  【关键优化】先复制依赖文件再复制源码，利用层缓存：\n"
                "    - requirements.txt 很少变化 → 这一层使用缓存\n"
                "    - 下一层的 pip install 也使用缓存 → 构建速度大幅提升\n"
                "    - 只有源码变化时，才从 COPY . . 那一层开始重建"
            ),
        },
        {
            "line": "RUN pip install --user --no-cache-dir -r requirements.txt",
            "explain": (
                "RUN — 在构建阶段执行 shell 命令。\n"
                "  pip install 安装 Python 依赖包。\n"
                "  --user: 安装到用户目录（/root/.local），而不是系统目录。\n"
                "    好处：后续阶段可以只复制用户目录，不需要 root 权限。\n"
                "  --no-cache-dir: 不保存 pip 的下载缓存。\n"
                "    Docker 镜像不会复用 pip 缓存，不保存可以减小体积。"
            ),
        },
        {
            "line": "FROM python:3.12-slim AS runtime",
            "explain": (
                "FROM（第二次）— 开始第二个构建阶段。\n"
                "  使用全新的 python:3.12-slim 作为运行环境。\n"
                "  这个阶段不包含 builder 阶段的构建工具和中间文件。\n"
                "  最终镜像只保留这个阶段的内容 → 体积更小。"
            ),
        },
        {
            "line": "RUN apt-get update && apt-get install -y ...",
            "explain": (
                "RUN — 安装系统工具。\n"
                "  这里安装 curl，用于后续的 HEALTHCHECK 指令。\n"
                "  --no-install-recommends: 不安装推荐的附加包，减小体积。\n"
                "  apt-get clean + rm -rf /var/lib/apt/lists/*: 清理 apt 缓存。\n"
                "  注意：所有操作合并在一个 RUN 中，减少镜像层数。"
            ),
        },
        {
            "line": "COPY --from=builder /root/.local /root/.local",
            "explain": (
                "COPY --from=builder — 跨阶段复制文件。\n"
                "  从 builder 阶段复制已安装的 Python 依赖到当前阶段。\n"
                "  这样运行阶段就有所有需要的 Python 包，但不包含构建工具。\n"
                "  这就是多阶段构建的威力：最终镜像干净、精简。"
            ),
        },
        {
            "line": "ENV PATH=/root/.local/bin:$PATH",
            "explain": (
                "ENV — 设置环境变量。\n"
                "  将 pip --user 安装的命令（如 uvicorn）加入 PATH。\n"
                "  这样 CMD 中可以直接使用 uvicorn 命令。"
            ),
        },
        {
            "line": "COPY . .",
            "explain": (
                "COPY . . — 复制应用源码到镜像中。\n"
                "  源文件从构建上下文（当前目录）复制到镜像的 WORKDIR（/app）。\n"
                "  注意 .dockerignore 会过滤掉不需要的文件。\n"
                "  这一层放在依赖安装之后，最大化利用层缓存。"
            ),
        },
        {
            "line": "RUN useradd -m -r appuser && ...",
            "explain": (
                "RUN — 创建非 root 用户。\n"
                "  -m: 创建用户主目录。\n"
                "  -r: 创建系统用户（不可登录）。\n"
                "  chown: 将应用目录的所有权交给 appuser。\n"
                "  【安全最佳实践】生产环境不应该用 root 运行应用。\n"
                "  即使容器有隔离，root 用户仍有更多权限，增加逃逸风险。"
            ),
        },
        {
            "line": "USER appuser",
            "explain": (
                "USER — 切换运行用户。\n"
                "  后续所有指令（包括 CMD）都以 appuser 身份运行。\n"
                "  这是 Docker 安全最佳实践之一。"
            ),
        },
        {
            "line": "EXPOSE 8000",
            "explain": (
                "EXPOSE — 声明端口（文档性质）。\n"
                "  告诉使用者这个容器会监听 8000 端口。\n"
                "  注意：EXPOSE 不会真正映射端口！\n"
                "  真正的端口映射在 docker run -p 或 docker-compose 中配置。"
            ),
        },
        {
            "line": "HEALTHCHECK ... CMD curl -f http://localhost:8000/health",
            "explain": (
                "HEALTHCHECK — 配置容器健康检查。\n"
                "  Docker 会定期执行 CMD 中的命令来检查容器是否健康。\n"
                "  --interval=30s: 每 30 秒检查一次。\n"
                "  --timeout=10s: 单次检查超时 10 秒。\n"
                "  --start-period=10s: 启动后等 10 秒再检查（给应用启动时间）。\n"
                "  --retries=3: 连续失败 3 次后标记为 unhealthy。\n"
                "  curl -f: 请求 /health 端点，HTTP 200 为成功，其他为失败。\n"
                "  docker-compose 的 depends_on: service_healthy 依赖此配置。"
            ),
        },
        {
            "line": 'CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]',
            "explain": (
                "CMD — 容器启动时执行的默认命令。\n"
                "  使用 exec 格式（JSON 数组），而不是 shell 格式。\n"
                "  exec 格式：应用直接作为 PID 1 运行，能正确接收信号。\n"
                "  shell 格式：会启动 /bin/sh -c，导致信号无法传递。\n"
                "  --host 0.0.0.0: 监听所有网络接口（不是 127.0.0.1）。\n"
                "    容器内的 localhost 只限于容器内部，外部无法访问。\n"
                "    必须绑定 0.0.0.0 才能通过端口映射从宿主机访问。"
            ),
        },
    ]

    for i, inst in enumerate(instructions, 1):
        print(f"\n[{i}/{len(instructions)}] {inst['line']}")
        print(f"  {inst['explain']}")


# ============================================================
# 第四部分：模拟构建流程
# ============================================================

def demo_build_process():
    """
    模拟 docker build 的构建流程，
    帮助理解镜像的分层结构和缓存机制。
    """
    section("第四部分：模拟 Docker 构建流程")

    print("\n执行 `docker build -t myapp:v1.0 .` 时，Docker 做了什么？\n")

    steps = [
        ("1. 读取 .dockerignore", "过滤构建上下文，排除不需要的文件"),
        ("2. 发送构建上下文", "将过滤后的文件打包发送给 Docker Daemon"),
        ("3. 执行 FROM python:3.12-slim AS builder", "拉取/使用基础镜像（Layer 1）"),
        ("4. 执行 WORKDIR /build", "设置工作目录（Layer 2，极小）"),
        ("5. 执行 COPY requirements.txt .", "复制依赖文件（Layer 3）"),
        ("6. 执行 RUN pip install ...", "安装 Python 依赖（Layer 4，耗时最长）"),
        ("7. 执行 FROM python:3.12-slim AS runtime", "开始新阶段（复用基础镜像）"),
        ("8. 执行 WORKDIR /app", "设置工作目录"),
        ("9. 执行 RUN apt-get ...", "安装系统工具（Layer 5）"),
        ("10. 执行 COPY --from=builder ...", "跨阶段复制依赖（Layer 6）"),
        ("11. 执行 ENV PATH=...", "设置环境变量"),
        ("12. 执行 COPY . .", "复制应用源码（Layer 7）"),
        ("13. 执行 RUN useradd ...", "创建用户（Layer 8）"),
        ("14. 执行 USER / EXPOSE / HEALTHCHECK", "元数据配置（不产生新层）"),
        ("15. 记录 CMD", "设置默认启动命令"),
    ]

    for step_name, step_desc in steps:
        print(f"  {step_name}")
        print(f"    → {step_desc}")

    print("\n" + "-" * 40)
    print("最终镜像 = runtime 阶段的所有层（不包含 builder 阶段）")
    print("-" * 40)

    print("\n\n--- 层缓存机制 ---")
    print("""
Docker 构建时，每一层会检查：
  "这一层的指令和输入有没有变化？"

  没有变化 → 使用缓存（CACHED），秒级完成
  有变化   → 重新构建，且之后所有层都要重建

示例：第二次构建（只修改了 main.py）

  Layer 1: FROM python:3.12-slim     → CACHED ✓
  Layer 2: WORKDIR /build            → CACHED ✓
  Layer 3: COPY requirements.txt     → CACHED ✓  ← 依赖文件没变
  Layer 4: RUN pip install           → CACHED ✓  ← 上一层没变，这层也缓存
  ...
  Layer 7: COPY . .                  → REBUILD   ← 源码变了！从这里开始重建
  Layer 8: RUN useradd               → REBUILD
  Layer 9: CMD                       → REBUILD

结论：requirements.txt 不变时，pip install 不需要重新执行，构建非常快。
这就是为什么要把 COPY requirements.txt 放在 COPY . . 之前。
""")


# ============================================================
# 第五部分：常见错误和最佳实践
# ============================================================

def demo_best_practices():
    """
    展示 Dockerfile 编写中的常见错误和最佳实践。
    """
    section("第五部分：常见错误 vs 最佳实践")

    comparisons = [
        {
            "title": "基础镜像选择",
            "bad": "FROM python:3.12          # 完整版，约 900MB",
            "good": "FROM python:3.12-slim     # 精简版，约 125MB",
            "reason": "slim 版本去除了不必要的系统工具，体积减小 85%，安全攻击面更小。",
        },
        {
            "title": "RUN 指令合并",
            "bad": (
                "RUN apt-get update\n"
                "RUN apt-get install -y gcc\n"
                "RUN apt-get install -y curl\n"
                "# 3 个 RUN = 3 层，且每层都保留了 apt 缓存"
            ),
            "good": (
                "RUN apt-get update && \\\n"
                "    apt-get install -y --no-install-recommends gcc curl && \\\n"
                "    apt-get clean && \\\n"
                "    rm -rf /var/lib/apt/lists/*\n"
                "# 1 个 RUN = 1 层，清理了缓存，体积更小"
            ),
            "reason": "每个 RUN 都创建新的镜像层。合并命令减少层数，清理缓存减小体积。",
        },
        {
            "title": "CMD 格式",
            "bad": (
                'CMD uvicorn main:app --host 0.0.0.0 --port 8000\n'
                "# shell 格式：PID 1 是 /bin/sh，信号无法传递给 uvicorn"
            ),
            "good": (
                'CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]\n'
                "# exec 格式：uvicorn 是 PID 1，能正确接收 SIGTERM 信号"
            ),
            "reason": "shell 格式导致 docker stop 无法优雅关闭应用（要等 10 秒后被 SIGKILL 强杀）。",
        },
        {
            "title": "监听地址",
            "bad": (
                'CMD ["uvicorn", "main:app", "--host", "127.0.0.1", "--port", "8000"]\n'
                "# 127.0.0.1 只监听容器内部的 localhost"
            ),
            "good": (
                'CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]\n'
                "# 0.0.0.0 监听所有网络接口，外部可以通过端口映射访问"
            ),
            "reason": "容器内的 127.0.0.1 不等于宿主机的 127.0.0.1。必须绑定 0.0.0.0。",
        },
    ]

    for i, comp in enumerate(comparisons, 1):
        print(f"\n{'─' * 40}")
        print(f"  {i}. {comp['title']}")
        print(f"{'─' * 40}")
        print(f"\n  ❌ 不好的写法：")
        for line in comp['bad'].split('\n'):
            print(f"    {line}")
        print(f"\n  ✅ 推荐写法：")
        for line in comp['good'].split('\n'):
            print(f"    {line}")
        print(f"\n  📖 原因：{comp['reason']}")


# ============================================================
# 主流程
# ============================================================

def main():
    """
    主函数：按顺序执行所有演示。

    流程：
    1. 生成 FastAPI 应用代码
    2. 生成 Dockerfile 和 .dockerignore
    3. 逐行解析 Dockerfile 指令
    4. 模拟构建流程和层缓存
    5. 常见错误和最佳实践
    """
    print("=" * 60)
    print("  Dockerfile 编写演示")
    print("  本脚本生成 FastAPI 应用的 Dockerfile 并逐行讲解")
    print("=" * 60)

    demo_generate_app()
    demo_generate_dockerfile()
    demo_explain_dockerfile()
    demo_build_process()
    demo_best_practices()

    # 总结
    section("演示完毕")
    print("""
本章核心知识点：

1. Dockerfile 核心指令
   FROM — 基础镜像（起点）
   RUN  — 构建时执行命令（每层一个 RUN）
   COPY — 复制文件到镜像
   CMD  — 容器启动命令（用 exec 格式）
   ENV  — 环境变量
   USER — 切换用户（安全）

2. 多阶段构建
   阶段 1（builder）：安装构建工具和依赖
   阶段 2（runtime）：只复制运行所需文件
   结果：最终镜像更小、更安全

3. 层缓存优化
   先复制 requirements.txt → pip install（缓存）
   再复制源码 → 源码变化不触发重新安装依赖

4. 安全最佳实践
   非 root 用户运行
   使用 .dockerignore 排除敏感文件
   不硬编码配置（通过环境变量注入）

下一步：
  - 尝试在你的项目目录创建 Dockerfile
  - 运行 `docker build -t myapp .` 构建镜像
  - 运行 `docker run -p 8000:8000 myapp` 启动容器
  - 访问 http://localhost:8000/health 验证
""")


if __name__ == "__main__":
    main()
