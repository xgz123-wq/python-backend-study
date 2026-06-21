"""
Docker 基础操作演示脚本
======================

本脚本通过 Python 代码演示 Docker 的核心操作，帮助你理解：
1. Docker 是否安装及版本信息
2. 镜像操作：拉取、查看、删除
3. 容器操作：运行、查看、停止、删除
4. 容器生命周期：创建 → 运行 → 暂停 → 恢复 → 停止 → 删除
5. 数据卷操作：创建、挂载、验证持久化
6. 容器间网络通信

运行前提：需要安装 Docker Desktop。
如果未安装 Docker，脚本会给出安装指引并优雅退出。

运行方式：
    python 1_docker_basics.py
"""

import subprocess
import sys
import time


# ============================================================
# 工具函数
# ============================================================

def run_cmd(cmd: str, check: bool = True, timeout: int = 60) -> subprocess.CompletedProcess:
    """
    执行 shell 命令并返回结果。

    参数:
        cmd: 要执行的命令字符串
        check: 是否在非零退出码时抛出异常
        timeout: 命令超时时间（秒）

    返回:
        subprocess.CompletedProcess 对象
    """
    print(f"\n>>> {cmd}")
    try:
        result = subprocess.run(
            cmd,
            shell=True,
            capture_output=True,
            text=True,
            check=check,
            timeout=timeout,
        )
        # 打印标准输出（去除末尾多余换行）
        if result.stdout.strip():
            print(result.stdout.strip())
        return result
    except subprocess.CalledProcessError as e:
        print(f"[错误] 命令执行失败（退出码 {e.returncode}）")
        if e.stderr.strip():
            print(f"  错误信息: {e.stderr.strip()}")
        return e
    except subprocess.TimeoutExpired:
        print(f"[错误] 命令超时（{timeout}秒）")
        return None


def section(title: str):
    """打印章节标题分隔线。"""
    print(f"\n{'=' * 60}")
    print(f"  {title}")
    print(f"{'=' * 60}")


# ============================================================
# 第一步：检查 Docker 是否安装
# ============================================================

def check_docker_installed() -> bool:
    """
    检查 Docker 是否已安装并正在运行。

    返回:
        True 表示 Docker 可用，False 表示不可用
    """
    section("第一步：检查 Docker 环境")

    # 检查 docker 命令是否存在
    result = run_cmd("docker --version", check=False)
    if result is None or (hasattr(result, 'returncode') and result.returncode != 0):
        print("\n" + "!" * 60)
        print("  Docker 未安装或不在 PATH 中！")
        print("!" * 60)
        print("\n请按照以下步骤安装 Docker：")
        print("  Windows: https://docs.docker.com/desktop/install/windows-install/")
        print("  macOS:   https://docs.docker.com/desktop/install/mac-install/")
        print("  Linux:   sudo apt-get install docker.io")
        print("\n安装完成后，重新启动本脚本。")
        return False

    # 检查 Docker Daemon 是否正在运行
    result = run_cmd("docker info --format '{{.ServerVersion}}'", check=False)
    if result is None or (hasattr(result, 'returncode') and result.returncode != 0):
        print("\n[警告] Docker 已安装，但 Docker Daemon（守护进程）未运行。")
        print("  Windows/macOS: 请启动 Docker Desktop 应用")
        print("  Linux: sudo systemctl start docker")
        return False

    print("\n[Docker 环境检查通过]")
    return True


# ============================================================
# 第二步：镜像操作演示
# ============================================================

def demo_image_operations():
    """
    演示镜像的核心操作：
    - docker pull: 从 Registry 拉取镜像
    - docker images: 查看本地镜像列表
    - docker tag: 给镜像打新标签
    - docker rmi: 删除镜像
    """
    section("第二步：镜像操作演示")

    # 使用 alpine 镜像做演示（体积小，约 7MB，下载快）
    test_image = "alpine:3.19"

    print(f"\n--- 拉取镜像: {test_image} ---")
    print("docker pull 从 Docker Hub（Registry）下载镜像到本地。")
    print("镜像是只读模板，包含运行环境所需的一切文件。\n")
    run_cmd(f"docker pull {test_image}", timeout=120)

    print("\n--- 查看本地镜像 ---")
    print("docker images 列出本地已有的镜像。")
    print("注意 SIZE 列，alpine 镜像只有约 7MB，非常精简。\n")
    run_cmd("docker images alpine")

    print("\n--- 给镜像打标签 ---")
    print("docker tag 给镜像创建一个别名（类似硬链接，不复制数据）。\n")
    run_cmd(f"docker tag {test_image} demo-alpine:latest")
    run_cmd("docker images demo-alpine")

    print("\n--- 清理演示镜像标签 ---")
    run_cmd("docker rmi demo-alpine:latest", check=False)


