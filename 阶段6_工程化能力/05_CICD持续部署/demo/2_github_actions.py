"""
GitHub Actions Workflow YAML 生成与解析演示

本脚本演示以下内容：
1. 用 Python 生成 GitHub Actions Workflow YAML 文件
2. 解析 YAML 结构并讲解每个字段的作用
3. 模拟 Workflow 的触发和执行流程
4. 展示 Secrets 管理的概念

运行方式：
    python 2_github_actions.py

依赖：
    pip install pyyaml    # 用于 YAML 解析（标准库无此功能）

学习目标：
    - 理解 GitHub Actions Workflow YAML 的完整结构
    - 掌握 name、on、env、jobs、steps 等关键字段
    - 了解 Secrets 的安全管理机制
    - 能够用代码动态生成 Workflow 配置
"""

import json
import time
import sys

# 尝试导入 yaml，如果未安装则提示
try:
    import yaml
except ImportError:
    print("需要安装 PyYAML 库：pip install pyyaml")
    print("尝试使用 json 模块作为替代方案...")
    yaml = None


# ========================= Workflow 生成器 =========================

class WorkflowGenerator:
    """GitHub Actions Workflow YAML 生成器

    用 Python 字典构建 Workflow 结构，然后序列化为 YAML 格式。
    这比手写 YAML 更不容易出错（缩进问题），也方便动态生成。
    """

    def __init__(self, name: str):
        """
        初始化 Workflow 生成器。

        Args:
            name: Workflow 名称，显示在 GitHub Actions 页面
        """
        self.workflow = {
            "name": name,
            "on": {},       # 触发条件
            "env": {},      # 全局环境变量
            "jobs": {},     # 作业定义
        }

    def add_trigger_push(self, branches: list[str] | None = None):
        """
        添加 push 触发条件。

        Args:
            branches: 监听的分支列表，None 表示所有分支
        """
        push_config = {}
        if branches:
            push_config["branches"] = branches
        self.workflow["on"]["push"] = push_config if push_config else None

    def add_trigger_pull_request(self, branches: list[str] | None = None):
        """
        添加 pull_request 触发条件。

        Args:
            branches: 监听的目标分支列表（PR 合并到的分支）
        """
        pr_config = {}
        if branches:
            pr_config["branches"] = branches
        self.workflow["on"]["pull_request"] = pr_config if pr_config else None

    def add_trigger_schedule(self, cron_expressions: list[str]):
        """
        添加定时触发条件（cron 表达式）。

        Args:
            cron_expressions: cron 表达式列表
                格式: "分 时 日 月 周几"（UTC 时间）
                示例: "0 2 * * *" 表示每天凌晨 2 点
        """
        self.workflow["on"]["schedule"] = [
            {"cron": expr} for expr in cron_expressions
        ]

    def add_trigger_manual(self, inputs: dict | None = None):
        """
        添加手动触发条件（workflow_dispatch）。

        Args:
            inputs: 手动触发时的输入参数定义
        """
        dispatch = {}
        if inputs:
            dispatch["inputs"] = inputs
        self.workflow["on"]["workflow_dispatch"] = dispatch if dispatch else None

    def set_global_env(self, env_vars: dict[str, str]):
        """
        设置全局环境变量（所有 Job 共享）。

        Args:
            env_vars: 环境变量键值对
        """
        self.workflow["env"] = env_vars

    def add_job(self, job_id: str, job_config: dict):
        """
        添加一个 Job。

        Args:
            job_id: Job 的唯一标识符（如 "test", "build", "deploy"）
            job_config: Job 配置字典，包含 runs-on, steps, needs 等
        """
        self.workflow["jobs"][job_id] = job_config

    def to_yaml(self) -> str:
        """
        将 Workflow 序列化为 YAML 字符串。

        Returns:
            YAML 格式的 Workflow 配置
        """
        if yaml is None:
            # 如果没有 PyYAML，用 json 近似展示
            return json.dumps(self.workflow, indent=2, ensure_ascii=False)
        return yaml.dump(
            self.workflow,
            default_flow_style=False,
            allow_unicode=True,
            sort_keys=False,
            width=120,
        )

    def save(self, filepath: str):
        """
        保存 Workflow 到文件。

        Args:
            filepath: 文件路径（如 .github/workflows/ci.yml）
        """
        content = self.to_yaml()
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"Workflow 已保存到: {filepath}")


