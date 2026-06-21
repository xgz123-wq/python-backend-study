"""
Demo 2: 用户请求的完整链路
==========================

对应理论：2.用户请求的完整链路

本脚本演示用户请求从发出到收到响应的完整过程：
1. DNS 解析模拟（用 socket 查询域名 IP）
2. 模拟 HTTP 请求经过的各个环节
3. 测量各环节耗时（DNS、连接、传输）
4. 展示 CDN vs 直连的速度差异

运行方式：
    python 2_request_chain.py
"""

import socket
import time
import urllib.request
import urllib.error


# ============================================================
# 第 1 部分：DNS 解析演示
# ============================================================

def demo_dns_resolution():
    """演示 DNS 解析过程。

    DNS（Domain Name System）将人类可读的域名翻译为机器可读的 IP 地址。
    这就像查电话簿：你知道对方的名字（域名），需要找到电话号码（IP）。
    """
    print("\n" + "=" * 60)
    print("  第 1 部分：DNS 解析演示")
    print("=" * 60)

    # 要查询的域名列表
    domains = [
        "www.baidu.com",
        "www.google.com",
        "github.com",
        "api.github.com",
        "cdn.jsdelivr.net",
    ]

    print("\n  使用 socket.gethostbyname() 进行 DNS 查询：")
    print(f"  {'域名':<25} {'解析到的 IP':<20} {'耗时':<10}")
    print(f"  {'----':<25} {'--------':<20} {'----':<10}")

    for domain in domains:
        try:
            # 测量 DNS 查询耗时
            start = time.perf_counter()
            ip = socket.gethostbyname(domain)
            elapsed = (time.perf_counter() - start) * 1000  # 转为毫秒

            print(f"  {domain:<25} {ip:<20} {elapsed:.2f} ms")
        except socket.gaierror:
            print(f"  {domain:<25} {'解析失败':<20} {'N/A':<10}")

    # 展示 getaddrinfo 的详细信息
    print("\n\n  使用 socket.getaddrinfo() 获取详细信息（以 baidu.com 为例）：")
    try:
        results = socket.getaddrinfo("www.baidu.com", 443, socket.AF_INET)
        # 去重
        seen = set()
        for family, socktype, proto, canonname, sockaddr in results:
            ip_port = f"{sockaddr[0]}:{sockaddr[1]}"
            if ip_port not in seen:
                seen.add(ip_port)
                family_name = "IPv4" if family == socket.AF_INET else "IPv6"
                type_name = "TCP" if socktype == socket.SOCK_STREAM else "UDP"
                print(f"  地址族: {family_name}, 协议: {type_name}, 地址: {ip_port}")
    except socket.gaierror as e:
        print(f"  查询失败: {e}")

    print("\n  💡 关键理解：")
    print("  • DNS 解析通常在 1-50ms 之间")
    print("  • 同一个域名可能解析到多个 IP（负载均衡）")
    print("  • 操作系统会缓存 DNS 结果，后续查询更快")
    print("  • CDN 域名会根据你的位置返回最近的节点 IP")


# ============================================================
# 第 2 部分：HTTP 请求各环节耗时测量
# ============================================================

