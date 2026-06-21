"""
CI/CD 流水线概念演示脚本

本脚本模拟一个完整的 CI/CD 流水线执行过程，包含以下阶段：
1. 代码检查（Lint）—— 模拟代码风格检查
2. 运行测试（Test）—— 模拟单元测试执行
3. 构建打包（Build）—— 模拟 Docker 镜像构建
4. 部署上线（Deploy）—— 模拟服务部署和健康检查

任何阶段失败都会导致流水线终止（和真实 CI/CD 行为一致）。

运行方式：
    python 1_cicd_concept.py

学习目标：
    - 理解 CI/CD 流水线的阶段划分
    - 理解"快速失败"原则（任意阶段失败则终止）
    - 通过可视化输出直观感受流水线执行过程
"""

import time
import random
import sys
from dataclasses import dataclass, field
from enum import Enum
from typing import Callable


# ========================= 枚举与数据结构 =========================

class StageStatus(Enum):
    """流水线阶段的执行状态"""
    PENDING = "pending"       # 等待执行
    RUNNING = "running"       # 正在执行
    PASSED = "passed"         # 执行成功
    FAILED = "failed"         # 执行失败
    SKIPPED = "skipped"       # 被跳过（因前序阶段失败）


# ANSI 颜色码，用于终端彩色输出
class Colors:
    """终端颜色定义"""
    GREEN = "\033[92m"
    RED = "\033[91m"
    YELLOW = "\033[93m"
    BLUE = "\033[94m"
    CYAN = "\033[96m"
    BOLD = "\033[1m"
    DIM = "\033[2m"
    RESET = "\033[0m"


@dataclass
class PipelineStage:
    """流水线阶段定义

    Attributes:
        name: 阶段名称（如 "代码检查"）
        icon: 阶段图标（用于可视化）
        duration_range: 执行时间范围（秒），用于模拟耗时
        success_rate: 成功概率（0.0~1.0），用于模拟失败
        description: 阶段描述
        status: 当前状态
        error_message: 失败时的错误信息
    """
    name: str
    icon: str
    duration_range: tuple[float, float]
    success_rate: float
    description: str
    status: StageStatus = StageStatus.PENDING
    error_message: str = ""


# ========================= 流水线引擎 =========================

