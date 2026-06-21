"""
Demo 4: 部署核心概念
=====================

对应理论：4.部署核心概念

本脚本演示部署中的核心概念：
1. 环境隔离：展示环境变量的读取和设置
2. 构建概念：展示 Python 代码打包的基本思路
3. 回滚概念：用 Git 模拟版本切换
4. 零停机部署概念：模拟新旧进程切换

运行方式：
    python 4_core_concepts.py
"""

import json
import os
import subprocess
import sys
import tempfile
import time


# ============================================================
# 第 1 部分：环境隔离演示
# ============================================================

def demo_environment_isolation():
    """演示环境隔离：通过环境变量区分不同环境的配置。

    在实际项目中，开发、测试、生产环境使用不同的配置：
    - 不同的数据库地址
    - 不同的密钥
    - 不同的日志级别

    环境变量是实现环境隔离最常用的方式。
    """
    print("\n" + "=" * 60)
    print("  第 1 部分：环境隔离演示")
    print("=" * 60)

    # 展示当前环境变量（只展示部分安全的信息）
    print(f"\n  当前环境变量（部分）：")
    safe_keys = ["PATH", "PYTHONPATH", "HOME", "USER", "SHELL", "LANG"]
    for key in safe_keys:
        value = os.environ.get(key, "未设置")
        # 截断过长的值
        if len(value) > 50:
            value = value[:50] + "..."
        print(f"  {key:<15} = {value}")

    # 模拟不同环境的配置
    print(f"\n  模拟三环境配置：")
    print(f"  {'─' * 50}")

    # 定义三个环境的配置
    environments = {
        "development": {
            "APP_ENV": "development",
            "DATABASE_URL": "sqlite:///dev.db",
            "DEBUG": "true",
            "LOG_LEVEL": "DEBUG",
            "SECRET_KEY": "dev-insecure-key-do-not-use-in-prod",
            "REDIS_URL": "redis://localhost:6379",
        },
        "testing": {
            "APP_ENV": "testing",
            "DATABASE_URL": "mysql://test-server:3306/test_db",
            "DEBUG": "true",
            "LOG_LEVEL": "INFO",
            "SECRET_KEY": "test-key-abc123",
            "REDIS_URL": "redis://test-redis:6379",
        },
        "production": {
            "APP_ENV": "production",
            "DATABASE_URL": "mysql://prod-server:3306/prod_db",
            "DEBUG": "false",
            "LOG_LEVEL": "WARNING",
            "SECRET_KEY": "k8s2m9d4f7g1h3j5l6n8p0q2r4t6v8x0z...",
            "REDIS_URL": "redis://prod-redis-cluster:6379",
        },
    }

    for env_name, config in environments.items():
        print(f"\n  [{env_name.upper()}] 环境：")
        for key, value in config.items():
            # 隐藏敏感的 SECRET_KEY
            if key == "SECRET_KEY" and env_name == "production":
                display = value[:10] + "..." + "（已隐藏）"
            else:
                display = value
            print(f"    {key:<15} = {display}")

    # 演示如何在代码中使用环境变量
    print(f"\n  Python 代码中读取环境变量：")
    print(f"  {'─' * 50}")

    # 设置一个临时环境变量来演示
    os.environ["APP_ENV"] = "development"
    os.environ["DATABASE_URL"] = "sqlite:///demo.db"

    app_env = os.environ.get("APP_ENV", "development")
    db_url = os.environ.get("DATABASE_URL", "sqlite:///default.db")
    debug = os.environ.get("DEBUG", "false").lower() == "true"
    log_level = os.environ.get("LOG_LEVEL", "INFO")

    print(f"  import os")
    print(f"")
    print(f"  app_env   = os.environ.get('APP_ENV', 'development')")
    print(f"  # 实际值: '{app_env}'")
    print(f"")
    print(f"  db_url    = os.environ.get('DATABASE_URL', 'sqlite:///default.db')")
    print(f"  # 实际值: '{db_url}'")
    print(f"")
    print(f"  debug     = os.environ.get('DEBUG', 'false').lower() == 'true'")
    print(f"  # 实际值: {debug}")
    print(f"")
    print(f"  log_level = os.environ.get('LOG_LEVEL', 'INFO')")
    print(f"  # 实际值: '{log_level}'")

    # 清理临时环境变量
    del os.environ["APP_ENV"]
    del os.environ["DATABASE_URL"]

    print(f"\n  💡 关键理解：")
    print(f"  • 不同环境使用不同的配置，通过环境变量切换")
    print(f"  • .env 文件绝不能提交到 Git（包含密钥）")
    print(f"  • 生产环境的 DEBUG 必须为 false")
    print(f"  • 生产环境的 SECRET_KEY 必须是强随机字符串")


