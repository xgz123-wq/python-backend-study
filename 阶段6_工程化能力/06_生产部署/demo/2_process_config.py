# -*- coding: utf-8 -*-
"""
进程管理与环境配置演示

本脚本演示：
    1. 读取 .env 文件（使用纯 Python 实现，不依赖第三方库）
    2. 环境变量管理
    3. 配置分离（开发/测试/生产）
    4. 结构化日志输出（JSON 格式）
    5. 模拟 systemd 服务管理

运行方式：
    python 2_process_config.py

前置要求：
    - Python 3.10+
    - 无额外依赖（全部使用标准库）

学习目标：
    - 理解 .env 文件的格式和解析原理
    - 掌握配置分离的最佳实践
    - 理解结构化日志的优势
    - 了解 systemd 服务管理的基本概念
"""

import os
import sys
import json
import logging
import platform
import subprocess
from datetime import datetime
from dataclasses import dataclass, field, asdict
from typing import Optional


# ============================================================
# 第一部分：.env 文件解析器
# ============================================================

def parse_env_file(filepath: str) -> dict[str, str]:
    """
    解析 .env 文件。

    .env 文件格式：
        KEY=value           # 基本格式
        KEY="value"         # 双引号（支持空格）
        KEY='value'         # 单引号（字面量）
        # 注释              # 注释行
        export KEY=value    # export 前缀（可选）

    参数：
        filepath: .env 文件路径

    返回：
        dict，键值对
    """
    env_vars = {}

    if not os.path.exists(filepath):
        print(f"  ⚠️ 文件不存在: {filepath}")
        return env_vars

    with open(filepath, "r", encoding="utf-8") as f:
        for line_num, line in enumerate(f, 1):
            line = line.strip()

            # 跳过空行和注释
            if not line or line.startswith("#"):
                continue

            # 去除 export 前缀
            if line.startswith("export "):
                line = line[7:]

            # 分割键值对
            if "=" not in line:
                print(f"  ⚠️ 第 {line_num} 行格式错误: {line}")
                continue

            key, value = line.split("=", 1)
            key = key.strip()
            value = value.strip()

            # 去除引号
            if len(value) >= 2:
                if (value.startswith('"') and value.endswith('"')) or \
                   (value.startswith("'") and value.endswith("'")):
                    value = value[1:-1]

            env_vars[key] = value

    return env_vars


def load_dotenv(filepath: str = ".env", override: bool = False) -> None:
    """
    加载 .env 文件到环境变量。

    参数：
        filepath: .env 文件路径
        override: 是否覆盖已存在的环境变量
    """
    env_vars = parse_env_file(filepath)

    for key, value in env_vars.items():
        if override or key not in os.environ:
            os.environ[key] = value

    print(f"  ✅ 已加载 {len(env_vars)} 个环境变量")


def demo_env_parsing():
    """演示 .env 文件解析"""
    print("\n" + "=" * 60)
    print("第一部分：.env 文件解析")
    print("=" * 60)

    # 创建临时 .env 文件用于演示
    demo_env_content = """# 数据库配置
DATABASE_URL=postgresql://user:pass@localhost/mydb
DATABASE_POOL_SIZE=5

# API 密钥
SECRET_KEY="my-super-secret-key-123"
API_KEY='sk-abc123def456'

# 应用配置
export APP_ENV=development
DEBUG=true
LOG_LEVEL=DEBUG

# Redis 配置
REDIS_URL=redis://localhost:6379/0

# 注释行会被跳过
# 空行也会被跳过

ALLOWED_HOSTS=localhost,127.0.0.1
"""

    # 写入临时文件
    demo_env_path = os.path.join(os.path.dirname(__file__), ".env.demo")
    with open(demo_env_path, "w", encoding="utf-8") as f:
        f.write(demo_env_content)

    print(f"\n创建演示 .env 文件: {demo_env_path}")
    print(f"\n文件内容：")
    print("-" * 40)
    print(demo_env_content)
    print("-" * 40)

    # 解析文件
    print(f"\n解析结果：")
    env_vars = parse_env_file(demo_env_path)
    for key, value in env_vars.items():
        # 敏感信息脱敏
        display_value = value
        if any(sensitive in key.upper() for sensitive in ["KEY", "SECRET", "PASSWORD"]):
            display_value = value[:4] + "****" + value[-4:] if len(value) > 8 else "****"
        print(f"  {key} = {display_value}")

    # 加载到环境变量
    print(f"\n加载到环境变量：")
    load_dotenv(demo_env_path, override=True)

    # 读取环境变量
    print(f"\n从环境变量读取：")
    print(f"  APP_ENV = {os.getenv('APP_ENV', '未设置')}")
    print(f"  DEBUG = {os.getenv('DEBUG', '未设置')}")
    print(f"  DATABASE_URL = {os.getenv('DATABASE_URL', '未设置')[:20]}...")

    # 清理临时文件
    os.remove(demo_env_path)
    print(f"\n已清理临时文件")


