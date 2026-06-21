"""
Demo 1: Linux 基础命令 - 用 Python 模拟 Shell 操作
对应理论文档: 1.Linux基础命令.md

本 Demo 通过 Python 的 subprocess 模块演示如何在代码中执行 Shell 命令，
包括文件操作、管道重定向、文件系统遍历等。这些技能在后端开发中非常常见，
比如自动化部署脚本、日志处理、系统管理等场景。

注意: 本脚本做了跨平台兼容处理，在 Windows 和 Linux 上均可运行。
      对于 Linux 特有命令，会给出说明和等效的 Windows 命令。
"""

import subprocess
import os
import sys
import platform
import shutil
import tempfile

# ============================================================
# 工具函数
# ============================================================

def print_section(title):
    """打印分隔线和标题"""
    print(f"\n{'=' * 60}")
    print(f"  {title}")
    print(f"{'=' * 60}")


def run_command(cmd, description="", shell=True, check=False):
    """
    执行 Shell 命令并打印结果。

    参数:
        cmd: 要执行的命令字符串
        description: 命令说明
        shell: 是否通过 Shell 执行（True 才能使用管道等 Shell 特性）
        check: 是否在命令失败时抛出异常
    """
    if description:
        print(f"\n# {description}")
    print(f"$ {cmd}")

    try:
        # subprocess.run 是执行外部命令的推荐方式
        # capture_output=True 捕获 stdout 和 stderr
        # text=True (Python 3.7+) 以字符串而非字节返回输出
        result = subprocess.run(
            cmd,
            shell=shell,
            capture_output=True,
            text=True,
            check=check,
            encoding='utf-8',
            errors='replace'  # 遇到编码错误时替换而非报错
        )

        if result.stdout.strip():
            print(result.stdout.strip())
        if result.stderr.strip():
            print(f"[stderr] {result.stderr.strip()}")
        if result.returncode != 0:
            print(f"[退出码: {result.returncode}]")

        return result
    except FileNotFoundError:
        print(f"[错误] 命令未找到: {cmd}")
        return None
    except subprocess.CalledProcessError as e:
        print(f"[错误] 命令执行失败，退出码: {e.returncode}")
        return None


# ============================================================
# 第一部分：系统信息与环境检测
# ============================================================

print_section("第一部分：系统信息与环境检测")

# 检测当前操作系统
system = platform.system()
print(f"当前操作系统: {system}")
print(f"操作系统版本: {platform.version()}")
print(f"Python 版本: {sys.version}")
print(f"机器架构: {platform.machine()}")

# 判断是否为 Linux 系统
IS_LINUX = system == "Linux"
IS_WINDOWS = system == "Windows"

if IS_WINDOWS:
    print("\n[提示] 当前在 Windows 上运行，部分 Linux 命令将使用 Windows 等效命令演示。")
    print("[建议] 安装 WSL (Windows Subsystem for Linux) 以获得完整 Linux 体验。")
else:
    print("\n[提示] 当前在 Linux 上运行，可以体验完整的 Linux 命令。")


# ============================================================
# 第二部分：基础文件操作
# ============================================================

print_section("第二部分：基础文件操作")

# 创建临时工作目录（跨平台安全）
work_dir = tempfile.mkdtemp(prefix="linux_demo_")
print(f"临时工作目录: {work_dir}")

# --- mkdir: 创建目录 ---
demo_dir = os.path.join(work_dir, "demo_project")
os.makedirs(demo_dir, exist_ok=True)
print(f"\n# 创建目录 (等价于 mkdir -p)")
print(f"$ mkdir -p {demo_dir}")
print(f"目录已创建: {os.path.isdir(demo_dir)}")

# 创建多级目录
nested_dir = os.path.join(demo_dir, "src", "utils")
os.makedirs(nested_dir, exist_ok=True)
print(f"多级目录已创建: {nested_dir}")

# --- touch: 创建文件 ---
print(f"\n# 创建文件 (等价于 touch)")
demo_files = ["README.md", "main.py", "config.txt", "data.csv"]
for fname in demo_files:
    filepath = os.path.join(demo_dir, fname)
    # Python 中等价于 touch 的操作
    with open(filepath, 'w', encoding='utf-8') as f:
        if fname == "main.py":
            f.write("# Main application\nprint('Hello, Linux!')\n")
        elif fname == "config.txt":
            f.write("DEBUG=true\nPORT=8080\nHOST=localhost\n")
        elif fname == "data.csv":
            f.write("name,age,city\nAlice,25,Beijing\nBob,30,Shanghai\nCharlie,35,Shenzhen\n")
    print(f"  已创建: {fname}")

