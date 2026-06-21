"""
演示脚本：gRPC 概念

本脚本用 Python 演示 gRPC 的核心概念，包括：
1. Protocol Buffers 的数据结构定义
2. REST JSON vs gRPC Protobuf 的数据大小对比
3. 序列化与反序列化的概念
4. .proto 文件示例解读
5. 模拟 gRPC 的请求/响应结构

⚠️ 这是概念演示，不需要安装 grpcio 库。
    使用 Python 标准库模拟 gRPC 的核心思想。

运行方式：
    python 2_grpc_concept.py
"""

import json
import struct


# ============================================================
# 第一部分：Protocol Buffers 概念介绍
# ============================================================

def section_title(title):
    """打印章节标题"""
    print(f"\n{'=' * 60}")
    print(f"  {title}")
    print(f"{'=' * 60}\n")


def intro_protobuf():
    """介绍 Protocol Buffers 的基本概念"""
    section_title("一、什么是 Protocol Buffers？")

    print("""
Protocol Buffers（简称 Protobuf）是 Google 开发的数据序列化格式。
它类似于 JSON，但有以下关键区别：

┌──────────────┬─────────────────┬─────────────────┐
│    特性       │     JSON        │   Protobuf      │
├──────────────┼─────────────────┼─────────────────┤
│ 格式         │ 文本（人可读）    │ 二进制（不可读）  │
│ 体积         │ 较大            │ 小（1/3 ~ 1/2） │
│ 速度         │ 较慢            │ 快（20~100 倍）  │
│ 类型安全     │ 无（弱类型）     │ 强类型           │
│ 接口定义     │ OpenAPI/Swagger │ .proto 文件      │
│ 版本兼容     │ 需手动处理       │ 原生支持         │
└──────────────┴─────────────────┴─────────────────┘

Protobuf 的核心思想：
  1. 先用 .proto 文件定义数据结构和服务接口
  2. 用编译器（protoc）生成各语言的代码
  3. 服务端和客户端使用生成的代码进行通信
""")


# ============================================================
# 第二部分：.proto 文件示例
# ============================================================

PROTO_FILE_EXAMPLE = '''
// ========================================
// user.proto — 用户服务的 Protobuf 定义
// ========================================
syntax = "proto3";    // 使用 proto3 语法版本

package user;         // 包名，避免不同服务间的命名冲突

// ---------- 数据结构定义 ----------

// 获取用户的请求消息
message GetUserRequest {
    int64 user_id = 1;    // 字段编号 1，类型 int64
                          // 编号是唯一的标识符，不能修改
}

// 用户信息响应消息
message UserResponse {
    int64 id = 1;
    string name = 2;
    string email = 3;
    int32 age = 4;
    UserStatus status = 5;

    // 枚举类型
    enum UserStatus {
        UNKNOWN = 0;     // proto3 要求第一个枚举值为 0
        ACTIVE = 1;
        INACTIVE = 2;
    }
}

// 创建用户的请求消息
message CreateUserRequest {
    string name = 1;
    string email = 2;
    int32 age = 3;
}

// ---------- 服务定义 ----------

// 用户服务，定义了 3 个 RPC 方法
service UserService {
    // 一元 RPC：客户端发一个请求，服务端返回一个响应
    rpc GetUser (GetUserRequest) returns (UserResponse);

    // 一元 RPC：创建用户
    rpc CreateUser (CreateUserRequest) returns (UserResponse);

    // 服务端流式 RPC：客户端发一个请求，服务端持续返回多个响应
    rpc ListUsers (GetUserRequest) returns (stream UserResponse);
}
'''


