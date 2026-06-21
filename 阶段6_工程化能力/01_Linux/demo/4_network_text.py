"""
Demo 4: 网络与文本处理 - 用 Python 实现 Linux 工具
对应理论文档: 4.网络与文本处理.md

本 Demo 用 Python 实现 Linux 常用网络和文本处理工具的等效功能：
- 用 urllib 实现类似 curl 的 HTTP 请求
- 用 socket 检查端口连通性
- 用 re 模块模拟 grep 功能
- 简单的日志分析脚本
- Shell 脚本的 Python 等效实现

这些是后端开发者日常最常用的技能组合。
"""

import os
import sys
import re
import socket
import json
import tempfile
import platform
import subprocess
from urllib.request import urlopen, Request
from urllib.error import URLError, HTTPError
from collections import Counter, defaultdict
from datetime import datetime

# ============================================================
# 工具函数
# ============================================================

def print_section(title):
    """打印分隔线和标题"""
    print(f"\n{'=' * 60}")
    print(f"  {title}")
    print(f"{'=' * 60}")


IS_LINUX = platform.system() == "Linux"
IS_WINDOWS = platform.system() == "Windows"


# ============================================================
# 第一部分：HTTP 请求（类似 curl）
# ============================================================

print_section("第一部分：HTTP 请求（Python 版 curl）")

# --- GET 请求 ---
print("\n# GET 请求 (等价于 curl https://httpbin.org/get)")

try:
    url = "https://httpbin.org/get?name=alice&age=25"
    print(f"  请求 URL: {url}")

    # urlopen 是 Python 标准库的 HTTP 客户端
    # 类似于 curl 的 GET 请求
    req = Request(url)
    req.add_header('User-Agent', 'Python-urllib/Demo')

    with urlopen(req, timeout=10) as response:
        # 读取响应
        status_code = response.status
        headers = dict(response.headers)
        body = response.read().decode('utf-8')

    print(f"  状态码: {status_code}")
    print(f"  Content-Type: {headers.get('Content-Type', 'N/A')}")

    # 解析 JSON 响应
    data = json.loads(body)
    print(f"  响应数据:")
    print(f"    URL: {data.get('url', 'N/A')}")
    print(f"    参数: {data.get('args', {})}")
    print(f"    Headers: {json.dumps(data.get('headers', {}), indent=6)}")

except (URLError, HTTPError, socket.timeout) as e:
    print(f"  [网络错误] {e}")
    print("  提示: 如果无法访问 httpbin.org，请检查网络连接")
except Exception as e:
    print(f"  [错误] {e}")

# --- POST 请求 ---
print("\n# POST 请求 (等价于 curl -X POST -d '...' url)")

try:
    url = "https://httpbin.org/post"
    payload = json.dumps({"name": "Alice", "age": 25, "role": "backend"}).encode('utf-8')

    req = Request(url, data=payload, method='POST')
    req.add_header('Content-Type', 'application/json')
    req.add_header('User-Agent', 'Python-urllib/Demo')

    with urlopen(req, timeout=10) as response:
        body = response.read().decode('utf-8')

    data = json.loads(body)
    print(f"  状态码: {response.status}")
    print(f"  发送的数据: {data.get('json', {})}")

except (URLError, HTTPError, socket.timeout) as e:
    print(f"  [网络错误] {e}")
except Exception as e:
    print(f"  [错误] {e}")


# ============================================================
# 第二部分：端口连通性检查（类似 netstat/ss）
# ============================================================

print_section("第二部分：端口连通性检查")

def check_port(host, port, timeout=2):
    """
    检查指定主机的端口是否开放。

    原理: 尝试建立 TCP 连接，成功则端口开放，失败则关闭。
    类似于: telnet host port 或 nc -zv host port
    """
    try:
        # 创建 TCP socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        result = sock.connect_ex((host, port))
        sock.close()
        return result == 0  # 0 表示连接成功
    except (socket.timeout, socket.error):
        return False


# 检查常见端口
print("\n# 检查本机常见端口")
ports_to_check = [
    (22, "SSH"),
    (80, "HTTP"),
    (443, "HTTPS"),
    (3306, "MySQL"),
    (5432, "PostgreSQL"),
    (6379, "Redis"),
    (8080, "HTTP Alt"),
    (27017, "MongoDB"),
]

print(f"  {'端口':<8}{'服务':<15}{'状态'}")
print(f"  {'-'*35}")
for port, service in ports_to_check:
    is_open = check_port("localhost", port, timeout=1)
    status = "✅ 开放" if is_open else "❌ 关闭"
    print(f"  {port:<8}{service:<15}{status}")

