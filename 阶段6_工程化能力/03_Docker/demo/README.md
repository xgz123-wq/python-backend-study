# Docker 章节演示脚本

## 运行说明

本目录包含 Docker 章节的演示脚本和配置文件示例。

> **前置要求**：需要安装 Docker Desktop（参见 [1.Docker基础概念.md](../1.Docker基础概念.md) 第六章）。
> 如果 Docker 未安装，脚本会提示安装指引并优雅退出。

## 文件清单

| 文件                     | 类型          | 说明                                       |
|------------------------|-------------|------------------------------------------|
| `1_docker_basics.py`   | Python 脚本   | 演示 Docker 基础操作：镜像拉取、容器运行、日志查看、数据卷  |
| `2_dockerfile_demo.py`  | Python 脚本   | 生成 FastAPI 应用和 Dockerfile，讲解每行指令的作用     |
| `3_compose_demo.py`     | Python 脚本   | 生成 docker-compose.yml，解析配置，讲解服务编排      |
| `Dockerfile`           | Docker 配置   | Python FastAPI 应用的生产级 Dockerfile 示例      |
| `docker-compose.yml`   | Docker 配置   | FastAPI + MySQL + Redis 完整编排示例           |
| `requirements.txt`     | Python 依赖   | fastapi, uvicorn                          |

## 运行顺序

```bash
# 1. 基础操作演示（需要 Docker 已安装）
python "阶段6_工程化能力/03_Docker/demo/1_docker_basics.py"

# 2. Dockerfile 生成与讲解（不需要 Docker）
python "阶段6_工程化能力/03_Docker/demo/2_dockerfile_demo.py"

# 3. docker-compose 编排讲解（需要 Docker 已安装才能实际启动）
python "阶段6_工程化能力/03_Docker/demo/3_compose_demo.py"
```

## Dockerfile 配置说明

`demo/Dockerfile` 展示了 Python FastAPI 应用的生产级 Dockerfile：

- **多阶段构建**：构建阶段安装依赖，运行阶段只保留必要文件
- **非 root 用户**：创建 appuser 运行应用，提升安全性
- **健康检查**：配置 HEALTHCHECK 指令，配合编排工具使用
- **层缓存优化**：先复制 requirements.txt 再复制源码，最大化利用缓存

## docker-compose.yml 配置说明

`demo/docker-compose.yml` 展示完整的三服务编排：

- **db**（MySQL 8.0）：带健康检查、数据持久化、用户配置
- **redis**（Redis 7.2）：带健康检查、数据持久化
- **web**（FastAPI）：依赖 db 和 redis 的健康状态、环境变量注入、端口映射

## 快速体验

如果你想直接用这套配置启动项目：

```bash
# 1. 进入 demo 目录
cd "阶段6_工程化能力/03_Docker/demo"

# 2. 创建 .env 文件
echo "APP_ENV=development" > .env

# 3. 一键启动（首次会自动构建镜像）
docker compose up -d --build

# 4. 查看服务状态
docker compose ps

# 5. 查看日志
docker compose logs -f

# 6. 访问应用
# http://localhost:8000          — FastAPI 应用
# http://localhost:8000/docs     — Swagger 文档
# http://localhost:8000/health   — 健康检查

# 7. 停止并清理
docker compose down
```