def show_proto_file():
    """展示并解读 .proto 文件"""
    section_title("二、.proto 文件示例与解读")

    print("下面是一个典型的 .proto 文件（用户服务接口定义）：")
    print("-" * 60)
    print(PROTO_FILE_EXAMPLE)
    print("-" * 60)

    print("""
关键语法解读：

1. message —— 定义数据结构（类似 Python 的 class）
   - 每个字段有：类型 + 名称 + 编号
   - 编号是序列化后的唯一标识，一旦确定不能修改
   - 常用类型：int32, int64, string, bool, float, double

2. service —— 定义 RPC 服务
   - 包含多个 rpc 方法
   - 每个方法指定请求消息类型和响应消息类型

3. rpc —— 定义远程调用方法
   - 一元 RPC：rpc Method(Req) returns (Resp)
   - 服务端流：rpc Method(Req) returns (stream Resp)
   - 客户端流：rpc Method(stream Req) returns (Resp)
   - 双向流：rpc Method(stream Req) returns (stream Resp)

4. enum —— 定义枚举类型
   - proto3 要求第一个值必须是 0（作为默认值）

5. 字段编号的规则：
   - 编号 1-15 只用 1 个字节编码（常用字段用小数字）
   - 编号 16-2047 用 2 个字节编码
   - 编号一旦使用，不能更改（否则破坏兼容性）
""")


# ============================================================
# 第三部分：模拟 Protobuf 编码
# ============================================================

def simulate_protobuf_encoding():
    """
    模拟 Protobuf 的编码过程

    真实的 Protobuf 使用 varint 编码和 wire type，
    这里用简化的方式演示核心思想：用二进制紧凑存储数据
    """
    section_title("三、序列化对比：JSON vs 模拟 Protobuf")

    # 示例数据：一个用户对象
    user_data = {
        "id": 12345,
        "name": "张三",
        "email": "zhangsan@example.com",
        "age": 28,
        "status": "ACTIVE",
    }

    print("原始数据：")
    print(f"  {user_data}")
    print()

    # ── JSON 序列化 ──
    json_bytes = json.dumps(user_data, ensure_ascii=False).encode("utf-8")
    json_size = len(json_bytes)

    print(f"JSON 序列化结果（文本格式）：")
    print(f"  内容: {json_bytes.decode('utf-8')}")
    print(f"  大小: {json_size} 字节")
    print()

    # ── 模拟 Protobuf 序列化 ──
    # 真实的 Protobuf 使用 (field_number << 3 | wire_type) 作为 tag
    # 这里简化为：字段编号(1字节) + 类型标识(1字节) + 数据
    proto_buffer = bytearray()

    # 字段 1: id (int64, wire_type=0 表示 varint)
    # tag = (1 << 3) | 0 = 8
    proto_buffer.append(8)
    proto_buffer.extend(struct.pack("<q", user_data["id"]))  # 8 字节 int64

    # 字段 2: name (string, wire_type=2 表示 length-delimited)
    # tag = (2 << 3) | 2 = 18
    name_bytes = user_data["name"].encode("utf-8")
    proto_buffer.append(18)
    proto_buffer.append(len(name_bytes))  # 长度前缀
    proto_buffer.extend(name_bytes)

    # 字段 3: email (string)
    # tag = (3 << 3) | 2 = 26
    email_bytes = user_data["email"].encode("utf-8")
    proto_buffer.append(26)
    proto_buffer.append(len(email_bytes))
    proto_buffer.extend(email_bytes)

    # 字段 4: age (int32, wire_type=0)
    # tag = (4 << 3) | 0 = 32
    proto_buffer.append(32)
    proto_buffer.extend(struct.pack("<i", user_data["age"]))  # 4 字节 int32

    # 字段 5: status (enum, 用 int32 存储)
    # tag = (5 << 3) | 0 = 40
    status_map = {"UNKNOWN": 0, "ACTIVE": 1, "INACTIVE": 2}
    proto_buffer.append(40)
    proto_buffer.extend(struct.pack("<i", status_map.get(user_data["status"], 0)))

    proto_size = len(proto_buffer)

    print(f"模拟 Protobuf 序列化结果（二进制格式）：")
    print(f"  十六进制: {proto_buffer.hex()}")
    print(f"  大小: {proto_size} 字节")
    print()

    # ── 对比 ──
    ratio = json_size / proto_size if proto_size > 0 else 0
    print(f"{'─' * 40}")
    print(f"  JSON 大小:          {json_size} 字节")
    print(f"  模拟 Protobuf 大小: {proto_size} 字节")
    print(f"  体积比:             JSON 是 Protobuf 的 {ratio:.1f} 倍")
    print(f"  节省空间:           {(1 - proto_size/json_size) * 100:.1f}%")
    print()
    print("  💡 真实的 Protobuf 使用 varint 编码，小整数只需 1 字节，")
    print("     压缩效果更好。这里的模拟版本为了教学目的做了简化。")

    return json_bytes, bytes(proto_buffer)


