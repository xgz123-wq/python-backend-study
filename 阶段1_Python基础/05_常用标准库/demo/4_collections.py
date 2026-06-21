"""
Demo 4: collections
对应理论文档: 4.collections.md

演示 Counter 和 defaultdict 的典型用法。
"""

from collections import Counter, defaultdict


print("=" * 55)
print("第一部分：Counter 基础")
print("=" * 55)

counter = Counter("banana")
print(f"Counter('banana') = {counter}")
print(f"'a' 出现次数 = {counter['a']}")
print(f"出现最多的 2 个元素 = {counter.most_common(2)}")


print("\n" + "=" * 55)
print("第二部分：访问次数统计")
print("=" * 55)

visits = ["u1", "u2", "u1", "u3", "u1", "u2", "u4"]
visit_counter = Counter(visits)
print(visit_counter)


print("\n" + "=" * 55)
print("第三部分：defaultdict 分组")
print("=" * 55)

topics = [
    ("python", "装饰器"),
    ("python", "生成器"),
    ("backend", "HTTP"),
    ("backend", "Redis"),
]

grouped = defaultdict(list)
for category, item in topics:
    grouped[category].append(item)

print(dict(grouped))


print("\n" + "=" * 55)
print("第四部分：后端场景模拟")
print("=" * 55)

status_codes = [200, 200, 404, 500, 200, 404, 401]
status_counter = Counter(status_codes)
print(f"状态码统计 = {status_counter}")

routes = [
    ("GET", "/users"),
    ("POST", "/users"),
    ("GET", "/orders"),
    ("GET", "/users"),
]

route_map = defaultdict(list)
for method, path in routes:
    route_map[path].append(method)

print(f"路由分组 = {dict(route_map)}")


print("\n" + "=" * 55)
print("Demo 4 完成!")
print("=" * 55)
