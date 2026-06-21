"""
TCP/IP 协议演示
对应理论：1.TCP-IP协议.md

演示内容：
1. TCP 三次握手过程的 socket 模拟
2. TCP vs UDP 传输对比
3. TCP 连接状态查看
"""

import socket
import threading
import time


# ============================================================
# 1. TCP 通信演示（体验"面向连接"的可靠传输）
# ============================================================
print("=" * 60)
print("1. TCP 通信演示")
print("=" * 60)

# TCP 服务端：在后台线程运行
def tcp_server():
    # AF_INET = IPv4, SOCK_STREAM = TCP
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind(("127.0.0.1", 9001))
    server.listen(1)  # 最多等待 1 个连接
    print("[TCP 服务端] 等待连接...")

    conn, addr = server.accept()  # 阻塞，等三次握手完成
    print(f"[TCP 服务端] 客户端已连接: {addr}")

    # 接收数据
    data = conn.recv(1024)
    print(f"[TCP 服务端] 收到: {data.decode()}")

    # 发送响应
    conn.send("TCP 服务端收到你的消息了！".encode())

    conn.close()
    server.close()

# TCP 客户端
def tcp_client():
    time.sleep(0.3)  # 等服务端启动
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # connect() 内部完成三次握手
    print("[TCP 客户端] 正在连接（三次握手）...")
    client.connect(("127.0.0.1", 9001))
    print("[TCP 客户端] 连接成功！")

    # 发送数据（TCP 保证对方一定收到）
    client.send("Hello TCP!".encode())
    print("[TCP 客户端] 已发送: Hello TCP!")

    # 接收响应
    response = client.recv(1024)
    print(f"[TCP 客户端] 收到响应: {response.decode()}")

    # close() 内部完成四次挥手
    client.close()
    print("[TCP 客户端] 连接关闭（四次挥手）")

# 启动 TCP 通信
server_thread = threading.Thread(target=tcp_server)
client_thread = threading.Thread(target=tcp_client)
server_thread.start()
client_thread.start()
server_thread.join()
client_thread.join()


# ============================================================
# 2. UDP 通信演示（体验"无连接"的快速传输）
# ============================================================
print("\n" + "=" * 60)
print("2. UDP 通信演示")
print("=" * 60)

def udp_server():
    # SOCK_DGRAM = UDP
    server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server.bind(("127.0.0.1", 9002))
    print("[UDP 服务端] 等待数据...（不需要建立连接）")

    data, addr = server.recvfrom(1024)
    print(f"[UDP 服务端] 收到来自 {addr} 的数据: {data.decode()}")

    # UDP 直接回复到来源地址
    server.sendto("UDP 服务端收到了！".encode(), addr)

    server.close()

def udp_client():
    time.sleep(0.3)
    client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    # 直接发送，不需要 connect()（无三次握手）
    print("[UDP 客户端] 直接发送数据（无需握手）...")
    client.sendto("Hello UDP!".encode(), ("127.0.0.1", 9002))
    print("[UDP 客户端] 已发送: Hello UDP!")

    response, _ = client.recvfrom(1024)
    print(f"[UDP 客户端] 收到响应: {response.decode()}")

    client.close()

server_thread = threading.Thread(target=udp_server)
client_thread = threading.Thread(target=udp_client)
server_thread.start()
client_thread.start()
server_thread.join()
client_thread.join()


# ============================================================
# 3. TCP vs UDP 对比总结
# ============================================================
print("\n" + "=" * 60)
print("3. TCP vs UDP 对比总结")
print("=" * 60)

comparison = {
    "连接方式": ("面向连接（三次握手）", "无连接（直接发送）"),
    "可靠性":   ("可靠（ACK 确认 + 重传）", "不可靠（发了不管）"),
    "有序性":   ("保证顺序（序列号）", "不保证顺序"),
    "速度":     ("较慢（有确认开销）", "更快（无额外开销）"),
    "典型场景": ("HTTP/数据库/文件传输", "DNS/视频直播/游戏"),
    "Socket 类型": ("SOCK_STREAM", "SOCK_DGRAM"),
}

print(f"{'特性':<12} {'TCP':<28} {'UDP':<28}")
print("-" * 68)
for feature, (tcp, udp) in comparison.items():
    print(f"{feature:<12} {tcp:<28} {udp:<28}")


# ============================================================
# 4. 查看 socket 信息（理解连接五元组）
# ============================================================
print("\n" + "=" * 60)
print("4. TCP 连接五元组演示")
print("=" * 60)

def show_socket_info():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind(("127.0.0.1", 9003))
    server.listen(1)

    def client_connect():
        time.sleep(0.2)
        c = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        c.connect(("127.0.0.1", 9003))
        return c

    client_thread_inner = threading.Thread(target=client_connect)
    client_thread_inner.start()

    conn, addr = server.accept()

    # TCP 连接由五元组唯一标识
    print("TCP 连接五元组（唯一标识一个连接）：")
    print(f"  协议:       TCP")
    print(f"  源 IP:      {addr[0]}")
    print(f"  源端口:     {addr[1]}  ← 操作系统随机分配的临时端口")
    print(f"  目标 IP:    {conn.getsockname()[0]}")
    print(f"  目标端口:   {conn.getsockname()[1]}  ← 我们指定的监听端口")
    print()
    print("理解：同一台机器可以同时建立多个 TCP 连接，")
    print("      因为每个连接的「源端口」不同，五元组就不同。")

    conn.close()
    server.close()
    client_thread_inner.join()

show_socket_info()

print("\n" + "=" * 60)
print("演示结束！")
print("=" * 60)
print("""
核心要点回顾：
1. TCP 通信前必须三次握手建立连接，结束时四次挥手断开
2. UDP 无需建立连接，直接发送数据包
3. TCP 保证可靠有序，UDP 追求速度
4. TCP 连接由五元组唯一标识（协议+源IP+源端口+目标IP+目标端口）
5. 后端开发 99% 的场景使用 TCP（HTTP、数据库、Redis 等）
""")