# ============================================================
# 第四部分：模拟反序列化
# ============================================================

def simulate_protobuf_decoding(proto_bytes):
    """模拟 Protobuf 的反序列化过程"""
    section_title("四、反序列化：从二进制恢复数据")

    print("将上面的二进制数据反序列化回 Python 对象：")
    print(f"  输入: {proto_bytes.hex()}")
    print()

    # 模拟解码过程
    data = {}
    offset = 0
    buf = proto_bytes

    while offset < len(buf):
        tag = buf[offset]
        field_number = tag >> 3
        wire_type = tag & 0x07
        offset += 1

        if wire_type == 0:
            # varint（这里简化为固定长度）
            if field_number == 1:  # id (int64)
                value = struct.unpack_from("<q", buf, offset)[0]
                offset += 8
                data["id"] = value
            elif field_number == 4:  # age (int32)
                value = struct.unpack_from("<i", buf, offset)[0]
                offset += 4
                data["age"] = value
            elif field_number == 5:  # status (enum)
                value = struct.unpack_from("<i", buf, offset)[0]
                offset += 4
                status_reverse = {0: "UNKNOWN", 1: "ACTIVE", 2: "INACTIVE"}
                data["status"] = status_reverse.get(value, "UNKNOWN")
        elif wire_type == 2:
            # length-delimited (string)
            length = buf[offset]
            offset += 1
            value = buf[offset:offset + length].decode("utf-8")
            offset += length
            if field_number == 2:
                data["name"] = value
            elif field_number == 3:
                data["email"] = value

    print("  解码过程：")
    print(f"    字段 1 (id):     tag=0x08, int64  → {data.get('id')}")
    print(f"    字段 2 (name):   tag=0x12, string → {data.get('name')}")
    print(f"    字段 3 (email):  tag=0x1a, string → {data.get('email')}")
    print(f"    字段 4 (age):    tag=0x20, int32  → {data.get('age')}")
    print(f"    字段 5 (status): tag=0x28, enum   → {data.get('status')}")
    print()
    print(f"  反序列化结果: {data}")
    print()
    print("  ✅ 成功从二进制数据恢复了完整的用户对象！")


# ============================================================
# 第五部分：批量数据对比
# ============================================================

