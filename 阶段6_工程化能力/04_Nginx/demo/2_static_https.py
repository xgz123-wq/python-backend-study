"""
静态文件与 HTTPS —— Python 概念演示脚本
========================================

本脚本用纯 Python 演示 Nginx 处理静态文件和 HTTPS 的底层机制。

演示内容：
  1. 用 Python 搭建简单的静态文件服务器
  2. 展示 gzip 压缩效果（压缩前后大小对比）
  3. 模拟 HTTPS/TLS 握手过程
  4. 展示证书验证原理

运行方式：
  python 2_static_https.py

依赖：
  仅使用 Python 标准库，无需额外安装
"""

import gzip
import hashlib
import http.server
import io
import json
import os
import socket
import ssl
import tempfile
import threading
import time
import urllib.request
import urllib.error
from pathlib import Path

# ===========================================================================
# 第一部分：Python 静态文件服务器
# ===========================================================================

class StaticFileHandler(http.server.SimpleHTTPRequestHandler):
    """
    自定义静态文件服务器处理器。

    继承自 SimpleHTTPRequestHandler，增加了：
    - 自定义响应头（模拟 Nginx 的 add_header）
    - Cache-Control 缓存控制
    - 请求日志

    这相当于 Nginx 中 location /static/ { alias ...; } 的功能。
    """

    def __init__(self, *args, static_dir: str = ".", **kwargs):
        """初始化，指定静态文件根目录。"""
        self.static_dir = static_dir
        super().__init__(*args, directory=static_dir, **kwargs)

    def end_headers(self):
        """
        在响应头中添加缓存控制信息。
        相当于 Nginx 的:
          add_header Cache-Control "public, max-age=86400";
          add_header X-Served-By "PythonStaticServer";
        """
        # 设置缓存策略（模拟 Nginx 的 expires 指令）
        if self.path.endswith((".html",)):
            # HTML 不缓存（模拟 no-cache）
            self.send_header("Cache-Control", "no-cache, no-store, must-revalidate")
        elif self.path.endswith((".css", ".js", ".png", ".jpg")):
            # 静态资源缓存 1 天
            self.send_header("Cache-Control", "public, max-age=86400")

        # 添加自定义头（模拟 Nginx 的 add_header）
        self.send_header("X-Served-By", "PythonStaticServer")
        super().end_headers()

    def log_message(self, format, *args):
        """自定义日志格式。"""
        print(f"  [静态服务器] {self.client_address[0]} - {args[0]}")


def create_sample_files(static_dir: str):
    """
    在指定目录创建示例静态文件。

    创建的文件：
    - index.html   （HTML 页面）
    - style.css    （CSS 样式表）
    - data.json    （JSON 数据）
    """
    os.makedirs(static_dir, exist_ok=True)

    # HTML 文件
    html_content = """<!DOCTYPE html>
<html>
<head>
    <title>Nginx 静态文件演示</title>
    <link rel="stylesheet" href="style.css">
</head>
<body>
    <h1>这是 Nginx 静态文件托管的演示页面</h1>
    <p>在实际部署中，这个文件由 Nginx 直接返回，不经过 Python 应用。</p>
    <p>Nginx 使用 sendfile() 系统调用，性能远高于 Python 处理。</p>
</body>
</html>"""

    # CSS 文件
    css_content = """/* 示例样式表 */
body {
    font-family: 'Segoe UI', sans-serif;
    max-width: 800px;
    margin: 0 auto;
    padding: 20px;
    background-color: #f5f5f5;
}
h1 { color: #333; }
p { color: #666; line-height: 1.6; }"""

    # JSON 数据文件
    json_content = json.dumps({
        "api_version": "1.0",
        "endpoints": ["/users", "/products", "/orders"],
        "note": "这是静态 JSON 文件，Nginx 可以直接返回",
    }, ensure_ascii=False, indent=2)

    # 写入文件
    files = {
        "index.html": html_content,
        "style.css": css_content,
        "data.json": json_content,
    }

    for filename, content in files.items():
        filepath = os.path.join(static_dir, filename)
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)

    return files


