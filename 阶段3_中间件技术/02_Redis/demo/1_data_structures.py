"""
Demo 1: Redis 五种数据结构操作示例
对应理论文档：1.五种数据结构.md

运行前提：
  - 已启动 Redis（docker-compose up -d 或本地 redis-server）
  - 已安装 redis-py：pip install redis

运行方式：
  python 1_data_structures.py
"""

import redis

# 连接 Redis（decode_responses=True 让返回值自动解码为字符串）
r = redis.Redis(host="localhost", port=6379, db=0, decode_responses=True)


def demo_ping():
    """测试 Redis 连接"""
    print("=" * 50)
    print("【连接测试】")
    result = r.ping()
    print(f"PING → {result}")  # True 表示连接成功


# ─────────────────────────────────────────────────
# 1. String（字符串）
# ─────────────────────────────────────────────────
def demo_string():
    print("\n" + "=" * 50)
    print("【1. String 字符串】")

    # 基础 SET / GET
    r.set("name", "张三")
    print(f"SET name '张三' → GET name = {r.get('name')}")

    # SETEX：设置值同时指定过期时间（秒）
    r.setex("session_token", 60, "abc123xyz")
    print(f"SETEX session_token 60 → TTL = {r.ttl('session_token')} 秒")

    # SETNX：仅当 Key 不存在时才设置（用于分布式锁）
    result1 = r.setnx("lock_key", "1")   # 第一次成功
    result2 = r.setnx("lock_key", "2")   # 第二次失败
    print(f"SETNX lock_key '1' → {result1}")  # True
    print(f"SETNX lock_key '2' → {result2}")  # False（已存在）

    # INCR / INCRBY：整数自增（原子操作，常用于计数器）
    r.set("page_views", 100)
    r.incr("page_views")            # +1
    r.incrby("page_views", 9)       # +9
    print(f"INCR + INCRBY page_views → {r.get('page_views')}")  # 110

    # 清理测试数据
    r.delete("name", "session_token", "lock_key", "page_views")


# ─────────────────────────────────────────────────
# 2. Hash（哈希）
# ─────────────────────────────────────────────────
def demo_hash():
    print("\n" + "=" * 50)
    print("【2. Hash 哈希】")

    key = "user:1001"

    # HSET：设置字段（Redis 4.0+ 支持一次设置多个字段）
    r.hset(key, mapping={
        "name": "李四",
        "age": "25",
        "email": "lisi@example.com",
    })

    # HGET：获取单个字段
    print(f"HGET name = {r.hget(key, 'name')}")

    # HMGET：批量获取多个字段
    fields = r.hmget(key, "name", "age", "email")
    print(f"HMGET name,age,email = {fields}")

    # HGETALL：获取所有字段
    print(f"HGETALL = {r.hgetall(key)}")

    # HINCRBY：字段整数自增（如购物车商品数量+1）
    r.hset("cart:user:1001", "sku_101", "2")
    r.hincrby("cart:user:1001", "sku_101", 1)  # 数量变为 3
    print(f"购物车 sku_101 数量（+1后）= {r.hget('cart:user:1001', 'sku_101')}")

    # HDEL：删除字段
    r.hdel(key, "email")
    print(f"HDEL email 后 HKEYS = {r.hkeys(key)}")

    r.delete(key, "cart:user:1001")


# ─────────────────────────────────────────────────
# 3. List（列表）
# ─────────────────────────────────────────────────
def demo_list():
    print("\n" + "=" * 50)
    print("【3. List 列表】")

    key = "messages:room:1"

    # LPUSH：从左端插入（最新消息在最前面）
    r.lpush(key, "消息1", "消息2", "消息3")
    # 此时列表：[消息3, 消息2, 消息1]（后 push 的在左边）

    # LRANGE：获取范围（0 到 -1 表示全部）
    print(f"全部消息（最新在前）: {r.lrange(key, 0, -1)}")

    # LLEN：获取长度
    print(f"消息数量: {r.llen(key)}")

    # RPUSH：从右端插入（用于消息队列场景）
    r.rpush("task_queue", "任务A", "任务B", "任务C")

    # LPOP：从左端弹出（FIFO 队列：先进先出）
    task = r.lpop("task_queue")
    print(f"从队列取出任务: {task}")  # 任务A

    # LTRIM：只保留最新 N 条（防止列表无限增长）
    for i in range(10):
        r.lpush("news_list", f"新闻{i}")
    r.ltrim("news_list", 0, 4)  # 只保留最新5条
    print(f"LTRIM 后（只保留5条）: {r.lrange('news_list', 0, -1)}")

    r.delete(key, "task_queue", "news_list")


