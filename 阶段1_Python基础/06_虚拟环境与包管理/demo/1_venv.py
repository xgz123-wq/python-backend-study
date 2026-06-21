"""
Demo 1: venv 虚拟环境操作演示

本 Demo 不直接运行 venv 命令（那需要在 shell 中操作），
而是演示：
  1. 如何用 Python 代码检测当前是否处于虚拟环境中
  2. 展示虚拟环境的关键路径信息
  3. 模拟后端项目启动时的环境检查逻辑

对应理论文档：../1.venv虚拟环境.md
"""

import sys
import os


# =====================================================
# 第一部分：检测是否在虚拟环境中
# =====================================================
print("=" * 55)
print("第一部分：检测虚拟环境状态")
print("=" * 55)

def is_in_virtualenv() -> bool:
    """判断当前 Python 是否运行在虚拟环境中"""
    # sys.prefix 是当前 Python 的 home 目录
    # sys.base_prefix 是系统原始 Python 的 home 目录
    # 如果两者不同，说明在虚拟环境里
    return sys.prefix != sys.base_prefix

in_venv = is_in_virtualenv()
print(f"是否在虚拟环境中: {in_venv}")
print(f"当前 Python 路径 (sys.prefix): {sys.prefix}")
print(f"系统 Python 路径 (sys.base_prefix): {sys.base_prefix}")
print(f"Python 可执行文件: {sys.executable}")


# =====================================================
# 第二部分：展示虚拟环境内部结构（如果在 venv 中）
# =====================================================
print()
print("=" * 55)
print("第二部分：虚拟环境目录结构")
print("=" * 55)

venv_home = sys.prefix
site_packages = None

# 找 site-packages 目录（第三方包的安装位置）
for path in sys.path:
    if "site-packages" in path:
        site_packages = path
        break

print(f"虚拟环境根目录: {venv_home}")
print(f"第三方包目录 (site-packages): {site_packages}")

if site_packages and os.path.exists(site_packages):
    packages = [p for p in os.listdir(site_packages)
                if not p.startswith("_") and os.path.isdir(os.path.join(site_packages, p))]
    print(f"已安装包数量: {len(packages)}")
    # 只显示前 8 个
    print(f"部分已安装包: {packages[:8]}")


# =====================================================
# 第三部分：Python 模块搜索路径
# =====================================================
print()
print("=" * 55)
print("第三部分：模块搜索路径 (sys.path)")
print("=" * 55)

print("Python 导入模块时按顺序搜索这些目录:")
for i, p in enumerate(sys.path, 1):
    print(f"  {i}. {p}")


# =====================================================
# 第四部分：后端项目启动时的环境检查
# =====================================================
print()
print("=" * 55)
print("第四部分：后端启动环境检查（最佳实践）")
print("=" * 55)

def check_environment():
    """
    后端项目启动时推荐做的环境检查。
    如果检测到不在虚拟环境中，给出警告。
    """
    # 检查 Python 版本
    version = sys.version_info
    min_version = (3, 10)
    version_ok = (version.major, version.minor) >= min_version
    print(f"Python 版本: {version.major}.{version.minor}.{version.micro} "
          f"{'✓' if version_ok else '✗ (需要 3.10+)'}")

    # 检查虚拟环境
    if is_in_virtualenv():
        print(f"虚拟环境: ✓ 已激活")
        print(f"  路径: {sys.prefix}")
    else:
        print(f"虚拟环境: ⚠ 警告 - 未激活虚拟环境！")
        print(f"  建议: python -m venv .venv && source .venv/bin/activate")

    # 检查关键环境变量（示例）
    required_vars = ["APP_ENV"]  # 实际项目可能有 DB_URL, SECRET_KEY 等
    for var in required_vars:
        value = os.getenv(var)
        if value:
            print(f"环境变量 {var}: ✓ = {value}")
        else:
            print(f"环境变量 {var}: ⚠ 未设置（使用默认值）")

check_environment()


print()
print("=" * 55)
print("Demo 1 完成!")
print("=" * 55)
print()
print("【虚拟环境操作速查】")
print("  创建:  python -m venv .venv")
print("  激活(Win PS): .venv\\Scripts\\Activate.ps1")
print("  激活(Mac/Linux): source .venv/bin/activate")
print("  退出:  deactivate")
print("  验证:  python -c \"import sys; print(sys.prefix != sys.base_prefix)\"")
