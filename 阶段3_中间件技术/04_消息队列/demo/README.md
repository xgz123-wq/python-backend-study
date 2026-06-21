# 消息队列章节 Demo 说明

## 学习顺序

| 顺序 | Demo 文件 | 对应理论文档 | 主要内容 |
|------|-----------|-------------|---------|
| 1 | `demo_1_celery_worker.py` + `demo_1_send_tasks.py` | `2.Celery异步任务.md` | 基础任务提交、状态查询、重试机制 |
| 2 | `demo_2_advanced.py` | `2.Celery异步任务.md` | 进度上报、多队列路由、group/chord/chain |

---

## 环境准备

### 1. 启动 Redis（作为 Broker）

```bash
# 在 demo/ 目录下
docker-compose up -d

# 验证启动成功
docker-compose ps       # redis_celery 应为 Up (healthy)
docker exec -it redis_celery redis-cli ping   # 返回 PONG
```

### 2. 安装依赖

```bash
pip install -r requirements.txt
```

---

## Demo 1：基础任务（2个终端）

```bash
# 终端1：启动 Worker（保持运行）
celery -A demo_1_celery_worker worker --loglevel=info

# 终端2：发送任务（看结果）
python demo_1_send_tasks.py
```

**预期输出（终端2）：**
```
【1. 基础任务提交（delay 方式）】
任务已提交，ID = xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
立即查询状态: PENDING
  状态: STARTED，等待中... (0.5s)
  状态: SUCCESS，等待中...
最终结果: {'task_id': '...', 'status': 'SUCCESS', 'result': 30}
...
```

**同时在终端1（Worker）中可以看到：**
```
[任务] 10 + 20 = 30，任务ID=xxxxxxxx
[任务开始] 发送邮件给 user@example.com: 欢迎注册
[任务完成] 邮件已发送给 user@example.com
```

---

## Demo 2：进阶功能（2-3个终端）

```bash
# 终端1：启动 Worker（消费3个队列）
celery -A demo_2_advanced worker -Q celery,high,low --loglevel=info

# 终端2（可选）：启动 Beat 定时调度器
celery -A demo_2_advanced beat --loglevel=info

# 终端3：运行演示脚本
python demo_2_advanced.py
```

**Demo 2 演示内容：**
1. **进度上报**：长任务实时上报百分比进度
2. **多队列**：不同优先级任务路由到不同队列
3. **group**：5个加法任务并行执行，收集所有结果
4. **chord**：并行 + 汇总回调（MapReduce 模式）
5. **chain**：任务串行执行，前一个结果传给下一个

---

## Flower 监控界面

```bash
# 启动 Flower（另开一个终端）
celery -A demo_1_celery_worker flower

# 访问：http://localhost:5555
# 可以看到：Worker 状态、任务队列、任务历史、实时统计
```

---

## 切换 RabbitMQ 作为 Broker

1. 取消注释 `docker-compose.yml` 中的 rabbitmq 服务
2. 重启 Docker：`docker-compose up -d`
3. 访问 RabbitMQ 管理界面：http://localhost:15672（admin/123456）
4. 修改 Demo 文件中的 broker URL：

```python
# 原来（Redis）
broker="redis://localhost:6379/0"

# 改为（RabbitMQ）
broker="amqp://admin:123456@localhost:5672//"
```

---

## 常用调试命令

```bash
# 查看 Redis 中的 Celery 队列（任务数量）
docker exec -it redis_celery redis-cli
> LLEN celery          # 默认队列中等待的任务数
> LLEN high            # high 队列中等待的任务数
> KEYS celery-task-meta-*  # 已完成任务的结果（不要用 KEYS * 在生产环境）

# 清空所有任务队列（慎用）
> DEL celery high low

# 查看 Worker 状态
celery -A demo_1_celery_worker inspect active    # 正在执行的任务
celery -A demo_1_celery_worker inspect reserved  # 已分配但未开始的任务
celery -A demo_1_celery_worker inspect stats     # Worker 统计信息

# 撤销任务（通过 task_id）
celery -A demo_1_celery_worker control revoke <task_id>
```

---

## 停止服务

```bash
docker-compose down          # 停止容器（保留数据）
docker-compose down -v       # 停止并清除数据卷
```
