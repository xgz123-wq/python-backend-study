"""
Demo 4: 过期策略、淘汰策略与持久化相关操作演示
对应理论文档：4.过期淘汰策略与持久化.md

运行前提：
  - 已启动 Redis（docker-compose up -d）
  - 已安装依赖：pip install redis

运行方式：
  python 4_expiry_persistence.py
"""

import time
import redis

r = redis.Redis(host="localhost", port=6379, db=0, decode_responses=True)


# ─────────────────────────────────────────────────
# 1. Key 过期时间操作
# ─────────────────────────────────────────────────
def demo_key_expiry():
    print("=" * 50)
    print("【1. Key 过期时间操作】")

    # SETEX：设置值同时指定过期时间
    r.setex("temp_key", 5, "临时数据")
    print(f"设置 temp_key，TTL={r.ttl('temp_key')} 秒")

    # EXPIRE：对已有 Key 设置过期时间
    r.set("another_key", "普通数据")
    r.expire("another_key", 10)
    print(f"another_key TTL={r.ttl('another_key')} 秒")

    # TTL 返回值说明
    r.set("no_expire_key", "永不过期")
    print(f"无过期 Key 的 TTL={r.ttl('no_expire_key')} （-1表示无过期）")
    print(f"不存在 Key 的 TTL={r.ttl('nonexistent_key')} （-2表示不存在）")

    # PERSIST：移除过期时间（变为永久）
    r.persist("another_key")
    print(f"PERSIST 后 TTL={r.ttl('another_key')} （-1=永久）")

    # PEXPIRE / PTTL：毫秒级精度
    r.pexpire("temp_key", 3000)  # 3000毫秒=3秒
    print(f"PTTL (毫秒精度) = {r.pttl('temp_key')} ms")

    print("\n  等待2秒，观察 temp_key 是否还存在...")
    time.sleep(2)
    print(f"  2秒后 temp_key 还存在: {r.exists('temp_key') == 1}")

    print("  再等待4秒，temp_key 应过期...")
    time.sleep(4)
    print(f"  6秒后 temp_key 还存在: {r.exists('temp_key') == 1}（已过期）")

    r.delete("another_key", "no_expire_key")


# ─────────────────────────────────────────────────
# 2. 内存使用信息查询
# ─────────────────────────────────────────────────
def demo_memory_info():
    print("\n" + "=" * 50)
    print("【2. 内存与淘汰策略信息】")

    info = r.info("memory")
    used_mb = info["used_memory_human"]
    peak_mb = info["used_memory_peak_human"]
    print(f"  当前内存占用: {used_mb}")
    print(f"  历史峰值内存: {peak_mb}")

    # 查看当前淘汰策略
    policy = r.config_get("maxmemory-policy")
    max_mem = r.config_get("maxmemory")
    print(f"  当前淘汰策略: {policy.get('maxmemory-policy', 'noeviction')}")
    print(f"  最大内存限制: {max_mem.get('maxmemory', '0')} 字节 (0=不限制)")


# ─────────────────────────────────────────────────
# 3. 过期 Key 的惰性删除演示
# ─────────────────────────────────────────────────
def demo_lazy_expiry():
    print("\n" + "=" * 50)
    print("【3. 惰性删除 vs 定期删除演示】")

    # 写入一批即将过期的 Key
    for i in range(5):
        r.setex(f"expire_demo:{i}", 2, f"value_{i}")

    print("  写入5个TTL=2秒的 Key")
    print(f"  立即查询存在数量: {sum(r.exists(f'expire_demo:{i}') for i in range(5))}")

    # 等待过期
    time.sleep(3)
    print("  等待3秒后...")

    # 惰性删除：只有访问时才真正删除
    for i in range(5):
        val = r.get(f"expire_demo:{i}")  # 访问时触发惰性删除
        # val 应该为 None（已过期）

    count_after = sum(r.exists(f"expire_demo:{i}") for i in range(5))
    print(f"  访问后查询存在数量: {count_after}（全部已过期并被删除）")


# ─────────────────────────────────────────────────
# 4. 持久化状态查询
# ─────────────────────────────────────────────────
def demo_persistence_info():
    print("\n" + "=" * 50)
    print("【4. 持久化状态查询】")

    info = r.info("persistence")

    # RDB 信息
    print("\n  [RDB 状态]")
    print(f"  上次 RDB 保存是否成功: {info.get('rdb_last_bgsave_status')}")
    print(f"  上次 RDB 保存时间: {info.get('rdb_last_save_time')} (Unix时间戳)")
    print(f"  当前是否在做 RDB 保存: {bool(info.get('rdb_current_bgsave_in_progress'))}")
    print(f"  上次 RDB 耗时(秒): {info.get('rdb_last_bgsave_time_sec')}")

    # AOF 信息
    print("\n  [AOF 状态]")
    print(f"  AOF 是否开启: {bool(info.get('aof_enabled'))}")
    if info.get("aof_enabled"):
        print(f"  AOF 文件大小: {info.get('aof_current_size')} bytes")
        print(f"  AOF 是否在重写: {bool(info.get('aof_rewrite_in_progress'))}")

    # 统计信息
    stats = r.info("stats")
    print("\n  [统计信息]")
    print(f"  已过期删除的 Key 数: {stats.get('expired_keys')}")
    print(f"  被淘汰的 Key 数: {stats.get('evicted_keys')}")
    print(f"  缓存命中次数: {stats.get('keyspace_hits')}")
    print(f"  缓存未命中次数: {stats.get('keyspace_misses')}")

    hits = stats.get("keyspace_hits", 0)
    misses = stats.get("keyspace_misses", 0)
    total = hits + misses
    if total > 0:
        hit_rate = hits / total * 100
        print(f"  缓存命中率: {hit_rate:.1f}%")


# ─────────────────────────────────────────────────
# 5. 手动触发 RDB 持久化
# ─────────────────────────────────────────────────
def demo_manual_rdb():
    print("\n" + "=" * 50)
    print("【5. 手动触发 RDB 持久化（BGSAVE）】")

    # 写入一些数据
    for i in range(100):
        r.set(f"rdb_test:{i}", f"value_{i}")

    # 触发异步后台保存
    r.bgsave()
    print("  已触发 BGSAVE（异步，不阻塞）")

    # 查询保存状态
    time.sleep(0.5)
    info = r.info("persistence")
    print(f"  BGSAVE 状态: {info.get('rdb_last_bgsave_status')}")
    print(f"  最近保存时间: {info.get('rdb_last_save_time')}")

    # 清理测试数据
    for i in range(100):
        r.delete(f"rdb_test:{i}")


if __name__ == "__main__":
    demo_key_expiry()
    demo_memory_info()
    demo_lazy_expiry()
    demo_persistence_info()
    demo_manual_rdb()
    print("\n" + "=" * 50)
    print("过期策略与持久化演示完成！")