# ============================================================
# 第三步：容器操作演示
# ============================================================

def demo_container_operations():
    """
    演示容器的核心操作：
    - docker run: 创建并运行容器
    - docker ps: 查看运行中的容器
    - docker logs: 查看容器日志
    - docker exec: 在容器内执行命令
    - docker stop/start: 停止和启动容器
    - docker rm: 删除容器
    """
    section("第三步：容器操作演示")

    container_name = "docker-demo-container"

    # 先清理可能存在的同名容器
    run_cmd(f"docker rm -f {container_name} 2>/dev/null || true", check=False)

    print("\n--- 运行容器 ---")
    print("docker run 的常用参数：")
    print("  -d          后台运行（不占用终端）")
    print("  --name      给容器起名字")
    print("  alpine:3.19 使用的镜像")
    print("  最后的命令   容器启动后执行的程序\n")

    # 运行一个持续输出时间的 alpine 容器
    run_cmd(
        f'docker run -d --name {container_name} alpine:3.19 '
        f'/bin/sh -c "i=0; while [ $i -lt 5 ]; do echo \\"Hello from Docker! Count: $i\\"; '
        f'i=$((i+1)); sleep 2; done; sleep 3600"'
    )

    # 等待容器产出一些日志
    print("\n等待 3 秒让容器产生日志...")
    time.sleep(3)

    print("\n--- 查看运行中的容器 ---")
    print("docker ps 显示正在运行的容器信息：")
    print("  CONTAINER ID  容器唯一标识")
    print("  IMAGE         使用的镜像")
    print("  STATUS        运行状态和时间")
    print("  NAMES         容器名称\n")
    run_cmd("docker ps")

    print("\n--- 查看容器日志 ---")
    print("docker logs 获取容器的标准输出（stdout/stderr）。\n")
    run_cmd(f"docker logs {container_name}")

    print("\n--- 在容器内执行命令 ---")
    print("docker exec 在运行中的容器内执行额外命令。\n")
    run_cmd(f"docker exec {container_name} cat /etc/os-release")

    # 清理容器
    print("\n--- 停止并删除容器 ---")
    run_cmd(f"docker stop {container_name}")
    run_cmd(f"docker rm {container_name}")


# ============================================================
# 第四步：容器生命周期演示
# ============================================================

def demo_container_lifecycle():
    """
    演示容器的完整生命周期：
    创建(create) → 运行(start) → 暂停(pause) → 恢复(unpause) → 停止(stop) → 删除(rm)

    容器状态转换图：
        created ──start──→ running ──pause──→ paused
                           │    ↑              │
                           │    └──unpause─────┘
                           │
                           └──stop──→ exited ──start──→ running
                                          │
                                          └──rm──→ (已删除)
    """
    section("第四步：容器生命周期演示")

    container_name = "docker-lifecycle-demo"
    run_cmd(f"docker rm -f {container_name} 2>/dev/null || true", check=False)

    print("\n容器有以下状态：")
    print("  created  — 已创建但未启动")
    print("  running  — 正在运行")
    print("  paused   — 已暂停（进程被冻结）")
    print("  exited   — 已停止\n")

    # 1. 创建容器（不启动）
    print("--- 1. 创建容器（docker create）---")
    print("create 只创建容器但不启动，类似 '组装好电脑但不开机'。\n")
    run_cmd(f"docker create --name {container_name} alpine:3.19 /bin/sh -c 'while true; do echo running; sleep 1; done'")
    run_cmd(f"docker ps -a --filter name={container_name} --format 'table {{{{.Names}}}}\\t{{{{.Status}}}}'")

    # 2. 启动容器
    print("\n--- 2. 启动容器（docker start）---")
    run_cmd(f"docker start {container_name}")
    time.sleep(2)
    run_cmd(f"docker ps --filter name={container_name} --format 'table {{{{.Names}}}}\\t{{{{.Status}}}}'")

    # 3. 暂停容器
    print("\n--- 3. 暂停容器（docker pause）---")
    print("pause 冻结容器内的所有进程，类似 '按下暂停键'。\n")
    run_cmd(f"docker pause {container_name}")
    run_cmd(f"docker ps --filter name={container_name} --format 'table {{{{.Names}}}}\\t{{{{.Status}}}}'")

    # 4. 恢复容器
    print("\n--- 4. 恢复容器（docker unpause）---")
    run_cmd(f"docker unpause {container_name}")
    run_cmd(f"docker ps --filter name={container_name} --format 'table {{{{.Names}}}}\\t{{{{.Status}}}}'")

    # 5. 停止容器
    print("\n--- 5. 停止容器（docker stop）---")
    print("stop 发送 SIGTERM 信号，优雅关闭。10 秒后强制 SIGKILL。\n")
    run_cmd(f"docker stop {container_name}")
    run_cmd(f"docker ps -a --filter name={container_name} --format 'table {{{{.Names}}}}\\t{{{{.Status}}}}'")

    # 6. 删除容器
    print("\n--- 6. 删除容器（docker rm）---")
    run_cmd(f"docker rm {container_name}")
    print("\n容器生命周期演示完毕！")