def run_static_server_demo():
    """
    启动静态文件服务器，演示 Nginx 静态文件托管的原理。
    """
    print("=" * 70)
    print("第一部分：Python 静态文件服务器")
    print("=" * 70)
    print()

    # 创建临时目录和示例文件
    static_dir = tempfile.mkdtemp(prefix="nginx_demo_static_")
    files = create_sample_files(static_dir)

    print(f"  静态文件目录: {static_dir}")
    print(f"  创建的文件:")
    for name, content in files.items():
        size = len(content.encode("utf-8"))
        print(f"    {name} ({size} 字节)")

    print()

    # 启动静态文件服务器
    port = 9100
    handler = lambda *args, **kwargs: StaticFileHandler(
        *args, static_dir=static_dir, **kwargs
    )
    server = http.server.HTTPServer(("127.0.0.1", port), handler)
    server_thread = threading.Thread(target=server.serve_forever, daemon=True)
    server_thread.start()
    print(f"  ✓ 静态文件服务器启动: http://127.0.0.1:{port}")
    print()

    time.sleep(0.3)

    # 测试请求各文件
    print("--- 请求静态文件 ---")
    for filename in files:
        try:
            url = f"http://127.0.0.1:{port}/{filename}"
            resp = urllib.request.urlopen(url, timeout=5)
            content_length = resp.headers.get("Content-Length", "未知")
            cache_control = resp.headers.get("Cache-Control", "未设置")
            served_by = resp.headers.get("X-Served-By", "未知")
            status = resp.status

            print(f"  GET /{filename}")
            print(f"    状态码: {status}")
            print(f"    大小:   {content_length} 字节")
            print(f"    缓存:   {cache_control}")
            print(f"    服务器: {served_by}")
            print()
        except Exception as e:
            print(f"  GET /{filename} → 失败: {e}")
            print()

    # 测试 404
    print("--- 请求不存在的文件（404）---")
    try:
        url = f"http://127.0.0.1:{port}/not_exist.txt"
        urllib.request.urlopen(url, timeout=5)
    except urllib.error.HTTPError as e:
        print(f"  GET /not_exist.txt → 状态码: {e.code}")
        print(f"  这就是 Nginx 返回 404 Not Found 的原理")

    print()
    server.shutdown()
    print("  ✓ 服务器已关闭")
    print()


# ===========================================================================
# 第二部分：gzip 压缩效果演示
# ===========================================================================

def demonstrate_gzip_compression():
    """
    演示 gzip 压缩对不同类型文件的压缩效果。

    Nginx 配置：
      gzip on;
      gzip_comp_level 6;
      gzip_types text/css application/javascript application/json;

    注意：Nginx 不对图片和视频做 gzip（它们已是压缩格式）。
    """
    print("=" * 70)
    print("第二部分：gzip 压缩效果演示")
    print("=" * 70)
    print()

    # 准备不同类型的测试数据
    test_data = {
        "HTML（文本，高重复）": "<html><body>" + "<p>Hello World</p>" * 500 + "</body></html>",
        "CSS（文本，中等重复）": "body { margin: 0; padding: 0; }\n" * 300,
        "JSON（文本，结构化）": json.dumps([
            {"id": i, "name": f"用户{i}", "email": f"user{i}@example.com"}
            for i in range(200)
        ], ensure_ascii=False),
        "随机文本（低重复）": os.urandom(2000).hex(),
    }

    print("  Nginx gzip 配置: gzip_comp_level 6")
    print()
    print(f"  {'文件类型':<25} {'原始大小':>10} {'压缩后':>10} {'压缩率':>10} {'节省':>10}")
    print("  " + "-" * 70)

    for name, content in test_data.items():
        # 原始数据大小
        original = content.encode("utf-8") if isinstance(content, str) else content
        original_size = len(original)

        # gzip 压缩（level=6 对应 Nginx 的 gzip_comp_level 6）
        compressed = gzip.compress(original, compresslevel=6)
        compressed_size = len(compressed)

        # 计算压缩率和节省比例
        ratio = compressed_size / original_size * 100
        saved = (1 - compressed_size / original_size) * 100

        print(
            f"  {name:<25} {original_size:>8,}B "
            f"{compressed_size:>8,}B {ratio:>8.1f}% {saved:>8.1f}%"
        )

    print()
    print("  结论：")
    print("  - 文本类文件（HTML/CSS/JSON）压缩率 60%-95%，效果显著")
    print("  - 随机数据（模拟已压缩文件）压缩效果差")
    print("  - 这就是为什么 Nginx 只对 gzip_types 中的文本类型启用压缩")
    print("  - 对图片（JPEG/PNG）做 gzip 是浪费 CPU 的")
    print()


# ===========================================================================
# 第三部分：模拟 HTTPS/TLS 握手过程
# ===========================================================================

