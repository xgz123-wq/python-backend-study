# Python Backend Study

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.x-blue.svg)](https://www.python.org/)
[![Status](https://img.shields.io/badge/status-learning--in--progress-brightgreen.svg)](#学习进度)

一个面向实习、就业和 AI 应用开发的 Python 后端学习仓库。

本项目采用 **理论文档 + 可运行 Demo + 学习进度记录** 的方式，系统覆盖 Python 基础、后端前置知识、中间件、FastAPI、项目实战和工程化部署。

> 仓库定位：这是一个学习型开源仓库，不是生产环境应用程序。

---

## 项目目标

通过本仓库，逐步建立以下能力：

- 掌握 Python 后端开发所需的核心语法和工程习惯
- 理解 HTTP、RESTful API、认证授权等 Web 后端基础
- 熟悉 MySQL、Redis、ORM、消息队列等常见中间件
- 使用 FastAPI 构建可维护的后端服务
- 完成一个接近真实业务的后端项目实战
- 理解 Linux、Git、Docker、Nginx、CI/CD、部署和微服务等工程化能力
- 形成适合 AI 辅助学习和开发的文档化工作流

---

## 适合人群

| 人群 | 适合原因 |
|---|---|
| Python 初学者 | 从基础语法开始，配套独立可运行 Demo |
| 后端实习准备者 | 路线覆盖面试和实战常见知识点 |
| 想系统补后端基础的人 | 按阶段组织，不只学框架，也补网络、协议、中间件 |
| AI 应用开发学习者 | 后续可在 FastAPI 和项目实战阶段衔接 LLM 应用开发 |
| 想用 AI 辅助学习的人 | 仓库包含学习路线、学习方式、进度记录和代码管理笔记 |

---

## 学习路线

本项目按 6 个阶段推进：

| 阶段 | 目录 | 目标 |
|---|---|---|
| 阶段 1 | `阶段1_Python基础/` | 掌握 Python 核心语法、OOP、高级特性、文件操作、标准库和包管理 |
| 阶段 2 | `阶段2_后端前置知识/` | 理解网络、HTTP、RESTful API、认证与授权 |
| 阶段 3 | `阶段3_中间件技术/` | 学习 MySQL、Redis、Python ORM、消息队列 |
| 阶段 4 | `阶段4_FastAPI框架/` | 掌握 FastAPI 核心能力和后端接口开发方式 |
| 阶段 5 | `阶段5_项目实战/` | 完成一个电商网站 MVP 项目 |
| 阶段 6 | `阶段6_工程化能力/` | 学习 Linux、Git、Docker、Nginx、CI/CD、部署和微服务 |

详细路线见：[`docs/01_后端学习路线.md`](docs/01_后端学习路线.md)

---

## 学习进度

当前整体进度以 [`docs/03_学习进度.md`](docs/03_学习进度.md) 为准。

截至当前记录：

- 阶段 1：Python 基础 ✅ 已完成
- 阶段 2：后端前置知识 ✅ 已完成
- 阶段 3：中间件技术 🔄 学习中
- 阶段 4：FastAPI 框架 📌 已规划
- 阶段 5：项目实战 📌 已规划
- 阶段 6：工程化能力 📌 已规划 / 部分内容已补充

---

## 仓库结构

```text
python-backend-study/
├── README.md
├── LICENSE
├── CHANGELOG.md
├── CONTRIBUTING.md
├── docs/
│   ├── 01_后端学习路线.md
│   ├── 02_学习方式.md
│   ├── 03_学习进度.md
│   └── Git与gh工作流笔记.md
├── 阶段1_Python基础/
│   ├── 01_基础语法/
│   ├── 02_面向对象编程/
│   ├── 03_高级特性/
│   ├── 04_异常处理与文件操作/
│   ├── 05_常用标准库/
│   └── 06_虚拟环境与包管理/
├── 阶段2_后端前置知识/
│   ├── 01_计算机网络基础/
│   ├── 02_HTTP协议/
│   ├── 03_RESTful_API设计/
│   └── 04_认证与授权基础/
├── 阶段3_中间件技术/
│   ├── 01_MySQL/
│   ├── 02_Redis/
│   ├── 03_Python_ORM/
│   └── 04_消息队列/
├── 阶段4_FastAPI框架/
│   └── 01_FastAPI核心/
├── 阶段5_项目实战/
│   └── 项目1_电商网站_MVP/
└── 阶段6_工程化能力/
    ├── 00_部署概览/
    ├── 01_Linux/
    ├── 02_Git版本控制/
    ├── 03_Docker/
    ├── 04_Nginx/
    ├── 05_CICD持续部署/
    ├── 06_生产部署/
    └── 07_微服务/
```

每个章节通常包含：

```text
章节目录/
├── N.知识点.md        # 理论说明
└── demo/
    ├── README.md      # 本章 demo 运行顺序
    └── N_topic.py     # 可独立运行的演示脚本
```

部分中间件章节会使用 `.sql`、Docker 或服务端组件演示，具体以章节内 `demo/README.md` 为准。

---

## 快速开始

### 1. 克隆仓库

```bash
git clone https://github.com/xgz123-wq/python-backend-study.git
cd python-backend-study
```

### 2. 检查 Python 环境

```bash
python --version
```

建议使用 Python 3.x。大多数基础 Demo 只依赖标准库，可以直接运行。

### 3. 运行一个 Demo

```bash
python "阶段1_Python基础/01_基础语法/demo/1_variables_types.py"
```

### 4. 按章节顺序学习

每个章节的 `demo/README.md` 都记录了建议运行顺序。例如：

```text
阶段1_Python基础/01_基础语法/demo/README.md
```

推荐顺序：

```text
先读理论文档 → 再运行 demo → 修改 demo 做练习 → 更新学习进度
```

---

## 推荐学习方式

详细学习方式见：[`docs/02_学习方式.md`](docs/02_学习方式.md)

### 每章标准流程

1. 阅读本章理论文档
2. 按 `demo/README.md` 顺序运行示例脚本
3. 修改 Demo 参数或逻辑，观察输出变化
4. 总结核心概念、常见误区和实战场景
5. 更新 [`docs/03_学习进度.md`](docs/03_学习进度.md)

### AI 辅助学习启动口令

```text
读取 docs/01_后端学习路线.md, docs/02_学习方式.md, docs/03_学习进度.md，开始学习
```

---

## Git 与 GitHub 工作流

本仓库使用 Git + GitHub 管理学习内容。

推荐日常流程：

```bash
git checkout main
git pull
git checkout -b docs/add-new-chapter

# 编写或修改文档、demo

git status
git add "阶段X_目录/具体文件.md" "阶段X_目录/demo/具体脚本.py"
git commit -m "docs: 新增 XXX 章节学习内容"
git push -u origin docs/add-new-chapter
gh pr create --title "docs: 新增 XXX 章节学习内容" --body "说明本次新增内容"
```

更多说明见：[`docs/Git与gh工作流笔记.md`](docs/Git与gh工作流笔记.md)

---

## 文档维护建议

作为开源学习仓库，建议重点维护以下文档：

| 文件 | 作用 |
|---|---|
| `README.md` | 项目首页，说明项目目标、结构和使用方式 |
| `LICENSE` | 声明开源协议 |
| `.gitignore` | 避免提交缓存、虚拟环境、密钥和日志 |
| `CONTRIBUTING.md` | 说明贡献流程和提交规范 |
| `CHANGELOG.md` | 记录重要更新 |
| `docs/01_后端学习路线.md` | 维护完整学习路线 |
| `docs/02_学习方式.md` | 维护学习方法和章节流程 |
| `docs/03_学习进度.md` | 维护当前学习进展 |

---

## 贡献指南

欢迎通过 Issue 或 Pull Request 参与改进。

提交内容建议遵循：

- 一个 PR 只解决一个明确问题
- 文档和 Demo 尽量一一对应
- Demo 应保持独立可运行
- Commit message 使用语义化前缀，例如：

```text
docs: 新增 Git 工作流笔记
feat: 新增 FastAPI 路由演示
fix: 修正 Redis 示例说明
chore: 补充项目基础文档
```

详细说明见：[`CONTRIBUTING.md`](CONTRIBUTING.md)

---

## License

本项目采用 [MIT License](LICENSE) 开源。

这意味着你可以自由使用、复制、修改和分发本项目内容，包括商业使用；但需要保留原始版权声明和许可证文本。