# ========================= YAML 解析器 =========================

class WorkflowParser:
    """GitHub Actions Workflow YAML 解析器

    解析 YAML 文件并以人类可读的方式展示每个字段的含义。
    """

    # Workflow 关键字段说明
    FIELD_DESCRIPTIONS = {
        "name": "Workflow 名称，显示在 GitHub Actions 页面和 PR 状态检查中",
        "on": "触发条件定义，决定什么事件会启动这个 Workflow",
        "on.push": "代码推送触发：当 git push 到指定分支/路径时触发",
        "on.pull_request": "PR 触发：当 Pull Request 创建或更新时触发",
        "on.schedule": "定时触发：按 cron 表达式定时执行（UTC 时间）",
        "on.workflow_dispatch": "手动触发：允许在 GitHub 页面手动运行",
        "env": "全局环境变量，所有 Job 和 Step 都能访问",
        "jobs": "作业定义，一个 Workflow 可以包含多个 Job",
        "jobs.*.runs-on": "Runner 环境，指定 Job 在什么系统上运行",
        "jobs.*.needs": "Job 依赖关系，指定当前 Job 必须等哪些 Job 完成",
        "jobs.*.if": "条件表达式，决定是否执行这个 Job",
        "jobs.*.steps": "步骤列表，Job 中最小的执行单元",
        "steps.*.uses": "引用预定义 Action（来自 GitHub Marketplace）",
        "steps.*.run": "执行 Shell 命令",
        "steps.*.with": "传递给 Action 的参数",
        "steps.*.env": "Step 级别的环境变量（仅当前 Step 可用）",
    }

    def __init__(self, yaml_content: str):
        """
        初始化解析器。

        Args:
            yaml_content: YAML 格式的字符串
        """
        if yaml is None:
            self.data = json.loads(yaml_content)
        else:
            self.data = yaml.safe_load(yaml_content)

    def explain_structure(self):
        """以结构化方式解释 Workflow 的每个字段"""
        print("\n" + "=" * 60)
        print("  📖 Workflow YAML 结构解析")
        print("=" * 60)

        # 解释 name
        name = self.data.get("name", "未命名")
        self._explain_field("name", name)

        # 解释 on（触发条件）
        print(f"\n  {'─' * 56}")
        triggers = self.data.get("on", {})
        self._explain_field("on", f"{len(triggers)} 个触发条件")
        if isinstance(triggers, dict):
            for trigger_name, trigger_config in triggers.items():
                full_key = f"on.{trigger_name}"
                desc = self.FIELD_DESCRIPTIONS.get(full_key, f"触发条件: {trigger_name}")
                print(f"    🔹 {Colors.BOLD}{trigger_name}{Colors.RESET}")
                print(f"       说明: {desc}")
                if trigger_config and isinstance(trigger_config, dict):
                    for k, v in trigger_config.items():
                        print(f"       {k}: {v}")

        # 解释 env
        print(f"\n  {'─' * 56}")
        env_vars = self.data.get("env", {})
        self._explain_field("env", f"{len(env_vars)} 个全局环境变量")
        for key, value in env_vars.items():
            print(f"    {Colors.CYAN}{key}{Colors.RESET} = {value}")

        # 解释 jobs
        print(f"\n  {'─' * 56}")
        jobs = self.data.get("jobs", {})
        self._explain_field("jobs", f"{len(jobs)} 个作业")
        for job_id, job_config in jobs.items():
            self._explain_job(job_id, job_config)

    def _explain_field(self, field: str, value: str):
        """打印单个字段的解释"""
        desc = self.FIELD_DESCRIPTIONS.get(field, "")
        print(f"\n  {Colors.BOLD}📌 {field}{Colors.RESET}: {value}")
        if desc:
            print(f"     {Colors.DIM}→ {desc}{Colors.RESET}")

    def _explain_job(self, job_id: str, config: dict):
        """详细解释一个 Job 的结构"""
        print(f"\n    {Colors.BOLD}{Colors.BLUE}┌─ Job: {job_id}{Colors.RESET}")

        # runs-on
        runs_on = config.get("runs-on", "ubuntu-latest")
        print(f"    {Colors.DIM}│{Colors.RESET}  runs-on: {runs_on}")
        print(f"    {Colors.DIM}│{Colors.RESET}  {Colors.DIM}→ {self.FIELD_DESCRIPTIONS['jobs.*.runs-on']}{Colors.RESET}")

        # needs
        needs = config.get("needs", [])
        if needs:
            print(f"    {Colors.DIM}│{Colors.RESET}  needs: {needs}")
            print(f"    {Colors.DIM}│{Colors.RESET}  {Colors.DIM}→ {self.FIELD_DESCRIPTIONS['jobs.*.needs']}{Colors.RESET}")

        # if
        condition = config.get("if", "")
        if condition:
            print(f"    {Colors.DIM}│{Colors.RESET}  if: {condition}")
            print(f"    {Colors.DIM}│{Colors.RESET}  {Colors.DIM}→ {self.FIELD_DESCRIPTIONS['jobs.*.if']}{Colors.RESET}")

        # steps
        steps = config.get("steps", [])
        print(f"    {Colors.DIM}│{Colors.RESET}  steps: {len(steps)} 个步骤")
        for i, step in enumerate(steps):
            step_name = step.get("name", f"Step {i + 1}")
            if "uses" in step:
                step_type = f"uses: {step['uses']}"
                desc = self.FIELD_DESCRIPTIONS["steps.*.uses"]
            elif "run" in step:
                # 只显示命令的第一行
                cmd_first_line = step["run"].split("\n")[0][:40]
                step_type = f"run: {cmd_first_line}..."
                desc = self.FIELD_DESCRIPTIONS["steps.*.run"]
            else:
                step_type = "unknown"
                desc = ""

            print(f"    {Colors.DIM}│{Colors.RESET}    {i + 1}. {Colors.BOLD}{step_name}{Colors.RESET}")
            print(f"    {Colors.DIM}│{Colors.RESET}       {step_type}")
            if desc:
                print(f"    {Colors.DIM}│{Colors.RESET}       {Colors.DIM}→ {desc}{Colors.RESET}")

        print(f"    {Colors.DIM}└─{'─' * 40}{Colors.RESET}")