# --- cp: 复制文件 ---
print(f"\n# 复制文件 (等价于 cp)")
src_file = os.path.join(demo_dir, "config.txt")
dst_file = os.path.join(demo_dir, "config_backup.txt")
shutil.copy2(src_file, dst_file)  # copy2 保留文件元数据（类似 cp -p）
print(f"  {src_file} -> {dst_file}")

# --- mv: 移动/重命名文件 ---
print(f"\n# 重命名文件 (等价于 mv)")
old_name = os.path.join(demo_dir, "config_backup.txt")
new_name = os.path.join(demo_dir, "config.old.txt")
shutil.move(old_name, new_name)
print(f"  重命名: config_backup.txt -> config.old.txt")

# --- ls: 列出目录内容 ---
print(f"\n# 列出目录内容 (等价于 ls -la)")
if IS_LINUX:
    run_command(f"ls -la {demo_dir}", "使用 ls 命令列出目录")
else:
    # Windows 上使用 Python 模拟 ls -la
    print("  (使用 Python 模拟 ls -la)")
    for item in sorted(os.listdir(demo_dir)):
        item_path = os.path.join(demo_dir, item)
        size = os.path.getsize(item_path)
        is_dir = "d" if os.path.isdir(item_path) else "-"
        print(f"  {is_dir}  {size:>8}  {item}")


# ============================================================
# 第三部分：管道和重定向的 Python 等效操作
# ============================================================

print_section("第三部分：管道和重定向的 Python 等效操作")

# --- cat 文件内容 ---
print("\n# 读取文件内容 (等价于 cat config.txt)")
config_path = os.path.join(demo_dir, "config.txt")
with open(config_path, 'r', encoding='utf-8') as f:
    content = f.read()
print(content)

# --- 管道: cat file | grep "pattern" ---
print("# 管道操作 (等价于 cat data.csv | grep 'Alice')")
data_path = os.path.join(demo_dir, "data.csv")
with open(data_path, 'r', encoding='utf-8') as f:
    for line in f:
        if "Alice" in line:
            print(f"  匹配: {line.strip()}")

# --- 输出重定向: echo "text" > file ---
print("\n# 输出重定向 (等价于 echo 'Hello' > output.txt)")
output_path = os.path.join(demo_dir, "output.txt")
with open(output_path, 'w', encoding='utf-8') as f:
    f.write("Hello from Python!\n")
    f.write("This is line 2\n")
print(f"  已写入: {output_path}")

# --- 追加重定向: echo "text" >> file ---
print("\n# 追加重定向 (等价于 echo 'More text' >> output.txt)")
with open(output_path, 'a', encoding='utf-8') as f:
    f.write("Appended line 3\n")
    f.write("Appended line 4\n")
print(f"  已追加到: {output_path}")

# 读取验证
with open(output_path, 'r', encoding='utf-8') as f:
    print(f"  文件内容:")
    for i, line in enumerate(f, 1):
        print(f"    {i}: {line.strip()}")

# --- 管道链: cat file | grep pattern | wc -l ---
print("\n# 管道链 (等价于 cat data.csv | grep -v 'name' | wc -l)")
print("# 功能: 统计 data.csv 中除标题外的数据行数")
with open(data_path, 'r', encoding='utf-8') as f:
    lines = f.readlines()
# 过滤掉标题行（包含 "name" 的行）
data_lines = [line for line in lines if "name" not in line]
print(f"  数据行数: {len(data_lines)}")

# --- 使用 subprocess 执行真正的管道（Linux 环境） ---
if IS_LINUX:
    print("\n# 在 Linux 上使用 subprocess 执行真正的管道命令")
    run_command(
        f'cat "{data_path}" | grep -v "name" | wc -l',
        "Shell 管道: cat | grep | wc"
    )
else:
    print("\n# [Windows] subprocess 管道示例:")
    # Windows 上也可以用 subprocess 做管道
    # 但语法不同，这里演示 Python 的等效方式
    p1 = subprocess.Popen(
        ['python', '-c', f'print(open(r"{data_path}").read())'],
        stdout=subprocess.PIPE,
        text=True
    )
    p2 = subprocess.Popen(
        ['python', '-c', 'import sys; [print(l,end="") for l in sys.stdin if "name" not in l]'],
        stdin=p1.stdout,
        stdout=subprocess.PIPE,
        text=True
    )
    p1.stdout.close()  # 允许 p1 在 p2 消费完数据后退出
    output = p2.communicate()[0]
    line_count = len([l for l in output.strip().split('\n') if l])
    print(f"  Python 管道结果: {line_count} 行")