def batch_size_comparison():
    """批量数据的大小对比，展示 Protobuf 在大规模数据下的优势"""
    section_title("五、大规模数据下的体积对比")

    print("场景：传输 1000 个用户记录")
    print()

    # 生成 1000 个用户数据
    users = []
    for i in range(1, 1001):
        user = {
            "id": i,
            "name": f"用户{i:04d}",
            "email": f"user{i:04d}@example.com",
            "age": 20 + (i % 40),
            "status": "ACTIVE" if i % 3 != 0 else "INACTIVE",
        }
        users.append(user)

    # JSON 序列化
    json_data = json.dumps(users, ensure_ascii=False)
    json_size = len(json_data.encode("utf-8"))

    # 模拟 Protobuf 序列化（计算总大小）
    proto_size = 0
    for user in users:
        # tag(1) + id(8)
        proto_size += 1 + 8
        # tag(1) + len(1) + name
        name_bytes = user["name"].encode("utf-8")
        proto_size += 1 + 1 + len(name_bytes)
        # tag(1) + len(1) + email
        email_bytes = user["email"].encode("utf-8")
        proto_size += 1 + 1 + len(email_bytes)
        # tag(1) + age(4)
        proto_size += 1 + 4
        # tag(1) + status(4)
        proto_size += 1 + 4

    print(f"  1000 个用户的 JSON 大小:          {json_size:>10,} 字节 ({json_size/1024:.1f} KB)")
    print(f"  1000 个用户的模拟 Protobuf 大小:   {proto_size:>10,} 字节 ({proto_size/1024:.1f} KB)")
    print(f"  体积比:                           JSON 是 Protobuf 的 {json_size/proto_size:.1f} 倍")
    print()

    # 模拟网络传输时间
    bandwidth_mbps = 100  # 假设 100 Mbps 网络
    json_time_ms = (json_size * 8) / (bandwidth_mbps * 1_000_000) * 1000
    proto_time_ms = (proto_size * 8) / (bandwidth_mbps * 1_000_000) * 1000

    print(f"  在 100 Mbps 网络下的理论传输时间：")
    print(f"    JSON:     {json_time_ms:.3f} ms")
    print(f"    Protobuf: {proto_time_ms:.3f} ms")
    print(f"    节省时间: {json_time_ms - proto_time_ms:.3f} ms")
    print()
    print("  💡 在高并发、大数据量的微服务场景下，")
    print("     Protobuf 的体积优势可以显著降低网络开销和延迟。")


# ============================================================
# 第六部分：模拟 gRPC 调用流程
# ============================================================

def simulate_grpc_flow():
    """模拟一次完整的 gRPC 调用流程"""
    section_title("六、模拟 gRPC 调用流程")

    print("以下模拟了一次 gRPC 调用的完整流程：")
    print("  客户端调用 stub.GetUser(user_id=123)")
    print()

    # 模拟请求消息
    request = {"user_id": 123}
    print(f"1️⃣  客户端构造请求消息:")
    print(f"    GetUserRequest {{ user_id: {request['user_id']} }}")
    print()

    # 模拟序列化
    print("2️⃣  gRPC 框架将消息序列化为 Protobuf 二进制:")
    # 简化的序列化
    req_bytes = struct.pack("<Bq", 8, request["user_id"])  # tag + int64
    print(f"    二进制: {req_bytes.hex()} ({len(req_bytes)} 字节)")
    print()

    # 模拟 HTTP/2 传输
    print("3️⃣  通过 HTTP/2 协议发送到服务端:")
    print("    POST /user.UserService/GetUser")
    print("    Content-Type: application/grpc")
    print("    协议: HTTP/2（支持多路复用、头部压缩）")
    print()

    # 模拟反序列化
    print("4️⃣  服务端接收并反序列化请求:")
    field_tag = req_bytes[0]
    user_id = struct.unpack_from("<q", req_bytes, 1)[0]
    print(f"    解析 tag=0x{field_tag:02x}, user_id={user_id}")
    print()

    # 模拟业务处理
    print("5️⃣  服务端执行业务逻辑（查询数据库）:")
    print(f"    SELECT * FROM users WHERE id = {user_id}")
    response = {
        "id": 123,
        "name": "张三",
        "email": "zhangsan@example.com",
        "age": 28,
        "status": "ACTIVE",
    }
    print(f"    查询结果: {response}")
    print()

    # 模拟响应序列化
    print("6️⃣  服务端将响应序列化为 Protobuf 并返回:")
    print(f"    UserResponse {{ id: 123, name: \"张三\", ... }}")
    print()

    # 模拟客户端反序列化
    print("7️⃣  客户端反序列化响应，得到 Python 对象:")
    print(f"    response.id    = {response['id']}")
    print(f"    response.name  = {response['name']}")
    print(f"    response.email = {response['email']}")
    print(f"    response.age   = {response['age']}")
    print(f"    response.status = {response['status']}")
    print()
    print("  ✅ 一次完整的 gRPC 调用完成！")
    print("     整个过程对开发者来说就像调用本地函数一样简单。")


# ============================================================
# 第七部分：gRPC 四种通信模式
# ============================================================