# ========================= 模拟执行引擎 =========================

class WorkflowSimulator:
    """模拟 GitHub Actions Workflow 的触发和执行流程"""

    # 终端颜色
    GREEN = "\033[92m"
    RED = "\033[91m"
    YELLOW = "\033[93m"
    BLUE = "\033[94m"
    CYAN = "\033[96m"
    BOLD = "\033[1m"
    DIM = "\033[2m"
    RESET = "\033[0m"

    def simulate_event(self, event_type: str, details: dict):
        """
        模拟一个触发事件。

        Args:
            event_type: 事件类型（push, pull_request, schedule 等）
            details: 事件详情（分支、commit 等）
        """
        print(f"\n{self.BOLD}{self.CYAN}{'=' * 60}")
        print(f"  🔔 Event Triggered: {event_type}")
        print(f"{'=' * 60}{self.RESET}\n")

        for key, value in details.items():
            print(f"  {self.DIM}{key}:{self.RESET} {value}")
        print()

    def simulate_job(self, job_id: str, config: dict) -> bool:
        """
        模拟一个 Job 的执行。

        Args:
            job_id: Job ID
            config: Job 配置

        Returns:
            True 表示成功，False 表示失败
        """
        runs_on = config.get("runs-on", "ubuntu-latest")
        print(f"  {self.BOLD}▶ Job: {job_id}{self.RESET} (runner: {runs_on})")

        # 模拟 Runner 分配
        print(f"    {self.DIM}⏳ Allocating runner ({runs_on})...{self.RESET}")
        time.sleep(0.3)

        steps = config.get("steps", [])
        for i, step in enumerate(steps):
            step_name = step.get("name", f"Step {i + 1}")
            print(f"    {self.BLUE}[{i + 1}/{len(steps)}]{self.RESET} {step_name}")

            if "uses" in step:
                print(f"      {self.DIM}→ Downloading action: {step['uses']}{self.RESET}")
            elif "run" in step:
                cmd = step["run"].split("\n")[0]
                print(f"      {self.DIM}$ {cmd}{self.RESET}")

            time.sleep(0.3)
            print(f"      {self.GREEN}✓ Done{self.RESET}")

        print(f"  {self.GREEN}✓ Job '{job_id}' completed successfully{self.RESET}\n")
        return True