# 检查远程主机
print(f"\n# 检查远程主机端口 (类似 nc -zv)")
remote_host = "httpbin.org"
for port in [80, 443]:
    is_open = check_port(remote_host, port, timeout=3)
    status = "开放" if is_open else "关闭"
    print(f"  {remote_host}:{port} -> {status}")

# 获取本机 IP
print(f"\n# 网络信息")
hostname = socket.gethostname()
print(f"  主机名: {hostname}")
try:
    local_ip = socket.gethostbyname(hostname)
    print(f"  本机 IP: {local_ip}")
except socket.gaierror:
    print(f"  本机 IP: 无法获取")


# ============================================================
# 第三部分：文本搜索（Python 版 grep）
# ============================================================

print_section("第三部分：文本搜索（Python 版 grep）")

# 创建模拟日志文件
log_dir = tempfile.mkdtemp(prefix="log_demo_")
log_file = os.path.join(log_dir, "app.log")

# 生成模拟日志数据
sample_logs = [
    '2024-01-15 10:00:01 INFO  [main] Application started on port 8080',
    '2024-01-15 10:00:02 INFO  [db] Connected to PostgreSQL at localhost:5432',
    '2024-01-15 10:00:05 WARN  [cache] Redis connection timeout, retrying...',
    '2024-01-15 10:00:06 INFO  [cache] Redis connected successfully',
    '2024-01-15 10:01:00 INFO  [api] GET /api/users 200 45ms',
    '2024-01-15 10:01:02 ERROR [api] GET /api/users/999 404 12ms - User not found',
    '2024-01-15 10:01:05 INFO  [api] POST /api/users 201 89ms',
    '2024-01-15 10:02:00 WARN  [auth] Failed login attempt for user "admin"',
    '2024-01-15 10:02:01 WARN  [auth] Failed login attempt for user "admin"',
    '2024-01-15 10:02:02 ERROR [auth] Account locked: too many failed attempts for "admin"',
    '2024-01-15 10:03:00 INFO  [api] GET /api/products 200 23ms',
    '2024-01-15 10:03:15 ERROR [db] Connection pool exhausted, waiting...',
    '2024-01-15 10:03:16 INFO  [db] Connection pool recovered',
    '2024-01-15 10:04:00 INFO  [api] DELETE /api/users/42 200 34ms',
    '2024-01-15 10:05:00 INFO  [scheduler] Running daily cleanup task',
    '2024-01-15 10:05:30 INFO  [scheduler] Cleanup completed: removed 150 expired sessions',
    '2024-01-15 10:06:00 ERROR [api] POST /api/orders 500 234ms - Internal server error',
    '2024-01-15 10:06:01 ERROR [api] Traceback: NullPointerException in OrderService',
    '2024-01-15 10:07:00 INFO  [api] GET /health 200 2ms',
    '2024-01-15 10:08:00 INFO  [main] Shutting down gracefully...',
]

with open(log_file, 'w', encoding='utf-8') as f:
    f.write('\n'.join(sample_logs) + '\n')

print(f"  模拟日志文件: {log_file}")
print(f"  共 {len(sample_logs)} 行日志")

# --- grep: 搜索关键词 ---
print("\n# 搜索 'ERROR' (等价于 grep 'ERROR' app.log)")
with open(log_file, 'r', encoding='utf-8') as f:
    for i, line in enumerate(f, 1):
        if "ERROR" in line:
            print(f"  行 {i}: {line.strip()}")

# --- grep -i: 忽略大小写 ---
print("\n# 忽略大小写搜索 'error' (等价于 grep -i 'error' app.log)")
with open(log_file, 'r', encoding='utf-8') as f:
    for i, line in enumerate(f, 1):
        if re.search(r'error', line, re.IGNORECASE):
            print(f"  行 {i}: {line.strip()}")

# --- grep -c: 统计匹配数 ---
print("\n# 统计各级别日志数量 (等价于 grep -c)")
level_counts = Counter()
with open(log_file, 'r', encoding='utf-8') as f:
    for line in f:
        match = re.search(r'\b(INFO|WARN|ERROR)\b', line)
        if match:
            level_counts[match.group(1)] += 1

for level, count in level_counts.most_common():
    print(f"  {level}: {count} 条")

# --- grep -E: 正则表达式搜索 ---
print("\n# 正则搜索状态码 4xx/5xx (等价于 grep -E '(4|5)\\d{2}' app.log)")
pattern = re.compile(r'\b([45]\d{2})\b')
with open(log_file, 'r', encoding='utf-8') as f:
    for line in f:
        match = pattern.search(line)
        if match:
            print(f"  状态码 {match.group(1)}: {line.strip()}")

# --- grep -A: 显示上下文 ---
print("\n# 显示 ERROR 行及其后 1 行 (等价于 grep -A 1 'ERROR')")
lines = sample_logs
for i, line in enumerate(lines):
    if "ERROR" in line:
        print(f"  >>> {line}")
        if i + 1 < len(lines):
            print(f"      {lines[i+1]}")