# ============================================================
# 第 2 部分：构建（Build）概念演示
# ============================================================

def demo_build_concept():
    """演示构建概念：将源代码转换为可运行产物。

    Python 项目虽然不需要编译，但仍需要构建步骤：
    1. 安装依赖
    2. 收集静态文件
    3. 打包为 wheel 或 Docker 镜像
    """
    print("\n" + "=" * 60)
    print("  第 2 部分：构建（Build）概念演示")
    print("=" * 60)

    # 展示 Python 项目的典型构建过程
    print(f"\n  Python 项目的构建流程：")
    print(f"  {'─' * 50}")

    steps = [
        ("源代码 + requirements.txt", "输入"),
        ("创建虚拟环境 (venv)", "隔离依赖"),
        ("pip install -r requirements.txt", "安装依赖"),
        ("收集静态文件 (collectstatic)", "准备资源"),
        ("打包为 wheel / Docker 镜像", "生成产物"),
    ]

    for i, (step, desc) in enumerate(steps, 1):
        arrow = "↓" if i < len(steps) else "✅"
        print(f"  {i}. {step:<40} [{desc}]")
        if i < len(steps):
            print(f"     {arrow}")

    # 演示 pyproject.toml 的内容
    print(f"\n  📄 pyproject.toml 示例（现代 Python 打包配置）：")
    print(f"  {'─' * 50}")

    pyproject = '''[build-system]
requires = ["setuptools>=68.0", "wheel"]
build-backend = "setuptools.backends._legacy:_Backend"

[project]
name = "my-api"
version = "1.0.0"
description = "我的后端 API 服务"
requires-python = ">=3.11"
dependencies = [
    "flask>=3.0",
    "gunicorn>=21.0",
    "sqlalchemy>=2.0",
    "redis>=5.0",
]

[project.optional-dependencies]
dev = ["pytest", "ruff", "mypy"]

[project.scripts]
my-api = "myapi.main:run"'''

    for line in pyproject.split("\n"):
        print(f"  {line}")
    print(f"  {'─' * 50}")

    # 演示 requirements.txt 和 lock 文件的区别
    print(f"\n  依赖管理方式对比：")
    print(f"  ┌──────────────────┬─────────────────────┬────────────────────┐")
    print(f"  │ 方式             │ 特点                │ 适用场景           │")
    print(f"  ├──────────────────┼─────────────────────┼────────────────────┤")
    print(f"  │ requirements.txt │ 简单直接            │ 小项目             │")
    print(f"  │ Pipfile          │ 区分开发/生产依赖   │ 中等项目           │")
    print(f"  │ poetry.lock      │ 锁定精确版本        │ 需要可重复构建     │")
    print(f"  │ uv.lock          │ 超快的包管理器      │ 追求速度           │")
    print(f"  └──────────────────┴─────────────────────┴────────────────────┘")

    # 模拟构建过程
    print(f"\n  📋 模拟构建过程：")
    temp_dir = tempfile.mkdtemp(prefix="build_demo_")
    print(f"  构建目录: {temp_dir}")

    # 创建模拟的项目文件
    os.makedirs(os.path.join(temp_dir, "src"), exist_ok=True)

    # 模拟源代码
    with open(os.path.join(temp_dir, "src", "app.py"), "w") as f:
        f.write('# app.py\nprint("Hello from my API!")\n')

    with open(os.path.join(temp_dir, "requirements.txt"), "w") as f:
        f.write("flask>=3.0\ngunicorn>=21.0\n")

    # 展示目录结构
    print(f"\n  构建前的项目结构：")
    print(f"  {temp_dir}/")
    print(f"  ├── src/")
    print(f"  │   └── app.py          (源代码)")
    print(f"  └── requirements.txt    (依赖清单)")

    # 模拟构建产物
    dist_dir = os.path.join(temp_dir, "dist")
    os.makedirs(dist_dir, exist_ok=True)
    with open(os.path.join(dist_dir, "my_api-1.0.0-py3-none-any.whl"), "w") as f:
        f.write("# 模拟的 wheel 文件")

    print(f"\n  构建后的产物：")
    print(f"  {temp_dir}/")
    print(f"  ├── src/")
    print(f"  │   └── app.py")
    print(f"  ├── requirements.txt")
    print(f"  └── dist/")
    print(f"      └── my_api-1.0.0-py3-none-any.whl  (可分发产物)")

    print(f"\n  💡 关键理解：")
    print(f"  • 构建将源代码转换为可部署的产物")
    print(f"  • 构建产物应该是不可变的（同一版本构建结果相同）")
    print(f"  • 锁定依赖版本确保构建可重复")
    print(f"  • Docker 镜像也是一种构建产物")


