"""
Git 基础操作演示脚本

使用 Python subprocess 模块演示 Git 的核心基础操作：
- 初始化仓库（git init）
- 文件暂存与提交（git add / git commit）
- 查看状态与历史（git status / git log）
- 查看差异（git diff）
- .gitignore 配置效果
- 远程仓库概念演示

运行方式：
    python 1_git_basics.py

前置要求：
    - Python 3.6+
    - 系统已安装 Git（命令行可用 `git` 命令）

原理：
    脚本会在系统临时目录下创建一个隔离的 Git 仓库，
    所有操作都在这个临时仓库中进行，不会影响你的实际项目。
    运行结束后会询问是否删除临时目录。
"""

import os
import sys
import subprocess
import tempfile
import shutil

# ============================================================
# 工具函数
# ============================================================

def run_git(args: list[str], cwd: str, check: bool = True) -> subprocess.CompletedProcess:
    """
    执行 git 命令并返回结果。

    参数：
        args: git 命令参数列表，如 ["add", "."]
        cwd: 工作目录（Git 仓库路径）
        check: 是否在命令失败时抛出异常

    返回：
        subprocess.CompletedProcess 对象
    """
    cmd = ["git"] + args
    result = subprocess.run(
        cmd,
        cwd=cwd,
        capture_output=True,
        text=True,
        # 防止 Windows 中文编码问题
        encoding="utf-8",
        errors="replace",
        check=False,
    )
    if check and result.returncode != 0:
        print(f"  [错误] git {' '.join(args)} 执行失败：")
        print(f"  {result.stderr.strip()}")
    return result


def print_section(title: str) -> None:
    """打印章节标题，带分隔线。"""
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}\n")


def print_output(result: subprocess.CompletedProcess) -> None:
    """打印命令输出（stdout），如果没有输出则提示。"""
    output = result.stdout.strip()
    if output:
        for line in output.splitlines():
            print(f"  {line}")
    else:
        print("  （无输出）")


def print_stderr(result: subprocess.CompletedProcess) -> None:
    """打印命令的 stderr 输出（Git 常把信息输出到 stderr）。"""
    err = result.stderr.strip()
    if err:
        for line in err.splitlines():
            print(f"  {line}")


def write_file(path: str, content: str) -> None:
    """创建或覆盖文件，并写入内容。"""
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"  已创建文件: {os.path.basename(path)}")


# ============================================================
# 检查 Git 是否可用
# ============================================================

def check_git_installed() -> bool:
    """检查系统是否安装了 Git。"""
    try:
        result = subprocess.run(
            ["git", "--version"],
            capture_output=True,
            text=True,
            check=False,
        )
        if result.returncode == 0:
            print(f"✓ 检测到 {result.stdout.strip()}")
            return True
    except FileNotFoundError:
        pass

    print("✗ 未检测到 Git，请先安装 Git：")
    print("  - Windows: https://git-scm.com/download/win")
    print("  - macOS:   brew install git")
    print("  - Linux:   sudo apt install git")
    return False


# ============================================================
# 演示流程
# ============================================================

def demo_init(repo_dir: str) -> None:
    """演示 git init：初始化一个新的 Git 仓库。"""
    print_section("1. git init — 初始化仓库")

    print("在临时目录中初始化 Git 仓库...")
    result = run_git(["init"], cwd=repo_dir)
    print_stderr(result)

    # 配置本地用户信息（不影响全局配置）
    run_git(["config", "user.name", "Demo User"], cwd=repo_dir, check=False)
    run_git(["config", "user.email", "demo@example.com"], cwd=repo_dir, check=False)
    print("  已设置本地用户信息（不影响你的全局配置）")

    # 查看 .git 目录
    git_dir = os.path.join(repo_dir, ".git")
    if os.path.isdir(git_dir):
        contents = os.listdir(git_dir)
        print(f"\n  .git/ 目录内容（Git 仓库的核心数据都在这里）：")
        for item in sorted(contents):
            print(f"    - {item}")


