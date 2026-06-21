# -*- coding: utf-8 -*-
"""
Gunicorn 生产环境配置文件

本文件是 Gunicorn 的配置文件，用于生产环境部署。
Gunicorn 启动时会自动读取此文件中的配置。

启动方式：
    gunicorn -c gunicorn_config.py app.main:app

配置说明：
    - bind：监听地址和端口
    - workers：工作进程数量
    - worker_class：工作进程类型
    - timeout：请求超时时间
    - 日志配置：访问日志和错误日志
"""

import multiprocessing
import os


# ============================================================
# 基础配置
# ============================================================

# 监听地址
# - 127.0.0.1:8000 表示只监听本地（由 Nginx 反向代理转发）
# - 0.0.0.0:8000 表示监听所有地址（直接暴露，不推荐生产环境）
bind = "127.0.0.1:8000"

# Worker 数量
# 经典公式：CPU 核数 * 2 + 1
# - CPU 密集型应用：worker 数 = CPU 核数
# - I/O 密集型应用（大多数 Web 应用）：worker 数 = CPU 核数 * 2 + 1
# - 异步 worker（UvicornWorker）：可以适当减少
workers = multiprocessing.cpu_count() * 2 + 1

# Worker 类型
# - sync：同步 worker（默认，适合 Flask/Django）
# - uvicorn.workers.UvicornWorker：异步 worker（适合 FastAPI）
# - gevent/eventlet：协程 worker（适合高并发同步代码）
worker_class = "uvicorn.workers.UvicornWorker"

# 每个 worker 的线程数（sync worker 时有效）
# 异步 worker 不需要多线程
threads = 1


# ============================================================
# 超时配置
# ============================================================

# 请求超时时间（秒）
# 如果 worker 处理一个请求超过这个时间，worker 会被杀掉并重启
# 根据实际业务调整：
# - 普通 API：30-60 秒
# - 需要调用外部 API：120 秒
# - 文件上传/下载：300 秒
timeout = 120

# 优雅停止超时时间（秒）
# 收到停止信号后，等待 worker 完成当前请求的最大时间
graceful_timeout = 30

# Keep-Alive 超时时间（秒）
# HTTP Keep-Alive 连接空闲多久后关闭
keepalive = 5


# ============================================================
# 进程管理
# ============================================================

# 最大请求数
# 每个 worker 处理 N 个请求后自动重启（防止内存泄漏）
max_requests = 1000

# 最大请求数的随机偏移
# 避免所有 worker 同时重启导致服务中断
max_requests_jitter = 50

# 预加载应用
# True：Master 进程加载应用，worker 进程 fork（节省内存，但热更新需要重启所有 worker）
# False：每个 worker 独立加载应用（占用更多内存，但可以单独重启 worker）
preload_app = True


# ============================================================
# 日志配置
# ============================================================

# 访问日志文件
# "-" 表示输出到 stdout（由 systemd journal 收集）
# "/var/log/myapp/access.log" 表示写入文件
accesslog = "-"

# 错误日志文件
errorlog = "-"

# 日志级别
# debug, info, warning, error, critical
loglevel = "info"

# 访问日志格式
# %(h)s - 客户端 IP
# %(r)s - 请求行
# %(s)s - 状态码
# %(b)s - 响应大小
# %(f)s - Referer
# %(a)s - User-Agent
# %(T)s - 请求处理时间（秒）
# %(D)s - 请求处理时间（微秒）
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(D)s'


# ============================================================
# 进程信息
# ============================================================

# 进程名称前缀
proc_name = "myapp"

# 守护进程（False，因为由 systemd 管理）
daemon = False

# PID 文件（systemd 不需要）
# pidfile = "/var/run/myapp.pid"


# ============================================================
# 钩子函数（可选）
# ============================================================

def on_starting(server):
    """Master 进程启动时调用"""
    pass


def on_reload(server):
    """收到 reload 信号时调用"""
    server.log.info("Gunicorn 正在重启...")


def post_fork(server, worker):
    """Worker 进程 fork 后调用"""
    server.log.info(f"Worker 启动 (pid: {worker.pid})")


def pre_fork(server, worker):
    """Worker 进程 fork 前调用"""
    pass


def pre_exec(server):
    """Master 进程 exec 新二进制前调用（热更新代码时使用）"""
    server.log.info("Forked child, re-executing.")


def when_ready(server):
    """Server 准备好接受连接时调用"""
    server.log.info("Server is ready. Spawning workers")


def worker_abort(worker):
    """Worker 收到 abort 信号时调用"""
    pass