# ============================================================
# 第二部分：配置分离（开发/测试/生产）
# ============================================================

@dataclass
class AppConfig:
    """
    应用配置数据类。

    使用 dataclass 定义配置，提供类型安全和默认值。
    """
    # 应用基本信息
    app_name: str = "MyApp"
    app_env: str = "development"
    debug: bool = True

    # 服务器配置
    host: str = "127.0.0.1"
    port: int = 8000
    workers: int = 1

    # 数据库配置
    database_url: str = "sqlite:///./dev.db"
    database_pool_size: int = 5

    # 日志配置
    log_level: str = "DEBUG"
    log_format: str = "text"  # text 或 json

    # 安全配置
    secret_key: str = "dev-secret-key"
    cors_origins: list = field(default_factory=lambda: ["*"])

    def is_production(self) -> bool:
        """是否为生产环境"""
        return self.app_env == "production"

    def is_development(self) -> bool:
        """是否为开发环境"""
        return self.app_env == "development"


def get_config(env: Optional[str] = None) -> AppConfig:
    """
    根据环境变量获取配置。

    配置优先级：环境变量 > 默认值

    参数：
        env: 环境名称（development/test/production）

    返回：
        AppConfig 实例
    """
    env = env or os.getenv("APP_ENV", "development")

    # 基础配置
    config = AppConfig()

    if env == "development":
        config.app_env = "development"
        config.debug = True
        config.database_url = "sqlite:///./dev.db"
        config.log_level = "DEBUG"
        config.log_format = "text"
        config.workers = 1
        config.cors_origins = ["*"]

    elif env == "test":
        config.app_env = "test"
        config.debug = True
        config.database_url = "sqlite:///./test.db"
        config.log_level = "INFO"
        config.log_format = "text"
        config.workers = 1
        config.cors_origins = ["*"]

    elif env == "production":
        config.app_env = "production"
        config.debug = False
        config.database_url = os.getenv("DATABASE_URL", "")
        config.secret_key = os.getenv("SECRET_KEY", "")
        config.log_level = "WARNING"
        config.log_format = "json"
        config.workers = 9  # 2 * CPU + 1
        config.host = "0.0.0.0"
        config.cors_origins = ["https://myapp.com"]
        config.database_pool_size = 20

    # 从环境变量覆盖
    if os.getenv("DATABASE_URL"):
        config.database_url = os.getenv("DATABASE_URL")
    if os.getenv("SECRET_KEY"):
        config.secret_key = os.getenv("SECRET_KEY")
    if os.getenv("LOG_LEVEL"):
        config.log_level = os.getenv("LOG_LEVEL")

    return config


def demo_config_separation():
    """演示配置分离"""
    print("\n" + "=" * 60)
    print("第二部分：配置分离（开发/测试/生产）")
    print("=" * 60)

    for env_name in ["development", "test", "production"]:
        print(f"\n--- {env_name.upper()} 环境 ---")
        config = get_config(env_name)

        # 显示配置（敏感信息脱敏）
        print(f"  app_env:      {config.app_env}")
        print(f"  debug:        {config.debug}")
        print(f"  host:         {config.host}")
        print(f"  port:         {config.port}")
        print(f"  workers:      {config.workers}")
        print(f"  database_url: {config.database_url[:30]}...")
        print(f"  log_level:    {config.log_level}")
        print(f"  log_format:   {config.log_format}")
        print(f"  cors_origins: {config.cors_origins}")

    print("\n配置分离的核心原则：")
    print("  1. 敏感信息（密码、密钥）从环境变量读取")
    print("  2. 不同环境有不同的配置值")
    print("  3. 开发环境：宽松配置，方便调试")
    print("  4. 生产环境：严格配置，安全优先")


# ============================================================
# 第三部分：结构化日志
# ============================================================

