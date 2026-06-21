"""
Demo 3: 文件读写与 pathlib
对应理论文档: 3.文件读写.md

演示文件读写的各种方式、pathlib 现代路径操作、
以及后端场景中的配置读取和日志写入。
注意：本 Demo 会在当前目录创建临时文件，运行结束后自动清理。
"""

from pathlib import Path
import sys

# 创建临时目录
TEMP_DIR = Path(__file__).parent / "temp_files"
TEMP_DIR.mkdir(exist_ok=True)

# ============================================================
# 第一部分：基本读写
# ============================================================

print("=" * 55)
print("第一部分：基本读写")
print("=" * 55)

# 写入文件
sample_file = TEMP_DIR / "sample.txt"
with open(sample_file, "w", encoding="utf-8") as f:
    f.write("第一行：你好世界\n")
    f.write("第二行：Python 后端\n")
    f.write("第三行：文件操作\n")
    f.write("第四行：pathlib\n")
    f.write("第五行：学习完毕\n")
print(f"  写入文件: {sample_file}")

# 读取方式一：read() 全部读取
print(f"\n  --- read() 全部读取 ---")
with open(sample_file, "r", encoding="utf-8") as f:
    content = f.read()
    print(f"  类型: {type(content).__name__}, 长度: {len(content)} 字符")
    print(f"  内容:\n{content}")

# 读取方式二：readlines() 返回列表
print(f"  --- readlines() 返回列表 ---")
with open(sample_file, "r", encoding="utf-8") as f:
    lines = f.readlines()
    print(f"  类型: {type(lines).__name__}, 行数: {len(lines)}")
    print(f"  第一行: {lines[0].strip()!r}")

# 读取方式三（推荐）：直接遍历
print(f"\n  --- for line in f（推荐）---")
with open(sample_file, "r", encoding="utf-8") as f:
    for i, line in enumerate(f, 1):
        print(f"  行{i}: {line.strip()}")


# ============================================================
# 第二部分：写入模式对比
# ============================================================

print("\n" + "=" * 55)
print("第二部分：写入模式对比（w vs a）")
print("=" * 55)

mode_file = TEMP_DIR / "mode_test.txt"

# "w" 模式：覆盖
with open(mode_file, "w", encoding="utf-8") as f:
    f.write("第一次写入\n")
with open(mode_file, "r", encoding="utf-8") as f:
    print(f"  w 第一次: {f.read().strip()!r}")

with open(mode_file, "w", encoding="utf-8") as f:
    f.write("第二次写入（覆盖了第一次）\n")
with open(mode_file, "r", encoding="utf-8") as f:
    print(f"  w 第二次: {f.read().strip()!r}")

# "a" 模式：追加
with open(mode_file, "a", encoding="utf-8") as f:
    f.write("追加的内容\n")
with open(mode_file, "r", encoding="utf-8") as f:
    content = f.read().strip()
    print(f"  a 追加后: {content!r}")


# ============================================================
# 第三部分：pathlib — 现代路径操作
# ============================================================

print("\n" + "=" * 55)
print("第三部分：pathlib — 现代路径操作")
print("=" * 55)

# 路径拼接
config_path = Path("project") / "config" / "settings.json"
print(f"  路径拼接: {config_path}")

# 路径信息
p = Path("/home/user/project/app/main.py")
print(f"\n  路径解析:")
print(f"    完整路径: {p}")
print(f"    文件名:   {p.name}")        # main.py
print(f"    无扩展名: {p.stem}")        # main
print(f"    扩展名:   {p.suffix}")      # .py
print(f"    父目录:   {p.parent}")      # /home/user/project/app
print(f"    所有部分: {p.parts}")

# 判断文件/目录
print(f"\n  路径判断:")
print(f"    {sample_file} 存在? {sample_file.exists()}")
print(f"    是文件? {sample_file.is_file()}")
print(f"    是目录? {sample_file.is_dir()}")
print(f"    {TEMP_DIR} 是目录? {TEMP_DIR.is_dir()}")


# ============================================================
# 第四部分：pathlib 快捷读写
# ============================================================