# ============================================================
# 第五步：数据卷演示
# ============================================================

def demo_volumes():
    """
    演示 Docker 数据卷的核心概念：
    - 创建命名卷
    - 挂载到容器
    - 写入数据
    - 删除容器后数据仍然存在
    - 新容器挂载同一个卷可以读到之前的数据

    这证明了数据卷的持久化能力：容器可以被删除和重建，
    但数据卷中的数据不会丢失。
    """
    section("第五步：数据卷（Volume）演示")

    volume_name = "docker-demo-volume"
    container1 = "volume-writer"
    container2 = "volume-reader"

    # 清理旧资源
    run_cmd(f"docker rm -f {container1} {container2} 2>/dev/null || true", check=False)
    run_cmd(f"docker volume rm {volume_name} 2>/dev/null || true", check=False)

    print("\n--- 1. 创建数据卷 ---")
    print("数据卷由 Docker 管理，存储在宿主机特定目录下。\n")
    run_cmd(f"docker volume create {volume_name}")
    run_cmd(f"docker volume inspect {volume_name}")

    print("\n--- 2. 写入数据到卷 ---")
    print("启动容器 1，将数据写入挂载的卷目录。\n")
    run_cmd(
        f"docker run --name {container1} "
        f"-v {volume_name}:/data "
        f"alpine:3.19 /bin/sh -c "
        f"\"echo 'Hello from volume! Written at '$(date) > /data/message.txt && "
        f"echo 'Data written successfully'\""
    )

    print("\n--- 3. 删除写入容器 ---")
    print("容器被删除后，卷中的数据应该仍然存在。\n")
    run_cmd(f"docker rm {container1}")

    print("\n--- 4. 用新容器读取卷中的数据 ---")
    print("启动容器 2，挂载同一个卷，读取之前写入的文件。\n")
    run_cmd(
        f"docker run --name {container2} "
        f"-v {volume_name}:/data "
        f"alpine:3.19 cat /data/message.txt"
    )

    # 清理
    print("\n--- 5. 清理演示资源 ---")
    run_cmd(f"docker rm {container2}")
    run_cmd(f"docker volume rm {volume_name}")

    print("\n数据卷演示完毕！")
    print("结论：即使容器被删除，数据卷中的数据仍然持久保存。")
    print("这就是为什么数据库等需要持久化存储的服务必须使用数据卷。")


# ============================================================
# 主流程
# ============================================================

def main():
    """
    主函数：按顺序执行所有演示。

    流程：
    1. 检查 Docker 环境
    2. 镜像操作演示
    3. 容器操作演示
    4. 容器生命周期演示
    5. 数据卷演示
    """
    print("=" * 60)
    print("  Docker 基础操作演示")
    print("  本脚本将演示 Docker 的核心概念和常用命令")
    print("=" * 60)

    # 检查 Docker 是否可用
    if not check_docker_installed():
        sys.exit(1)

    # 依次执行各个演示
    demo_image_operations()
    demo_container_operations()
    demo_container_lifecycle()
    demo_volumes()

    # 总结
    section("演示完毕")
    print("""
本章演示了以下 Docker 核心概念：

1. 镜像（Image）
   - 只读模板，包含运行应用所需的一切
   - docker pull / images / tag / rmi

2. 容器（Container）
   - 镜像的运行实例
   - docker run / ps / stop / start / rm / exec / logs

3. 容器生命周期
   - created → running → paused → exited → deleted
   - docker create / start / pause / unpause / stop / rm

4. 数据卷（Volume）
   - 持久化存储，容器删除后数据不丢失
   - docker volume create / inspect / rm

建议：
- 多练习 docker run 和 docker exec 命令
- 理解 -d（后台）、-p（端口映射）、-v（数据卷）等关键参数
- 尝试用 docker logs -f 实时查看容器日志
""")


if __name__ == "__main__":
    main()
