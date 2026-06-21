# -*- coding: utf-8 -*-
"""
安全配置检查器

本脚本演示：
    1. 检查端口暴露情况
    2. 检查环境变量中的敏感信息
    3. 检查 HTTPS 配置
    4. 检查常见安全配置
    5. 生成安全报告

运行方式：
    python 3_security_check.py

前置要求：
    - Python 3.10+
    - 无额外依赖（全部使用标准库）

学习目标：
    - 了解生产环境的安全检查项
    - 理解常见的安全风险和防护措施
    - 学会编写自动化的安全检查脚本
"""

import os
import sys
import socket
import json
import re
from datetime import datetime
from dataclasses import dataclass, field
from typing import Optional
from enum import Enum


# ============================================================
# 数据模型
# ============================================================

class Severity(Enum):
    """安全问题严重级别"""
    INFO = "ℹ️  信息"
    WARNING = "⚠️  警告"
    ERROR = "❌ 严重"
    CRITICAL = "🔴 危险"


@dataclass
class SecurityIssue:
    """
    安全问题数据类。

    记录每个检查发现的问题，包括：
    - 检查项名称
    - 严重级别
    - 问题描述
    - 修复建议
    """
    name: str
    severity: Severity
    description: str
    recommendation: str
    passed: bool = False


@dataclass
class SecurityReport:
    """
    安全报告数据类。

    汇总所有检查结果。
    """
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    hostname: str = field(default_factory=socket.gethostname)
    issues: list = field(default_factory=list)
    passed_count: int = 0
    failed_count: int = 0

    def add_issue(self, issue: SecurityIssue):
        """添加检查结果"""
        self.issues.append(issue)
        if issue.passed:
            self.passed_count += 1
        else:
            self.failed_count += 1

    def get_score(self) -> float:
        """计算安全评分（0-100）"""
        total = self.passed_count + self.failed_count
        if total == 0:
            return 100.0
        return (self.passed_count / total) * 100


# ============================================================
# 安全检查器
# ============================================================

