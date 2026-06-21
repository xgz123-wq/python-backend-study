# Redis 章节 Demo 说明

## 学习顺序

| 顺序 | Demo 文件 | 对应理论文档 | 主要内容 |
|------|-----------|-------------|---------|
| 1 | `1_data_structures.py` | `1.五种数据结构.md` | String/Hash/List/Set/ZSet 基础操作 |
| 2 | `2_cache_scenarios.py` | `2.典型使用场景.md` | 缓存/Session/排行榜/分布式锁 |
| 3 | `3_cache_problems.py` | `3.缓存问题穿透击穿雪崩.md` | 三大缓存问题复现与解决方案 |
| 4 | `4_expiry_persistence.py` | `4.过期淘汰策略与持久化.md` | Key 过期、内存信息、RDB 持久化 |

---

## 环境准备

### 1. 启动 Redis

```bash
# 在 demo/ 目录下执行
docker-compose up -d

# 验证启动成功
docker-compose ps
# redis_learn 状态应为 Up (healthy)

# 连接测试
docker exec -it redis_learn redis-cli ping
# 返回 PONG 即正常
```

### 2. 安装 Python 依赖

```bash
pip install -r requirements.txt
```

---

## 运行各 Demo

```bash
# 按顺序运行
python 1_data_structures.py
python 2_cache_scenarios.py
python 3_cache_problems.py
python 4_expiry_persistence.py
```

---

## 停止 Redis

```bash
docker-compose down          # 停止容器（数据保留）
docker-compose down -v       # 停止并删除数据卷（完全清除）
```

---

## Demo 运行预期输出

### Demo 1（数据结构）
- 演示 5 种数据结构的常用命令
- 每种结构展示核心操作和结果

### Demo 2（使用场景）
- 缓存：3次请求只查1次数据库
- Session：创建→验证→注销完整流程
- 排行榜：积分更新后名次变化
- 分布式锁：20并发抢10库存，不超卖

### Demo 3（缓存问题）
- 穿透：无防护时5次查5次库，有防护只查1次
- 击穿：无保护时20个并发都打库，有互斥锁只打1次
- 雪崩：对比有无抖动的 TTL 分布差异

### Demo 4（过期与持久化）
- 演示 Key 过期的各种命令（TTL/EXPIRE/PERSIST）
- 查看 Redis 内存和持久化状态信息
- 手动触发 BGSAVE

---

## Redis CLI 常用调试命令

```bash
# 进入 Redis CLI
docker exec -it redis_learn redis-cli

# 常用命令
KEYS *                     # 查看所有 Key（测试环境可用，生产禁止）
SCAN 0 COUNT 10            # 安全扫描（生产环境替代 KEYS）
TYPE key                   # 查看 Key 的数据类型
OBJECT ENCODING key        # 查看底层编码
DEBUG SLEEP 0              # 测试连接
INFO memory                # 内存信息
INFO persistence           # 持久化信息
INFO stats                 # 统计信息
CONFIG GET maxmemory-policy # 查看淘汰策略
FLUSHDB                    # 清空当前数据库（测试时使用）
```