def explain_communication_modes():
    """解释 gRPC 的四种通信模式"""
    section_title("七、gRPC 的四种通信模式")

    print("""
gRPC 基于 HTTP/2 协议，支持四种通信模式：

1. 一元 RPC（Unary RPC）
   ───────────────────────────────────────
   客户端 ──[1个请求]──▶ 服务端
   客户端 ◀──[1个响应]── 服务端

   最常用，类似普通的 HTTP 请求/响应。
   例：GetUser(id=123) → UserResponse

2. 服务端流式 RPC（Server Streaming RPC）
   ───────────────────────────────────────
   客户端 ──[1个请求]──▶ 服务端
   客户端 ◀──[响应1]──── 服务端
   客户端 ◀──[响应2]──── 服务端
   客户端 ◀──[响应3]──── 服务端

   服务端持续推送数据给客户端。
   例：ListUsers() → stream UserResponse（逐个返回用户）

3. 客户端流式 RPC（Client Streaming RPC）
   ───────────────────────────────────────
   客户端 ──[请求1]──▶ 服务端
   客户端 ──[请求2]──▶ 服务端
   客户端 ──[请求3]──▶ 服务端
   客户端 ◀──[1个响应]── 服务端

   客户端持续发送数据，服务端汇总后返回一个响应。
   例：UploadFile(stream Chunk) → UploadResult

4. 双向流式 RPC（Bidirectional Streaming RPC）
   ───────────────────────────────────────
   客户端 ──[消息1]──▶ 服务端
   客户端 ◀──[消息2]── 服务端
   客户端 ──[消息3]──▶ 服务端
   客户端 ◀──[消息4]── 服务端

   双方持续通信，类似 WebSocket。
   例：Chat(stream Message) → stream Message
""")


# ============================================================
# 第八部分：Python gRPC 实际代码示例（伪代码）
# ============================================================

def show_python_grpc_code():
    """展示 Python gRPC 的实际代码结构"""
    section_title("八、Python gRPC 代码结构（伪代码）")

    print("""
以下是使用 Python 实现 gRPC 服务的典型代码结构：

┌─────────────────────────────────────────────────────────┐
│  步骤 1: 编写 .proto 文件                                │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  # user.proto                                           │
│  syntax = "proto3";                                     │
│  service UserService {                                  │
│      rpc GetUser (GetUserRequest) returns (UserResp);   │
│  }                                                      │
│  message GetUserRequest { int64 user_id = 1; }          │
│  message UserResp { int64 id=1; string name=2; }        │
│                                                         │
├─────────────────────────────────────────────────────────┤
│  步骤 2: 编译生成 Python 代码                            │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  $ python -m grpc_tools.protoc \\                       │
│        -I. \\                                           │
│        --python_out=. \\                                │
│        --grpc_python_out=. \\                           │
│        user.proto                                       │
│                                                         │
│  生成文件：                                              │
│    user_pb2.py       ← 数据结构类（message）             │
│    user_pb2_grpc.py  ← 服务类和 Stub 类                 │
│                                                         │
├─────────────────────────────────────────────────────────┤
│  步骤 3: 实现服务端                                      │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  import grpc                                            │
│  from concurrent import futures                         │
│  import user_pb2, user_pb2_grpc                         │
│                                                         │
│  class UserService(user_pb2_grpc.UserServiceServicer):  │
│      def GetUser(self, request, context):               │
│          # request.user_id 就是客户端传来的 ID           │
│          return user_pb2.UserResp(                      │
│              id=request.user_id,                        │
│              name="张三"                                 │
│          )                                              │
│                                                         │
│  server = grpc.server(futures.ThreadPoolExecutor(10))   │
│  user_pb2_grpc.add_UserServiceServicer_to_server(       │
│      UserService(), server                              │
│  )                                                      │
│  server.add_insecure_port('[::]:50051')                 │
│  server.start()                                         │
│                                                         │
├─────────────────────────────────────────────────────────┤
│  步骤 4: 实现客户端                                      │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  import grpc                                            │
│  import user_pb2, user_pb2_grpc                         │
│                                                         │
│  channel = grpc.insecure_channel('localhost:50051')     │
│  stub = user_pb2_grpc.UserServiceStub(channel)          │
│                                                         │
│  # 就像调用本地函数一样调用远程服务！                      │
│  response = stub.GetUser(                               │
│      user_pb2.GetUserRequest(user_id=123)               │
│  )                                                      │
│  print(response.name)  # 输出: 张三                     │
│                                                         │
└─────────────────────────────────────────────────────────┘
""")


