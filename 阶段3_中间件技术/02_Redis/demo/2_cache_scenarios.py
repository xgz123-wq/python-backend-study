"""
Demo 2: Redis 典型使用场景（缓存、Session、排行榜、分布式锁）
对应理论文档：2.典型使用场景.md

运行前提：
  - 已启动 Redis（docker-compose up -d）
  - 已安装依赖：pip install redis

运行方式：
  python 2_cache_scenarios.py
"""

import json
import time
import uuid
import random
import threading
import redis

r = redis.Redis(host="localhost", port=6379, db=0, decode_responses=True)


# ─────────────────────────────────────────────────
# 模拟数据库（用字典替代真实数据库）
# ─────────────────────────────────────────────────
FAKE_DB = {
    1: {"id": 1, "name": "张三", "age": 28, "email": "zs@example.com"},
    2: {"id": 2, "name": "李四", "age": 25, "email": "ls@example.com"},
    3: {"id": 3, "name": "王五", "age": 30, "email": "ww@example.com"},
}
DB_QUERY_COUNT = 0  # 记录数据库查询次数


def fake_db_get_user(user_id: int) -> dict | None:
    """模拟数据库查询（有50ms延迟）"""
    global DB_QUERY_COUNT
    DB_QUERY_COUNT += 1
    time.sleep(0.05)  # 模拟数据库 IO 延迟
    return FAKE_DB.get(user_id)


# ─────────────────────────────────────────────────
# 场景一：Cache-Aside 缓存模式
# ─────────────────────────────────────────────────
def get_user_with_cache(user_id: int) -> dict | None:
    """带缓存的用户查询（Cache-Aside 模式）"""
    cache_key = f"user:{user_id}"

    # 1. 先查缓存
    cached = r.get(cache_key)
    if cached:
        print(f"  [缓存命中] user:{user_id}")
        return json.loads(cached)

    # 2. 缓存未命中，查数据库
    print(f"  [缓存未命中] user:{user_id} → 查数据库")
    user = fake_db_get_user(user_id)

    # 3. 写入缓存
    if user:
        r.setex(cache_key, 60, json.dumps(user, ensure_ascii=False))

    return user


def update_user_with_cache(user_id: int, new_data: dict):
    """更新用户（先写库，再删缓存）"""
    FAKE_DB[user_id] = {**FAKE_DB.get(user_id, {}), **new_data}
    r.delete(f"user:{user_id}")
    print(f"  [更新] user:{user_id} → 删除缓存")


def demo_cache():
    print("\n" + "=" * 50)
    print("【场景一：Cache-Aside 缓存】")
    global DB_QUERY_COUNT
    DB_QUERY_COUNT = 0

    # 第1次：缓存未命中，查数据库
    user = get_user_with_cache(1)
    print(f"  结果: {user}")

    # 第2次：缓存命中，不查数据库
    user = get_user_with_cache(1)
    print(f"  结果: {user}")

    # 第3次：同样命中
    get_user_with_cache(1)

    print(f"\n  共查询数据库 {DB_QUERY_COUNT} 次（3次请求只查了1次）")

    # 更新数据后，缓存失效
    update_user_with_cache(1, {"age": 29})
    print("  更新后重新查询:")
    user = get_user_with_cache(1)  # 缓存被删，重新查库
    print(f"  结果: {user}")

    # 清理
    r.delete("user:1", "user:2", "user:3")


# ─────────────────────────────────────────────────
# 场景二：Session 存储
# ─────────────────────────────────────────────────
SESSION_EXPIRE = 30  # 30秒（演示用，实际30分钟）


def create_session(user_id: int, role: str) -> str:
    """创建 Session，返回 session_id"""
    session_id = str(uuid.uuid4())
    session_data = {"user_id": user_id, "role": role, "login_time": time.time()}
    r.setex(
        f"session:{session_id}",
        SESSION_EXPIRE,
        json.dumps(session_data),
    )
    return session_id


def get_session(session_id: str) -> dict | None:
    """获取 Session，同时刷新过期时间（滑动过期）"""
    data = r.get(f"session:{session_id}")
    if not data:
        return None
    r.expire(f"session:{session_id}", SESSION_EXPIRE)  # 刷新过期时间
    return json.loads(data)


