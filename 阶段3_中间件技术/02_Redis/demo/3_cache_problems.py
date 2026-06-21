"""
Demo 3: 缓存三大问题演示（穿透、击穿、雪崩）
对应理论文档：3.缓存问题穿透击穿雪崩.md

运行前提：
  - 已启动 Redis（docker-compose up -d）
  - 已安装依赖：pip install redis

运行方式：
  python 3_cache_problems.py
"""

import json
import time
import uuid
import random
import threading
import redis

r = redis.Redis(host="localhost", port=6379, db=0, decode_responses=True)

# 数据库查询计数
db_query_count = 0


def fake_db_get_product(product_id: int) -> dict | None:
    """模拟数据库查询（30ms延迟），只有 id=1~5 的商品存在"""
    global db_query_count
    db_query_count += 1
    time.sleep(0.03)
    if 1 <= product_id <= 5:
        return {"id": product_id, "name": f"商品{product_id}", "price": product_id * 100}
    return None  # 不存在


# ─────────────────────────────────────────────────
# 问题一：缓存穿透
# ─────────────────────────────────────────────────
def get_product_without_protection(product_id: int) -> dict | None:
    """没有防护的查询（有穿透漏洞）"""
    cache_key = f"product:{product_id}"
    cached = r.get(cache_key)
    if cached:
        return json.loads(cached)

    product = fake_db_get_product(product_id)
    if product:
        r.setex(cache_key, 60, json.dumps(product))
    # ← 漏洞：null 结果没有缓存！下次还会查数据库

    return product


def get_product_with_null_cache(product_id: int) -> dict | None:
    """解决方案1：缓存空值"""
    cache_key = f"product:{product_id}"
    cached = r.get(cache_key)

    if cached is not None:
        if cached == "NULL":
            return None  # 命中空值缓存
        return json.loads(cached)

    product = fake_db_get_product(product_id)

    if product is None:
        r.setex(cache_key, 60, "NULL")  # 缓存空值，5分钟（演示用60s）
        return None

    r.setex(cache_key, 300, json.dumps(product))
    return product


def demo_cache_penetration():
    print("\n" + "=" * 50)
    print("【问题一：缓存穿透（Penetration）】")
    global db_query_count

    # 演示穿透问题
    print("\n  [无防护] 5次查询不存在的 id=-1:")
    r.flushdb()
    db_query_count = 0
    for _ in range(5):
        get_product_without_protection(-1)
    print(f"  → 数据库被查询了 {db_query_count} 次（每次都穿透！）")

    # 演示空值缓存解决方案
    print("\n  [有防护-空值缓存] 5次查询不存在的 id=-1:")
    r.flushdb()
    db_query_count = 0
    for _ in range(5):
        get_product_with_null_cache(-1)
    print(f"  → 数据库被查询了 {db_query_count} 次（只查了1次，后续命中空值缓存）")
    print(f"  → Redis 中缓存的空值: {r.get('product:-1')}")

    r.flushdb()


# ─────────────────────────────────────────────────
# 问题二：缓存击穿
# ─────────────────────────────────────────────────
RELEASE_LOCK_LUA = """
if redis.call("GET", KEYS[1]) == ARGV[1] then
    return redis.call("DEL", KEYS[1])
else
    return 0
end
"""

db_hit_count_breakdown = 0  # 统计数据库并发命中次数


def get_hot_product_no_protection(product_id: int) -> dict | None:
    """无保护（模拟击穿瞬间）"""
    global db_hit_count_breakdown
    cache_key = f"hot_product:{product_id}"
    cached = r.get(cache_key)
    if cached:
        return json.loads(cached)

    # 模拟数据库查询（50ms）
    db_hit_count_breakdown += 1
    time.sleep(0.05)
    product = {"id": product_id, "name": f"热门商品{product_id}"}
    r.setex(cache_key, 3, json.dumps(product))  # 缓存3秒（演示短TTL）
    return product


