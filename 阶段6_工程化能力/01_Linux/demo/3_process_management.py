"""
Demo 3: 进程管理 - 用 Python 管理进程
对应理论文档: 3.进程管理.md

本 Demo 演示 Python 中的进程管理：
- 用 subprocess 启动和管理子进程
- 获取当前进程 PID 和父进程 PPID
- 列出系统进程（跨平台方式）
- 模拟 nohup 后台运行
- 进程信号概念（SIGTERM、SIGKILL）
- 僵尸进程和孤儿进程的概念演示

注意: 部分功能（如信号、进程列表）在 Windows 和 Linux 上行为不同，
      Demo 会分别演示。
"""

import os
import sys
import time
import signal
import subprocess
import platform
import tempfile

# ============================================================
# 工具函数
# ============================================================

def print_section(title):
    """打印分隔线和标题"""
    print(f"\n{'=' * 60}")
    print(f"  {title}")
    print(f"{'=' * 60}")


def run_command(cmd, description=""):
    """执行 Shell 命令并打印结果"""
    if description:
        print(f"\n# {description}")
    print(f"$ {cmd}")
    try:
        result = subprocess.run(
            cmd, shell=True, capture_output=True,
            text=True, encoding='utf-8', errors='replace'
        )
        if result.stdout.strip():
            print(result.stdout.strip())
        if result.stderr.strip():
            print(f"[stderr] {result.stderr.strip()}")
        return result
    except Exception as e:
        print(f"[错误] {e}")
        return None


IS_LINUX = platform.system() == "Linux"
IS_WINDOWS = platform.system() == "Windows"


# ============================================================
# 第一部分：进程基础概念
# ============================================================

print_section("第一部分：进程基础概念")

# 当前进程的 PID（Process ID）
current_pid = os.getpid()
print(f"  当前进程 PID:     {current_pid}")

# 父进程的 PPID（Parent Process ID）
if IS_LINUX:
    parent_pid = os.getppid()
    print(f"  父进程 PPID:      {parent_pid}")
else:
    print(f"  父进程 PPID:      (Windows 不提供 os.getppid())")

# CPU 数量
cpu_count = os.cpu_count()
print(f"  CPU 核心数:       {cpu_count}")

print(f"""
  进程生命周期:
    创建 (fork/exec) → 就绪 → 运行 → 阻塞 (等待 I/O) → 终止

  进程状态 (Linux ps 命令中的 STAT 列):
    R - Running     运行中或等待运行
    S - Sleeping    休眠中，等待事件
    D - Disk sleep  不可中断的 I/O 等待 (kill -9 也杀不掉)
    Z - Zombie      僵尸进程 (已终止但父进程未回收)
    T - Stopped     已停止 (收到 SIGSTOP 或 Ctrl+Z)
""")


# ============================================================
# 第二部分：用 subprocess 启动子进程
# ============================================================

print_section("第二部分：用 subprocess 启动子进程")

# --- 方式 1: subprocess.run（等待完成） ---
print("\n# 方式 1: subprocess.run - 启动进程并等待完成")
print("# 等价于在终端执行命令，命令完成后才继续")

result = subprocess.run(
    [sys.executable, '-c', 'import os; print(f"子进程 PID: {os.getpid()}")'],
    capture_output=True, text=True, encoding='utf-8'
)
print(f"  {result.stdout.strip()}")
print(f"  子进程退出码: {result.returncode}")
print(f"  当前进程 PID: {os.getpid()}")

# --- 方式 2: subprocess.Popen（不等待，异步） ---
print("\n# 方式 2: subprocess.Popen - 启动进程但不阻塞")
print("# 类似于在命令末尾加 & 放到后台")

# 启动一个后台子进程：每秒打印一次计数，共 3 次
proc = subprocess.Popen(
    [sys.executable, '-c', '''
import time, os
print(f"后台进程 PID: {os.getpid()}")
for i in range(3):
    print(f"  后台任务进度: {i+1}/3")
    time.sleep(0.5)
print("后台任务完成!")
'''],
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
    text=True,
    encoding='utf-8'
)

print(f"  子进程已启动，PID: {proc.pid}")
print(f"  子进程是否结束? {proc.poll()}")  # None 表示还在运行

