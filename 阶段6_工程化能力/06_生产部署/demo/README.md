# 生产部署 - 演示脚本

本章演示脚本展示生产部署的核心概念和工具。

## 运行顺序

| 顺序 | 文件 | 说明 |
|------|------|------|
| 1 | `1_wsgi_asgi.py` | WSGI/ASGI 概念演示，单进程 vs 多进程对比 |
| 2 | `2_process_config.py` | 环境变量管理、配置分离、结构化日志 |
| 3 | `3_security_check.py` | 安全配置检查器，生成安全报告 |

## 配置文件

| 文件 | 说明 |
|------|------|
| `gunicorn_config.py` | Gunicorn 生产配置文件（详细注释） |
| `app.service` | systemd 服务文件模板 |
| `deploy.sh` | 完整部署脚本（服务器初始化→部署→HTTPS→回滚） |

## 运行方式

```bash
# 演示脚本 1：WSGI/ASGI 概念
python "阶段6_工程化能力/06_生产部署/demo/1_wsgi_asgi.py"

# 演示脚本 2：环境变量与配置管理
python "阶段6_工程化能力/06_生产部署/demo/2_process_config.py"

# 演示脚本 3：安全检查器
python "阶段6_工程化能力/06_生产部署/demo/3_security_check.py"
```

## deploy.sh 部署脚本说明

`deploy.sh` 是一个**完整的生产部署脚本示例**，包含以下步骤：

1. **服务器初始化**：安装 Python 3.11、Nginx、Git
2. **拉取代码**：从 Git 仓库克隆项目
3. **安装依赖**：创建虚拟环境，安装 requirements.txt
4. **配置 Gunicorn**：复制 gunicorn_config.py
5. **配置 systemd**：复制 app.service，启用开机启动
6. **配置 Nginx**：反向代理 + 静态文件托管
7. **配置 HTTPS**：使用 Let's Encrypt 自动配置
8. **健康检查**：验证服务是否正常运行
9. **回滚机制**：部署失败时自动回滚到上一版本

**注意**：此脚本仅供学习参考，实际部署前需要根据你的项目修改配置。

```bash
# 使用方法（在服务器上执行）
chmod +x deploy.sh
sudo ./deploy.sh
```

## 前置要求

- Python 3.10+
- 无额外依赖（全部使用标准库）