def demo_add_commit(repo_dir: str) -> None:
    """演示 git add 和 git commit：暂存与提交。"""
    print_section("2. git add & git commit — 暂存与提交")

    # 创建一个 Python 文件
    print("创建第一个文件...")
    write_file(
        os.path.join(repo_dir, "hello.py"),
        '"""Hello World 示例"""\n\ndef greet(name: str) -> str:\n    return f"Hello, {name}!"\n\n\nif __name__ == "__main__":\n    print(greet("World"))\n',
    )

    # 查看状态（应该显示未跟踪文件）
    print("\n  → git status（文件还未被 Git 跟踪）：")
    result = run_git(["status"], cwd=repo_dir)
    print_output(result)

    # 暂存文件
    print("\n  → git add hello.py（将文件加入暂存区）：")
    run_git(["add", "hello.py"], cwd=repo_dir)

    print("  → git status（文件已暂存，等待提交）：")
    result = run_git(["status", "-s"], cwd=repo_dir)
    print_output(result)
    print("  提示：A = Added（已暂存的新文件）")

    # 提交
    print("\n  → git commit -m 'init: 添加 hello.py'：")
    result = run_git(["commit", "-m", "init: 添加 hello.py"], cwd=repo_dir)
    print_output(result)

    # 再查看状态（应该是干净的）
    print("\n  → git status（工作区干净了）：")
    result = run_git(["status", "-s"], cwd=repo_dir)
    output = result.stdout.strip()
    print(f"  '{output}'" if output else "  （无输出，说明工作区干净）")


def demo_log(repo_dir: str) -> None:
    """演示 git log：查看提交历史。"""
    print_section("3. git log — 查看提交历史")

    # 再添加一次提交，让历史更丰富
    write_file(
        os.path.join(repo_dir, "utils.py"),
        '"""工具函数模块"""\n\ndef add(a: int, b: int) -> int:\n    """返回两个数的和"""\n    return a + b\n',
    )
    run_git(["add", "utils.py"], cwd=repo_dir)
    run_git(["commit", "-m", "feat: 添加 utils.py 工具模块"], cwd=repo_dir)

    print("  → git log --oneline（简洁模式，每行一个提交）：")
    result = run_git(["log", "--oneline"], cwd=repo_dir)
    print_output(result)

    print("\n  → git log（完整模式，包含作者、日期、详细信息）：")
    result = run_git(["log", "--format=medium", "-2"], cwd=repo_dir)
    print_output(result)


def demo_diff(repo_dir: str) -> None:
    """演示 git diff：查看文件差异。"""
    print_section("4. git diff — 查看文件差异")

    # 修改已有文件
    print("  修改 hello.py（添加一个新函数）...")
    write_file(
        os.path.join(repo_dir, "hello.py"),
        '"""Hello World 示例"""\n\ndef greet(name: str) -> str:\n    return f"Hello, {name}!"\n\n\ndef farewell(name: str) -> str:\n    """告别函数"""\n    return f"Goodbye, {name}!"\n\n\nif __name__ == "__main__":\n    print(greet("World"))\n    print(farewell("World"))\n',
    )

    print("\n  → git diff（工作区 vs 暂存区，还没 add 的改动）：")
    result = run_git(["diff"], cwd=repo_dir)
    print_output(result)
    print("  提示：+ 开头是新增行，- 开头是删除行")

    # 暂存后再看 diff
    run_git(["add", "hello.py"], cwd=repo_dir)
    print("\n  → git diff --staged（暂存区 vs 最新提交）：")
    result = run_git(["diff", "--staged"], cwd=repo_dir)
    print_output(result)

    # 提交这个改动
    run_git(["commit", "-m", "feat: 添加 farewell 函数"], cwd=repo_dir)
    print("\n  已提交修改。")


def demo_gitignore(repo_dir: str) -> None:
    """演示 .gitignore：忽略特定文件。"""
    print_section("5. .gitignore — 忽略不需要跟踪的文件")

    # 创建一些应该被忽略的文件
    print("  创建一些临时文件（日志、缓存、.env）...")
    write_file(os.path.join(repo_dir, "app.log"), "2024-01-01 ERROR: something broke\n")
    write_file(os.path.join(repo_dir, "__pycache__", "hello.cpython-311.pyc"), "binary cache")
    write_file(os.path.join(repo_dir, ".env"), "SECRET_KEY=super_secret_123\n")

    print("\n  → git status（这些文件都显示为未跟踪）：")
    result = run_git(["status", "-s"], cwd=repo_dir)
    print_output(result)

    # 创建 .gitignore
    print("\n  创建 .gitignore 文件，忽略 *.log、__pycache__/、.env：")
    write_file(
        os.path.join(repo_dir, ".gitignore"),
        "# 忽略日志文件\n*.log\n\n# 忽略 Python 缓存\n__pycache__/\n\n# 忽略环境变量（包含敏感信息）\n.env\n",
    )

    print("\n  → git status（被忽略的文件不再显示）：")
    result = run_git(["status", "-s"], cwd=repo_dir)
    print_output(result)
    print("  注意：app.log、__pycache__/、.env 已经消失了！")
    print("  只有 .gitignore 本身显示为未跟踪（它应该被提交到仓库）。")

    # 提交 .gitignore
    run_git(["add", ".gitignore"], cwd=repo_dir)
    run_git(["commit", "-m", "chore: 添加 .gitignore"], cwd=repo_dir)
    print("\n  已提交 .gitignore。")