# 等待子进程完成
stdout, stderr = proc.communicate(timeout=10)
print(f"  子进程输出:")
for line in stdout.strip().split('\n'):
    print(f"    {line}")
print(f"  子进程退出码: {proc.returncode}")

# --- 方式 3: 启动多个子进程并行执行 ---
print("\n# 方式 3: 同时启动多个子进程（并行）")

processes = []
for i in range(3):
    p = subprocess.Popen(
        [sys.executable, '-c', f'''
import time, os
time.sleep({0.3 * (i + 1)})
print(f"任务 {i+1} 完成 (PID: {{os.getpid()}})")
'''],
        stdout=subprocess.PIPE, text=True, encoding='utf-8'
    )
    processes.append(p)
    print(f"  启动任务 {i+1}, PID: {p.pid}")

# 等待所有子进程完成
for i, p in enumerate(processes):
    stdout, _ = p.communicate(timeout=10)
    print(f"  {stdout.strip()}")


# ============================================================
# 第三部分：列出系统进程
# ============================================================

print_section("第三部分：列出系统进程")

if IS_LINUX:
    # Linux: 使用 ps 命令
    run_command("ps aux --sort=-%cpu | head -15", "CPU 使用最多的 15 个进程")
    run_command(f"ps aux | grep python | grep -v grep", "查找 Python 进程")
else:
    # Windows: 使用 tasklist 或 wmic
    print("\n# Windows 上使用 tasklist 查看进程")
    run_command("tasklist /FI \"IMAGENAME eq python.exe\" /FO CSV", "查找 Python 进程")

    print("\n# 使用 Python 列出当前用户的所有 Python 进程")
    try:
        result = subprocess.run(
            ['tasklist', '/FI', 'IMAGENAME eq python.exe', '/FO', 'CSV'],
            capture_output=True, text=True, encoding='utf-8', errors='replace'
        )
        if result.returncode == 0:
            lines = result.stdout.strip().split('\n')
            print(f"  {'进程名':<20}{'PID':<10}{'会话':<10}{'内存使用'}")
            print(f"  {'-'*60}")
            for line in lines[1:]:  # 跳过标题
                parts = line.strip().strip('"').split('","')
                if len(parts) >= 5:
                    print(f"  {parts[0]:<20}{parts[1]:<10}{parts[2]:<10}{parts[4]}")
    except Exception as e:
        print(f"  无法列出进程: {e}")


# ============================================================
# 第四部分：进程信号
# ============================================================

print_section("第四部分：进程信号")

print("""
  Linux 进程信号（Signal）是进程间通信的一种机制:

  | 信号       | 编号 | 含义                     | 可捕获? |
  |------------|------|-------------------------|---------|
  | SIGHUP     | 1    | 终端断开 / 重新加载配置    | 是      |
  | SIGINT     | 2    | 中断 (Ctrl+C)             | 是      |
  | SIGTERM    | 15   | 请求终止（优雅退出）       | 是      |
  | SIGKILL    | 9    | 强制终止（不可捕获/忽略）  | 否      |
  | SIGSTOP    | 19   | 暂停进程                  | 否      |
  | SIGCONT    | 18   | 继续被暂停的进程          | 是      |
""")

# 演示信号处理（跨平台兼容部分）
print("# 演示: 注册信号处理器")

if IS_LINUX:
    # 在 Linux 上可以处理 SIGTERM
    def handle_sigterm(signum, frame):
        print(f"  收到 SIGTERM (信号 {signum})，正在清理...")
        # 这里可以做清理工作：关闭文件、保存状态等

    # 注册信号处理器
    original_handler = signal.signal(signal.SIGTERM, handle_sigterm)
    print(f"  已注册 SIGTERM 处理器")

    # 向自己发送 SIGTERM
    os.kill(os.getpid(), signal.SIGTERM)
    # 处理器会被调用

    # 恢复原始处理器
    signal.signal(signal.SIGTERM, original_handler)
    print(f"  已恢复原始 SIGTERM 处理器")