def demo_request_timing():
    """测量 HTTP 请求各个环节的耗时。

    一次完整的 HTTP 请求包括：
    1. DNS 解析：域名 → IP
    2. TCP 连接：三次握手
    3. TLS 握手（HTTPS）：协商加密参数
    4. 发送请求 + 等待响应（TTFB）
    5. 下载响应体
    """
    print("\n" + "=" * 60)
    print("  第 2 部分：HTTP 请求各环节耗时")
    print("=" * 60)

    url = "https://httpbin.org/get"
    print(f"\n  目标 URL: {url}")
    print(f"\n  测量各个环节（使用 urllib）：\n")

    # 整体请求耗时
    try:
        start_total = time.perf_counter()

        # DNS 解析耗时（单独测量）
        hostname = "httpbin.org"
        start_dns = time.perf_counter()
        ip = socket.gethostbyname(hostname)
        dns_time = (time.perf_counter() - start_dns) * 1000

        # 发送完整请求
        start_request = time.perf_counter()
        req = urllib.request.Request(url, headers={"User-Agent": "Python-Demo"})
        response = urllib.request.urlopen(req, timeout=10)
        request_time = (time.perf_counter() - start_request) * 1000

        # 读取响应体
        start_read = time.perf_counter()
        data = response.read()
        read_time = (time.perf_counter() - start_read) * 1000

        total_time = (time.perf_counter() - start_total) * 1000

        # 展示结果
        timing_results = [
            ("DNS 解析", dns_time, f"域名 {hostname} → {ip}"),
            ("TCP+TLS+请求+等待", request_time - read_time, "连接建立 + 等待首字节（TTFB）"),
            ("下载响应体", read_time, f"接收 {len(data)} bytes"),
            ("总耗时", total_time, "从开始到结束"),
        ]

        print(f"  {'环节':<20} {'耗时':<12} {'说明':<30}")
        print(f"  {'----':<20} {'----':<12} {'----':<30}")
        for name, ms, desc in timing_results:
            print(f"  {name:<20} {ms:>8.2f} ms   {desc}")

        print(f"\n  响应状态码: {response.status}")
        print(f"  响应头数量: {len(response.headers)}")

    except (urllib.error.URLError, socket.timeout) as e:
        print(f"  ❌ 请求失败: {e}")
        print(f"  提示：可能需要检查网络连接")

    print("\n  💡 关键理解：")
    print("  • TTFB（Time To First Byte）是衡量后端性能的核心指标")
    print("  • DNS 解析通常很快（有缓存），但首次查询可能较慢")
    print("  • HTTPS 比 HTTP 多了 TLS 握手开销")
    print("  • 服务器距离越远，TCP 连接和 TTFB 越高")


# ============================================================
# 第 3 部分：CDN vs 直连速度对比
# ============================================================

def demo_cdn_vs_direct():
    """比较通过 CDN 访问和直连源站的速度差异。

    CDN（Content Delivery Network）在全球部署缓存节点，
    用户访问最近的 CDN 节点比直连远端源站快得多。

    这里通过访问同一个资源的不同 URL 来模拟对比。
    """
    print("\n" + "=" * 60)
    print("  第 3 部分：CDN vs 直连速度对比")
    print("=" * 60)

    # 对比测试：使用不同地区的服务器
    test_urls = [
        ("国内 CDN（百度）", "https://www.baidu.com"),
        ("国内直连（httpbin 中国镜像）", "https://httpbin.org/get"),
        ("海外 CDN（GitHub CDN）", "https://cdn.jsdelivr.net/npm/vue@3/dist/vue.global.js"),
        ("海外直连（GitHub API）", "https://api.github.com"),
    ]

    print(f"\n  {'测试目标':<30} {'DNS (ms)':<10} {'总耗时 (ms)':<12} {'状态':<8}")
    print(f"  {'--------':<30} {'--------':<10} {'----------':<12} {'----':<8}")

    for name, url in test_urls:
        try:
            # 提取域名
            hostname = url.split("//")[1].split("/")[0]

            # DNS 查询耗时
            start = time.perf_counter()
            ip = socket.gethostbyname(hostname)
            dns_ms = (time.perf_counter() - start) * 1000

            # 完整请求耗时
            start = time.perf_counter()
            req = urllib.request.Request(url, headers={"User-Agent": "Python-Demo"})
            response = urllib.request.urlopen(req, timeout=10)
            _ = response.read()
            total_ms = (time.perf_counter() - start) * 1000

            print(f"  {name:<30} {dns_ms:>7.2f}   {total_ms:>9.2f}     {response.status}")

        except Exception as e:
            print(f"  {name:<30} {'N/A':>10} {'失败':>12}   ❌")

    print("\n  💡 关键理解：")
    print("  • CDN 节点通常离用户更近，DNS 解析和网络延迟更低")
    print("  • 静态资源（JS/CSS/图片）最适合使用 CDN")
    print("  • API 请求通常不走 CDN（因为内容是动态的）")
    print("  • 选择服务器地区时，优先考虑用户所在地区")


# ============================================================
# 第 4 部分：模拟完整请求链路
# ============================================================

