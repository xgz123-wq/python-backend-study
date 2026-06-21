# Python 后端学习路线仓库

一个面向实习与就业的 Python 后端学习项目，覆盖从基础语法到 FastAPI、中间件、项目实战与工程化部署。

## 项目简介

本仓库采用“文档 + 可运行 Demo + 进度记录”的学习方式，目标是帮助你建立完整的后端工程能力。

## 核心文档（使用指南）

请优先使用 `docs/` 目录中的三份核心文档：

1. 学习路线：`docs/01_后端学习路线.md`
- 用途：定义阶段目标、学习范围、时间线。
- 什么时候看：开始学习前、每周复盘时。

2. 学习方式：`docs/02_学习方式.md`
- 用途：定义每章的标准流程（理论、Demo、注释、进度更新）。
- 什么时候看：每次开始一个新章节前。

3. 学习进度：`docs/03_学习进度.md`
- 用途：记录已完成章节、核心理解、产出文件。
- 什么时候更新：每章完成后立即更新。

推荐启动口令（给 AI）：

```text
读取 docs/01_后端学习路线.md, docs/02_学习方式.md, docs/03_学习进度.md，开始学习
```

## 当前进度

当前已完成并落地内容：
- 阶段 1 / 第 01 章：基础语法（理论 + Demo）

其余阶段已定义目录规范，可按计划逐章补齐。

## 仓库结构

```text
python后端_claude/
├── README.md
├── docs/
│   ├── 01_后端学习路线.md
│   ├── 02_学习方式.md
│   └── 03_学习进度.md
├── 阶段1_Python基础/
│   └── 01_基础语法/
│       ├── 1.变量与数据类型.md
│       ├── 2.容器类型.md
│       ├── 3.条件判断与循环.md
│       ├── 4.函数.md
│       ├── 5.字符串格式化.md
│       └── demo/
│           ├── README.md
│           ├── 1_variables_types.py
│           ├── 2_containers.py
│           ├── 3_control_flow.py
│           ├── 4_functions.py
│           └── 5_string_format.py
├── CONTRIBUTING.md
├── CHANGELOG.md
├── LICENSE
└── .gitignore
```

## 快速开始

1. 克隆项目

```bash
git clone <your-repo-url>
cd python后端_claude
```

2. 运行阶段 1 Demo

```bash
python "阶段1_Python基础/01_基础语法/demo/1_variables_types.py"
python "阶段1_Python基础/01_基础语法/demo/2_containers.py"
python "阶段1_Python基础/01_基础语法/demo/3_control_flow.py"
python "阶段1_Python基础/01_基础语法/demo/4_functions.py"
python "阶段1_Python基础/01_基础语法/demo/5_string_format.py"
```

3.在你当前学习仓库里的最佳用法
你这个仓库是“章节 md + demo 脚本”，最适合双轨制：

md 继续当权威内容源
所有知识点、进度、理论说明都留在现有 md，不改工作流。
html 当学习消费层
每章自动生成一个 chapter-review.html，包含：
学习目标、关键图示、代码片段注释、常见误区、自测题、关联 demo 跳转。
用 html 做“高带宽复盘”
每周生成一页周报 HTML：学了什么、哪里卡住、错题分布、下周重点。
用 html 做“代码理解”
对每个 demo 生成 explain.html：
执行流程图、关键变量变化、易错点、建议练习。
保留“可验证轨道”
HTML 页面必须附：
原始证据区（引用 md 段落和脚本位置）、结论区、待确认区，避免“漂亮但不准”。
给你一套可直接用的提示词思路

章节学习页
“读取本章 md 与 demo，生成单文件 HTML 学习页：左侧目录，右侧正文，含目标-概念-示例-误区-自测五区块，移动端可读。”
代码讲解页
“读取 demo 脚本，生成 HTML 代码导读：按执行顺序分段，给每段输入输出示意和常见错误。”
周复盘页
“读取 03_学习进度.md 和本周新增文件，生成复盘 HTML：已完成、未掌握、下周计划、3 道针对性练习。”

## 贡献指南

欢迎贡献与共建，提交前请阅读：
- `CONTRIBUTING.md`
- `CHANGELOG.md`

## License

本项目采用 MIT License，详见 `LICENSE`。
