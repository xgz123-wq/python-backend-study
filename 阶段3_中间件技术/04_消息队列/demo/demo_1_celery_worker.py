"""
Demo 1: Celery 基础用法演示
对应理论文档：2.Celery异步任务.md

演示内容：
  - Celery 实例创建与配置
  - 定义基础异步任务
  - 发送任务到队列（delay / apply_async）
  - 查询任务状态和结果
  - 多种任务调用方式对比

运行前提：
  - 已启动 Redis（docker-compose up -d）
  - 已安装依赖：pip install -r requirements.txt

运行步骤（需要两个终端）：
  终端1（启动 Worker）：
    celery -A demo_1_celery_worker worker --loglevel=info

  终端2（发送任务）：
    python demo_1_send_tasks.py
"""

# ── 文件：celery_app.py（公共 Celery 实例）──
# 内容已嵌入到本文件底部的注释中，实际项目应拆分为独立文件

from celery import Celery
import time

# ─────────────────────────────────────────────────
# Celery 实例（Worker 启动时加载此文件）
# ─────────────────────────────────────────────────
app = Celery(
    "demo",
    broker="redis://localhost:6379/0",   # 任务队列
    backend="redis://localhost:6379/1",  # 结果存储
)

app.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    timezone="Asia/Shanghai",
    enable_utc=True,
    task_track_started=True,       # 任务开始时记录状态
    task_acks_late=True,           # 执行完成后才 ACK（提高可靠性）
    worker_prefetch_multiplier=1,  # Worker 每次预取1个任务
    result_expires=3600,           # 结果保留1小时
)


# ─────────────────────────────────────────────────
# 任务定义
# ─────────────────────────────────────────────────
@app.task(name="tasks.send_email")
def send_email(to: str, subject: str, body: str) -> dict:
    """模拟发送邮件（耗时2秒）"""
    print(f"[任务开始] 发送邮件给 {to}: {subject}")
    time.sleep(2)
    print(f"[任务完成] 邮件已发送给 {to}")
    return {"status": "sent", "to": to, "subject": subject}


@app.task(name="tasks.generate_report")
def generate_report(user_id: int, report_type: str = "monthly") -> str:
    """模拟生成报表（耗时3秒）"""
    print(f"[任务开始] 为用户 {user_id} 生成 {report_type} 报表")
    time.sleep(3)
    url = f"https://example.com/reports/{user_id}/{report_type}.pdf"
    print(f"[任务完成] 报表生成完毕: {url}")
    return url


@app.task(name="tasks.add", bind=True)
def add(self, x: int, y: int) -> int:
    """简单加法（用于快速验证 Celery 是否工作）"""
    print(f"[任务] {x} + {y} = {x + y}，任务ID={self.request.id}")
    return x + y


@app.task(name="tasks.risky_task", bind=True, max_retries=3, default_retry_delay=2)
def risky_task(self, should_fail: bool = False) -> str:
    """演示任务重试机制"""
    print(f"[任务] risky_task 第 {self.request.retries + 1} 次尝试")
    if should_fail and self.request.retries < 2:
        # 前2次失败，第3次成功
        raise self.retry(exc=Exception("模拟临时失败"))
    return f"成功（共尝试 {self.request.retries + 1} 次）"
