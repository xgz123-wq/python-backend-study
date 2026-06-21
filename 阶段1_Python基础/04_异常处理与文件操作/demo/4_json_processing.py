"""
Demo 4: JSON 处理
对应理论文档: 4.JSON处理.md

演示 json.dumps/loads（字符串）、json.dump/load（文件）、
特殊类型序列化、API 响应构造、配置管理器。
注意：本 Demo 会在当前目录创建临时文件，运行结束后自动清理。
"""

import json
from pathlib import Path
from datetime import datetime, date

# 临时目录
TEMP_DIR = Path(__file__).parent / "temp_json"
TEMP_DIR.mkdir(exist_ok=True)

# ============================================================
# 第一部分：dumps — Python → JSON 字符串
# ============================================================

print("=" * 55)
print("第一部分：json.dumps — Python → JSON 字符串")
print("=" * 55)

user = {
    "name": "张三",
    "age": 20,
    "skills": ["Python", "FastAPI", "MySQL"],
    "is_active": True,
    "address": None,
}

# 默认输出（中文变成 \uXXXX）
json_str = json.dumps(user)
print(f"  默认: {json_str}")

# ensure_ascii=False 保留中文
json_str = json.dumps(user, ensure_ascii=False)
print(f"  中文: {json_str}")

# indent 格式化
json_str = json.dumps(user, ensure_ascii=False, indent=2)
print(f"  格式化:\n{json_str}")

# sort_keys 排序
json_str = json.dumps(user, ensure_ascii=False, indent=2, sort_keys=True)
print(f"\n  排序后:\n{json_str}")


# ============================================================
# 第二部分：loads — JSON 字符串 → Python
# ============================================================

print("\n" + "=" * 55)
print("第二部分：json.loads — JSON 字符串 → Python")
print("=" * 55)

json_str = '{"name": "张三", "age": 20, "is_active": true, "address": null}'
data = json.loads(json_str)

print(f"  类型: {type(data).__name__}")
print(f"  内容: {data}")
print(f"  name: {data['name']}")
print(f"  is_active: {data['is_active']} (类型: {type(data['is_active']).__name__})")
print(f"  address: {data['address']} (类型: {type(data['address']).__name__})")

# 类型转换对照
print(f"\n  JSON → Python 类型转换:")
print(f"    true  → {json.loads('true')}  ({type(json.loads('true')).__name__})")
print(f"    false → {json.loads('false')} ({type(json.loads('false')).__name__})")
print(f"    null  → {json.loads('null')}  ({type(json.loads('null')).__name__})")
print(f"    123   → {json.loads('123')}   ({type(json.loads('123')).__name__})")
print(f"    3.14  → {json.loads('3.14')}  ({type(json.loads('3.14')).__name__})")


# ============================================================
# 第三部分：dump/load — 文件读写
# ============================================================

print("\n" + "=" * 55)
print("第三部分：json.dump/load — 文件读写")
print("=" * 55)

users = [
    {"id": 1, "name": "张三", "email": "zs@qq.com", "role": "admin"},
    {"id": 2, "name": "李四", "email": "ls@qq.com", "role": "user"},
    {"id": 3, "name": "王五", "email": "ww@qq.com", "role": "user"},
]

# 写入 JSON 文件
json_file = TEMP_DIR / "users.json"
with open(json_file, "w", encoding="utf-8") as f:
    json.dump(users, f, ensure_ascii=False, indent=2)
print(f"  写入: {json_file}")
print(f"  文件内容:\n{json_file.read_text(encoding='utf-8')}")

# 从文件读取
with open(json_file, "r", encoding="utf-8") as f:
    loaded_users = json.load(f)
print(f"  读取回来: {len(loaded_users)} 个用户")
for u in loaded_users:
    print(f"    {u['id']}: {u['name']} <{u['email']}> ({u['role']})")


# ============================================================
# 第四部分：处理特殊类型
# ============================================================

print("\n" + "=" * 55)
print("第四部分：处理特殊类型（datetime/Path/set）")
print("=" * 55)

# 直接序列化特殊类型会报错
print("  --- 默认不支持 datetime ---")
try:
    json.dumps({"time": datetime.now()})
except TypeError as e:
    print(f"  ❌ {e}")


# 方式一：自定义编码器
class CustomEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, (datetime, date)):
            return obj.isoformat()
        if isinstance(obj, Path):
            return str(obj)
        if isinstance(obj, set):
            return sorted(list(obj))
        return super().default(obj)


data_special = {
    "created_at": datetime(2024, 3, 15, 10, 30, 0),
    "date": date(2024, 3, 15),
    "config_path": Path("/etc/app/config.json"),
    "tags": {"python", "backend", "fastapi"},
}

print(f"\n  --- 自定义编码器 ---")
json_str = json.dumps(data_special, cls=CustomEncoder, ensure_ascii=False, indent=2)
print(json_str)

# 方式二：default=str（简单粗暴）
print(f"\n  --- default=str（简单场景）---")
json_str = json.dumps(data_special, default=str, ensure_ascii=False, indent=2)
print(json_str)


# ============================================================
# 第五部分：后端场景 — API 响应构造
# ============================================================