def demo_full_chain():
    """模拟展示一次完整请求经过的所有环节。

    用文字 + 实际测量来展示从用户输入 URL 到看到结果的全过程。
    """
    print("\n" + "=" * 60)
    print("  第 4 部分：完整请求链路模拟")
    print("=" * 60)

    target_url = "https://httpbin.org/get"
    hostname = "httpbin.org"

    print(f"\n  模拟用户在浏览器输入: {target_url}")
    print(f"\n  {'─' * 50}")

    # 环节 1：DNS 解析
    print(f"\n  ① DNS 解析")
    print(f"     浏览器查找 DNS 缓存...")
    start = time.perf_counter()
    ip = socket.gethostbyname(hostname)
    dns_ms = (time.perf_counter() - start) * 1000
    print(f"     解析结果: {hostname} → {ip}")
    print(f"     耗时: {dns_ms:.2f} ms")

    # 环节 2：TCP 连接
    print(f"\n  ② TCP 三次握手")
    print(f"     客户端 → SYN → 服务器 ({ip}:443)")
    start = time.perf_counter()
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(5)
    sock.connect((ip, 443))
    tcp_ms = (time.perf_counter() - start) * 1000
    print(f"     连接建立成功")
    print(f"     耗时: {tcp_ms:.2f} ms")
    sock.close()

    # 环节 3-5：发送完整 HTTP 请求
    print(f"\n  ③ TLS 加密握手（HTTPS）")
    print(f"     协商加密算法、交换证书...")

    print(f"\n  ④ 发送 HTTP 请求")
    print(f"     GET /get HTTP/1.1")
    print(f"     Host: {hostname}")

    start = time.perf_counter()
    req = urllib.request.Request(target_url, headers={"User-Agent": "Python-Demo"})
    response = urllib.request.urlopen(req, timeout=10)
    request_ms = (time.perf_counter() - start) * 1000

    print(f"\n  ⑤ 服务器处理请求")
    print(f"     Nginx 接收 → 转发给应用 → 处理逻辑 → 生成响应")

    print(f"\n  ⑥ 接收响应")
    start_read = time.perf_counter()
    data = response.read()
    read_ms = (time.perf_counter() - start_read) * 1000
    print(f"     状态码: {response.status}")
    print(f"     响应大小: {len(data)} bytes")
    print(f"     下载耗时: {read_ms:.2f} ms")

    print(f"\n  ⑦ 浏览器渲染")
    print(f"     解析 HTML/JSON → 渲染到页面")

    total = dns_ms + tcp_ms + request_ms + read_ms
    print(f"\n  {'─' * 50}")
    print(f"\n  📊 总耗时统计：")
    print(f"     DNS 解析:     {dns_ms:>8.2f} ms")
    print(f"     TCP 连接:     {tcp_ms:>8.2f} ms")
    print(f"     请求+等待:    {request_ms:>8.2f} ms")
    print(f"     下载响应:     {read_ms:>8.2f} ms")
    print(f"     ─────────────────────────")
    print(f"     总计:         {total:>8.2f} ms")


# ============================================================
# 主程序
# ============================================================

def main():
    """主程序入口，依次运行各个演示。"""
    print("\n" + "█" * 60)
    print("  部署概览 Demo 2：用户请求的完整链路")
    print("█" * 60)
    print("\n  本 Demo 将演示用户请求从发出到收到响应的完整过程。")
    print("  需要网络连接才能运行。\n")

    # 第 1 部分：DNS 解析
    demo_dns_resolution()

    # 第 2 部分：各环节耗时
    demo_request_timing()

    # 第 3 部分：CDN vs 直连
    demo_cdn_vs_direct()

    # 第 4 部分：完整链路
    demo_full_chain()

    # 总结
    print("\n" + "=" * 60)
    print("  Demo 2 总结")
    print("=" * 60)
    print("""
  一次用户请求经过的完整链路：

  用户输入 URL
      ↓
  ① DNS 解析（域名 → IP 地址）        通常 1-50ms
      ↓
  ② CDN 判断（缓存命中？直接返回）      0ms（命中）或跳过
      ↓
  ③ TCP 三次握手                       10-200ms（取决于距离）
      ↓
  ④ TLS 加密握手（HTTPS）              10-100ms
      ↓
  ⑤ 发送 HTTP 请求                     < 1ms
      ↓
  ⑥ 服务器处理（Nginx → 应用 → 数据库） 10-500ms
      ↓
  ⑦ 返回响应 + 浏览器渲染              取决于数据大小

  优化重点：
  • DNS：使用可靠的 DNS 服务商
  • CDN：缓存静态资源
  • 服务器：选择离用户近的地区
  • 应用：优化代码和数据库查询
""")


if __name__ == "__main__":
    main()