def get_hot_product_with_mutex(product_id: int) -> dict | None:
    """解决方案：互斥锁（只允许一个请求查库）"""
    global db_hit_count_breakdown
    cache_key = f"hot_product_mutex:{product_id}"
    lock_key = f"lock:hot_product:{product_id}"

    cached = r.get(cache_key)
    if cached:
        return json.loads(cached)

    lock_value = str(uuid.uuid4())
    acquired = r.set(lock_key, lock_value, nx=True, ex=3)

    if acquired:
        try:
            db_hit_count_breakdown += 1
            time.sleep(0.05)  # 模拟数据库查询
            product = {"id": product_id, "name": f"热门商品{product_id}"}
            r.setex(cache_key, 10, json.dumps(product))
            return product
        finally:
            r.eval(RELEASE_LOCK_LUA, 1, lock_key, lock_value)
    else:
        time.sleep(0.06)  # 等待锁释放后重试
        cached = r.get(cache_key)
        return json.loads(cached) if cached else None


def demo_cache_breakdown():
    print("\n" + "=" * 50)
    print("【问题二：缓存击穿（Breakdown）】")
    global db_hit_count_breakdown

    thread_count = 20

    # 演示无保护（模拟 Key 过期瞬间的并发）
    print(f"\n  [无保护] {thread_count} 个并发请求同时 Miss（模拟热点Key过期瞬间）:")
    r.flushdb()
    db_hit_count_breakdown = 0
    threads = [
        threading.Thread(target=get_hot_product_no_protection, args=(1,))
        for _ in range(thread_count)
    ]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    print(f"  → 数据库被并发查询了 {db_hit_count_breakdown} 次（击穿！）")

    # 演示互斥锁保护
    print(f"\n  [互斥锁保护] {thread_count} 个并发请求同时 Miss:")
    r.flushdb()
    db_hit_count_breakdown = 0
    threads = [
        threading.Thread(target=get_hot_product_with_mutex, args=(1,))
        for _ in range(thread_count)
    ]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    print(f"  → 数据库只被查询了 {db_hit_count_breakdown} 次（互斥锁生效！）")

    r.flushdb()


# ─────────────────────────────────────────────────
# 问题三：缓存雪崩
# ─────────────────────────────────────────────────
def demo_cache_avalanche():
    print("\n" + "=" * 50)
    print("【问题三：缓存雪崩（Avalanche）- TTL 随机抖动演示】")

    # 模拟 10 个 Key，观察过期时间分布
    print("\n  [无抖动] 所有 Key 相同 TTL=10秒:")
    for i in range(10):
        r.setex(f"product_no_jitter:{i}", 10, f"data_{i}")

    ttls = [r.ttl(f"product_no_jitter:{i}") for i in range(10)]
    print(f"  TTL 分布: {ttls}")
    print(f"  → 所有 Key 将在同一时刻集中过期！（雪崩风险）")

    print("\n  [有抖动] TTL 基准10秒，±20% 随机抖动:")
    for i in range(10):
        base_ttl = 10
        jitter = random.randint(-base_ttl // 5, base_ttl // 5)  # ±20%
        actual_ttl = base_ttl + jitter
        r.setex(f"product_jitter:{i}", actual_ttl, f"data_{i}")

    ttls_jitter = [r.ttl(f"product_jitter:{i}") for i in range(10)]
    print(f"  TTL 分布: {ttls_jitter}")
    print(f"  → Key 的过期时间分散在 {min(ttls_jitter)}~{max(ttls_jitter)} 秒之间")
    print(f"  → 不会同时大量过期，避免雪崩")

    # 清理
    for i in range(10):
        r.delete(f"product_no_jitter:{i}", f"product_jitter:{i}")


if __name__ == "__main__":
    demo_cache_penetration()
    demo_cache_breakdown()
    demo_cache_avalanche()
    print("\n" + "=" * 50)
    print("三大缓存问题演示完成！")