# ========================= Secrets 管理演示 =========================

class SecretsDemo:
    """演示 GitHub Actions 的 Secrets 管理机制"""

    @staticmethod
    def explain_secrets():
        """解释 Secrets 的概念和使用方式"""
        print(f"\n{Colors.BOLD}{'=' * 60}")
        print("  🔐 GitHub Actions Secrets 管理")
        print(f"{'=' * 60}{Colors.RESET}")

        print(f"""
  {Colors.BOLD}什么是 Secrets？{Colors.RESET}
  Secrets 是加密的敏感信息（密码、密钥、Token 等），
  存储在 GitHub 仓库设置中，通过环境变量注入到 Workflow。

  {Colors.BOLD}三级作用域：{Colors.RESET}
  ┌────────────────────────────────────────────────────┐
  │  Organization Secrets  →  组织内所有仓库可用       │
  │       ↓ 继承                                        │
  │  Repository Secrets    →  单个仓库内所有 Workflow   │
  │       ↓ 继承                                        │
  │  Environment Secrets   →  只限特定环境（如 prod）   │
  └────────────────────────────────────────────────────┘

  {Colors.BOLD}使用方式：{Colors.RESET}
  1. 在 GitHub 仓库 → Settings → Secrets → Actions 中添加
  2. 在 YAML 中通过 ${{{{ secrets.SECRET_NAME }}}} 引用
  3. 日志中自动遮蔽（显示为 ***）

  {Colors.BOLD}示例配置：{Colors.RESET}
""")

        # 展示 Secrets 使用的 YAML 示例
        example = {
            "steps": [{
                "name": "Deploy to server",
                "env": {
                    "DATABASE_URL": "${{ secrets.DATABASE_URL }}",
                    "SSH_KEY": "${{ secrets.SSH_PRIVATE_KEY }}",
                    "API_KEY": "${{ secrets.API_KEY }}",
                },
                "run": "python deploy.py"
            }]
        }

        if yaml:
            print(yaml.dump(example, default_flow_style=False, allow_unicode=True, sort_keys=False))
        else:
            print(json.dumps(example, indent=2, ensure_ascii=False))

        print(f"""
  {Colors.BOLD}⚠️ 安全注意事项：{Colors.RESET}
  ✗ 永远不要把密钥写在代码或 YAML 文件里
  ✗ 不要在日志中打印 Secrets 的值
  ✓ 使用 Environment Secrets 区分 staging 和 production
  ✓ 定期轮换密钥（Rotate Secrets）
  ✓ 使用最小权限原则，只给 Workflow 需要的权限
""")

    @staticmethod
    def simulate_secret_injection():
        """模拟 Secrets 注入过程"""
        print(f"\n{Colors.BOLD}🔄 模拟 Secrets 注入过程：{Colors.RESET}\n")

        # 模拟 Secrets 存储（实际是 GitHub 加密存储）
        secrets_store = {
            "DATABASE_URL": "postgresql://user:***@db.example.com:5432/prod",
            "SSH_PRIVATE_KEY": "-----BEGIN RSA PRIVATE KEY-----\n***\n-----END RSA PRIVATE KEY-----",
            "API_KEY": "sk-proj-***-***-***",
            "SERVER_HOST": "192.168.1.100",
        }

        print("  📦 GitHub Secrets Store（加密存储）:")
        for name in secrets_store:
            print(f"     {Colors.CYAN}{name}{Colors.RESET} = ***（已加密）")

        print(f"\n  🚀 Workflow 执行时，Secrets 被注入为环境变量：")
        for name, value in secrets_store.items():
            # 模拟注入：显示真实值但在日志中被遮蔽
            masked = value[:5] + "***" + value[-5:] if len(value) > 10 else "***"
            print(f"     export {name}=\"{masked}\"")

        print(f"\n  📋 日志输出中的 Secrets 自动遮蔽：")
        print(f"     $ echo $DATABASE_URL")
        print(f"     postgresql://user:***@db.example.com:5432/prod")
        print(f"     {Colors.DIM}（GitHub Actions 自动将 Secret 值替换为 ***）{Colors.RESET}")