# ============================================================
# 第 3 部分：回滚（Rollback）概念演示
# ============================================================

def demo_rollback_concept():
    """演示回滚概念：用 Git 模拟版本切换和回滚。

    回滚是在新版本出问题时，快速恢复到之前稳定版本的操作。
    这是部署安全网中最重要的一环。
    """
    print("\n" + "=" * 60)
    print("  第 3 部分：回滚（Rollback）概念演示")
    print("=" * 60)

    # 在临时目录中创建 Git 仓库来演示
    temp_dir = tempfile.mkdtemp(prefix="rollback_demo_")
    print(f"\n  创建临时 Git 仓库: {temp_dir}")

    original_dir = os.getcwd()

    try:
        os.chdir(temp_dir)

        # 初始化 Git 仓库
        subprocess.run(
            ["git", "init"],
            capture_output=True, text=True
        )
        subprocess.run(
            ["git", "config", "user.email", "demo@example.com"],
            capture_output=True, text=True
        )
        subprocess.run(
            ["git", "config", "user.name", "Demo"],
            capture_output=True, text=True
        )

        # 模拟版本 1.0：稳定版本
        with open("app.py", "w") as f:
            f.write('# 版本 1.0 - 稳定版本\ndef hello():\n    return "Hello v1.0"\n')

        subprocess.run(["git", "add", "."], capture_output=True)
        subprocess.run(
            ["git", "commit", "-m", "v1.0: 初始稳定版本"],
            capture_output=True, text=True
        )
        print(f"  ✅ 提交 v1.0: 初始稳定版本")

        # 模拟版本 1.1：功能更新
        time.sleep(1)  # 确保时间戳不同
        with open("app.py", "w") as f:
            f.write('# 版本 1.1 - 新增功能\ndef hello():\n    return "Hello v1.1"\n\ndef new_feature():\n    return "新功能"\n')

        subprocess.run(["git", "add", "."], capture_output=True)
        subprocess.run(
            ["git", "commit", "-m", "v1.1: 新增功能"],
            capture_output=True, text=True
        )
        print(f"  ✅ 提交 v1.1: 新增功能")

        # 模拟版本 1.2：引入 bug
        time.sleep(1)
        with open("app.py", "w") as f:
            f.write('# 版本 1.2 - 有 BUG！\ndef hello():\n    return "Hello v1.2"\n\ndef new_feature():\n    return "新功能"\n\ndef buggy_code():\n    raise Exception("这个函数有严重 bug!")  # 生产环境崩溃了！\n')

        subprocess.run(["git", "add", "."], capture_output=True)
        subprocess.run(
            ["git", "commit", "-m", "v1.2: 添加新功能（有 bug）"],
            capture_output=True, text=True
        )
        print(f"  ✅ 提交 v1.2: 添加新功能（有 bug）")

        # 展示当前状态
        print(f"\n  📋 Git 提交历史：")
        result = subprocess.run(
            ["git", "log", "--oneline", "--all"],
            capture_output=True, text=True
        )
        for line in result.stdout.strip().split("\n"):
            print(f"  {line}")

        # 模拟发现问题，执行回滚
        print(f"\n  ⚠️  v1.2 部署到生产环境后发现严重 bug！")
        print(f"  🔄 执行回滚到 v1.1...")

        # 使用 git revert 回滚
        subprocess.run(
            ["git", "revert", "HEAD", "--no-edit"],
            capture_output=True, text=True
        )

        # 展示回滚后的状态
        with open("app.py", "r") as f:
            content = f.read()
        print(f"\n  回滚后的 app.py 内容：")
        for line in content.split("\n"):
            print(f"  {line}")

        print(f"\n  📋 回滚后的 Git 历史：")
        result = subprocess.run(
            ["git", "log", "--oneline", "--all"],
            capture_output=True, text=True
        )
        for line in result.stdout.strip().split("\n"):
            print(f"  {line}")

        print(f"\n  ✅ 回滚成功！生产环境恢复到 v1.1 的稳定状态")

    except FileNotFoundError:
        print(f"  ⚠️  Git 未安装，跳过回滚演示")
        print(f"  以下是回滚的概念说明：")
        print(f"  1. 部署 v1.2 → 发现 bug")
        print(f"  2. 执行 git revert HEAD → 生成回滚提交")
        print(f"  3. 重新部署 → 恢复到 v1.1 状态")
    finally:
        os.chdir(original_dir)

    # 展示回滚策略对比
    print(f"\n  📋 回滚策略对比：")
    print(f"  ┌──────────────────┬───────────────────┬───────────────────┐")
    print(f"  │ 策略             │ 操作方式          │ 适用场景          │")
    print(f"  ├──────────────────┼───────────────────┼───────────────────┤")
    print(f"  │ Git revert       │ 生成反向提交      │ 代码级别的回滚    │")
    print(f"  │ 版本目录切换     │ 修改软链接        │ 快速切换版本      │")
    print(f"  │ Docker 标签切换  │ 使用旧镜像重新部署│ 容器化应用        │")
    print(f"  │ K8s rollout undo │ K8s 原生命令      │ K8s 部署的应用    │")
    print(f"  └──────────────────┴───────────────────┴───────────────────┘")

    print(f"\n  💡 关键理解：")
    print(f"  • 回滚是部署失败时的安全网")
    print(f"  • 回滚要快（秒级），不要现场修 bug")
    print(f"  • 数据库迁移也要设计可回滚的方案")
    print(f"  • 定期演练回滚操作")


