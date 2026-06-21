"""
Demo 2: Celery 进阶功能演示
对应理论文档：2.Celery异步任务.md

演示内容：
  - 带进度上报的长任务（update_state）
  - 定时任务（Celery Beat）配置
  - 多队列分级处理
  - 任务链（chord / group）

运行步骤：
  终端1（启动 Worker，消费所有队列）：
    celery -A demo_2_advanced worker -Q celery,high,low --loglevel=info

  终端2（启动 Beat 调度器，用于定时任务）：
    celery -A demo_2_advanced beat --loglevel=info

  终端3（运行演示脚本）：
    python demo_2_advanced.py
"""

import time
from celery import Celery, group, chain, chord
from celery.schedules import crontab
from kombu import Queue

# ─────────────────────────────────────────────────
# Celery 实例（多队列 + 定时任务配置）
# ─────────────────────────────────────────────────
app = Celery(
    "demo_advanced",
    broker="redis://localhost:6379/0",
    backend="redis://localhost:6379/1",
)

app.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    timezone="Asia/Shanghai",
    enable_utc=True,
    task_track_started=True,
    task_acks_late=True,
    result_expires=3600,

    # ── 多队列配置 ──
    task_queues=(
        Queue("celery"),    # 默认队列
        Queue("high"),      # 高优先级（紧急通知、支付回调）
        Queue("low"),       # 低优先级（报表、统计）
    ),
    task_default_queue="celery",

    # ── 任务自动路由：按任务名分配到对应队列 ──
    task_routes={
        "demo_2_advanced.urgent_notify": {"queue": "high"},
        "demo_2_advanced.generate_stats": {"queue": "low"},
    },

    # ── 定时任务（Celery Beat）配置 ──
    beat_schedule={
        # 每30秒执行一次心跳（演示用，实际不要这么频繁）
        "heartbeat": {
            "task": "demo_2_advanced.heartbeat",
            "schedule": 30.0,
        },
        # 每天凌晨1点生成日报（注释掉避免干扰演示）
        # "daily-report": {
        #     "task": "demo_2_advanced.generate_daily_report",
        #     "schedule": crontab(hour=1, minute=0),
        # },
    },
)


# ─────────────────────────────────────────────────
# 任务定义
# ─────────────────────────────────────────────────
@app.task(name="demo_2_advanced.heartbeat")
def heartbeat() -> str:
    """定时心跳任务（由 Beat 调度）"""
    import datetime
    now = datetime.datetime.now().strftime("%H:%M:%S")
    print(f"[心跳] {now}")
    return f"heartbeat at {now}"


@app.task(bind=True, name="demo_2_advanced.long_task_with_progress")
def long_task_with_progress(self, items: list) -> dict:
    """带进度上报的长任务"""
    total = len(items)
    results = []

    for i, item in enumerate(items):
        # 更新进度（存入 Backend，前端可轮询查询）
        self.update_state(
            state="PROGRESS",
            meta={
                "current": i + 1,
                "total": total,
                "percent": int((i + 1) / total * 100),
                "current_item": item,
            },
        )
        # 模拟处理每个 item
        time.sleep(0.3)
        results.append(f"processed:{item}")

    return {"total": total, "results": results}


@app.task(name="demo_2_advanced.urgent_notify")
def urgent_notify(user_id: int, message: str) -> dict:
    """高优先级任务：紧急通知（路由到 high 队列）"""
    time.sleep(0.1)
    print(f"[HIGH 队列] 发送紧急通知给用户 {user_id}: {message}")
    return {"user_id": user_id, "notified": True}


@app.task(name="demo_2_advanced.generate_stats")
def generate_stats(date_range: str) -> dict:
    """低优先级任务：统计报表（路由到 low 队列）"""
    time.sleep(2)
    print(f"[LOW 队列] 生成 {date_range} 统计报表完成")
    return {"date_range": date_range, "rows": 1234}


@app.task(name="demo_2_advanced.add")
def add(x: int, y: int) -> int:
    """用于任务组合演示的加法任务"""
    time.sleep(0.2)
    return x + y


@app.task(name="demo_2_advanced.sum_results")
def sum_results(results: list) -> int:
    """聚合任务：汇总 group 任务的结果"""
    total = sum(results)
    print(f"[聚合] 所有结果之和: {total}")
    return total