class SecurityChecker:
    """
    安全配置检查器。

    检查生产环境的常见安全问题：
    - 端口暴露
    - 敏感信息泄露
    - HTTPS 配置
    - 文件权限
    - 调试模式
    """

    def __init__(self):
        """初始化检查器"""
        self.report = SecurityReport()

    def check_all(self):
        """运行所有检查"""
        print("=" * 60)
        print("🔒 安全配置检查器")
        print("=" * 60)
        print(f"时间: {self.report.timestamp}")
        print(f"主机: {self.report.hostname}")
        print()

        self.check_open_ports()
        self.check_sensitive_env_vars()
        self.check_debug_mode()
        self.check_env_file_permissions()
        self.check_https_config()
        self.check_database_port()
        self.check_ssh_config()
        self.check_firewall()
        self.check_root_user()

        return self.report

    def check_open_ports(self):
        """
        检查开放端口。

        扫描常见端口，检查是否有不必要的端口暴露。
        """
        print("🔍 检查开放端口...")

        # 常见端口列表
        common_ports = {
            22: "SSH",
            80: "HTTP",
            443: "HTTPS",
            3000: "开发服务器",
            5000: "Flask 开发服务器",
            5432: "PostgreSQL",
            6379: "Redis",
            8000: "Gunicorn/Uvicorn",
            8080: "HTTP 代理",
            27017: "MongoDB",
            3306: "MySQL",
        }

        open_ports = []
        closed_ports = []

        for port, service in common_ports.items():
            if self._is_port_open("127.0.0.1", port):
                open_ports.append((port, service))
            else:
                closed_ports.append((port, service))

        # 判断结果
        dangerous_ports = [p for p, s in open_ports if p in [5432, 6379, 27017, 3306]]

        if dangerous_ports:
            issue = SecurityIssue(
                name="端口暴露检查",
                severity=Severity.CRITICAL,
                description=f"发现数据库/缓存端口暴露: {', '.join(f'{p}({s})' for p, s in dangerous_ports)}",
                recommendation="数据库和缓存端口应该只监听 localhost，不要暴露到公网",
                passed=False,
            )
        elif open_ports:
            issue = SecurityIssue(
                name="端口暴露检查",
                severity=Severity.INFO,
                description=f"开放端口: {', '.join(f'{p}({s})' for p, s in open_ports)}",
                recommendation="确保只开放必要的端口（80, 443）",
                passed=True,
            )
        else:
            issue = SecurityIssue(
                name="端口暴露检查",
                severity=Severity.INFO,
                description="未发现常见端口开放",
                recommendation="服务可能未运行或端口已更改",
                passed=True,
            )

        self.report.add_issue(issue)
        self._print_result(issue)

    def check_sensitive_env_vars(self):
        """
        检查环境变量中的敏感信息。

        检查是否有敏感信息硬编码在环境变量名中（不常见），
        主要检查敏感环境变量是否已设置。
        """
        print("🔍 检查敏感环境变量...")

        # 应该设置的敏感环境变量
        sensitive_vars = {
            "SECRET_KEY": "应用密钥",
            "DATABASE_URL": "数据库连接字符串",
            "API_KEY": "API 密钥",
            "REDIS_PASSWORD": "Redis 密码",
        }

        missing_vars = []
        set_vars = []

        for var, desc in sensitive_vars.items():
            value = os.getenv(var)
            if value:
                set_vars.append(var)
                # 检查是否是弱密码
                if var == "SECRET_KEY" and len(value) < 32:
                    missing_vars.append(f"{var}（密钥太短，建议 32 字符以上）")
                if var == "SECRET_KEY" and value in ["secret", "password", "123456", "dev-secret-key"]:
                    missing_vars.append(f"{var}（使用弱密钥）")
            else:
                missing_vars.append(f"{var}（{desc}）")

        if missing_vars:
            issue = SecurityIssue(
                name="敏感环境变量检查",
                severity=Severity.WARNING,
                description=f"以下敏感变量未设置或配置不当: {', '.join(missing_vars)}",
                recommendation="在 .env 文件或系统环境变量中设置这些变量，使用强密码",
                passed=False,
            )
        else:
            issue = SecurityIssue(
                name="敏感环境变量检查",
                severity=Severity.INFO,
                description=f"所有敏感环境变量已设置: {', '.join(set_vars)}",
                recommendation="确保这些变量的值足够强，且文件权限正确",
                passed=True,
            )

        self.report.add_issue(issue)
        self._print_result(issue)

    def check_debug_mode(self):
        """
        检查调试模式是否开启。

        生产环境必须关闭 DEBUG 模式，否则会：
        - 暴露源代码和数据库结构
        - 降低性能
        - 泄露敏感信息
        """
        print("🔍 检查调试模式...")

        debug = os.getenv("DEBUG", "").lower()
        app_env = os.getenv("APP_ENV", "development")

        if app_env == "production" and debug in ["true", "1", "yes"]:
            issue = SecurityIssue(
                name="调试模式检查",
                severity=Severity.CRITICAL,
                description="生产环境开启了 DEBUG 模式！",
                recommendation="设置 DEBUG=false 或 DEBUG=0",
                passed=False,
            )
        elif debug in ["true", "1", "yes"]:
            issue = SecurityIssue(
                name="调试模式检查",
                severity=Severity.INFO,
                description=f"DEBUG 模式已开启（当前环境: {app_env}）",
                recommendation="开发环境可以开启，生产环境必须关闭",
                passed=True,
            )
        else:
            issue = SecurityIssue(
                name="调试模式检查",
                severity=Severity.INFO,
                description="DEBUG 模式已关闭",
                recommendation="✅ 配置正确",
                passed=True,
            )

        self.report.add_issue(issue)
        self._print_result(issue)

    def check_env_file_permissions(self):
        """
        检查 .env 文件权限。

        .env 文件包含敏感信息，权限应该设置为 600（只有所有者可读写）。
        """
        print("🔍 检查 .env 文件权限...")

        # 检查当前目录和常见位置的 .env 文件
        env_paths = [
            os.path.join(os.getcwd(), ".env"),
            os.path.join(os.path.dirname(__file__), ".env"),
            "/opt/myapp/.env",
        ]

        found_env = False
        issues_found = []

        for env_path in env_paths:
            if os.path.exists(env_path):
                found_env = True
                try:
                    stat = os.stat(env_path)
                    mode = oct(stat.st_mode)[-3:]

                    if mode != "600":
                        issues_found.append(f"{env_path} 权限为 {mode}（应为 600）")
                except OSError:
                    pass

        if not found_env:
            issue = SecurityIssue(
                name=".env 文件权限检查",
                severity=Severity.INFO,
                description="未找到 .env 文件",
                recommendation="如果使用 .env 文件，确保权限设置为 600",
                passed=True,
            )
        elif issues_found:
            issue = SecurityIssue(
                name=".env 文件权限检查",
                severity=Severity.WARNING,
                description="; ".join(issues_found),
                recommendation="执行: chmod 600 .env",
                passed=False,
            )
        else:
            issue = SecurityIssue(
                name=".env 文件权限检查",
                severity=Severity.INFO,
                description=".env 文件权限正确（600）",
                recommendation="✅ 配置正确",
                passed=True,
            )

        self.report.add_issue(issue)
        self._print_result(issue)

    def check_https_config(self):
        """
        检查 HTTPS 配置。

        生产环境必须使用 HTTPS，防止：
        - 中间人攻击
        - 数据窃听
        - 会话劫持
        """
        print("🔍 检查 HTTPS 配置...")

        # 检查 Nginx 配置文件
        nginx_conf_paths = [
            "/etc/nginx/sites-enabled/",
            "/etc/nginx/conf.d/",
        ]

        https_found = False
        http_only = False

        for conf_dir in nginx_conf_paths:
            if os.path.exists(conf_dir):
                try:
                    for filename in os.listdir(conf_dir):
                        filepath = os.path.join(conf_dir, filename)
                        if os.path.isfile(filepath):
                            with open(filepath, "r") as f:
                                content = f.read()
                                if "listen 443 ssl" in content:
                                    https_found = True
                                if "listen 80" in content and "return 301 https" not in content:
                                    http_only = True
                except (OSError, PermissionError):
                    pass

        if https_found:
            issue = SecurityIssue(
                name="HTTPS 配置检查",
                severity=Severity.INFO,
                description="已配置 HTTPS",
                recommendation="确保 SSL 证书有效且自动续期",
                passed=True,
            )
        elif http_only:
            issue = SecurityIssue(
                name="HTTPS 配置检查",
                severity=Severity.ERROR,
                description="Nginx 只配置了 HTTP，未配置 HTTPS",
                recommendation="使用 Certbot 配置 HTTPS: sudo certbot --nginx -d yourdomain.com",
                passed=False,
            )
        else:
            issue = SecurityIssue(
                name="HTTPS 配置检查",
                severity=Severity.WARNING,
                description="未检测到 Nginx HTTPS 配置",
                recommendation="生产环境必须配置 HTTPS，使用 Let's Encrypt 免费证书",
                passed=False,
            )

        self.report.add_issue(issue)
        self._print_result(issue)

    def check_database_port(self):
        """
        检查数据库端口是否暴露到公网。

        数据库端口（5432, 3306, 27017）不应该暴露到公网，
        应该只监听 localhost。
        """
        print("🔍 检查数据库端口...")

        db_ports = {
            5432: "PostgreSQL",
            3306: "MySQL",
            27017: "MongoDB",
            6379: "Redis",
        }

        exposed_dbs = []

        for port, db_name in db_ports.items():
            # 检查是否监听在 0.0.0.0（所有地址）
            if self._is_port_open("0.0.0.0", port):
                exposed_dbs.append(f"{db_name} (端口 {port})")

        if exposed_dbs:
            issue = SecurityIssue(
                name="数据库端口检查",
                severity=Severity.CRITICAL,
                description=f"以下数据库端口可能暴露到公网: {', '.join(exposed_dbs)}",
                recommendation="修改数据库配置，只监听 localhost: listen_addresses = 'localhost'",
                passed=False,
            )
        else:
            issue = SecurityIssue(
                name="数据库端口检查",
                severity=Severity.INFO,
                description="未发现数据库端口暴露到公网",
                recommendation="✅ 配置正确",
                passed=True,
            )

        self.report.add_issue(issue)
        self._print_result(issue)

    def check_ssh_config(self):
        """
        检查 SSH 安全配置。

        检查项：
        - 是否禁用密码登录
        - 是否禁用 root 登录
        - 是否修改默认端口
        """
        print("🔍 检查 SSH 配置...")

        ssh_config_path = "/etc/ssh/sshd_config"
        issues_found = []

        if os.path.exists(ssh_config_path):
            try:
                with open(ssh_config_path, "r") as f:
                    content = f.read()

                # 检查密码登录
                if "PasswordAuthentication yes" in content or \
                   "PasswordAuthentication" not in content:
                    issues_found.append("密码登录未禁用")

                # 检查 root 登录
                if "PermitRootLogin yes" in content:
                    issues_found.append("root 登录未禁用")

            except PermissionError:
                issues_found.append("无法读取 SSH 配置（权限不足）")
        else:
            issues_found.append("未找到 SSH 配置文件")

        if issues_found:
            issue = SecurityIssue(
                name="SSH 配置检查",
                severity=Severity.WARNING,
                description="; ".join(issues_found),
                recommendation="禁用密码登录、禁用 root 登录、修改默认端口",
                passed=False,
            )
        else:
            issue = SecurityIssue(
                name="SSH 配置检查",
                severity=Severity.INFO,
                description="SSH 配置安全",
                recommendation="✅ 配置正确",
                passed=True,
            )

        self.report.add_issue(issue)
        self._print_result(issue)

    def check_firewall(self):
        """
        检查防火墙配置。

        生产环境应该：
        - 启用防火墙
        - 只开放 80、443 端口
        - SSH 端口限制 IP 来源
        """
        print("🔍 检查防火墙配置...")

        # 检查 UFW（Ubuntu）
        ufw_status = self._run_command("ufw status")
        if ufw_status and "active" in ufw_status.lower():
            issue = SecurityIssue(
                name="防火墙检查",
                severity=Severity.INFO,
                description="UFW 防火墙已启用",
                recommendation="确保只开放必要端口（80, 443, SSH）",
                passed=True,
            )
        else:
            # 检查 iptables
            iptables_status = self._run_command("iptables -L")
            if iptables_status and len(iptables_status.splitlines()) > 3:
                issue = SecurityIssue(
                    name="防火墙检查",
                    severity=Severity.INFO,
                    description="iptables 防火墙已配置",
                    recommendation="确保规则正确，只开放必要端口",
                    passed=True,
                )
            else:
                issue = SecurityIssue(
                    name="防火墙检查",
                    severity=Severity.WARNING,
                    description="未检测到防火墙",
                    recommendation="启用 UFW: sudo ufw enable，或配置 iptables",
                    passed=False,
                )

        self.report.add_issue(issue)
        self._print_result(issue)

    def check_root_user(self):
        """
        检查是否以 root 用户运行。

        生产环境不应该以 root 用户运行应用，
        应该使用专用用户（如 www-data）。
        """
        print("🔍 检查运行用户...")

        current_user = os.getenv("USER", "")
        uid = os.getuid() if hasattr(os, "getuid") else -1

        if uid == 0 or current_user == "root":
            issue = SecurityIssue(
                name="运行用户检查",
                severity=Severity.ERROR,
                description=f"当前以 root 用户运行 (UID: {uid})",
                recommendation="创建专用用户运行应用: useradd -r -s /bin/false www-data",
                passed=False,
            )
        else:
            issue = SecurityIssue(
                name="运行用户检查",
                severity=Severity.INFO,
                description=f"当前用户: {current_user} (UID: {uid})",
                recommendation="✅ 配置正确",
                passed=True,
            )

        self.report.add_issue(issue)
        self._print_result(issue)

    def _is_port_open(self, host: str, port: int, timeout: float = 0.5) -> bool:
        """
        检查端口是否开放。

        参数：
            host: 主机地址
            port: 端口号
            timeout: 超时时间（秒）

        返回：
            端口是否开放
        """
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(timeout)
            result = sock.connect_ex((host, port))
            sock.close()
            return result == 0
        except (socket.error, OSError):
            return False

    def _run_command(self, command: str) -> Optional[str]:
        """
        运行系统命令。

        参数：
            command: 命令字符串

        返回：
            命令输出，失败返回 None
        """
        try:
            import subprocess
            result = subprocess.run(
                command.split(),
                capture_output=True,
                text=True,
                timeout=5,
            )
            return result.stdout
        except (subprocess.SubprocessError, FileNotFoundError, PermissionError):
            return None

    def _print_result(self, issue: SecurityIssue):
        """打印检查结果"""
        status = "✅ 通过" if issue.passed else "❌ 未通过"
        print(f"  {issue.severity.value} | {status}")
        print(f"  描述: {issue.description}")
        if not issue.passed:
            print(f"  建议: {issue.recommendation}")
        print()