# ============================================================
# 第 4 部分：零停机部署概念演示
# ============================================================

def demo_zero_downtime():
    """演示零停机部署的概念：模拟新旧进程的平滑切换。

    零停机部署的核心思想：在部署新版本时，用户完全感知不到服务中断。
    常见策略：蓝绿部署、滚动更新。
    """
    print("\n" + "=" * 60)
    print("  第 4 部分：零停机部署概念演示")
    print("=" * 60)

    # 模拟蓝绿部署
    print(f"\n  📌 模拟蓝绿部署（Blue-Green Deployment）：")
    print(f"  {'─' * 50}")

    # 定义两个"环境"
    blue_env = {"name": "蓝色环境", "version": "v1.1", "status": "运行中", "traffic": "100%"}
    green_env = {"name": "绿色环境", "version": "v1.2", "status": "部署中", "traffic": "0%"}

    def print_env(blue, green, step_desc):
        """打印蓝绿环境状态。"""
        print(f"\n  [{step_desc}]")
        print(f"  ┌─────────────────────┬─────────────────────┐")
        print(f"  │ 🔵 {blue['name']:<18}│ 🟢 {green['name']:<18}│")
        print(f"  │ 版本: {blue['version']:<14}│ 版本: {green['version']:<14}│")
        print(f"  │ 状态: {blue['status']:<14}│ 状态: {green['status']:<14}│")
        print(f"  │ 流量: {blue['traffic']:<14}│ 流量: {green['traffic']:<14}│")
        print(f"  └─────────────────────┴─────────────────────┘")

    # 步骤 1：初始状态
    print_env(blue_env, green_env, "步骤 1: 初始状态")

    # 步骤 2：在绿色环境部署新版本
    green_env["status"] = "部署中..."
    print(f"\n  [步骤 2: 在绿色环境部署 v1.2]")
    print(f"  正在部署新版本到绿色环境...")
    time.sleep(0.5)
    green_env["status"] = "健康检查中"
    print(f"  绿色环境部署完成，正在进行健康检查...")
    time.sleep(0.3)
    green_env["status"] = "就绪"
    print_env(blue_env, green_env, "步骤 2 完成")

    # 步骤 3：切换流量
    print(f"\n  [步骤 3: 切换流量]")
    print(f"  负载均衡器: 将流量从蓝色切换到绿色...")
    blue_env["traffic"] = "0%"
    green_env["traffic"] = "100%"
    blue_env["status"] = "待命（回滚备用）"
    green_env["status"] = "运行中"
    print_env(blue_env, green_env, "步骤 3 完成: 切换成功！")

    # 模拟滚动更新
    print(f"\n\n  📌 模拟滚动更新（Rolling Update）：")
    print(f"  {'─' * 50}")

    # 4 个实例
    instances = ["v1.1", "v1.1", "v1.1", "v1.1"]

    def print_instances(insts, step_desc):
        """打印实例状态。"""
        print(f"\n  [{step_desc}]")
        boxes = "  "
        for i, v in enumerate(insts):
            emoji = "🟢" if v == "v1.2" else "🔵"
            boxes += f"  {emoji} 实例{i+1}({v})  "
        print(boxes)

        # 统计
        v11_count = insts.count("v1.1")
        v12_count = insts.count("v1.2")
        print(f"  旧版本(v1.1): {v11_count} 个  |  新版本(v1.2): {v12_count} 个  |  服务可用: ✅")

    print_instances(instances, "初始状态: 4 个 v1.1 实例")

    # 逐个更新
    for i in range(4):
        time.sleep(0.3)
        instances[i] = "更新中"
        print(f"\n  正在更新实例 {i+1}...")
        time.sleep(0.2)
        instances[i] = "v1.2"
        print_instances(instances, f"步骤 {i+1}: 实例 {i+1} 已更新")

    print(f"\n  ✅ 滚动更新完成！所有实例已升级到 v1.2")

    # 对比两种策略
    print(f"\n  📋 蓝绿部署 vs 滚动更新：")
    print(f"  ┌────────────┬─────────────────────┬─────────────────────┐")
    print(f"  │ 维度       │ 蓝绿部署            │ 滚动更新            │")
    print(f"  ├────────────┼─────────────────────┼─────────────────────┤")
    print(f"  │ 资源需求   │ 2 倍（两套环境）    │ 略多于正常          │")
    print(f"  │ 切换速度   │ 秒级                │ 分钟级              │")
    print(f"  │ 回滚速度   │ 秒级（切回蓝色）    │ 需再次滚动更新      │")
    print(f"  │ 新旧共存   │ 不会                │ 会（更新过程中）    │")
    print(f"  │ 适用场景   │ 重要服务            │ 一般服务            │")
    print(f"  └────────────┴─────────────────────┴─────────────────────┘")

    print(f"\n  💡 关键理解：")
    print(f"  • 零停机部署 = 用户感知不到服务中断")
    print(f"  • 蓝绿部署：两套环境切换，回滚快但成本高")
    print(f"  • 滚动更新：逐步替换，资源省但新旧版本会共存")
    print(f"  • 选择哪种取决于业务的重要性和预算")


