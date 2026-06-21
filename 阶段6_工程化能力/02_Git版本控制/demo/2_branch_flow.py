"""
Git 分支管理与 Git Flow 演示脚本

使用 Python subprocess 模块演示分支管理相关操作：
- 创建和切换分支（git branch / git checkout / git switch）
- 模拟 Git Flow 工作流（feature → develop → release → main）
- 制造合并冲突并演示如何解决
- 演示 rebase 操作
- 用 ASCII art 展示分支图

运行方式：
    python 2_branch_flow.py

前置要求：
    - Python 3.6+
    - 系统已安装 Git（命令行可用 `git` 命令）

原理：
    脚本会在系统临时目录下创建一个隔离的 Git 仓库，
    所有操作都在这个临时仓库中进行，不会影响你的实际项目。
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
        args: git 命令参数列表，如 ["branch", "-a"]
        cwd: 工作目录（Git 仓库路径）
        check: 是否在命令失败时打印错误信息

    返回：
        subprocess.CompletedProcess 对象
    """
    cmd = ["git"] + args
    result = subprocess.run(
        cmd,
        cwd=cwd,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=False,
    )
    if check and result.returncode != 0:
        print(f"  [错误] git {' '.join(args)} 执行失败：")
        print(f"  {result.stderr.strip()}")
    return result


def print_section(title: str) -> None:
    """打印章节标题。"""
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}\n")


def print_output(result: subprocess.CompletedProcess) -> None:
    """打印命令的 stdout 输出。"""
    output = result.stdout.strip()
    if output:
        for line in output.splitlines():
            print(f"  {line}")
    else:
        print("  （无输出）")


def print_graph(repo_dir: str) -> None:
    """用 git log --graph 打印分支图。"""
    result = run_git(
        ["log", "--oneline", "--graph", "--all", "--decorate"],
        cwd=repo_dir,
    )
    print_output(result)


def write_file(path: str, content: str) -> None:
    """写入文件内容。"""
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)


def read_file(path: str) -> str:
    """读取文件内容。"""
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def commit_file(repo_dir: str, filename: str, content: str, message: str) -> None:
    """
    辅助函数：创建/修改文件、暂存并提交。
    减少重复代码。
    """
    write_file(os.path.join(repo_dir, filename), content)
    run_git(["add", filename], cwd=repo_dir)
    run_git(["commit", "-m", message], cwd=repo_dir)


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

    print("✗ 未检测到 Git，请先安装：https://git-scm.com/downloads")
    return False


# ============================================================
# 演示流程
# ============================================================

def setup_repo(repo_dir: str) -> None:
    """初始化仓库并创建初始提交。"""
    print_section("0. 准备工作 — 初始化仓库")

    run_git(["init"], cwd=repo_dir)
    run_git(["config", "user.name", "Demo User"], cwd=repo_dir)
    run_git(["config", "user.email", "demo@example.com"], cwd=repo_dir)

    # 确保默认分支名是 main
    run_git(["checkout", "-b", "main"], cwd=repo_dir, check=False)

    # 创建初始文件
    commit_file(
        repo_dir,
        "README.md",
        "# My Project\n\n这是一个演示项目。\n",
        "init: 初始化项目",
    )
    print("  ✓ 仓库已初始化，创建了首次提交")

    # 打印当前分支
    result = run_git(["branch"], cwd=repo_dir)
    print("\n  当前分支列表：")
    print_output(result)


def demo_branch_basics(repo_dir: str) -> None:
    """演示基础的分支操作。"""
    print_section("1. 基础分支操作 — 创建、切换、查看")

    # 创建分支
    print("  → git branch feature/login（创建新分支，但不切换）：")
    run_git(["branch", "feature/login"], cwd=repo_dir)
    result = run_git(["branch"], cwd=repo_dir)
    print_output(result)
    print("  注意：* 号在 main 前面，说明我们仍在 main 分支上。\n")

    # 切换到新分支
    print("  → git checkout feature/login（切换到新分支）：")
    run_git(["checkout", "feature/login"], cwd=repo_dir)
    result = run_git(["branch"], cwd=repo_dir)
    print_output(result)
    print("  现在 * 号移到了 feature/login 前面。\n")

    # 在新分支上做开发
    print("  在 feature/login 分支上创建登录模块...")
    commit_file(
        repo_dir,
        "login.py",
        '"""用户登录模块"""\n\ndef login(username: str, password: str) -> bool:\n    """验证用户名和密码"""\n    # 简单演示，实际应该查询数据库\n    return username == "admin" and password == "123456"\n',
        "feat: 添加登录模块",
    )

    # 切回 main 看看——login.py 不存在
    print("\n  → git checkout main（切回 main 分支）：")
    run_git(["checkout", "main"], cwd=repo_dir)
    login_path = os.path.join(repo_dir, "login.py")
    print(f"  login.py 是否存在？ {os.path.exists(login_path)}")
    print("  这就是分支隔离——main 分支看不到 feature 分支的改动。\n")

    # 合并
    print("  → git merge feature/login（把功能合并回 main）：")
    result = run_git(["merge", "feature/login"], cwd=repo_dir)
    print_output(result)
    print(f"  合并后 login.py 是否存在？ {os.path.exists(login_path)}")

    print("\n  分支图：")
    print_graph(repo_dir)


