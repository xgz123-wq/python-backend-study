# ========================================
# Python FastAPI 应用 Dockerfile（生产级示例）
# ========================================
# 本文件演示了构建 Python 后端应用 Docker 镜像的最佳实践：
#   1. 多阶段构建 — 减小最终镜像体积
#   2. 非 root 用户运行 — 提升安全性
#   3. 健康检查 — 配合编排工具监控服务状态
#   4. 层缓存优化 — 加快构建速度

# ===== 阶段 1：依赖安装（构建阶段）=====
# 使用 AS builder 给这个阶段起别名，方便后续引用
FROM python:3.12-slim AS builder

# 设置工作目录，后续所有命令都在 /build 下执行
WORKDIR /build

# 【关键优化】先复制 requirements.txt，利用 Docker 层缓存
# 只要 requirements.txt 没变，这一层就会使用缓存，不需要重新安装依赖
COPY requirements.txt .

# --user: 安装到用户目录，方便后续复制到最终镜像
# --no-cache-dir: 不缓存 pip 下载文件，减小层体积
RUN pip install --user --no-cache-dir -r requirements.txt

# ===== 阶段 2：运行环境（最终镜像）=====
# 重新指定基础镜像，这个镜像不包含构建阶段的中间文件
FROM python:3.12-slim AS runtime

# 设置工作目录
WORKDIR /app

# 安装 curl，用于后续的健康检查指令
# --no-install-recommends: 不安装推荐的附加包，减小体积
# 最后清理 apt 缓存，避免留在镜像层中
RUN apt-get update && \
    apt-get install -y --no-install-recommends curl && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# 从 builder 阶段复制已安装的 Python 依赖
# --from=builder 指定从哪个阶段复制
# /root/.local 是 pip install --user 的安装位置
COPY --from=builder /root/.local /root/.local

# 将 Python 用户目录的 bin 加入 PATH
# 这样 uvicorn 等命令可以直接使用
ENV PATH=/root/.local/bin:$PATH

# 复制应用源码
COPY . .

# 【安全最佳实践】创建非 root 用户
# -m: 创建用户主目录
# -r: 创建系统用户（无登录权限）
RUN useradd -m -r appuser && \
    chown -R appuser:appuser /app

# 切换到非 root 用户，后续所有指令（包括 CMD）都以 appuser 身份运行
USER appuser

# 声明容器监听的端口（文档性质，不实际映射）
EXPOSE 8000

# 配置健康检查
# --interval=30s: 每 30 秒检查一次
# --timeout=10s: 单次检查超时 10 秒
# --start-period=10s: 容器启动后等待 10 秒再开始检查（给应用启动时间）
# --retries=3: 连续失败 3 次后标记为 unhealthy
# CMD: 检查 /health 端点是否返回 200
HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# 容器启动时执行的命令（exec 格式，应用直接作为 PID 1）
# --host 0.0.0.0: 监听所有网络接口（不是 127.0.0.1，否则容器外无法访问）
# --port 8000: 监听 8000 端口
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