def delete_session(session_id: str):
    """注销（删除 Session）"""
    r.delete(f"session:{session_id}")


def demo_session():
    print("\n" + "=" * 50)
    print("【场景二：Session 存储】")

    # 登录创建 Session
    sid = create_session(user_id=1001, role="admin")
    print(f"  登录成功，session_id = {sid[:8]}...（已截断）")

    # 验证 Session
    session = get_session(sid)
    print(f"  验证 Session: user_id={session['user_id']}, role={session['role']}")
    print(f"  TTL = {r.ttl(f'session:{sid}')} 秒（每次访问刷新）")

    # 注销
    delete_session(sid)
    result = get_session(sid)
    print(f"  注销后验证 Session: {result}")  # None


# ─────────────────────────────────────────────────
# 场景三：排行榜
# ─────────────────────────────────────────────────
def demo_leaderboard():
    print("\n" + "=" * 50)
    print("【场景三：排行榜（ZSet）】")

    key = "demo:leaderboard"
    r.delete(key)

    # 模拟玩家积分数据
    players = {
        "player:张三": 9800,
        "player:李四": 9500,
        "player:王五": 8800,
        "player:赵六": 9900,
        "player:钱七": 7600,
        "player:孙八": 10200,
    }
    r.zadd(key, players)

    # 获取 Top 3
    print("  Top 3 排行榜:")
    top3 = r.zrevrange(key, 0, 2, withscores=True)
    for i, (player, score) in enumerate(top3, 1):
        print(f"    第{i}名: {player} - {int(score)}分")

    # 张三打了一局，+500分
    r.zincrby(key, 500, "player:张三")
    new_rank = r.zrevrank(key, "player:张三")
    new_score = r.zscore(key, "player:张三")
    print(f"\n  张三 +500分后: 积分={int(new_score)}, 排名=第{new_rank + 1}名")

    r.delete(key)


# ─────────────────────────────────────────────────
# 场景四：分布式锁
# ─────────────────────────────────────────────────
# Lua 脚本：原子检查并删除（防止误删他人的锁）
RELEASE_LOCK_LUA = """
if redis.call("GET", KEYS[1]) == ARGV[1] then
    return redis.call("DEL", KEYS[1])
else
    return 0
end
"""

purchase_count = 0  # 记录成功购买次数
stock = 10          # 商品库存


def acquire_lock(lock_key: str, expire: int = 5) -> str | None:
    lock_value = str(uuid.uuid4())
    result = r.set(lock_key, lock_value, nx=True, ex=expire)
    return lock_value if result else None


def release_lock(lock_key: str, lock_value: str) -> bool:
    result = r.eval(RELEASE_LOCK_LUA, 1, lock_key, lock_value)
    return bool(result)


def buy_product(user_id: int):
    """模拟购买：用分布式锁防止超卖"""
    global stock, purchase_count
    lock_key = "lock:product:sku_001"

    lock_value = acquire_lock(lock_key, expire=3)
    if not lock_value:
        print(f"  用户{user_id}: 系统繁忙，获取锁失败")
        return

    try:
        # 临界区：检查库存并扣减
        if stock <= 0:
            print(f"  用户{user_id}: 库存不足")
            return

        # 模拟业务处理时间
        time.sleep(random.uniform(0.01, 0.05))
        stock -= 1
        purchase_count += 1
        print(f"  用户{user_id}: 购买成功！剩余库存: {stock}")
    finally:
        release_lock(lock_key, lock_value)


def demo_distributed_lock():
    print("\n" + "=" * 50)
    print("【场景四：分布式锁（防超卖）】")
    print(f"  初始库存: {stock} 件，模拟 20 个用户并发抢购")

    r.delete("lock:product:sku_001")

    # 20 个线程并发购买
    threads = [threading.Thread(target=buy_product, args=(i,)) for i in range(1, 21)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    print(f"\n  最终结果: 库存={stock}, 成功购买={purchase_count}")
    print(f"  是否超卖: {'否 ✓' if purchase_count <= 10 else '是 ✗（有Bug）'}")


if __name__ == "__main__":
    demo_cache()
    demo_session()
    demo_leaderboard()
    demo_distributed_lock()
    print("\n" + "=" * 50)
    print("场景演示完成！")