# ========================= 主程序 =========================

# 复用颜色定义
class Colors:
    GREEN = "\033[92m"
    RED = "\033[91m"
    YELLOW = "\033[93m"
    BLUE = "\033[94m"
    CYAN = "\033[96m"
    BOLD = "\033[1m"
    DIM = "\033[2m"
    RESET = "\033[0m"


def create_python_backend_workflow() -> WorkflowGenerator:
    """
    创建一个完整的 Python 后端 CI/CD Workflow。

    这个 Workflow 包含：
    - push 和 PR 触发
    - 测试 Job（lint + pytest）
    - 构建 Job（Docker 镜像）
    - 部署 Job（SSH 远程部署）
    """
    gen = WorkflowGenerator("Python Backend CI/CD")

    # 配置触发条件
    gen.add_trigger_push(branches=["main", "develop"])
    gen.add_trigger_pull_request(branches=["main"])
    gen.add_trigger_manual(inputs={
        "environment": {
            "description": "选择部署环境",
            "required": True,
            "default": "staging",
            "type": "choice",
            "options": ["staging", "production"],
        }
    })

    # 配置全局环境变量
    gen.set_global_env({
        "PYTHON_VERSION": "3.11",
        "REGISTRY": "ghcr.io",
    })

    # Job 1: 测试
    gen.add_job("test", {
        "name": "Run Tests",
        "runs-on": "ubuntu-latest",
        "timeout-minutes": 15,
        "steps": [
            {
                "name": "Checkout code",
                "uses": "actions/checkout@v4",
            },
            {
                "name": "Set up Python",
                "uses": "actions/setup-python@v5",
                "with": {
                    "python-version": "${{ env.PYTHON_VERSION }}",
                    "cache": "pip",
                },
            },
            {
                "name": "Install dependencies",
                "run": "pip install -r requirements.txt && pip install pytest",
            },
            {
                "name": "Run tests",
                "run": "pytest tests/ -v --cov=src",
                "env": {
                    "DATABASE_URL": "sqlite:///./test.db",
                },
            },
        ],
    })

    # Job 2: 构建（依赖测试通过）
    gen.add_job("build", {
        "name": "Build Docker Image",
        "runs-on": "ubuntu-latest",
        "needs": ["test"],
        "if": "github.ref == 'refs/heads/main'",
        "steps": [
            {
                "name": "Checkout code",
                "uses": "actions/checkout@v4",
            },
            {
                "name": "Build and push",
                "uses": "docker/build-push-action@v5",
                "with": {
                    "context": ".",
                    "push": True,
                    "tags": "${{ env.REGISTRY }}/${{ github.repository }}:${{ github.sha }}",
                },
            },
        ],
    })

    # Job 3: 部署（依赖构建通过）
    gen.add_job("deploy", {
        "name": "Deploy to Server",
        "runs-on": "ubuntu-latest",
        "needs": ["build"],
        "environment": {"name": "production"},
        "steps": [
            {
                "name": "Deploy via SSH",
                "uses": "appleboy/ssh-action@v1",
                "with": {
                    "host": "${{ secrets.SERVER_HOST }}",
                    "username": "${{ secrets.SERVER_USER }}",
                    "key": "${{ secrets.SSH_PRIVATE_KEY }}",
                    "script": "cd /opt/app && docker compose pull && docker compose up -d",
                },
            },
        ],
    })

    return gen