# ─────────────────────────────────────────────────
# 演示脚本（需在另一个终端运行 Worker 后执行）
# ─────────────────────────────────────────────────
def demo_progress_task():
    """演示：带进度上报的长任务"""
    print("=" * 55)
    print("【1. 带进度上报的长任务】")
    from celery.result import AsyncResult

    items = [f"item_{i}" for i in range(10)]
    result = long_task_with_progress.delay(items)
    print(f"任务 ID = {result.id}")

    # 轮询进度
    while not result.ready():
        task = AsyncResult(result.id, app=app)
        if task.status == "PROGRESS":
            meta = task.info
            print(f"  进度: {meta['percent']}% ({meta['current']}/{meta['total']}) - {meta['current_item']}")
        else:
            print(f"  状态: {task.status}")
        time.sleep(0.4)

    print(f"任务完成！处理了 {result.result['total']} 条数据")


def demo_multi_queue():
    """演示：多队列任务路由"""
    print("\n" + "=" * 55)
    print("【2. 多队列任务路由】")

    # 这些任务会自动路由到对应队列（通过 task_routes 配置）
    r_high = urgent_notify.delay(user_id=1001, message="账户异常登录警告！")
    r_low = generate_stats.delay(date_range="2024-01")

    print(f"高优先级任务（→ high 队列）ID = {r_high.id[:8]}...")
    print(f"低优先级任务（→ low 队列）ID = {r_low.id[:8]}...")

    # 也可以手动指定队列
    r_manual = urgent_notify.apply_async(
        args=[1002, "手动指定队列"],
        queue="high",
    )
    print(f"手动指定 high 队列，ID = {r_manual.id[:8]}...")

    # 等待完成
    for r in [r_high, r_low, r_manual]:
        r.get(timeout=15)
    print("所有多队列任务完成！")


def demo_task_group():
    """演示：group（并行执行多个任务）"""
    print("\n" + "=" * 55)
    print("【3. group：并行执行多个任务】")

    # group：多个任务并行执行，收集所有结果
    job = group(add.s(i, i) for i in range(5))  # 0+0, 1+1, 2+2, 3+3, 4+4
    result = job.apply_async()

    print(f"并行提交 5 个加法任务...")
    results = result.get(timeout=10)
    print(f"各任务结果: {results}")  # [0, 2, 4, 6, 8]


def demo_task_chord():
    """演示：chord（并行执行 + 汇总回调）"""
    print("\n" + "=" * 55)
    print("【4. chord：并行执行 + 汇总回调】")

    # chord：先并行执行 header 中的任务，全部完成后执行 callback
    # 相当于 MapReduce：Map（并行）→ Reduce（汇总）
    result = chord(
        header=[add.s(i, i) for i in range(5)],   # Map：并行执行 5 个加法
        body=sum_results.s(),                       # Reduce：汇总所有结果
    ).apply_async()

    print("chord 已提交（并行5个加法 → 汇总）...")
    total = result.get(timeout=15)
    print(f"最终汇总结果: {total}")  # 0+2+4+6+8 = 20


def demo_task_chain():
    """演示：chain（串行执行，前一个的输出作为后一个的输入）"""
    print("\n" + "=" * 55)
    print("【5. chain：串行任务链】")

    # chain：任务串行执行，前一个任务的返回值自动传给下一个
    # add(1,1)=2 → add(2,10)=12 → add(12,100)=112
    result = chain(
        add.s(1, 1),    # 返回 2
        add.s(10),      # 接收 2，执行 add(2, 10)=12（s() 会把前一个结果作为第一个参数）
        add.s(100),     # 接收 12，执行 add(12, 100)=112
    ).apply_async()

    print("chain 已提交（1+1=2 → 2+10=12 → 12+100=112）...")
    final = result.get(timeout=10)
    print(f"最终结果: {final}")  # 112


if __name__ == "__main__":
    print("确保已启动 Worker：")
    print("  celery -A demo_2_advanced worker -Q celery,high,low --loglevel=info\n")

    demo_progress_task()
    demo_multi_queue()
    demo_task_group()
    demo_task_chord()
    demo_task_chain()

    print("\n" + "=" * 55)
    print("Demo 2 进阶演示完成！")