else:
    # Windows 上信号支持有限
    print("  [Windows] 支持的信号:")
    print(f"    signal.SIGINT  = {signal.SIGINT}  (Ctrl+C)")
    print(f"    signal.SIGTERM = {signal.SIGTERM} (终止)")
    print(f"    signal.SIGBREAK = {getattr(signal, 'SIGBREAK', 'N/A')} (Ctrl+Break)")
    print("  注意: Windows 不支持 SIGKILL、SIGSTOP 等 Unix 信号")

# 演示优雅退出的模式
print("\n# 优雅退出模式（后端服务常用）")
print("""
  import signal
  import sys

  running = True

  def shutdown_handler(signum, frame):
      global running
      print("收到终止信号，正在优雅退出...")
      running = False
      # 关闭数据库连接
      # 保存当前状态
      # 关闭文件句柄

  signal.signal(signal.SIGTERM, shutdown_handler)
  signal.signal(signal.SIGINT, shutdown_handler)

  while running:
      # 主循环
      do_work()

  print("服务已安全退出")
""")


# ============================================================
# 第五部分：模拟 nohup 后台运行
# ============================================================

print_section("第五部分：模拟 nohup 后台运行")

if IS_LINUX:
    print("""
  nohup (No Hang Up) 的作用:
    - 让进程在终端关闭后继续运行
    - 忽略 SIGHUP 信号（终端挂断信号）
    - 默认输出重定向到 nohup.out

  典型用法:
    nohup python app.py > app.log 2>&1 &

  各部分含义:
    nohup          忽略 SIGHUP 信号
    > app.log      stdout 重定向到文件
    2>&1           stderr 也重定向到同一文件
    &              放到后台运行
""")

    # 演示: 用 Python 模拟 nohup 行为
    log_file = os.path.join(tempfile.gettempdir(), "nohup_demo.log")

    print(f"# 用 subprocess.Popen 模拟 nohup 后台运行")
    print(f"# 日志文件: {log_file}")

    with open(log_file, 'w', encoding='utf-8') as f:
        bg_proc = subprocess.Popen(
            [sys.executable, '-c', '''
import time, os
for i in range(3):
    print(f"[PID {os.getpid()}] 后台任务运行中... ({i+1}/3)")
    time.sleep(0.5)
print(f"[PID {os.getpid()}] 后台任务完成!")
'''],
            stdout=f,
            stderr=subprocess.STDOUT,  # stderr 合并到 stdout
            # 在 Linux 上可以设置 start_new_session=True
            # 使子进程脱离当前终端（类似 nohup 的效果）
            start_new_session=True
        )

    print(f"  后台进程 PID: {bg_proc.pid}")
    print(f"  进程已脱离当前终端 (start_new_session=True)")

    # 等待完成并读取日志
    bg_proc.wait(timeout=10)
    with open(log_file, 'r', encoding='utf-8') as f:
        print(f"\n  日志内容:")
        for line in f:
            print(f"    {line.strip()}")

    # 清理日志文件
    os.remove(log_file)
else:
    print("""
  [Windows] nohup 的等效方案:

  1. 使用 start 命令（后台运行）:
     start /B python app.py > app.log 2>&1

  2. 使用 Python 的 subprocess:
     subprocess.Popen(
         ['python', 'app.py'],
         stdout=open('app.log', 'w'),
         stderr=subprocess.STDOUT,
         creationflags=subprocess.CREATE_NEW_PROCESS_GROUP
     )

  3. 使用 Windows 服务（正式部署）:
     - NSSM (Non-Sucking Service Manager)
     - pywin32 的 win32service

  4. 推荐：使用任务计划程序（Task Scheduler）
""")

    # Windows 上也演示后台进程
    log_file = os.path.join(tempfile.gettempdir(), "bg_demo.log")

    print(f"# 用 subprocess.Popen 启动后台进程")
    print(f"# 日志文件: {log_file}")

    with open(log_file, 'w', encoding='utf-8') as f:
        bg_proc = subprocess.Popen(
            [sys.executable, '-c', '''
import time, os
for i in range(3):
    print(f"[PID {os.getpid()}] 后台任务运行中... ({i+1}/3)")
    time.sleep(0.5)
print("后台任务完成!")
'''],
            stdout=f,
            stderr=subprocess.STDOUT,
        )

    print(f"  后台进程 PID: {bg_proc.pid}")
    bg_proc.wait(timeout=10)

    with open(log_file, 'r', encoding='utf-8') as f:
        print(f"\n  日志内容:")
        for line in f:
            print(f"    {line.strip()}")

    os.remove(log_file)