# ============================================================
# 第四部分：日志分析脚本
# ============================================================

print_section("第四部分：日志分析脚本")

print("\n# 完整的日志分析（类似 awk 统计分析）")

# 解析日志
log_entries = []
log_pattern = re.compile(
    r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}) '  # 时间戳
    r'(\w+)\s+'                                    # 日志级别
    r'\[(\w+)\]\s+'                                # 模块
    r'(.+)'                                        # 消息
)

with open(log_file, 'r', encoding='utf-8') as f:
    for line in f:
        match = log_pattern.match(line.strip())
        if match:
            log_entries.append({
                'timestamp': match.group(1),
                'level': match.group(2),
                'module': match.group(3),
                'message': match.group(4),
            })

# --- 按模块统计错误 ---
print("\n## 1. 按模块统计错误数 (awk '{print $4}' | sort | uniq -c)")
module_errors = Counter()
for entry in log_entries:
    if entry['level'] == 'ERROR':
        module_errors[entry['module']] += 1

for module, count in module_errors.most_common():
    bar = '█' * count
    print(f"  {module:<12} {count:>3} {bar}")

# --- 统计 HTTP 状态码 ---
print("\n## 2. HTTP 状态码分布")
status_pattern = re.compile(r'\b(\d{3})\b.*?\d+ms')
status_counts = Counter()
for entry in log_entries:
    match = re.search(r'\b([1-5]\d{2})\b\s+\d+ms', entry['message'])
    if match:
        status_counts[match.group(1)] += 1

for status, count in sorted(status_counts.items()):
    print(f"  HTTP {status}: {count} 次")

# --- 提取 API 路径 ---
print("\n## 3. API 请求路径统计")
api_pattern = re.compile(r'(GET|POST|PUT|DELETE)\s+(/\S+)')
api_counts = Counter()
for entry in log_entries:
    match = api_pattern.search(entry['message'])
    if match:
        method_path = f"{match.group(1)} {match.group(2)}"
        api_counts[method_path] += 1

for api, count in api_counts.most_common():
    print(f"  {api:<35} {count} 次")

# --- 时间线分析 ---
print("\n## 4. 每分钟事件数量")
minute_counts = Counter()
for entry in log_entries:
    # 提取 HH:MM
    time_part = entry['timestamp'].split(' ')[1][:5]
    minute_counts[time_part] += 1

for minute in sorted(minute_counts.keys()):
    count = minute_counts[minute]
    bar = '▓' * count
    print(f"  {minute}  {count:>3} {bar}")


# ============================================================
# 第五部分：sed 等效操作（文本替换）
# ============================================================

print_section("第五部分：文本替换（Python 版 sed）")

# 创建测试文件
config_file = os.path.join(log_dir, "config.ini")
with open(config_file, 'w', encoding='utf-8') as f:
    f.write("""[server]
host = 192.168.1.100
port = 8080
debug = true

[database]
host = 192.168.1.100
port = 3306
name = myapp_db
""")

print(f"  原始配置文件: {config_file}")
with open(config_file, 'r', encoding='utf-8') as f:
    print(f.read())

# --- sed 's/old/new/g': 全局替换 ---
print("# 替换 IP 地址 (等价于 sed 's/192.168.1.100/10.0.0.1/g')")
with open(config_file, 'r', encoding='utf-8') as f:
    content = f.read()

new_content = content.replace('192.168.1.100', '10.0.0.1')

# --- sed 正则替换 ---
print("# 替换端口 (等价于 sed 's/port = [0-9]*/port = 9090/g')")
new_content = re.sub(r'port = \d+', 'port = 9090', new_content)

# --- 将 debug 改为 false ---
print("# 修改 debug 配置 (等价于 sed 's/debug = true/debug = false/')")
new_content = new_content.replace('debug = true', 'debug = false')

print(f"\n  修改后的配置:")
print(new_content)


# ============================================================
# 第六部分：Shell 脚本的 Python 等效实现
# ============================================================

print_section("第六部分：Shell 脚本 vs Python")

print("""
  很多 Shell 脚本的任务可以用 Python 更优雅地完成。
  以下对比常见的 Shell 操作和 Python 等效实现:
""")

# --- 对比 1: 遍历文件 ---
print("# 对比 1: 遍历目录下所有 .py 文件并统计行数")
print("""
  # Bash:
  total=0
  for f in $(find . -name "*.py"); do
      lines=$(wc -l < "$f")
      total=$((total + lines))
      echo "$f: $lines 行"
  done
  echo "总计: $total 行"
""")