# ============================================================
# 第九部分：常见坑总结
# ============================================================

def show_pitfalls():
    """总结 gRPC 的常见坑"""
    section_title("九、gRPC 常见坑")

    print("""
坑 1：字段编号不能修改
─────────────────────
  .proto 文件中的字段编号（如 = 1, = 2）一旦确定就不能修改。
  修改编号会导致旧客户端无法解析新服务端的数据，破坏向后兼容性。

  ✅ 正确做法：新增字段用新编号，废弃字段保留编号但标记为 reserved。

坑 2：Protobuf 不可读，调试困难
─────────────────────────────
  Protobuf 是二进制格式，不能像 JSON 那样直接阅读。
  网络抓包时看到的是一堆乱码。

  ✅ 解决方案：使用 grpcurl 或 Postman 的 gRPC 支持来调试。

坑 3：gRPC 不直接支持浏览器
───────────────────────────
  浏览器不支持原生 gRPC（需要 HTTP/2 +  trailers）。
  前端不能直接调用 gRPC 服务。

  ✅ 解决方案：使用 gRPC-Web 代理（如 Envoy）或 API 网关转换。

坑 4：HTTP/2 长连接导致负载均衡失效
──────────────────────────────────
  gRPC 基于 HTTP/2，一个连接上复用多个请求。
  L4 负载均衡器只在连接建立时分配一次，导致负载不均。

  ✅ 解决方案：使用客户端负载均衡或 L7 负载均衡器（如 Envoy）。

坑 5：忽略超时和重试配置
───────────────────────
  gRPC 默认没有超时，如果不设置，调用可能永远等待。

  ✅ 正确做法：
    stub.GetUser(request, timeout=5)  # 5 秒超时
""")


# ============================================================
# 主程序
# ============================================================

def main():
    """运行所有演示"""
    print("=" * 60)
    print("  gRPC 与 Protocol Buffers 概念演示")
    print("=" * 60)

    # 一、Protobuf 概念介绍
    intro_protobuf()

    # 二、.proto 文件示例
    show_proto_file()

    # 三、序列化对比
    json_bytes, proto_bytes = simulate_protobuf_encoding()

    # 四、反序列化
    simulate_protobuf_decoding(proto_bytes)

    # 五、批量数据对比
    batch_size_comparison()

    # 六、模拟 gRPC 调用流程
    simulate_grpc_flow()

    # 七、四种通信模式
    explain_communication_modes()

    # 八、Python 代码结构
    show_python_grpc_code()

    # 九、常见坑
    show_pitfalls()

    # 总结
    section_title("总结")
    print("""
本节核心要点：

1. Protocol Buffers 是 gRPC 的数据序列化格式
   - 比 JSON 更小、更快
   - 强类型，通过 .proto 文件定义

2. gRPC 是基于 HTTP/2 的高性能 RPC 框架
   - 支持一元、服务端流、客户端流、双向流四种模式
   - 自动生成多语言客户端代码

3. gRPC 适合微服务内部通信
   - 追求高性能的场景
   - 多语言团队协作
   - 对外 API 仍建议使用 REST

4. 实际使用需要安装 grpcio 和 grpcio-tools
   - 编写 .proto → 编译生成代码 → 实现服务端/客户端

了解级别不需要深入实操，但要理解：
  - 为什么 gRPC 比 REST 快（Protobuf + HTTP/2）
  - .proto 文件的作用（接口定义 + 代码生成）
  - gRPC 的适用场景（内部微服务通信）
""")


if __name__ == "__main__":
    main()