class StructuredFormatter(logging.Formatter):
    """
    结构化日志格式化器（JSON 格式）。

    将日志输出为 JSON 格式，便于：
    - 日志收集系统（ELK、Loki）解析
    - 按字段搜索和过滤
    - 机器可读，自动化处理
    """

    def format(self, record: logging.LogRecord) -> str:
        """将日志记录格式化为 JSON 字符串"""
        log_data = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "level": record.levelname,
            "message": record.getMessage(),
            "logger": record.name,
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
            "process_id": os.getpid(),
            "thread": threading.current_thread().name if hasattr(threading, 'current_thread') else "main",
        }

        # 添加异常信息
        if record.exc_info and record.exc_info[0] is not None:
            log_data["exception"] = {
                "type": record.exc_info[0].__name__,
                "message": str(record.exc_info[1]),
            }

        # 添加自定义字段（通过 extra 参数传入）
        for key in ["request_id", "user_id", "ip", "method", "path", "status_code", "duration"]:
            if hasattr(record, key):
                log_data[key] = getattr(record, key)

        return json.dumps(log_data, ensure_ascii=False)


class TextFormatter(logging.Formatter):
    """
    文本日志格式化器（人类可读）。

    开发环境使用，格式简洁直观。
    """

    def format(self, record: logging.LogRecord) -> str:
        timestamp = datetime.fromtimestamp(record.created).strftime("%H:%M:%S")
        return f"[{timestamp}] {record.levelname:8s} | {record.message}"


def setup_logger(name: str, config: AppConfig) -> logging.Logger:
    """
    根据配置创建日志记录器。

    参数：
        name: 日志记录器名称
        config: 应用配置

    返回：
        配置好的 Logger 实例
    """
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, config.log_level))

    # 避免重复添加 handler
    if not logger.handlers:
        handler = logging.StreamHandler()

        if config.log_format == "json":
            handler.setFormatter(StructuredFormatter())
        else:
            handler.setFormatter(TextFormatter())

        logger.addHandler(handler)

    return logger


import threading  # noqa: E402 (needed for StructuredFormatter)


def demo_structured_logging():
    """演示结构化日志"""
    print("\n" + "=" * 60)
    print("第三部分：结构化日志")
    print("=" * 60)

    # 开发环境日志（文本格式）
    print("\n--- 开发环境日志（文本格式）---")
    dev_config = get_config("development")
    dev_logger = setup_logger("app.dev", dev_config)

    dev_logger.info("应用启动")
    dev_logger.warning("数据库连接池已满")
    dev_logger.info("用户登录成功", extra={"user_id": 123, "ip": "192.168.1.1"})

    # 生产环境日志（JSON 格式）
    print("\n--- 生产环境日志（JSON 格式）---")
    prod_config = get_config("production")
    prod_logger = setup_logger("app.prod", prod_config)

    prod_logger.info("应用启动")
    prod_logger.warning("数据库连接池已满")
    prod_logger.info(
        "用户登录成功",
        extra={
            "user_id": 123,
            "ip": "192.168.1.1",
            "request_id": "req-abc-123",
            "method": "POST",
            "path": "/api/login",
            "status_code": 200,
            "duration": 0.15,
        }
    )

    print("\n结构化日志的优势：")
    print("  1. 机器可读：日志收集系统可以直接解析")
    print("  2. 按字段搜索：grep '\"user_id\": 123' 即可找到相关日志")
    print("  3. 统计分析：统计错误率、响应时间分布")
    print("  4. 告警规则：错误率 > 5% 时触发告警")


# ============================================================
# 第四部分：模拟 systemd 服务管理
# ============================================================