def simulate_tls_handshake():
    """
    模拟 TLS 握手过程，展示 HTTPS 通信的原理。

    TLS 握手的关键步骤：
    1. ClientHello：客户端发送支持的加密算法列表
    2. ServerHello：服务器选择算法，发送证书
    3. 客户端验证证书，生成预主密钥
    4. 双方用三个随机数生成会话密钥
    5. 后续通信使用对称加密（快）
    """
    print("=" * 70)
    print("第三部分：模拟 HTTPS/TLS 握手过程")
    print("=" * 70)
    print()

    # 步骤 1：ClientHello
    print("  步骤 1：ClientHello（客户端 → 服务器）")
    print("  ─────────────────────────────────────")

    client_random = os.urandom(32).hex()
    supported_ciphers = [
        "TLS_AES_256_GCM_SHA384",
        "TLS_AES_128_GCM_SHA256",
        "TLS_CHACHA20_POLY1305_SHA256",
        "ECDHE-RSA-AES256-GCM-SHA384",
        "ECDHE-RSA-AES128-GCM-SHA256",
    ]

    print(f"    客户端随机数: {client_random[:32]}...")
    print(f"    支持的加密算法: {', '.join(supported_ciphers)}")
    print(f"    支持的 TLS 版本: TLSv1.2, TLSv1.3")
    print()

    # 步骤 2：ServerHello
    print("  步骤 2：ServerHello（服务器 → 客户端）")
    print("  ─────────────────────────────────────")

    server_random = os.urandom(32).hex()
    selected_cipher = supported_ciphers[0]  # 服务器选择最强算法

    # 模拟证书信息
    cert_info = {
        "subject": "CN=example.com",
        "issuer": "CN=Let's Encrypt Authority X3",
        "valid_from": "2024-01-01",
        "valid_to": "2024-03-31",
        "san": ["example.com", "www.example.com"],
    }

    print(f"    服务器随机数: {server_random[:32]}...")
    print(f"    选定加密算法: {selected_cipher}")
    print(f"    证书信息:")
    print(f"      颁发给: {cert_info['subject']}")
    print(f"      颁发者: {cert_info['issuer']}")
    print(f"      有效期: {cert_info['valid_from']} ~ {cert_info['valid_to']}")
    print(f"      域名:   {', '.join(cert_info['san'])}")
    print()

    # 步骤 3：证书验证
    print("  步骤 3：客户端验证证书")
    print("  ─────────────────────")

    checks = [
        ("证书是否过期", True, "当前日期在有效期内"),
        ("域名是否匹配", True, "请求的域名在 SAN 列表中"),
        ("证书链是否完整", True, "Let's Encrypt → 根 CA 链验证通过"),
        ("证书是否被吊销", True, "OCSP 查询结果为 good"),
    ]

    for check_name, passed, detail in checks:
        status = "✓ 通过" if passed else "✗ 失败"
        print(f"    [{status}] {check_name}: {detail}")

    print()

    # 步骤 4：密钥交换
    print("  步骤 4：密钥交换（非对称加密）")
    print("  ──────────────────────────────")

    # 模拟预主密钥
    pre_master_secret = os.urandom(48).hex()
    print(f"    客户端生成预主密钥: {pre_master_secret[:32]}...")
    print(f"    用服务器公钥加密后发送（非对称加密，安全但慢）")
    print(f"    服务器用私钥解密得到预主密钥")
    print()

    # 步骤 5：生成会话密钥
    print("  步骤 5：生成会话密钥")
    print("  ────────────────────")

    # 模拟会话密钥生成
    master_input = (client_random + server_random + pre_master_secret).encode()
    session_key = hashlib.sha256(master_input).hexdigest()

    print(f"    会话密钥 = SHA256(客户端随机数 + 服务器随机数 + 预主密钥)")
    print(f"    会话密钥: {session_key[:32]}...")
    print(f"    双方各自独立计算出相同的会话密钥")
    print()

    # 步骤 6：对称加密通信
    print("  步骤 6：对称加密通信开始")
    print("  ────────────────────────")
    print(f"    后续所有数据用会话密钥加密（对称加密，速度快）")
    print(f"    客户端发送: AES-256 加密的 HTTP 请求")
    print(f"    服务器返回: AES-256 加密的 HTTP 响应")
    print()

    # 总结
    print("  TLS 握手核心原理：")
    print("  ┌─────────────────────────────────────────────────────┐")
    print("  │  非对称加密（RSA/ECDHE）: 用于握手阶段传递密钥    │")
    print("  │    优点: 安全（不需要事先共享密钥）                 │")
    print("  │    缺点: 慢（计算量大）                             │")
    print("  │                                                      │")
    print("  │  对称加密（AES）: 用于实际数据传输                  │")
    print("  │    优点: 快（比非对称快 100-1000 倍）               │")
    print("  │    缺点: 需要双方事先有相同的密钥                    │")
    print("  │                                                      │")
    print("  │  TLS = 非对称加密传密钥 + 对称加密传数据            │")
    print("  └─────────────────────────────────────────────────────┘")
    print()