print("\n" + "=" * 55)
print("第四部分：pathlib 快捷读写")
print("=" * 55)

# write_text / read_text
quick_file = TEMP_DIR / "quick.txt"
quick_file.write_text("pathlib 快捷写入\n第二行", encoding="utf-8")
content = quick_file.read_text(encoding="utf-8")
print(f"  快捷写入并读取: {content!r}")

# write_bytes / read_bytes（二进制）
bin_file = TEMP_DIR / "binary.dat"
bin_file.write_bytes(b"\x00\x01\x02\x03\xff")
data = bin_file.read_bytes()
print(f"  二进制读取: {data}")
print(f"  字节数: {len(data)}")


# ============================================================
# 第五部分：遍历目录
# ============================================================

print("\n" + "=" * 55)
print("第五部分：遍历目录")
print("=" * 55)

# 创建一些测试文件
for name in ["a.py", "b.py", "c.txt", "d.json"]:
    (TEMP_DIR / name).write_text(f"# {name}", encoding="utf-8")

# glob 匹配
print(f"  TEMP_DIR 下所有文件:")
for f in sorted(TEMP_DIR.glob("*")):
    print(f"    {f.name:15s} ({f.suffix})")

print(f"\n  只找 .py 文件:")
for f in sorted(TEMP_DIR.glob("*.py")):
    print(f"    {f.name}")

# rglob 递归查找（从当前 demo 目录向上找 .md 文件）
print(f"\n  当前章节的 .md 文件:")
chapter_dir = Path(__file__).parent.parent
for f in sorted(chapter_dir.glob("*.md")):
    print(f"    {f.name}")


# ============================================================
# 第六部分：后端场景 — 配置文件读取
# ============================================================

print("\n" + "=" * 55)
print("第六部分：后端场景 — .env 配置文件")
print("=" * 55)

# 创建模拟的 .env 文件
env_file = TEMP_DIR / ".env"
env_file.write_text("""# 数据库配置
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=secret123
DB_NAME=myapp

# Redis 配置
REDIS_HOST=localhost
REDIS_PORT=6379

# 应用配置
DEBUG=true
SECRET_KEY=my-secret-key
""", encoding="utf-8")


def load_env(filepath):
    """读取 .env 文件，返回配置字典"""
    config = {}
    env_path = Path(filepath)
    if not env_path.exists():
        print(f"  ⚠️ 配置文件不存在: {filepath}")
        return config

    for line in env_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if "=" in line:
            key, value = line.split("=", 1)
            config[key.strip()] = value.strip()
    return config


config = load_env(env_file)
print(f"  读取到 {len(config)} 项配置:")
for key, value in config.items():
    display_value = "***" if "PASSWORD" in key or "SECRET" in key else value
    print(f"    {key} = {display_value}")


# ============================================================
# 第七部分：后端场景 — 简单日志写入
# ============================================================

print("\n" + "=" * 55)
print("第七部分：后端场景 — 日志写入")
print("=" * 55)

from datetime import datetime


def write_log(message, level="INFO", log_file=None):
    """写入日志"""
    if log_file is None:
        log_file = TEMP_DIR / "app.log"
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_line = f"[{timestamp}] [{level:5s}] {message}\n"
    with open(log_file, "a", encoding="utf-8") as f:
        f.write(log_line)
    print(f"  写入: {log_line.strip()}")


write_log("服务启动成功", "INFO")
write_log("用户 zhangsan 登录", "INFO")
write_log("查询超时 db=mysql", "WARN")
write_log("支付接口异常 code=500", "ERROR")

print(f"\n  日志文件内容:")
log_content = (TEMP_DIR / "app.log").read_text(encoding="utf-8")
print(log_content)


# ============================================================
# 清理临时文件
# ============================================================

print("=" * 55)
print("清理临时文件...")
print("=" * 55)

import shutil
shutil.rmtree(TEMP_DIR)
print(f"  已删除: {TEMP_DIR}")


print("\n" + "=" * 55)
print("✅ Demo 3 完成！")
print("=" * 55)