class ServiceManager:
    """
    模拟 systemd 服务管理器。

    展示 systemd 的核心概念：
    - 服务状态（active/inactive/failed）
    - 启动/停止/重启
    - 自动重启策略
    - 日志查看
    """

    def __init__(self, service_name: str):
        """
        初始化管理器。

        参数：
            service_name: 服务名称
        """
        self.service_name = service_name
        self.status = "inactive"
        self.pid = None
        self.restart_count = 0
        self.max_restarts = 3
        self.logs = []

    def _log(self, message: str):
        """记录日志"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] {self.service_name}: {message}"
        self.logs.append(log_entry)
        print(f"  {log_entry}")

    def start(self) -> bool:
        """
        启动服务。

        返回：
            是否启动成功
        """
        if self.status == "active":
            self._log("服务已在运行中")
            return True

        self._log("正在启动服务...")
        self.status = "active"
        self.pid = os.getpid()
        self._log(f"服务已启动 (PID: {self.pid})")
        return True

    def stop(self) -> bool:
        """
        停止服务。

        返回：
            是否停止成功
        """
        if self.status == "inactive":
            self._log("服务未运行")
            return True

        self._log("正在停止服务...")
        self._log(f"发送 SIGTERM 信号到进程 {self.pid}")
        self.status = "inactive"
        self.pid = None
        self._log("服务已停止")
        return True

    def restart(self) -> bool:
        """
        重启服务。

        返回：
            是否重启成功
        """
        self._log("正在重启服务...")
        self.stop()
        return self.start()

    def simulate_crash(self):
        """
        模拟服务崩溃和自动重启。

        展示 systemd 的 Restart=always 策略。
        """
        if self.status != "active":
            self._log("服务未运行，无法模拟崩溃")
            return

        self._log("❌ 服务崩溃！（模拟异常退出）")
        self.status = "failed"
        self.pid = None

        # 模拟 systemd 自动重启
        self._log("systemd 检测到服务崩溃")
        self._log(f"Restart=always，将在 5 秒后自动重启")

        if self.restart_count < self.max_restarts:
            self.restart_count += 1
            self._log(f"自动重启 (第 {self.restart_count} 次)")
            self.start()
        else:
            self._log(f"已达到最大重启次数 ({self.max_restarts})，停止重启")
            self._log("请检查服务日志排查问题")

    def show_status(self):
        """显示服务状态"""
        print(f"\n  服务名称: {self.service_name}")
        print(f"  状态:     {self.status}")
        print(f"  PID:      {self.pid or 'N/A'}")
        print(f"  重启次数: {self.restart_count}")

    def show_logs(self, last_n: int = 5):
        """显示最近日志"""
        print(f"\n  最近 {last_n} 条日志：")
        for log in self.logs[-last_n:]:
            print(f"    {log}")


def demo_systemd_simulation():
    """演示 systemd 服务管理"""
    print("\n" + "=" * 60)
    print("第四部分：模拟 systemd 服务管理")
    print("=" * 60)

    # 创建服务管理器
    manager = ServiceManager("myapp")

    # 1. 启动服务
    print("\n--- 1. 启动服务 ---")
    manager.start()
    manager.show_status()

    # 2. 模拟崩溃和自动重启
    print("\n--- 2. 模拟崩溃和自动重启 ---")
    manager.simulate_crash()
    manager.show_status()

    # 3. 重启服务
    print("\n--- 3. 重启服务 ---")
    manager.restart()
    manager.show_status()

    # 4. 停止服务
    print("\n--- 4. 停止服务 ---")
    manager.stop()
    manager.show_status()

    # 5. 查看日志
    print("\n--- 5. 查看日志 ---")
    manager.show_logs()

    print("\nsystemd 常用命令：")
    print("  sudo systemctl start myapp    # 启动")
    print("  sudo systemctl stop myapp     # 停止")
    print("  sudo systemctl restart myapp  # 重启")
    print("  sudo systemctl status myapp   # 查看状态")
    print("  sudo systemctl enable myapp   # 设置开机启动")
    print("  sudo journalctl -u myapp -f   # 查看日志")


# ============================================================
# 主函数
# ============================================================

def main():
    """主函数：运行所有演示"""
    print("=" * 60)
    print("进程管理与环境配置演示")
    print("=" * 60)

    # 1. .env 文件解析
    demo_env_parsing()

    # 2. 配置分离
    demo_config_separation()

    # 3. 结构化日志
    demo_structured_logging()

    # 4. systemd 服务管理
    demo_systemd_simulation()

    # 总结
    print("\n" + "=" * 60)
    print("本章总结")
    print("=" * 60)
    print("""
    1. .env 文件：开发环境使用，生产环境用系统环境变量
    2. 配置分离：根据 APP_ENV 自动选择配置
    3. 敏感信息：从环境变量读取，不硬编码
    4. 结构化日志：JSON 格式，便于日志收集和分析
    5. systemd：Linux 标准进程管理器，生产首选
    6. 安全：不用 root 运行，.env 权限 600
    """)


if __name__ == "__main__":
    main()