# ===========================================================================
# 第四部分：证书验证演示（使用 Python ssl 模块）
# ===========================================================================

def demonstrate_ssl_certificates():
    """
    使用 Python 的 ssl 模块展示真实的证书验证过程。

    演示内容：
    - 创建自签名证书
    - 验证证书信息
    - 解释 Let's Encrypt 的证书链
    """
    print("=" * 70)
    print("第四部分：证书验证原理")
    print("=" * 70)
    print()

    # 展示 SSL 上下文的基本信息
    print("--- Python ssl 模块默认配置 ---")

    ctx = ssl.create_default_context()
    print(f"  默认协议: TLS（自动协商最高版本）")
    print(f"  最低 TLS 版本: {ctx.minimum_version}")
    print(f"  最高 TLS 版本: {ctx.maximum_version}")
    print(f"  验证模式: {ctx.verify_mode} (CERT_REQUIRED = 必须验证)")
    print(f"  检查主机名: {ctx.check_hostname}")

    # 统计系统信任的 CA 证书数量
    try:
        ca_certs = ssl.get_default_verify_paths()
        print(f"  CA 证书路径: {ca_certs.cafile or ca_certs.capath or '内置'}")
    except Exception:
        print(f"  CA 证书路径: 使用系统默认")

    print()

    # 解释证书链
    print("--- 证书链验证原理 ---")
    print()
    print("  根 CA（Root CA）")
    print("    │  ← 预装在操作系统/浏览器中（约 150 个）")
    print("    ▼")
    print("  中间 CA（Intermediate CA）")
    print("    │  ← 由根 CA 签发，可以有多层")
    print("    ▼")
    print("  网站证书（End-Entity Certificate）")
    print("    │  ← 由中间 CA 签发，包含域名和公钥")
    print("    ▼")
    print("  TLS 连接建立")
    print()

    # Let's Encrypt 证书链
    print("--- Let's Encrypt 证书链 ---")
    print()
    print("  ISRG Root X1（根 CA，预装在浏览器中）")
    print("    │")
    print("    ▼")
    print("  Let's Encrypt Authority X3 / R3（中间 CA）")
    print("    │")
    print("    ▼")
    print("  example.com 证书（网站证书，90 天有效期）")
    print()

    # Certbot 自动续期流程
    print("--- Certbot 自动续期流程 ---")
    print()
    print("  1. Certbot 生成密钥对（私钥留在服务器）")
    print("  2. Certbot 创建 CSR（证书签名请求），包含域名信息")
    print("  3. Let's Encrypt 通过 HTTP-01 挑战验证域名所有权:")
    print("     - Let's Encrypt 给出一个 token")
    print("     - Certbot 在 Nginx 上放置文件:")
    print("       /.well-known/acme-challenge/{token}")
    print("     - Let's Encrypt 访问该文件确认域名归属")
    print("  4. 验证通过后签发证书")
    print("  5. Certbot 配置 Nginx 使用新证书")
    print("  6. 自动设置 cron/systemd timer 每 60 天检查续期")
    print()

    # 自签名证书 vs CA 签发证书
    print("--- 自签名证书 vs CA 签发证书 ---")
    print()
    print("  ┌─────────────┬─────────────────┬───────────────────┐")
    print("  │             │   自签名证书    │   CA 签发证书     │")
    print("  ├─────────────┼─────────────────┼───────────────────┤")
    print("  │ 费用        │    免费         │ 免费(Let's Encrypt)│")
    print("  │ 浏览器信任  │    ✗ 警告      │    ✓ 信任         │")
    print("  │ 生成方式    │  openssl 命令   │  Certbot          │")
    print("  │ 适用场景    │ 开发/内网       │ 生产环境          │")
    print("  │ 有效期      │ 自定义          │ 90天(自动续期)    │")
    print("  └─────────────┴─────────────────┴───────────────────┘")
    print()

    # 用 openssl 生成自签名证书的命令
    print("--- 生成自签名证书（开发环境用）---")
    print()
    print("  openssl req -x509 -newkey rsa:2048 -nodes \\")
    print("    -keyout key.pem -out cert.pem \\")
    print("    -days 365 -subj '/CN=localhost'")
    print()
    print("  对应的 Nginx 配置:")
    print("    ssl_certificate     /path/to/cert.pem;")
    print("    ssl_certificate_key /path/to/key.pem;")
    print()


