"""
Demo 1: os 与 sys
对应理论文档: 1.os与sys.md

演示环境变量、命令行参数、工作目录、路径处理，
以及后端启动脚本中的基础检查逻辑。
"""

import os
import sys


print("=" * 55)
print("第一部分：环境变量")
print("=" * 55)

db_host = os.getenv("DB_HOST", "localhost")
api_mode = os.getenv("API_MODE", "dev")

print(f"DB_HOST = {db_host}")
print(f"API_MODE = {api_mode}")


print("\n" + "=" * 55)
print("第二部分：当前工作目录与目录内容")
print("=" * 55)

current_dir = os.getcwd()
print(f"当前工作目录: {current_dir}")

entries = os.listdir(".")
print("当前目录前 10 个条目:")
for name in entries[:10]:
    print(f"  - {name}")


print("\n" + "=" * 55)
print("第三部分：路径处理")
print("=" * 55)

log_dir = os.path.join("logs")
log_file = os.path.join(log_dir, "app.log")

print(f"log_dir = {log_dir}")
print(f"log_file = {log_file}")
print(f"log_file 绝对路径 = {os.path.abspath(log_file)}")
print(f"logs 是否存在 = {os.path.exists(log_dir)}")


print("\n" + "=" * 55)
print("第四部分：命令行参数")
print("=" * 55)

print(f"sys.argv = {sys.argv}")
mode = sys.argv[1] if len(sys.argv) > 1 else "dev"
print(f"运行模式 = {mode}")


print("\n" + "=" * 55)
print("第五部分：后端启动场景模拟")
print("=" * 55)


def boot_app():
    """模拟一个非常简化的后端启动流程。"""
    env = os.getenv("APP_ENV", mode)
    port = os.getenv("API_PORT", "8000")

    if env not in {"dev", "test", "prod"}:
        print(f"非法运行环境: {env}")
        sys.exit(1)

    print(f"应用启动中: env={env}, port={port}")


boot_app()


print("\n" + "=" * 55)
print("Demo 1 完成!")
print("=" * 55)