print("\n" + "=" * 55)
print("第五部分：后端场景 — API 响应构造")
print("=" * 55)


def make_response(data=None, code=200, message="success"):
    """构造标准 API 响应"""
    response = {
        "code": code,
        "message": message,
        "data": data,
    }
    return json.dumps(response, ensure_ascii=False, indent=2)


# 成功响应
print("  --- 成功响应 ---")
print(make_response(
    data={"id": 1, "name": "张三", "email": "zs@qq.com"},
))

# 列表响应（带分页）
print("\n  --- 列表响应 ---")
print(make_response(
    data={
        "items": [
            {"id": 1, "name": "张三"},
            {"id": 2, "name": "李四"},
        ],
        "total": 50,
        "page": 1,
        "page_size": 10,
    },
))

# 错误响应
print("\n  --- 错误响应 ---")
print(make_response(data=None, code=404, message="用户不存在"))


# ============================================================
# 第六部分：后端场景 — 解析第三方 API
# ============================================================

print("\n" + "=" * 55)
print("第六部分：后端场景 — 解析第三方 API 响应")
print("=" * 55)

# 模拟第三方 API 返回
api_response = '''
{
    "status": "success",
    "data": {
        "users": [
            {"id": 1, "name": "张三", "role": "admin", "score": 95},
            {"id": 2, "name": "李四", "role": "user", "score": 87},
            {"id": 3, "name": "王五", "role": "user", "score": 72}
        ],
        "pagination": {
            "total": 100,
            "page": 1,
            "per_page": 10
        }
    }
}
'''

result = json.loads(api_response)

# 安全取值（用 get 避免 KeyError）
status = result.get("status", "unknown")
users = result.get("data", {}).get("users", [])
pagination = result.get("data", {}).get("pagination", {})

print(f"  状态: {status}")
print(f"  用户数: {len(users)}")
print(f"  分页: 第 {pagination.get('page')} 页，共 {pagination.get('total')} 条")
print(f"\n  用户列表:")
for user in users:
    print(f"    {user['id']}: {user['name']} ({user['role']}) - 分数: {user['score']}")


# ============================================================
# 第七部分：后端场景 — JSON 配置管理器
# ============================================================

print("\n" + "=" * 55)
print("第七部分：后端场景 — JSON 配置管理器")
print("=" * 55)


class JsonConfig:
    """JSON 配置文件管理器"""
    def __init__(self, filepath):
        self.path = Path(filepath)
        self.data = {}
        self._load()

    def _load(self):
        if self.path.exists():
            self.data = json.loads(self.path.read_text(encoding="utf-8"))

    def save(self):
        self.path.write_text(
            json.dumps(self.data, ensure_ascii=False, indent=2),
            encoding="utf-8"
        )

    def get(self, key, default=None):
        return self.data.get(key, default)

    def set(self, key, value):
        self.data[key] = value
        self.save()

    def delete(self, key):
        if key in self.data:
            del self.data[key]
            self.save()

    def __repr__(self):
        return f"JsonConfig({self.data})"


config_file = TEMP_DIR / "app_config.json"
config = JsonConfig(config_file)

config.set("app_name", "我的后端项目")
config.set("debug", True)
config.set("database", {
    "host": "localhost",
    "port": 3306,
    "name": "myapp"
})
config.set("allowed_origins", ["http://localhost:3000", "https://myapp.com"])

print(f"  配置文件内容:")
print(config_file.read_text(encoding="utf-8"))

print(f"  读取配置:")
print(f"    app_name: {config.get('app_name')}")
print(f"    debug: {config.get('debug')}")
print(f"    db_host: {config.get('database', {}).get('host')}")


# ============================================================
# 第八部分：常见坑演示
# ============================================================

print("\n" + "=" * 55)
print("第八部分：常见坑")
print("=" * 55)

# 坑1：int 键会变成 str
print("  坑1: int 键变 str 键")
data = {1: "one", 2: "two"}
json_str = json.dumps(data)
loaded = json.loads(json_str)
print(f"    原始: {data}")
print(f"    转回: {loaded}")
print(f"    键类型变了: {type(list(loaded.keys())[0]).__name__}")

# 坑2：单引号不是合法 JSON
print(f"\n  坑2: 单引号不合法")
try:
    json.loads("{'name': 'zhangsan'}")
except json.JSONDecodeError as e:
    print(f"    ❌ {e}")
print(f"    ✅ 正确: {json.loads('{\"name\": \"zhangsan\"}')}")

# 坑3：混淆 loads/load
print(f"\n  坑3: loads 接收字符串，load 接收文件对象")
print(f"    json.loads(字符串) → Python 对象")
print(f"    json.load(文件对象) → Python 对象")
print(f"    json.dumps(Python) → 字符串")
print(f"    json.dump(Python, 文件对象) → 写入文件")


# ============================================================
# 清理临时文件
# ============================================================

print("\n" + "=" * 55)
print("清理临时文件...")
print("=" * 55)

import shutil
shutil.rmtree(TEMP_DIR)
print(f"  已删除: {TEMP_DIR}")


print("\n" + "=" * 55)
print("✅ Demo 4 完成！")
print("=" * 55)