# ===========================================================================
# 第五部分：ETag 缓存机制演示
# ===========================================================================

def demonstrate_etag():
    """
    演示 ETag 缓存机制的工作原理。

    ETag 是服务器为每个资源生成的唯一标识符（通常是内容的哈希值）。
    浏览器再次请求时带上 If-None-Match 头，服务器比较 ETag：
    - 相同 → 返回 304 Not Modified（不传文件体）
    - 不同 → 返回 200 + 新文件 + 新 ETag
    """
    print("=" * 70)
    print("第五部分：ETag 缓存机制")
    print("=" * 70)
    print()

    # 模拟文件内容
    file_content_v1 = "body { color: black; } /* v1 */"
    file_content_v2 = "body { color: blue; }  /* v2 - 修改了颜色 */"

    # 生成 ETag（Nginx 默认用文件的修改时间和大小生成 ETag）
    etag_v1 = hashlib.md5(file_content_v1.encode()).hexdigest()[:16]
    etag_v2 = hashlib.md5(file_content_v2.encode()).hexdigest()[:16]

    print("--- 请求 1：首次请求（浏览器无缓存）---")
    print(f"  → GET /style.css")
    print(f"  ← 200 OK")
    print(f"    Content-Length: {len(file_content_v1)}")
    print(f"    ETag: \"{etag_v1}\"")
    print(f"    Body: {file_content_v1}")
    print(f"    （浏览器缓存文件和 ETag）")
    print()

    print("--- 请求 2：再次请求（文件未变化）---")
    print(f"  → GET /style.css")
    print(f"    If-None-Match: \"{etag_v1}\"")
    print(f"  ← 304 Not Modified")
    print(f"    （不传输文件体！节省带宽和时间）")
    print(f"    （浏览器使用本地缓存的文件）")
    print()

    print("--- 请求 3：文件已更新 ---")
    print(f"  → GET /style.css")
    print(f"    If-None-Match: \"{etag_v1}\"")
    print(f"  ← 200 OK")
    print(f"    ETag: \"{etag_v2}\"")
    print(f"    Body: {file_content_v2}")
    print(f"    （ETag 不同，服务器返回新文件）")
    print()

    print("  ETag vs Last-Modified:")
    print("  ┌──────────────┬───────────────────┬──────────────────────┐")
    print("  │              │      ETag         │   Last-Modified      │")
    print("  ├──────────────┼───────────────────┼──────────────────────┤")
    print("  │ 精度         │ 内容哈希，精确    │ 秒级，可能不够精确   │")
    print("  │ 性能         │ 需要计算哈希      │ 直接读文件 mtime     │")
    print("  │ 适用场景     │ 内容频繁变化      │ 内容不常变化         │")
    print("  │ Nginx 默认   │ 开启              │ 开启                 │")
    print("  └──────────────┴───────────────────┴──────────────────────┘")
    print()


# ===========================================================================
# 主程序
# ===========================================================================

def main():
    """运行所有演示。"""
    print()
    print("╔══════════════════════════════════════════════════════════════════╗")
    print("║         静态文件与 HTTPS —— Python 概念演示                    ║")
    print("╚══════════════════════════════════════════════════════════════════╝")
    print()

    # 第一部分：静态文件服务器
    run_static_server_demo()

    # 第二部分：gzip 压缩
    demonstrate_gzip_compression()

    # 第三部分：TLS 握手
    simulate_tls_handshake()

    # 第四部分：证书验证
    demonstrate_ssl_certificates()

    # 第五部分：ETag 缓存
    demonstrate_etag()

    print("=" * 70)
    print("演示结束！")
    print()
    print("核心收获：")
    print("  1. Nginx 处理静态文件用 sendfile()，性能远超 Python")
    print("  2. gzip 对文本文件压缩率 60%-95%，不对图片压缩")
    print("  3. TLS = 非对称加密传密钥 + 对称加密传数据")
    print("  4. Let's Encrypt 免费证书 + Certbot 自动续期")
    print("  5. ETag/304 机制避免重复传输未变化的文件")
    print("=" * 70)


if __name__ == "__main__":
    main()