def demo_git_flow(repo_dir: str) -> None:
    """模拟 Git Flow 工作流。"""
    print_section("2. Git Flow 工作流 — feature → develop → release → main")

    print("  Git Flow 分支结构：")
    print("  ┌──────────────────────────────────────────────────────┐")
    print("  │ main ────────────────────● (v1.0.0)                 │")
    print("  │                         ↗                            │")
    print("  │ release/1.0 ──────●───●                              │")
    print("  │                    ↗                                 │")
    print("  │ develop ──●───●───●───●───●                          │")
    print("  │          ↗           ↗                               │")
    print("  │ feature ──●───●   feature ──●                        │")
    print("  └──────────────────────────────────────────────────────┘\n")

    # --- Step 1: 创建 develop 分支 ---
    print("  [Step 1] 从 main 创建 develop 分支...")
    run_git(["checkout", "-b", "develop"], cwd=repo_dir)
    commit_file(
        repo_dir,
        "config.py",
        '"""项目配置"""\nDEBUG = True\nDATABASE_URL = "sqlite:///dev.db"\n',
        "chore: 添加项目配置",
    )

    # --- Step 2: 创建两个 feature 分支 ---
    print("  [Step 2] 创建 feature/user-profile 分支，开发用户资料功能...")
    run_git(["checkout", "-b", "feature/user-profile"], cwd=repo_dir)
    commit_file(
        repo_dir,
        "user.py",
        '"""用户模块"""\n\nclass User:\n    def __init__(self, name: str, email: str):\n        self.name = name\n        self.email = email\n\n    def profile(self) -> dict:\n        return {"name": self.name, "email": self.email}\n',
        "feat: 添加 User 类",
    )

    print("  [Step 3] 合并 feature/user-profile 到 develop...")
    run_git(["checkout", "develop"], cwd=repo_dir)
    run_git(["merge", "--no-ff", "feature/user-profile", "-m", "Merge feature/user-profile into develop"], cwd=repo_dir)
    run_git(["branch", "-d", "feature/user-profile"], cwd=repo_dir)

    print("  [Step 4] 创建 feature/search 分支，开发搜索功能...")
    run_git(["checkout", "-b", "feature/search"], cwd=repo_dir)
    commit_file(
        repo_dir,
        "search.py",
        '"""搜索模块"""\n\ndef search(query: str) -> list:\n    """简单搜索演示"""\n    return [f"result for: {query}"]\n',
        "feat: 添加搜索功能",
    )

    print("  [Step 5] 合并 feature/search 到 develop...")
    run_git(["checkout", "develop"], cwd=repo_dir)
    run_git(["merge", "--no-ff", "feature/search", "-m", "Merge feature/search into develop"], cwd=repo_dir)
    run_git(["branch", "-d", "feature/search"], cwd=repo_dir)

    # --- Step 3: 创建 release 分支 ---
    print("  [Step 6] 从 develop 创建 release/1.0.0 分支...")
    run_git(["checkout", "-b", "release/1.0.0"], cwd=repo_dir)
    commit_file(
        repo_dir,
        "CHANGELOG.md",
        "# Changelog\n\n## v1.0.0\n- 添加用户资料功能\n- 添加搜索功能\n",
        "docs: 添加 CHANGELOG",
    )

    # --- Step 4: 发布到 main ---
    print("  [Step 7] 合并 release/1.0.0 到 main，打 tag...")
    run_git(["checkout", "main"], cwd=repo_dir)
    run_git(["merge", "--no-ff", "release/1.0.0", "-m", "Release v1.0.0"], cwd=repo_dir)
    run_git(["tag", "-a", "v1.0.0", "-m", "Release v1.0.0"], cwd=repo_dir)

    # 把 release 的改动也合并回 develop
    print("  [Step 8] 把 release 的改动同步回 develop...")
    run_git(["checkout", "develop"], cwd=repo_dir)
    run_git(["merge", "--no-ff", "release/1.0.0", "-m", "Merge release/1.0.0 back to develop"], cwd=repo_dir)
    run_git(["branch", "-d", "release/1.0.0"], cwd=repo_dir)

    print("\n  Git Flow 完成后的分支图：")
    print_graph(repo_dir)

    print("\n  标签列表：")
    result = run_git(["tag", "-l"], cwd=repo_dir)
    print_output(result)


