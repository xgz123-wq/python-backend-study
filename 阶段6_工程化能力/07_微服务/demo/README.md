# 第 7 章：微服务（了解）— 演示脚本

## 运行顺序

| 序号 | 脚本 | 说明 |
|------|------|------|
| 1 | `1_microservice_concept.py` | 用 Python 模拟微服务架构：用户服务、订单服务、服务注册与发现、API 网关、调用链追踪 |
| 2 | `2_grpc_concept.py` | 用 Python 演示 gRPC 概念：Protocol Buffers 结构、REST vs Protobuf 大小对比、序列化概念、.proto 文件示例 |

## 运行方式

```bash
# 脚本 1：微服务概念演示
python "阶段6_工程化能力/07_微服务/demo/1_microservice_concept.py"

# 脚本 2：gRPC 概念演示
python "阶段6_工程化能力/07_微服务/demo/2_grpc_concept.py"
```

## 说明

- 本章为**了解级别**，脚本以演示概念为主，不需要安装额外依赖（除标准库外）
- 脚本 1 使用 Python 内置的 `http.server` 和 `json` 模拟微服务通信，无需 `requests` 库
- 脚本 2 使用 Python 标准库演示序列化和数据大小对比，无需安装 `grpcio`
- 每个脚本都有详细的中文注释，建议边运行边阅读输出和代码