def main():
    """主函数：完整演示 GitHub Actions 的各个方面"""
    print(f"""
{Colors.BOLD}{'=' * 60}
  GitHub Actions Workflow YAML 生成与解析演示
{'=' * 60}{Colors.RESET}
  本脚本将演示：
  1. 用 Python 生成 Workflow YAML
  2. 解析 YAML 结构并讲解每个字段
  3. 模拟触发和执行流程
  4. Secrets 管理概念
""")

    # ===== 第一部分：生成 YAML =====
    print(f"{Colors.BOLD}{'─' * 60}")
    print(f"  Part 1: 生成 Python 后端 CI/CD Workflow YAML")
    print(f"{'─' * 60}{Colors.RESET}\n")

    gen = create_python_backend_workflow()
    yaml_content = gen.to_yaml()

    print(f"  生成的 YAML（共 {len(yaml_content.splitlines())} 行）:\n")
    # 显示前 30 行
    for i, line in enumerate(yaml_content.splitlines()[:30]):
        print(f"  {Colors.DIM}{i + 1:3d} |{Colors.RESET} {line}")
    if len(yaml_content.splitlines()) > 30:
        print(f"  {Colors.DIM}... (省略 {len(yaml_content.splitlines()) - 30} 行){Colors.RESET}")

    # ===== 第二部分：解析结构 =====
    input(f"\n{Colors.YELLOW}按 Enter 继续：解析 YAML 结构...{Colors.RESET}")

    parser = WorkflowParser(yaml_content)
    parser.explain_structure()

    # ===== 第三部分：模拟执行 =====
    input(f"\n{Colors.YELLOW}按 Enter 继续：模拟 Workflow 触发和执行...{Colors.RESET}")

    simulator = WorkflowSimulator()

    # 模拟 push 事件
    simulator.simulate_event("push", {
        "repository": "myorg/python-backend",
        "branch": "main",
        "commit": "abc1234 - fix: 修复用户登录 bug",
        "author": "developer@example.com",
    })

    # 模拟各个 Job 执行
    print(f"  {Colors.BOLD}📋 Starting Workflow execution...{Colors.RESET}\n")

    # 获取 jobs 配置
    if yaml:
        workflow_data = yaml.safe_load(yaml_content)
    else:
        workflow_data = json.loads(yaml_content)

    jobs = workflow_data.get("jobs", {})
    for job_id, job_config in jobs.items():
        # 检查 if 条件
        condition = job_config.get("if", "")
        if condition:
            print(f"  {Colors.DIM}⏭ Job '{job_id}' has condition: {condition}{Colors.RESET}")
            print(f"  {Colors.DIM}  (Evaluating... condition met, proceeding){Colors.RESET}\n")

        simulator.simulate_job(job_id, job_config)

    print(f"  {Colors.GREEN}{Colors.BOLD}✓ All jobs completed successfully!{Colors.RESET}")

    # ===== 第四部分：Secrets 管理 =====
    input(f"\n{Colors.YELLOW}按 Enter 继续：Secrets 管理演示...{Colors.RESET}")

    SecretsDemo.explain_secrets()
    SecretsDemo.simulate_secret_injection()

    # ===== 总结 =====
    print(f"\n{Colors.BOLD}{Colors.CYAN}{'=' * 60}")
    print("  📚 总结")
    print(f"{'=' * 60}{Colors.RESET}")
    print(f"""
  通过本脚本，你学习了：

  1. YAML 生成
     用 Python 字典构建 Workflow 结构，序列化为 YAML 文件
     优势：避免缩进错误，支持动态生成

  2. YAML 结构
     name → on（触发条件）→ env（环境变量）→ jobs → steps
     每个字段都有明确的职责和作用域

  3. 触发与执行
     Event（push/PR/schedule/manual）触发 Workflow
     → Jobs 按依赖关系执行（needs 控制顺序）
     → Steps 在 Job 内顺序执行

  4. Secrets 安全
     加密存储 → 环境变量注入 → 日志自动遮蔽
     三级作用域：Organization → Repository → Environment

  📝 下一步：
     在你的 GitHub 仓库中创建 .github/workflows/ci.yml
     参考本脚本生成的 YAML 模板，配置你自己的 CI/CD 流水线！
""")


if __name__ == "__main__":
    main()