# ============================================================
# 第四部分：文件系统遍历 (等价于 find 命令)
# ============================================================

print_section("第四部分：文件系统遍历 (等价于 find 命令)")

# 创建一些额外的文件用于演示
for subdir in ["logs", "logs/archive", "cache"]:
    os.makedirs(os.path.join(demo_dir, subdir), exist_ok=True)

for fname in ["app.log", "error.log", "logs/access.log", "logs/archive/old.log", "cache/temp.tmp"]:
    fpath = os.path.join(demo_dir, fname)
    with open(fpath, 'w', encoding='utf-8') as f:
        f.write(f"# {fname}\n")

# --- Python 版 find: 按文件名搜索 ---
print("\n# 查找所有 .log 文件 (等价于 find . -name '*.log')")
log_files = []
for root, dirs, files in os.walk(demo_dir):
    for fname in files:
        if fname.endswith('.log'):
            full_path = os.path.join(root, fname)
            # 显示相对路径，更清晰
            rel_path = os.path.relpath(full_path, demo_dir)
            log_files.append(rel_path)
            print(f"  {rel_path}")

print(f"  共找到 {len(log_files)} 个 .log 文件")

# --- Python 版 find: 按大小搜索 ---
print("\n# 查找大于 0 字节的文件 (等价于 find . -size +0)")
for root, dirs, files in os.walk(demo_dir):
    for fname in files:
        full_path = os.path.join(root, fname)
        size = os.path.getsize(full_path)
        if size > 0:
            rel_path = os.path.relpath(full_path, demo_dir)
            print(f"  {rel_path} ({size} bytes)")

# --- Python 版 find: 按类型搜索 ---
print("\n# 列出所有目录 (等价于 find . -type d)")
for root, dirs, files in os.walk(demo_dir):
    for d in dirs:
        rel_path = os.path.relpath(os.path.join(root, d), demo_dir)
        print(f"  [目录] {rel_path}")

# --- Linux 上使用真实的 find 命令 ---
if IS_LINUX:
    print("\n# 在 Linux 上使用真正的 find 命令")
    run_command(f'find "{demo_dir}" -name "*.log" -type f', "find 查找所有 .log 文件")


# ============================================================
# 第五部分：包管理概念演示
# ============================================================

print_section("第五部分：包管理概念 (apt/yum)")

print("""
Linux 包管理器对比:

  Ubuntu/Debian (apt):
    sudo apt update              # 更新软件源索引
    sudo apt install nginx -y    # 安装软件
    sudo apt remove nginx        # 卸载软件
    apt search redis             # 搜索软件

  CentOS/Rocky (yum/dnf):
    sudo yum update              # 更新
    sudo yum install nginx -y    # 安装
    sudo yum remove nginx        # 卸载
    yum search redis             # 搜索

Python 中的等价操作 (pip):
    pip install requests         # 安装 Python 包
    pip uninstall requests       # 卸载
    pip search requests          # 搜索 (已禁用)
    pip list                     # 列出已安装的包
""")

# 演示用 subprocess 调用 pip list
print("# 当前已安装的 Python 包（前 10 个）:")
try:
    result = subprocess.run(
        [sys.executable, '-m', 'pip', 'list', '--format=columns'],
        capture_output=True, text=True, encoding='utf-8', errors='replace'
    )
    if result.returncode == 0:
        lines = result.stdout.strip().split('\n')
        # 打印标题和前 10 个包
        for line in lines[:12]:
            print(f"  {line}")
        if len(lines) > 12:
            print(f"  ... 共 {len(lines) - 2} 个包")
except Exception as e:
    print(f"  [错误] 无法获取包列表: {e}")


# ============================================================
# 清理临时文件
# ============================================================

print_section("清理临时文件")

# 删除创建的临时目录
shutil.rmtree(work_dir, ignore_errors=True)
print(f"已清理临时目录: {work_dir}")
print("(等价于 rm -rf，但在 Python 中更安全)")


print(f"\n{'=' * 60}")
print("Demo 1 完成！")
print(f"{'=' * 60}")
print("""
核心收获:
  1. subprocess.run() 是 Python 执行 Shell 命令的标准方式
  2. Python 的 os/shutil 模块可以跨平台替代大部分文件操作命令
  3. 管道操作在 Python 中可以用文件读写 + 字符串处理实现
  4. os.walk() 是 Python 版的 find 命令，可以递归遍历文件系统
  5. 后端开发中常用 subprocess 执行部署脚本、系统管理等任务
""")