class CICDPipeline:
    """CI/CD 流水线模拟器

    模拟真实 CI/CD 系统的行为：
    - 按顺序执行各个阶段
    - 任意阶段失败则终止后续阶段
    - 每个阶段有模拟的执行时间和成功/失败概率
    """

    def __init__(self, pipeline_name: str, trigger: str):
        """
        初始化流水线。

        Args:
            pipeline_name: 流水线名称（如 "Python Backend CI/CD"）
            trigger: 触发事件（如 "push to main"）
        """
        self.pipeline_name = pipeline_name
        self.trigger = trigger
        self.stages: list[PipelineStage] = []
        self.start_time: float = 0
        self.end_time: float = 0

    def add_stage(self, stage: PipelineStage) -> "CICDPipeline":
        """添加一个阶段到流水线（支持链式调用）"""
        self.stages.append(stage)
        return self

    def _print_header(self):
        """打印流水线启动的头部信息"""
        width = 60
        print(f"\n{Colors.BOLD}{Colors.CYAN}{'=' * width}")
        print(f"  🚀 CI/CD Pipeline: {self.pipeline_name}")
        print(f"  📌 Trigger: {self.trigger}")
        print(f"  ⏰ Start: {time.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"{'=' * width}{Colors.RESET}\n")

    def _print_stage_start(self, stage: PipelineStage, index: int):
        """打印阶段开始的信息"""
        total = len(self.stages)
        print(
            f"  {Colors.BLUE}[{index + 1}/{total}]{Colors.RESET} "
            f"{stage.icon} {Colors.BOLD}{stage.name}{Colors.RESET}"
        )
        print(f"  {Colors.DIM}├── {stage.description}{Colors.RESET}")

    def _print_stage_progress(self, message: str):
        """打印阶段内的进度信息"""
        print(f"  {Colors.DIM}│   {message}{Colors.RESET}")
        time.sleep(0.3)

    def _print_stage_result(self, stage: PipelineStage, elapsed: float):
        """打印阶段执行结果"""
        if stage.status == StageStatus.PASSED:
            status_str = f"{Colors.GREEN}✓ PASSED{Colors.RESET}"
        elif stage.status == StageStatus.FAILED:
            status_str = f"{Colors.RED}✗ FAILED{Colors.RESET}"
        else:
            status_str = f"{Colors.YELLOW}⊘ SKIPPED{Colors.RESET}"

        print(
            f"  {Colors.DIM}└──{Colors.RESET} "
            f"{status_str} ({elapsed:.1f}s)"
        )
        if stage.error_message:
            print(f"      {Colors.RED}Error: {stage.error_message}{Colors.RESET}")
        print()

    def _simulate_stage(self, stage: PipelineStage) -> bool:
        """
        模拟单个阶段的执行。

        模拟逻辑：
        1. 随机等待一段时间（模拟真实执行耗时）
        2. 根据 success_rate 决定成功或失败
        3. 返回是否成功

        Returns:
            True 表示阶段成功，False 表示阶段失败
        """
        # 模拟执行时间
        duration = random.uniform(*stage.duration_range)
        time.sleep(min(duration, 1.5))  # 最多等 1.5 秒，避免演示太慢

        # 根据成功率决定结果
        if random.random() < stage.success_rate:
            stage.status = StageStatus.PASSED
            return True
        else:
            stage.status = StageStatus.FAILED
            stage.error_message = f"{stage.name}过程中发现了问题，请查看日志"
            return False

    def run(self, force_fail_stage: int | None = None) -> bool:
        """
        执行整个流水线。

        Args:
            force_fail_stage: 强制指定某个阶段失败（用于演示失败场景）。
                            None 表示使用随机概率。

        Returns:
            True 表示流水线全部通过，False 表示有阶段失败
        """
        self._print_header()
        self.start_time = time.time()
        all_passed = True

        for index, stage in enumerate(self.stages):
            # 如果前面有阶段失败，后续阶段全部跳过
            if not all_passed:
                stage.status = StageStatus.SKIPPED
                self._print_stage_start(stage, index)
                self._print_stage_result(stage, 0)
                continue

            # 打印阶段开始
            stage.status = StageStatus.RUNNING
            self._print_stage_start(stage, index)

            # 模拟执行过程
            stage_start = time.time()

            # 根据阶段类型打印不同的进度信息
            self._simulate_progress(stage)

            # 判断是否失败
            if force_fail_stage is not None and index == force_fail_stage:
                stage.status = StageStatus.FAILED
                stage.error_message = f"[演示模式] 强制阶段 {index + 1} 失败"
                all_passed = False
            else:
                if not self._simulate_stage(stage):
                    all_passed = False

            elapsed = time.time() - stage_start
            self._print_stage_result(stage, elapsed)

        self.end_time = time.time()
        self._print_summary(all_passed)
        return all_passed

    def _simulate_progress(self, stage: PipelineStage):
        """根据阶段类型输出不同的模拟进度信息"""
        # 不同阶段的模拟日志
        progress_messages = {
            "代码检查": [
                "扫描 src/ 目录下的 .py 文件...",
                "检查 PEP8 代码风格...",
                "检查未使用的导入...",
            ],
            "运行测试": [
                "收集测试用例... found 42 tests",
                "执行单元测试...",
                "生成覆盖率报告... coverage: 87%",
            ],
            "构建打包": [
                "读取 Dockerfile...",
                "构建镜像层: base image python:3.11-slim",
                "安装依赖: pip install -r requirements.txt",
                "打标签: app:latest",
            ],
            "部署上线": [
                "SSH 连接服务器...",
                "docker pull app:latest",
                "docker-compose up -d",
                "curl http://localhost:8000/health → 200 OK",
            ],
        }

        messages = progress_messages.get(stage.name, ["执行中..."])
        for msg in messages:
            self._print_stage_progress(msg)

    def _print_summary(self, all_passed: bool):
        """打印流水线执行总结"""
        total_time = self.end_time - self.start_time
        width = 60

        if all_passed:
            status = f"{Colors.GREEN}{Colors.BOLD}ALL STAGES PASSED ✓{Colors.RESET}"
            emoji = "🎉"
        else:
            status = f"{Colors.RED}{Colors.BOLD}PIPELINE FAILED ✗{Colors.RESET}"
            emoji = "💥"

        passed = sum(1 for s in self.stages if s.status == StageStatus.PASSED)
        failed = sum(1 for s in self.stages if s.status == StageStatus.FAILED)
        skipped = sum(1 for s in self.stages if s.status == StageStatus.SKIPPED)

        print(f"{Colors.BOLD}{Colors.CYAN}{'=' * width}{Colors.RESET}")
        print(f"  {emoji} {status}")
        print(f"  ⏱  总耗时: {total_time:.1f}s")
        print(f"  📊 通过: {passed} | 失败: {failed} | 跳过: {skipped}")
        print(f"{Colors.BOLD}{Colors.CYAN}{'=' * width}{Colors.RESET}\n")

    def visualize(self):
        """可视化展示流水线结构（不执行，只显示结构）"""
        print(f"\n{Colors.BOLD}📐 Pipeline Structure: {self.pipeline_name}{Colors.RESET}\n")

        for i, stage in enumerate(self.stages):
            connector = "    ↓" if i < len(self.stages) - 1 else "    ✓ Done"
            print(f"  ┌─────────────────────────────────────┐")
            print(f"  │ {stage.icon} {stage.name:<35}│")
            print(f"  │   {stage.description:<37}│")
            print(f"  └─────────────────────────────────────┘")
            print(f"  {Colors.DIM}{connector}{Colors.RESET}")

        print()


# ========================= 演示入口 =========================

def create_demo_pipeline() -> CICDPipeline:
    """创建演示用的 CI/CD 流水线"""
    pipeline = CICDPipeline(
        pipeline_name="Python Backend CI/CD",
        trigger="push to main branch (commit abc1234)"
    )

    # 阶段 1: 代码检查（Lint）
    pipeline.add_stage(PipelineStage(
        name="代码检查",
        icon="🔍",
        duration_range=(0.5, 1.0),
        success_rate=0.95,  # 95% 成功率
        description="运行 flake8 / ruff 检查代码风格和质量"
    ))

    # 阶段 2: 运行测试（Test）
    pipeline.add_stage(PipelineStage(
        name="运行测试",
        icon="🧪",
        duration_range=(1.0, 2.0),
        success_rate=0.90,  # 90% 成功率
        description="执行 pytest 单元测试和集成测试"
    ))

    # 阶段 3: 构建打包（Build）
    pipeline.add_stage(PipelineStage(
        name="构建打包",
        icon="📦",
        duration_range=(1.0, 1.5),
        success_rate=0.95,  # 95% 成功率
        description="构建 Docker 镜像并推送到镜像仓库"
    ))

    # 阶段 4: 部署上线（Deploy）
    pipeline.add_stage(PipelineStage(
        name="部署上线",
        icon="🚀",
        duration_range=(0.5, 1.0),
        success_rate=0.90,  # 90% 成功率
        description="SSH 部署到服务器并执行健康检查"
    ))

    return pipeline


def main():
    """主函数：运行多次演示，展示成功和失败场景"""
    print(f"\n{Colors.BOLD}{'=' * 60}")
    print("  CI/CD 流水线概念演示")
    print("  本脚本模拟 CI/CD 的完整执行过程")
    print(f"{'=' * 60}{Colors.RESET}")

    # ---- 演示 1：展示流水线结构 ----
    pipeline = create_demo_pipeline()
    pipeline.visualize()

    input(f"{Colors.YELLOW}按 Enter 开始演示 1：正常流水线执行...{Colors.RESET}")

    # ---- 演示 2：正常执行（可能随机失败） ----
    pipeline = create_demo_pipeline()
    result = pipeline.run()

    if result:
        print(f"{Colors.GREEN}✅ 演示 1 完成：流水线全部通过，代码已成功部署到生产环境！{Colors.RESET}")
    else:
        print(f"{Colors.RED}❌ 演示 1 完成：流水线在某个阶段失败了。{Colors.RESET}")
        print(f"   真实场景中，团队会收到失败通知并排查问题。")

    # ---- 演示 3：强制失败场景 ----
    print(f"\n{Colors.YELLOW}{'─' * 60}{Colors.RESET}")
    input(f"{Colors.YELLOW}按 Enter 开始演示 2：模拟测试失败的场景...{Colors.RESET}")

    pipeline = create_demo_pipeline()
    # 强制让"运行测试"阶段（index=1）失败
    pipeline.run(force_fail_stage=1)

    print(f"{Colors.RED}❌ 演示 2 完成：测试阶段失败，后续阶段全部跳过。{Colors.RESET}")
    print(f"   这就是 CI/CD 的「快速失败」原则 —— 不把问题带到下一阶段。")
    print(f"   构建和部署阶段被自动跳过，避免了将未通过测试的代码部署到生产环境。")

    # ---- 总结 ----
    print(f"\n{Colors.BOLD}{Colors.CYAN}{'=' * 60}")
    print("  📚 关键概念总结")
    print(f"{'=' * 60}{Colors.RESET}")
    print(f"""
  1. Pipeline（流水线）
     整个自动化流程的容器，包含多个阶段

  2. Stage（阶段）
     流水线中的一步操作，如：测试、构建、部署

  3. Fast Fail（快速失败）
     任意阶段失败 → 立即终止 → 不执行后续阶段
     目的：不把问题传递到下游，尽早发现问题

  4. Trigger（触发器）
     启动流水线的条件，如：git push、PR 创建、定时任务

  5. 真实流程
     git push → GitHub Actions 检测到 push 事件
     → 自动启动 Workflow → 依次执行各个 Job
     → 全部通过则部署成功 → 失败则发送通知
""")


if __name__ == "__main__":
    main()