def demo_conflict(repo_dir: str) -> None:
    """制造合并冲突并演示如何解决。"""
    print_section("3. 合并冲突 — 产生原因与解决方法")

    print("  冲突产生条件：两个分支修改了同一文件的同一区域。\n")

    # 从 main 创建两个分支，各自修改 config.py 的同一行
    run_git(["checkout", "main"], cwd=repo_dir)

    print("  [Step 1] 创建 branch-a，修改 config.py...")
    run_git(["checkout", "-b", "branch-a"], cwd=repo_dir)
    commit_file(
        repo_dir,
        "config.py",
        '"""项目配置"""\nDEBUG = False  # branch-a: 关闭调试模式\nDATABASE_URL = "sqlite:///prod.db"\n',
        "feat(branch-a): 修改配置为生产环境",
    )

    print("  [Step 2] 回到 main，创建 branch-b，也修改 config.py...")
    run_git(["checkout", "main"], cwd=repo_dir)
    run_git(["checkout", "-b", "branch-b"], cwd=repo_dir)
    commit_file(
        repo_dir,
        "config.py",
        '"""项目配置"""\nDEBUG = True  # branch-b: 开启调试模式\nDATABASE_URL = "sqlite:///dev.db"\nLOG_LEVEL = "DEBUG"\n',
        "feat(branch-b): 修改配置为开发环境",
    )

    print("  [Step 3] 切回 main，先合并 branch-a...")
    run_git(["checkout", "main"], cwd=repo_dir)
    result_a = run_git(["merge", "branch-a"], cwd=repo_dir)
    print_output(result_a)

    print("\n  [Step 4] 再合并 branch-b（将产生冲突！）...")
    result_b = run_git(["merge", "branch-b"], cwd=repo_dir, check=False)
    print_output(result_b)
    print_stderr_if_any(result_b)

    # 读取冲突文件展示冲突标记
    print("\n  冲突文件 config.py 的内容（注意冲突标记）：")
    print("  " + "-" * 40)
    conflict_content = read_file(os.path.join(repo_dir, "config.py"))
    for line in conflict_content.splitlines():
        print(f"  {line}")
    print("  " + "-" * 40)

    print("\n  [Step 5] 手动解决冲突（合并两个分支的优点）...")
    # 写入解决后的内容
    resolved_content = (
        '"""项目配置"""\n'
        'import os\n'
        'DEBUG = os.getenv("DEBUG", "True") == "True"\n'
        'DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///dev.db")\n'
        'LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")\n'
    )
    write_file(os.path.join(repo_dir, "config.py"), resolved_content)

    print("  解决后的 config.py：")
    print("  " + "-" * 40)
    for line in resolved_content.splitlines():
        print(f"  {line}")
    print("  " + "-" * 40)

    # 标记冲突已解决并提交
    run_git(["add", "config.py"], cwd=repo_dir)
    run_git(["commit", "-m", "merge: 解决 config.py 冲突，使用环境变量"], cwd=repo_dir)
    print("\n  ✓ 冲突已解决并提交！")

    # 清理临时分支
    run_git(["branch", "-d", "branch-a"], cwd=repo_dir)
    run_git(["branch", "-d", "branch-b"], cwd=repo_dir)

    print("\n  冲突解决后的分支图：")
    print_graph(repo_dir)


def print_stderr_if_any(result: subprocess.CompletedProcess) -> None:
    """打印 stderr（Git 经常把提示信息输出到 stderr）。"""
    err = result.stderr.strip()
    if err:
        for line in err.splitlines():
            print(f"  {line}")


