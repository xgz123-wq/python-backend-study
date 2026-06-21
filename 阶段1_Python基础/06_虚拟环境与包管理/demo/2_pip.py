"""
Demo 2: pip 依赖管理演示

演示如何用 Python 代码：
  1. 查询当前环境已安装的包（等价于 pip list）
  2. 检查某个包是否已安装
  3. 获取包的版本信息
  4. 模拟后端项目启动前的依赖检查

对应理论文档：../2.pip依赖管理.md
"""

import sys
import importlib.util
import importlib.metadata


# =====================================================
# 第一部分：查看已安装的包（等价于 pip list）
# =====================================================
print("=" * 55)
print("第一部分：已安装的包（等价 pip list）")
print("=" * 55)

# importlib.metadata 是 Python 3.8+ 的标准库，可以查询已安装包
distributions = sorted(
    importlib.metadata.distributions(),
    key=lambda d: d.metadata["Name"].lower()
)

print(f"当前环境共安装了 {len(list(importlib.metadata.distributions()))} 个包")
print()

# 只展示前 10 个
print(f"{'包名':<30} {'版本':<15}")
print("-" * 45)
for dist in list(distributions)[:10]:
    name = dist.metadata["Name"]
    version = dist.metadata["Version"]
    print(f"{name:<30} {version:<15}")
print("  ... (更多包省略)")


# =====================================================
# 第二部分：检查某个包是否已安装
# =====================================================
print()
print("=" * 55)
print("第二部分：检查包是否已安装")
print("=" * 55)

def is_package_installed(package_name: str) -> bool:
    """
    检查某个包是否已安装。
    两种方法：
    1. importlib.util.find_spec - 找包的文件位置
    2. importlib.metadata - 查询已安装的元数据
    """
    return importlib.util.find_spec(package_name) is not None

def get_package_version(package_name: str) -> str | None:
    """获取包的版本号，未安装返回 None"""
    try:
        return importlib.metadata.version(package_name)
    except importlib.metadata.PackageNotFoundError:
        return None

# 检查一些常见包
packages_to_check = ["os", "sys", "json", "fastapi", "sqlalchemy", "pydantic", "requests"]

print(f"{'包名':<20} {'是否安装':<12} {'版本'}")
print("-" * 45)
for pkg in packages_to_check:
    installed = is_package_installed(pkg)
    version = get_package_version(pkg) if installed else None
    status = "✓ 已安装" if installed else "✗ 未安装"
    ver_str = version if version else "-"
    print(f"{pkg:<20} {status:<12} {ver_str}")


# =====================================================
# 第三部分：后端项目启动前的依赖检查
# =====================================================
print()
print("=" * 55)
print("第三部分：后端项目依赖检查（最佳实践）")
print("=" * 55)

# 定义项目必须的依赖及最低版本
REQUIRED_PACKAGES = {
    "fastapi": "0.100.0",
    "pydantic": "2.0.0",
    "uvicorn": "0.20.0",
}

def check_version(installed: str, minimum: str) -> bool:
    """简单的版本比较（仅比较主版本号）"""
    def parse(v: str) -> tuple:
        return tuple(int(x) for x in v.split(".")[:3])
    return parse(installed) >= parse(minimum)

print("检查项目依赖：")
all_ok = True
for pkg, min_ver in REQUIRED_PACKAGES.items():
    installed_ver = get_package_version(pkg)
    if installed_ver is None:
        print(f"  ✗ {pkg}: 未安装！运行 pip install {pkg}>={min_ver}")
        all_ok = False
    elif not check_version(installed_ver, min_ver):
        print(f"  ✗ {pkg}: 版本 {installed_ver} 低于要求 {min_ver}，运行 pip install -U {pkg}>={min_ver}")
        all_ok = False
    else:
        print(f"  ✓ {pkg}=={installed_ver}")

print()
if all_ok:
    print("所有依赖满足要求，可以启动！")
else:
    print("依赖检查不通过，请先安装缺失的包。")
    print("提示: pip install -r requirements.txt")


# =====================================================
# 第四部分：模拟 pip freeze 输出
# =====================================================
print()
print("=" * 55)
print("第四部分：模拟 pip freeze 输出")
print("=" * 55)

print("以下是 pip freeze 格式的输出（前 5 条）：")
distributions_list = sorted(
    importlib.metadata.distributions(),
    key=lambda d: d.metadata["Name"].lower()
)
for dist in list(distributions_list)[:5]:
    name = dist.metadata["Name"]
    version = dist.metadata["Version"]
    print(f"{name}=={version}")
print("...")
print()
print("【pip 常用命令速查】")
print("  pip install 包名              安装最新版")
print("  pip install 包名==版本        安装指定版本")
print("  pip install -r requirements.txt  批量安装")
print("  pip list                      查看已安装")
print("  pip freeze > requirements.txt 导出依赖")
print("  pip uninstall 包名            卸载")
print("  pip install -U 包名           升级")


print()
print("=" * 55)
print("Demo 2 完成!")
print("=" * 55)
