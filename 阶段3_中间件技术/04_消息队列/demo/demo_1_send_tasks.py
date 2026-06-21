"""
Demo 1（发送端）: 向 Celery 提交任务并查询结果
对应理论文档：2.Celery异步任务.md

运行步骤（先启动 Worker，再运行本文件）：
  终端1：celery -A demo_1_celery_worker worker --loglevel=info
  终端2：python demo_1_send_tasks.py
"""

import time
from demo_1_celery_worker import app, send_email, generate_report, add, risky_task


def check_result(result, timeout: int = 15) -> dict:
    """轮询等待任务结果（演示用）"""
    start = time.time()
    while not result.ready():
        elapsed = time.time() - start
        if elapsed > timeout:
            return {"status": "TIMEOUT", "task_id": result.id}
        print(f"  状态: {result.status}，等待中... ({elapsed:.1f}s)")
        time.sleep(0.5)
    return {
        "task_id": result.id,
        "status": result.status,
        "result": result.result if result.successful() else str(result.result),
    }


# ─────────────────────────────────────────────────
# 1. 基础任务提交（delay）
# ─────────────────────────────────────────────────
def demo_basic_tasks():
    print("=" * 55)
    print("【1. 基础任务提交（delay 方式）】")

    # delay() 是最简单的提交方式
    # 立即返回 AsyncResult，任务在后台执行
    result = add.delay(10, 20)
    print(f"任务已提交，ID = {result.id}")
    print(f"立即查询状态: {result.status}")  # PENDING 或 STARTED

    output = check_result(result)
    print(f"最终结果: {output}")


# ─────────────────────────────────────────────────
# 2. apply_async（完整参数控制）
# ─────────────────────────────────────────────────
def demo_apply_async():
    print("\n" + "=" * 55)
    print("【2. apply_async（完整参数）】")

    # 立即执行
    result = send_email.apply_async(
        args=["user@example.com", "欢迎注册", "感谢您的注册！"],
    )
    print(f"发邮件任务已提交，ID = {result.id}")
    output = check_result(result)
    print(f"结果: {output}")

    # 延迟10秒执行（countdown）
    result_delayed = send_email.apply_async(
        args=["vip@example.com", "VIP 专属优惠", "专属内容..."],
        countdown=10,  # 10秒后执行
    )
    print(f"\n延迟10秒的任务已提交，ID = {result_delayed.id}")
    print(f"状态（应为 PENDING）: {result_delayed.status}")
    # 不等待，继续往下执行


# ─────────────────────────────────────────────────
# 3. 通过任务 ID 异步查询结果
# ─────────────────────────────────────────────────
def demo_check_by_id():
    print("\n" + "=" * 55)
    print("【3. 通过任务 ID 查询结果（模拟 Web 轮询）】")

    # 模拟 Web API 场景：
    # - 请求1：提交任务，返回 task_id 给前端
    # - 请求2（轮询）：前端用 task_id 查询任务进度
    from celery.result import AsyncResult

    # 提交任务
    result = generate_report.delay(user_id=1001, report_type="quarterly")
    task_id = result.id
    print(f"接口返回给前端的 task_id = {task_id}")

    # 模拟前端轮询（每0.5秒查一次）
    for _ in range(20):
        task_result = AsyncResult(task_id, app=app)
        status_info = {
            "task_id": task_id,
            "status": task_result.status,
            "done": task_result.ready(),
        }
        print(f"  轮询: {status_info}")

        if task_result.ready():
            if task_result.successful():
                print(f"  任务完成！报表地址: {task_result.result}")
            else:
                print(f"  任务失败！错误: {task_result.result}")
            break
        time.sleep(0.5)


# ─────────────────────────────────────────────────
# 4. 任务重试演示
# ─────────────────────────────────────────────────
def demo_retry():
    print("\n" + "=" * 55)
    print("【4. 任务重试机制】")

    result = risky_task.delay(should_fail=True)
    print(f"提交会失败的任务，ID = {result.id}")
    output = check_result(result, timeout=30)
    print(f"最终结果（经过重试后）: {output}")


# ─────────────────────────────────────────────────
# 5. 批量提交任务
# ─────────────────────────────────────────────────
def demo_batch():
    print("\n" + "=" * 55)
    print("【5. 批量提交任务（模拟群发邮件）】")

    recipients = [f"user{i}@example.com" for i in range(1, 6)]

    # 批量提交，立即返回，后台并发处理
    results = []
    for email in recipients:
        r = send_email.delay(email, "系统公告", "重要通知内容")
        results.append((email, r))
        print(f"  已提交: {email} → task_id={r.id[:8]}...")

    print(f"\n已批量提交 {len(results)} 个任务，等待全部完成...")

    # 等待所有任务完成
    all_done = False
    while not all_done:
        statuses = [r.status for _, r in results]
        done_count = sum(1 for s in statuses if s in ("SUCCESS", "FAILURE"))
        print(f"  进度: {done_count}/{len(results)} 完成")
        if done_count == len(results):
            all_done = True
        else:
            time.sleep(1)

    print("所有邮件发送完毕！")


if __name__ == "__main__":
    print("确保已启动 Worker：")
    print("  celery -A demo_1_celery_worker worker --loglevel=info\n")

    demo_basic_tasks()
    demo_apply_async()
    demo_check_by_id()
    demo_retry()
    demo_batch()

    print("\n" + "=" * 55)
    print("Demo 1 运行完成！")
