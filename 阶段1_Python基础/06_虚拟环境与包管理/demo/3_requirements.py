"""
Demo 3: requirements.txt 规范演示

演示：
  1. 读取和解析 requirements.txt 文件
  2. 对比 requirements.txt 与当前环境的差异
  3. 生成规范的 requirements.txt 示例内容
  4. 展示分环境管理的结构

对应理论文档：../3.requirements.txt规范.md
"""

import importlib.metadata
import importlib.util
import os


# 本 Demo 的 requirements.txt 路径
DEMO_DIR = os.path.dirname(os.path.abspath(__file__))
REQ_FILE = os.path.join(DEMO_DIR, "requirements.txt")


# =====================================================
# 第一部分：解析 requirements.txt 文件
# =====================================================
print("=" * 55)
print("第一部分：解析 requirements.txt")
print("=" * 55)

def parse_requirements(filepath: str) -> list[dict]:
    """
    简单解析 requirements.txt，返回包名和版本约束列表。
    忽略注释行（#）和空行，忽略 -r 继承语法（简化版）。
    """
    requirements = []
    if not os.path.exists(filepath):
        return requirements

    with open(filepath, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            # 跳过空行、注释、继承指令
            if not line or line.startswith("#") or line.startswith("-"):
                continue
            # 去掉行内注释
            line = line.split("#")[0].strip()
            # 解析包名和版本
            for sep in ("==", ">=", "<=", "!=", "~=", ">", "<"):
                if sep in line:
                    name, version = line.split(sep, 1)
                    requirements.append({
                        "name": name.strip().lower(),
                        "operator": sep,
                        "version": version.strip(),
                        "raw": line,
                    })
                    break
            else:
                # 没有版本约束
                requirements.append({
                    "name": line.lower(),
                    "operator": "",
                    "version": "",
                    "raw": line,
                })

    return requirements

reqs = parse_requirements(REQ_FILE)

if reqs:
    print(f"读取到 {len(reqs)} 条依赖：")
    for r in reqs:
        ver_str = f"{r['operator']}{r['version']}" if r['operator'] else "(无版本约束)"
        print(f"  {r['name']:<25} {ver_str}")
else:
    print(f"requirements.txt 不存在或为空：{REQ_FILE}")
    print("（Demo 会在第三部分生成示例文件）")


# =====================================================
# 第二部分：对比 requirements.txt 与当前环境
# =====================================================
print()
print("=" * 55)
print("第二部分：依赖与当前环境对比")
print("=" * 55)

def get_installed_version(package_name: str) -> str | None:
    """获取已安装包的版本"""
    # requirements.txt 里包名可能有 [extra]，需要去掉
    pkg = package_name.split("[")[0].lower()
    try:
        return importlib.metadata.version(pkg)
    except importlib.metadata.PackageNotFoundError:
        return None

if reqs:
    print(f"{'包名':<25} {'要求版本':<20} {'已安装版本':<15} {'状态'}")
    print("-" * 70)
    for r in reqs:
        installed = get_installed_version(r["name"])
        required = f"{r['operator']}{r['version']}" if r['operator'] else "不限"
        if installed:
            status = "✓ 已安装"
        else:
            status = "✗ 未安装"
        print(f"{r['name']:<25} {required:<20} {installed or '-':<15} {status}")
else:
    print("（跳过，requirements.txt 为空）")


# =====================================================
# 第三部分：生成示例 requirements.txt
# =====================================================
print()
print("=" * 55)
print("第三部分：生成示例 requirements.txt")
print("=" * 55)

EXAMPLE_REQUIREMENTS = """\
# ============================================================
# requirements.txt - FastAPI 项目标准依赖清单
# 生成时间: 2026-05-12
# 使用方法: pip install -r requirements.txt
# ============================================================

# Web 框架
fastapi==0.110.0
uvicorn[standard]==0.29.0

# 数据验证
pydantic==2.6.4
pydantic-settings==2.2.1

# 数据库 ORM（第三阶段会用到）
sqlalchemy==2.0.28
asyncpg==0.29.0
alembic==1.13.1

# 认证（第四阶段会用到）
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4

# 环境变量管理
python-dotenv==1.0.1

# HTTP 客户端（测试用）
httpx==0.27.0
"""

EXAMPLE_DEV_REQUIREMENTS = """\
# requirements-dev.txt - 开发环境额外依赖
# 使用方法: pip install -r requirements-dev.txt
# ============================================================

# 继承生产依赖
-r requirements.txt

# 测试
pytest==8.1.1
pytest-asyncio==0.23.6

# 代码质量
ruff==0.3.7
mypy==1.9.0
"""

print("FastAPI 项目的 requirements.txt 示例：")
print("-" * 55)
print(EXAMPLE_REQUIREMENTS)

# 写入示例文件（如果不存在的话）
example_path = os.path.join(DEMO_DIR, "requirements.txt")
if not os.path.exists(example_path):
    with open(example_path, "w", encoding="utf-8") as f:
        f.write(EXAMPLE_REQUIREMENTS)
    print(f"已写入示例文件: {example_path}")
else:
    print(f"文件已存在，未覆盖: {example_path}")


# =====================================================
# 第四部分：分环境管理结构展示
# =====================================================
print()
print("=" * 55)
print("第四部分：分环境管理结构（最佳实践）")
print("=" * 55)

print("""
推荐的项目依赖文件结构：

  my_project/
  ├── requirements.txt          # 生产依赖（精确版本）
  ├── requirements-dev.txt      # 开发依赖（含测试/lint工具）
  └── .gitignore                # 包含 .venv/

requirements-dev.txt 内容示例：
  -r requirements.txt           ← 继承生产依赖
  pytest==8.1.1
  ruff==0.3.7
  mypy==1.9.0

使用方式：
  生产环境:  pip install -r requirements.txt
  开发环境:  pip install -r requirements-dev.txt
""")

print()
print("【requirements.txt 关键约定】")
print("  ✅ 精确版本号 ==   保证可复现")
print("  ✅ 注释分组        让文件可读")
print("  ✅ 提交到 Git      团队共享")
print("  ❌ 不提交 .venv/   虚拟环境不可移植")

print()
print("=" * 55)
print("Demo 3 完成!")
print("=" * 55)