# ============================================================
# 第六部分：僵尸进程和孤儿进程概念
# ============================================================

print_section("第六部分：僵尸进程与孤儿进程")

print("""
  僵尸进程 (Zombie):
    - 子进程已终止，但父进程没有调用 wait() 回收其退出状态
    - 进程表中仍保留一条记录（状态 Z）
    - 不占 CPU 和内存，但浪费 PID 槽位
    - kill -9 无法杀死僵尸进程（因为已经"死"了）
    - 解决：杀死父进程，僵尸进程会被 init (PID 1) 收养并清理

  孤儿进程 (Orphan):
    - 父进程先终止，子进程还在运行
    - 孤儿进程会被 init (PID 1) 收养
    - 通常无害，systemd 会自动管理
""")

# 演示: 正确使用 wait 回收子进程
print("# 演示: 正确回收子进程（避免僵尸进程）")

# 启动子进程
child = subprocess.Popen(
    [sys.executable, '-c', 'import os; print(f"子进程 PID: {os.getpid()}"); import time; time.sleep(0.5)'],
    stdout=subprocess.PIPE, text=True, encoding='utf-8'
)

print(f"  子进程 PID: {child.pid}")

# 检查子进程是否还在运行
while child.poll() is None:
    print(f"  子进程 {child.pid} 仍在运行...")
    time.sleep(0.2)

# communicate() 内部会调用 wait()，正确回收子进程
stdout, _ = child.communicate()
print(f"  {stdout.strip()}")
print(f"  子进程已退出，退出码: {child.returncode}")
print(f"  子进程已被正确回收（不会产生僵尸进程）")


# ============================================================
# 第七部分：systemd 服务配置示例
# ============================================================

print_section("第七部分：systemd 服务配置")

print("""
  systemd 是现代 Linux 的服务管理器，后端应用通常通过 systemd 管理。

  创建服务文件: /etc/systemd/system/myapp.service

  [Unit]
  Description=My Python Web App
  After=network.target             # 在网络就绪后启动

  [Service]
  Type=simple
  User=www-data                    # 运行用户（不要用 root）
  WorkingDirectory=/home/alice/myapp
  ExecStart=/home/alice/myapp/venv/bin/python app.py
  Restart=always                   # 崩溃后自动重启
  RestartSec=5                     # 重启间隔 5 秒
  Environment=FLASK_ENV=production

  [Install]
  WantedBy=multi-user.target       # 开机自启的目标

  常用命令:
    sudo systemctl daemon-reload     # 重新加载配置
    sudo systemctl enable myapp     # 设置开机自启
    sudo systemctl start myapp      # 启动
    sudo systemctl restart myapp    # 重启
    sudo systemctl status myapp     # 查看状态
    sudo journalctl -u myapp -f     # 查看日志
""")

if IS_LINUX:
    # 查看一个真实服务的状态
    run_command("systemctl status ssh 2>/dev/null || systemctl status sshd 2>/dev/null",
                "查看 SSH 服务状态")
else:
    print("  [Windows] 服务管理的等效命令:")
    print("  sc query                          # 列出所有服务")
    print("  sc start MyService                # 启动服务")
    print("  sc stop MyService                 # 停止服务")
    print("  net start MyService               # 启动服务（另一种方式）")


# ============================================================
# 清理和总结
# ============================================================

print(f"\n{'=' * 60}")
print("Demo 3 完成！")
print(f"{'=' * 60}")
print("""
核心收获:
  1. os.getpid() 获取当前进程 PID，os.getppid() 获取父进程 PID
  2. subprocess.run() 阻塞等待，subprocess.Popen() 异步启动
  3. 进程信号: SIGTERM(15) 优雅退出，SIGKILL(9) 强制杀死
  4. nohup 让进程在终端关闭后继续运行，生产环境推荐用 systemd
  5. 僵尸进程: 子进程已终止但父进程未 wait()，解决: 杀死父进程
  6. 后端服务应该注册信号处理器，实现优雅退出（保存状态、关闭连接）
""")