# ============================================================
# 主程序
# ============================================================

def main():
    """主程序入口，依次演示各个核心概念。"""
    print("\n" + "█" * 60)
    print("  部署概览 Demo 4：部署核心概念")
    print("█" * 60)
    print("\n  本 Demo 将演示部署中的核心概念：")
    print("  环境隔离、构建、回滚、零停机部署\n")

    # 第 1 部分：环境隔离
    demo_environment_isolation()

    # 第 2 部分：构建
    demo_build_concept()

    # 第 3 部分：回滚
    demo_rollback_concept()

    # 第 4 部分：零停机部署
    demo_zero_downtime()

    # 总结
    print("\n" + "=" * 60)
    print("  Demo 4 总结")
    print("=" * 60)
    print("""
  部署核心概念回顾：

  1️⃣ 环境隔离
     └── 开发/测试/生产三环境，通过环境变量切换配置
     └── .env 文件不能提交到 Git

  2️⃣ 构建（Build）
     └── 源代码 → 可运行产物（wheel、Docker 镜像）
     └── 锁定依赖版本确保构建可重复

  3️⃣ 回滚（Rollback）
     └── 新版本出问题 → 快速恢复到稳定版本
     └── 先恢复服务，再修复 bug

  4️⃣ 零停机部署
     └── 蓝绿部署：两套环境切换
     └── 滚动更新：逐步替换实例

  5️⃣ CI/CD（持续集成/持续部署）
     └── 代码提交 → 自动测试 → 自动构建 → 自动部署
     └── GitHub Actions、GitLab CI 等工具

  这些概念贯穿整个部署流程，是做好工程化的基础。
""")


if __name__ == "__main__":
    main()
