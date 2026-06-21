# CI/CD 持续部署 - Demo 演示

## 运行顺序

按照以下顺序运行演示脚本，逐步理解 CI/CD 的核心概念和实战操作。

## 文件说明

| 序号 | 文件 | 说明 |
|------|------|------|
| 1 | `1_cicd_concept.py` | 模拟 CI/CD 流水线：代码检查 → 测试 → 构建 → 部署，任意阶段失败则终止 |
| 2 | `2_github_actions.py` | 生成并解析 GitHub Actions Workflow YAML，讲解字段含义，模拟触发执行 |

## 配置文件

| 文件 | 说明 |
|------|------|
| `.github/workflows/ci.yml` | GitHub Actions 完整 Workflow 示例（push → 测试 → 构建 → 部署） |
| `deploy.sh` | 部署脚本示例：拉取代码、安装依赖、测试、构建镜像、启动服务、健康检查、回滚 |

## 运行方式

```bash
# 演示 1：CI/CD 流水线概念模拟
python "阶段6_工程化能力/05_CICD持续部署/demo/1_cicd_concept.py"

# 演示 2：GitHub Actions YAML 生成与解析
python "阶段6_工程化能力/05_CICD持续部署/demo/2_github_actions.py"
```

## 学习目标

- 理解 CI/CD 流水线的阶段划分和执行逻辑
- 掌握 GitHub Actions Workflow YAML 的结构和关键字段
- 了解 Secrets 管理和环境变量注入的安全实践
- 能够独立编写部署脚本和 CI/CD 配置文件