def demo_remote_concepts(repo_dir: str) -> None:
    """演示远程仓库相关概念（不实际连接远程）。"""
    print_section("6. 远程仓库概念 — remote / push / pull / fetch")

    print("  远程仓库（remote）是托管在服务器上的仓库副本（如 GitHub、GitLab）。")
    print("  常用命令说明：\n")
    print("  git remote add origin <url>   — 关联远程仓库，命名为 'origin'")
    print("  git remote -v                 — 查看所有远程仓库地址")
    print("  git push origin main          — 把本地提交推送到远程")
    print("  git pull origin main          — 拉取远程更新并合并到本地")
    print("  git fetch origin              — 只拉取，不合并（更安全）\n")

    print("  典型工作流：")
    print("  ┌─────────┐    git push     ┌─────────┐")
    print("  │  本地    │ ──────────────→ │  远程    │")
    print("  │  仓库    │ ←────────────── │  仓库    │")
    print("  └─────────┘    git pull     └─────────┘")
    print("                   (= fetch + merge)\n")

    # 展示当前仓库的 remote（应该为空）
    print("  → git remote -v（当前仓库没有配置远程）：")
    result = run_git(["remote", "-v"], cwd=repo_dir)
    output = result.stdout.strip()
    print(f"  '{output}'" if output else "  （无输出，说明没有配置远程仓库）")


def demo_final_summary(repo_dir: str) -> None:
    """展示最终的仓库状态和提交历史。"""
    print_section("7. 最终状态 — 仓库提交历史总览")

    print("  → git log --oneline --all：")
    result = run_git(["log", "--oneline", "--all"], cwd=repo_dir)
    print_output(result)

    print("\n  → 仓库中的文件：")
    for root, dirs, files in os.walk(repo_dir):
        # 排除 .git 目录
        dirs[:] = [d for d in dirs if d != ".git"]
        level = root.replace(repo_dir, "").count(os.sep)
        indent = "  " * level
        print(f"  {indent}{os.path.basename(root)}/")
        sub_indent = "  " * (level + 1)
        for file in sorted(files):
            print(f"  {sub_indent}{file}")


# ============================================================
# 主程序
# ============================================================

def main() -> None:
    print("=" * 60)
    print("  Git 基础操作 — 交互式演示")
    print("=" * 60)

    # 检查 Git
    if not check_git_installed():
        sys.exit(1)

    # 创建临时目录
    repo_dir = tempfile.mkdtemp(prefix="git_demo_")
    print(f"\n临时仓库位置: {repo_dir}")

    try:
        # 按顺序演示各个 Git 操作
        demo_init(repo_dir)
        demo_add_commit(repo_dir)
        demo_log(repo_dir)
        demo_diff(repo_dir)
        demo_gitignore(repo_dir)
        demo_remote_concepts(repo_dir)
        demo_final_summary(repo_dir)

        print_section("演示完成！")
        print("  本次演示涵盖了 Git 的核心基础操作：")
        print("  ✓ git init — 初始化仓库")
        print("  ✓ git add / commit — 暂存与提交")
        print("  ✓ git log — 查看历史")
        print("  ✓ git diff — 查看差异")
        print("  ✓ .gitignore — 忽略文件")
        print("  ✓ 远程仓库概念\n")

    finally:
        # 询问是否清理
        try:
            answer = input(f"是否删除临时目录 {repo_dir}？(Y/n): ").strip().lower()
        except (EOFError, KeyboardInterrupt):
            answer = "y"

        if answer in ("", "y", "yes"):
            shutil.rmtree(repo_dir, ignore_errors=True)
            print("  已删除临时目录。")
        else:
            print(f"  临时目录已保留: {repo_dir}")


if __name__ == "__main__":
    main()