print("  # Python 等效实现:")
# 创建一些测试 .py 文件
py_dir = os.path.join(log_dir, "scripts")
os.makedirs(py_dir, exist_ok=True)
test_scripts = {
    "main.py": "# Main app\nimport os\nprint('hello')\n",
    "utils.py": "# Utils\ndef add(a, b):\n    return a + b\n\ndef mul(a, b):\n    return a * b\n",
    "config.py": "# Config\nDEBUG = True\nPORT = 8080\n",
}
for fname, content in test_scripts.items():
    with open(os.path.join(py_dir, fname), 'w', encoding='utf-8') as f:
        f.write(content)

total_lines = 0
for root, dirs, files in os.walk(py_dir):
    for fname in sorted(files):
        if fname.endswith('.py'):
            fpath = os.path.join(root, fname)
            with open(fpath, 'r', encoding='utf-8') as f:
                lines = len(f.readlines())
            total_lines += lines
            rel = os.path.relpath(fpath, py_dir)
            print(f"    {rel}: {lines} 行")
print(f"    总计: {total_lines} 行")

# --- 对比 2: 条件判断 ---
print("\n# 对比 2: 文件存在性检查和条件逻辑")
print("""
  # Bash:
  if [ -f "/etc/nginx/nginx.conf" ]; then
      echo "Nginx 配置存在"
  else
      echo "Nginx 未安装"
  fi
""")

print("  # Python 等效实现:")
check_files = ["/etc/nginx/nginx.conf", "/etc/hosts", log_file]
for fpath in check_files:
    exists = os.path.isfile(fpath)
    size = os.path.getsize(fpath) if exists else 0
    print(f"    {fpath}: {'存在' if exists else '不存在'} ({size} bytes)")

# --- 对比 3: 环境变量 ---
print("\n# 对比 3: 环境变量操作")
print("""
  # Bash:
  export APP_ENV=production
  echo $APP_ENV
  echo $PATH
""")

print("  # Python 等效实现:")
os.environ['APP_ENV'] = 'production'
print(f"    APP_ENV = {os.environ.get('APP_ENV', '未设置')}")
print(f"    HOME = {os.environ.get('HOME', os.environ.get('USERPROFILE', '未设置'))}")

# 列出部分环境变量
print(f"\n    部分环境变量:")
env_keys = ['PATH', 'PYTHONPATH', 'USER', 'USERNAME', 'SHELL']
for key in env_keys:
    value = os.environ.get(key)
    if value:
        # 截断太长的值
        display = value if len(value) < 60 else value[:57] + "..."
        print(f"      {key} = {display}")


# ============================================================
# 第七部分：实用网络工具函数
# ============================================================

print_section("第七部分：实用网络工具函数")

def dns_lookup(domain):
    """
    DNS 查询（类似 nslookup / dig 命令）。
    """
    try:
        ip = socket.gethostbyname(domain)
        print(f"    {domain} -> {ip}")
        return ip
    except socket.gaierror as e:
        print(f"    {domain} -> 解析失败: {e}")
        return None


print("\n# DNS 查询 (类似 nslookup)")
domains = ["httpbin.org", "localhost"]
for domain in domains:
    dns_lookup(domain)

def http_status_check(url, timeout=5):
    """
    检查 URL 的 HTTP 状态码（类似 curl -I）。
    """
    try:
        req = Request(url, method='HEAD')
        req.add_header('User-Agent', 'Python-StatusChecker')
        with urlopen(req, timeout=timeout) as response:
            return response.status
    except HTTPError as e:
        return e.code
    except (URLError, socket.timeout) as e:
        return f"错误: {e}"


print("\n# HTTP 状态码检查 (类似 curl -I -o /dev/null -s -w '%{http_code}')")
urls = [
    "https://httpbin.org/status/200",
    "https://httpbin.org/status/404",
    "https://httpbin.org/status/500",
]
for url in urls:
    status = http_status_check(url)
    print(f"    {url} -> {status}")


# ============================================================
# 清理
# ============================================================

import shutil
print_section("清理")
shutil.rmtree(log_dir, ignore_errors=True)
print(f"  已清理临时目录: {log_dir}")


print(f"\n{'=' * 60}")
print("Demo 4 完成！")
print(f"{'=' * 60}")
print("""
核心收获:
  1. urllib.request 是 Python 标准库的 HTTP 客户端，可以替代 curl
  2. socket 模块可以检查端口连通性，替代 nc/telnet
  3. re 模块是 Python 版 grep/sed/awk，正则功能更强大
  4. Counter 和 defaultdict 是日志分析的利器
  5. Python 可以优雅地替代大部分 Shell 脚本，且跨平台、更易维护
  6. 后端开发中，日志分析、端口检查、HTTP 调试是最常用的 Linux 技能
""")
