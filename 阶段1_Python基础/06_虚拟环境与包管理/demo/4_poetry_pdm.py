"""
Demo 4: Poetry / PDM 概念对比演示

本 Demo 不需要安装 Poetry 或 PDM，
通过读取和展示 pyproject.toml 的内容格式，
帮助理解现代依赖管理工具的设计理念。

对应理论文档：../4.了解Poetry与PDM.md
"""

import os
import sys
import importlib.metadata


# =====================================================
# 第一部分：pip vs Poetry 核心差异对比
# =====================================================
print("=" * 60)
print("第一部分：pip vs Poetry 设计理念对比")
print("=" * 60)

comparison = [
    ("文件", "requirements.txt", "pyproject.toml + poetry.lock"),
    ("记录内容", "手动添加/pip freeze", "自动追踪直接依赖"),
    ("传递依赖", "全混在一起", "自动解析，lock file 完整记录"),
    ("虚拟环境", "手动 venv + 激活", "自动创建和管理"),
    ("添加依赖", "pip install + 手动写入", "poetry add（自动更新两个文件）"),
    ("锁定文件", "无（freeze 是近似）", "poetry.lock 完全确定版本树"),
    ("学习成本", "低", "中"),
]

print(f"\n  {'对比项':<15} {'pip + requirements.txt':<28} {'Poetry'}")
print("  " + "-" * 70)
for item, pip_way, poetry_way in comparison:
    print(f"  {item:<15} {pip_way:<28} {poetry_way}")


# =====================================================
# 第二部分：展示 pyproject.toml 格式
# =====================================================
print()
print("=" * 60)
print("第二部分：pyproject.toml 格式示例")
print("=" * 60)

EXAMPLE_PYPROJECT = '''
[tool.poetry]
name = "my-backend-app"
version = "0.1.0"
description = "A FastAPI backend application"
authors = ["Your Name <you@example.com>"]
python = "^3.11"

# ---- 生产依赖（直接依赖，不写传递依赖）----
[tool.poetry.dependencies]
fastapi = "^0.110.0"        # ^ 表示兼容更新（^0.110 = >=0.110, <0.111）
uvicorn = {extras = ["standard"], version = "^0.29.0"}
pydantic = "^2.6"
sqlalchemy = "^2.0"
python-dotenv = "^1.0"

# ---- 开发依赖（测试/lint 工具）----
[tool.poetry.group.dev.dependencies]
pytest = "^8.0"
pytest-asyncio = "^0.23"
ruff = "^0.3"
mypy = "^1.9"
httpx = "^0.27"             # 测试 HTTP 客户端
'''

print(EXAMPLE_PYPROJECT)

print("对应 poetry.lock 的部分内容（自动生成，不要手动修改）：")
EXAMPLE_LOCK = '''
[[package]]
name = "fastapi"
version = "0.110.0"
description = "FastAPI framework, high performance"
requires-python = ">=3.8"
dependencies = [
    {name = "pydantic", version = ">=2.0.1,<3.0.0"},
    {name = "starlette", version = ">=0.36.3,<0.37.0"},
    ...
]
'''
print(EXAMPLE_LOCK)


# =====================================================
# 第三部分：Poetry 常用命令速查
# =====================================================
print("=" * 60)
print("第三部分：Poetry 常用命令速查")
print("=" * 60)

commands = [
    ("poetry new myapp", "创建新项目（生成目录结构）"),
    ("poetry init", "在现有目录初始化（交互式）"),
    ("poetry install", "安装 lock file 中所有依赖"),
    ("poetry add fastapi", "添加依赖（自动更新 pyproject.toml + lock）"),
    ("poetry add -D pytest", "添加开发依赖"),
    ("poetry remove fastapi", "移除依赖"),
    ("poetry update", "更新所有依赖到最新兼容版本"),
    ("poetry show", "查看已安装包"),
    ("poetry shell", "激活虚拟环境"),
    ("poetry run python main.py", "在虚拟环境中运行命令"),
    ("poetry export -f requirements.txt", "导出为 requirements.txt"),
]

print(f"\n  {'命令':<40} {'说明'}")
print("  " + "-" * 70)
for cmd, desc in commands:
    print(f"  {cmd:<40} {desc}")


# =====================================================
# 第四部分：什么时候该升级到 Poetry/PDM？
# =====================================================
print()
print("=" * 60)
print("第四部分：工具选型建议")
print("=" * 60)

print("""
  学习阶段（现在）
    → 用 pip + venv + requirements.txt
    → 简单直接，重点在学 Python 和后端知识

  项目开发阶段（第五阶段）
    → 考虑引入 Poetry
    → poetry add 不会手抖漏写 requirements.txt
    → lock file 杜绝"在我机器上能跑"

  团队协作 / 开源项目
    → 强烈推荐 Poetry 或 PDM
    → 所有人 poetry install 保证完全一致的环境

  现阶段行动
    → 能看懂 pyproject.toml 格式 ✓
    → 知道 poetry.lock ≈ 更严格的 requirements.txt ✓
    → 进入项目实战再深入实操 ✓
""")


# =====================================================
# 第五部分：检测当前系统是否安装了 Poetry/PDM
# =====================================================
print("=" * 60)
print("第五部分：检查系统工具安装状态")
print("=" * 60)

import subprocess

def check_tool(name: str) -> str:
    """检查命令行工具是否可用"""
    try:
        result = subprocess.run(
            [name, "--version"],
            capture_output=True, text=True, timeout=5
        )
        if result.returncode == 0:
            return result.stdout.strip().split("\n")[0]
        return "未安装"
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return "未安装"

tools = [("poetry", "现代依赖管理（推荐）"), ("pdm", "现代依赖管理（官方标准）")]

for tool, desc in tools:
    status = check_tool(tool)
    print(f"  {tool:<10} {desc:<30} → {status}")

print()
print("  如需安装 Poetry:")
print("  pip install poetry")
print()

print("=" * 60)
print("Demo 4 完成!")
print("=" * 60)