# ─────────────────────────────────────────────────
# 4. Set（集合）
# ─────────────────────────────────────────────────
def demo_set():
    print("\n" + "=" * 50)
    print("【4. Set 集合】")

    # 模拟：用户 A 和 用户 B 的关注列表
    r.sadd("follow:user_a", "user_1", "user_2", "user_3", "user_4")
    r.sadd("follow:user_b", "user_2", "user_3", "user_5", "user_6")

    # SMEMBERS：获取所有元素
    print(f"用户A的关注列表: {r.smembers('follow:user_a')}")

    # SCARD：元素数量
    print(f"用户A关注了 {r.scard('follow:user_a')} 人")

    # SISMEMBER：是否包含
    print(f"用户A是否关注了user_2: {r.sismember('follow:user_a', 'user_2')}")

    # SINTER：交集（共同关注）
    common = r.sinter("follow:user_a", "follow:user_b")
    print(f"A和B的共同关注: {common}")

    # SUNION：并集（合并去重）
    union = r.sunion("follow:user_a", "follow:user_b")
    print(f"A和B关注的总人数（去重）: {len(union)}")

    # SDIFF：差集（A关注但B没关注的）
    diff = r.sdiff("follow:user_a", "follow:user_b")
    print(f"A独有的关注（不在B中）: {diff}")

    # SRANDMEMBER：随机抽取（抽奖）
    r.sadd("lottery", "用户甲", "用户乙", "用户丙", "用户丁", "用户戊")
    winners = r.srandmember("lottery", 2)  # 随机取2个，不删除
    print(f"随机抽奖中奖者: {winners}")

    r.delete("follow:user_a", "follow:user_b", "lottery")


# ─────────────────────────────────────────────────
# 5. ZSet（有序集合）
# ─────────────────────────────────────────────────
def demo_zset():
    print("\n" + "=" * 50)
    print("【5. ZSet 有序集合（排行榜）】")

    key = "leaderboard:weekly"

    # ZADD：添加玩家分数
    r.zadd(key, {
        "player:张三": 9800,
        "player:李四": 9500,
        "player:王五": 8800,
        "player:赵六": 9900,
        "player:钱七": 7600,
    })

    # ZREVRANGE：倒序获取（分数高的在前）+ withscores 同时返回分数
    top3 = r.zrevrange(key, 0, 2, withscores=True)
    print("Top 3 排行榜（倒序）:")
    for rank, (player, score) in enumerate(top3, 1):
        print(f"  第{rank}名: {player} - {int(score)}分")

    # ZREVRANK：获取某玩家排名（从0开始，+1 转为1起）
    rank = r.zrevrank(key, "player:张三")
    print(f"张三当前排名: 第{rank + 1}名")

    # ZSCORE：获取分数
    score = r.zscore(key, "player:张三")
    print(f"张三当前积分: {int(score)}")

    # ZINCRBY：增加积分（原子操作，线程安全）
    new_score = r.zincrby(key, 200, "player:张三")
    print(f"张三赢了一局，+200分，新积分: {int(new_score)}")

    # 更新后重新查排名
    new_rank = r.zrevrank(key, "player:张三")
    print(f"张三更新后排名: 第{new_rank + 1}名")

    # ZCARD：总参与人数
    print(f"排行榜总人数: {r.zcard(key)}")

    r.delete(key)


if __name__ == "__main__":
    demo_ping()
    demo_string()
    demo_hash()
    demo_list()
    demo_set()
    demo_zset()
    print("\n" + "=" * 50)
    print("所有演示完成！")