# ============================================================
# 报告生成器
# ============================================================

def generate_report(report: SecurityReport):
    """
    生成安全报告。

    参数：
        report: SecurityReport 实例
    """
    print("\n" + "=" * 60)
    print("📊 安全报告")
    print("=" * 60)

    # 基本信息
    print(f"检查时间: {report.timestamp}")
    print(f"主机名称: {report.hostname}")
    print()

    # 安全评分
    score = report.get_score()
    if score >= 90:
        grade = "A (优秀)"
        color = "🟢"
    elif score >= 70:
        grade = "B (良好)"
        color = "🟡"
    elif score >= 50:
        grade = "C (一般)"
        color = "🟠"
    else:
        grade = "D (危险)"
        color = "🔴"

    print(f"安全评分: {score:.0f}/100 {color} {grade}")
    print(f"通过: {report.passed_count} 项")
    print(f"未通过: {report.failed_count} 项")
    print()

    # 问题汇总
    if report.failed_count > 0:
        print("❌ 需要修复的问题：")
        print("-" * 40)
        for issue in report.issues:
            if not issue.passed:
                print(f"\n  {issue.severity.value} {issue.name}")
                print(f"  问题: {issue.description}")
                print(f"  修复: {issue.recommendation}")
    else:
        print("✅ 所有检查项均通过！")

    print()

    # 安全检查清单
    print("=" * 60)
    print("📋 生产环境安全检查清单")
    print("=" * 60)
    checklist = [
        ("数据库端口不暴露到公网", report),
        ("SSH 禁用密码登录", report),
        ("SSH 禁用 root 登录", report),
        ("防火墙只开放 80/443", report),
        ("HTTPS 已配置", report),
        ("HTTP 强制跳转 HTTPS", report),
        ("DEBUG = False（生产环境）", report),
        ("敏感信息从环境变量读取", report),
        (".env 文件权限 600", report),
        (".env 已加入 .gitignore", report),
        ("应用不以 root 运行", report),
        ("日志轮转已配置", report),
        ("健康检查端点可用", report),
        ("监控告警已配置", report),
    ]

    for item, _ in checklist:
        print(f"  ☐ {item}")

    print()
    print("部署前请逐项检查并确认！")


# ============================================================
# 主函数
# ============================================================

def main():
    """主函数：运行安全检查并生成报告"""
    print("=" * 60)
    print("安全配置检查器")
    print("=" * 60)
    print()

    # 创建检查器
    checker = SecurityChecker()

    # 运行所有检查
    report = checker.check_all()

    # 生成报告
    generate_report(report)

    # 总结
    print("\n" + "=" * 60)
    print("本章总结")
    print("=" * 60)
    print("""
    1. 防火墙：只开放 80、443，SSH 限制 IP
    2. SSH：密钥登录，禁用 root
    3. HTTPS：Let's Encrypt 免费证书
    4. 数据库：只监听 localhost，强密码
    5. 敏感信息：环境变量，不硬编码
    6. 调试模式：生产环境必须关闭
    7. 运行用户：不用 root，用 www-data
    8. 监控：健康检查 + 告警
    """)


if __name__ == "__main__":
    main()