def demo_rebase(repo_dir: str) -> None:
    """演示 rebase 操作。"""
    print_section("4. Rebase — 变基操作")

    print("  Rebase 把分支的提交'摘下来'，重新接到目标分支最新提交之后。")
    print("  对比：merge 创建合并提交，rebase 改写提交历史使其线性。\n")

    # 在 main 上做一些提交
    run_git(["checkout", "main"], cwd=repo_dir)
    commit_file(
        repo_dir,
        "main_file.txt",
        "这是 main 分支的文件\n版本 1\n",
        "main: 更新 1",
    )

    # 创建 feature 分支
    run_git(["checkout", "-b", "feature/rebase-demo"], cwd=repo_dir)
    commit_file(
        repo_dir,
        "feature_file.txt",
        "这是 feature 分支的文件\n",
        "feature: 新功能 A",
    )
    commit_file(
        repo_dir,
        "feature_file.txt",
        "这是 feature 分支的文件\n第二行内容\n",
        "feature: 新功能 B",
    )

    # 回到 main 再做一个提交（模拟其他人也在开发）
    run_git(["checkout", "main"], cwd=repo_dir)
    commit_file(
        repo_dir,
        "main_file.txt",
        "这是 main 分支的文件\n版本 1\n版本 2（其他人添加的）\n",
        "main: 其他人的更新",
    )

    print("  Rebase 前的分支图（feature 和 main 已经分叉）：")
    print_graph(repo_dir)

    # 执行 rebase
    print("\n  → git checkout feature/rebase-demo && git rebase main")
    run_git(["checkout", "feature/rebase-demo"], cwd=repo_dir)
    result = run_git(["rebase", "main"], cwd=repo_dir, check=False)
    print_output(result)
    print_stderr_if_any(result)

    print("\n  Rebase 后的分支图（feature 的提交被重新应用到 main 最新提交之后）：")
    print_graph(repo_dir)

    print("\n  注意：rebase 后历史变成了线性的！")
    print("  feature 的提交看起来是在 main 最新提交之后才做的。")
    print("  ⚠ 黄金法则：绝对不要在公共分支上 rebase！")

    # 清理
    run_git(["checkout", "main"], cwd=repo_dir)
    run_git(["merge", "feature/rebase-demo"], cwd=repo_dir)
    run_git(["branch", "-d", "feature/rebase-demo"], cwd=repo_dir)


def demo_tag(repo_dir: str) -> None:
    """演示 tag 标签操作。"""
    print_section("5. Tag — 标签管理")

    run_git(["checkout", "main"], cwd=repo_dir)

    # 创建附注标签
    print("  → git tag -a v1.0.0 -m 'Release v1.0.0'：")
    # 可能已经有 v1.0.0 了（Git Flow 演示中创建的），检查一下
    existing = run_git(["tag", "-l", "v1.0.0"], cwd=repo_dir)
    if not existing.stdout.strip():
        run_git(["tag", "-a", "v1.0.0", "-m", "Release v1.0.0"], cwd=repo_dir)
        print("  ✓ 已创建标签 v1.0.0")
    else:
        print("  （v1.0.0 已在 Git Flow 演示中创建）")

    # 再创建一个标签
    run_git(["tag", "-a", "v2.0.0", "-m", "Release v2.0.0: 包含搜索和冲突修复"], cwd=repo_dir)
    print("  ✓ 已创建标签 v2.0.0")

    # 列出所有标签
    print("\n  → git tag -l（列出所有标签）：")
    result = run_git(["tag", "-l"], cwd=repo_dir)
    print_output(result)

    # 查看标签详情
    print("\n  → git show v2.0.0（查看标签详情）：")
    result = run_git(["show", "v2.0.0"], cwd=repo_dir)
    print_output(result)


def demo_final(repo_dir: str) -> None:
    """展示最终的完整分支图。"""
    print_section("6. 最终总览 — 完整分支图")

    print("  完整的仓库提交历史：\n")
    print_graph(repo_dir)

    print("\n  所有分支：")
    result = run_git(["branch", "-a"], cwd=repo_dir)
    print_output(result)

    print("\n  所有标签：")
    result = run_git(["tag", "-l"], cwd=repo_dir)
    print_output(result)


# ============================================================
# 主程序
# ============================================================

def main() -> None:
    print("=" * 60)
    print("  Git 分支管理与 Git Flow — 交互式演示")
    print("=" * 60)

    # 检查 Git
    if not check_git_installed():
        sys.exit(1)

    # 创建临时目录
    repo_dir = tempfile.mkdtemp(prefix="git_branch_demo_")
    print(f"\n临时仓库位置: {repo_dir}")

    try:
        # 按顺序演示
        setup_repo(repo_dir)
        demo_branch_basics(repo_dir)
        demo_git_flow(repo_dir)
        demo_conflict(repo_dir)
        demo_rebase(repo_dir)
        demo_tag(repo_dir)
        demo_final(repo_dir)

        print_section("演示完成！")
        print("  本次演示涵盖了 Git 分支管理的核心操作：")
        print("  ✓ 创建、切换、合并分支")
        print("  ✓ Git Flow 完整工作流")
        print("  ✓ 合并冲突的产生与解决")
        print("  ✓ Rebase 变基操作")
        print("  ✓ Tag 标签管理\n")

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
