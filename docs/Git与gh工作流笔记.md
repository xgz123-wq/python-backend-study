# Git 与 gh 工作流笔记

## 1. 这次实操的目标

用当前学习项目跑通一次完整代码管理流程：

```text
本地目录 → git 初始化 → 本地提交 → GitHub 创建远程仓库 → 推送 main
       → 新建日常开发分支 → 提交笔记 → 推送分支 → 创建 PR → 合并 PR
```

本次远程仓库：

```text
https://github.com/xgz123-wq/python-backend-study
```

## 2. git 和 gh 的分工

| 工具 | 负责什么 | 典型操作 |
|---|---|---|
| `git` | 本地版本历史 | `init`、`add`、`commit`、`branch`、`checkout`、`push`、`pull` |
| `gh` | GitHub 平台协作 | 创建仓库、创建 PR、查看 PR、合并 PR、查看 Issue |

一句话：

```text
git 管代码版本；gh 管 GitHub 上的仓库和协作流程。
```

## 3. 本次项目初始化流程

当前项目目录：

```text
D:\AGI大模型\python后端_claude
```

### 3.1 初始化本地仓库

```bash
git init -b main
```

结果：当前目录生成 `.git/`，项目开始被 git 管理。

### 3.2 配置本地排除项

本项目里有本地工具目录：

```text
.codegraph/
.claude/
```

这些是本机工具状态，不适合提交到 GitHub。因为当前约束是不修改 `.gitignore`，所以使用本地专用排除文件：

```bash
printf '\n# Local tool state\n.codegraph/\n.claude/\n' >> .git/info/exclude
```

区别：

| 文件 | 是否提交 | 作用范围 |
|---|---:|---|
| `.gitignore` | 会提交 | 团队共享忽略规则 |
| `.git/info/exclude` | 不会提交 | 只影响当前电脑 |

## 4. 本次首次提交的范围

本次首次提交不是 `git add .`，而是只提交：

```text
README.md
阶段1_Python基础/
阶段2_后端前置知识/
阶段3_中间件技术/
阶段4_FastAPI框架/
阶段5_项目实战/
阶段6_工程化能力/
```

对应命令：

```bash
git add README.md \
  "阶段1_Python基础" \
  "阶段2_后端前置知识" \
  "阶段3_中间件技术" \
  "阶段4_FastAPI框架" \
  "阶段5_项目实战" \
  "阶段6_工程化能力"

git commit -m "chore: 初始化学习阶段内容"
```

本次实际结果：

```text
首次 commit：c09cbad
已跟踪文件数：288
```

首次提交后仍未纳入 git 的文件包括：

```text
.gitignore
.vscode/
AGENTS.md
CHANGELOG.md
CLAUDE.md
CONTRIBUTING.md
LICENSE
docs/
```

说明：

```text
这些文件不是丢失，只是暂时没有被提交。以后需要时可以单独 add + commit。
```

## 5. 用 gh 创建 GitHub 远程仓库

执行命令：

```bash
gh repo create python-backend-study --public --source=. --remote=origin --push
```

参数含义：

| 参数 | 含义 |
|---|---|
| `python-backend-study` | GitHub 仓库名 |
| `--public` | 创建公开仓库 |
| `--source=.` | 当前目录就是本地仓库 |
| `--remote=origin` | 把远程仓库命名为 `origin` |
| `--push` | 创建后立刻推送当前分支 |

本次实际远程地址：

```text
https://github.com/xgz123-wq/python-backend-study.git
```

执行成功后，`main` 会跟踪远程分支：

```text
main → origin/main
```

## 6. 日常开发推荐流程

不要长期直接在 `main` 上开发。推荐流程：

```text
main 拉最新 → 新建功能分支 → 修改文件 → add → commit → push 分支 → 开 PR → 合并 → 回到 main 拉最新
```

对应命令模板：

```bash
# 1. 回到 main
git checkout main

# 2. 拉取远程最新代码
git pull

# 3. 新建功能分支
git checkout -b docs/add-git-workflow-notes

# 4. 修改文件后查看状态
git status

# 5. 暂存指定文件
git add "docs/Git与gh工作流笔记.md"

# 6. 本地提交
git commit -m "docs: 新增 git 与 gh 全流程实操笔记"

# 7. 推送分支
git push -u origin docs/add-git-workflow-notes

# 8. 创建 PR
gh pr create \
  --title "docs: 新增 git 与 gh 全流程实操笔记" \
  --body "跑通 git 初始化、远程创建、推送、分支、PR、合并全流程的实操记录"

# 9. 合并 PR，并删除远程分支
gh pr merge --squash --delete-branch

# 10. 回到 main 并同步
git checkout main
git pull
```

## 7. 常用命令速查

### 7.1 git 常用命令

| 命令 | 作用 |
|---|---|
| `git status` | 查看当前有哪些文件改动 |
| `git add <file>` | 把文件加入暂存区 |
| `git commit -m "message"` | 生成一个本地版本快照 |
| `git log --oneline` | 查看提交历史 |
| `git branch` | 查看分支 |
| `git checkout -b <branch>` | 新建并切换分支 |
| `git checkout main` | 切回 main 分支 |
| `git push` | 把本地提交推到远程 |
| `git pull` | 拉取远程最新提交 |
| `git remote -v` | 查看远程仓库地址 |

### 7.2 gh 常用命令

| 命令 | 作用 |
|---|---|
| `gh auth status` | 查看 GitHub 登录状态 |
| `gh repo create` | 创建 GitHub 仓库 |
| `gh repo view --web` | 在浏览器打开当前仓库 |
| `gh pr create` | 创建 Pull Request |
| `gh pr list` | 查看 PR 列表 |
| `gh pr view` | 查看当前 PR |
| `gh pr merge` | 合并 PR |

## 8. 关键概念

| 概念 | 操作级定义 |
|---|---|
| `main` | 主分支，保存稳定版本 |
| `origin` | 默认远程仓库别名 |
| `commit` | 一次本地版本快照 |
| `push` | 把本地 commit 上传到 GitHub |
| `pull` | 把 GitHub 上的新 commit 拉到本地 |
| `branch` | 分支，用于隔离不同任务 |
| `PR` | Pull Request，请求把一个分支合并进另一个分支 |
| `squash merge` | 合并 PR 时把多个 commit 压成一个 commit |

## 9. 推荐提交信息格式

格式：

```text
类型: 简短说明
```

常见类型：

| 类型 | 适用场景 |
|---|---|
| `docs:` | 文档变化 |
| `feat:` | 新功能 |
| `fix:` | 修 bug |
| `chore:` | 项目维护、初始化、配置类任务 |
| `refactor:` | 重构，不改变功能 |

示例：

```bash
git commit -m "docs: 新增 Git 工作流笔记"
git commit -m "feat: 新增 FastAPI 路由演示"
git commit -m "fix: 修正 Redis 示例连接参数"
```

## 10. 避坑清单

| 场景 | 建议 |
|---|---|
| 不确定要提交哪些文件 | 先 `git status`，再 `git add 指定文件`，不要无脑 `git add .` |
| 本地工具目录 | 放进 `.git/info/exclude` 或 `.gitignore` |
| 敏感信息 | `.env`、密钥、token 不提交 |
| 主分支开发 | 尽量避免，使用功能分支 + PR |
| 强制推送 | 不使用 `git push --force`，容易覆盖远程历史 |
| 大量文件第一次提交 | 先确认范围，再 commit |

## 11. 本项目之后怎么继续

如果继续学习并新增一章，推荐这样做：

```bash
git checkout main
git pull
git checkout -b docs/add-new-chapter

# 写理论文档和 demo 脚本

git status
git add "阶段X_目录/具体文件.md" "阶段X_目录/demo/具体脚本.py"
git commit -m "docs: 新增 XXX 章节学习内容"
git push -u origin docs/add-new-chapter
gh pr create --title "docs: 新增 XXX 章节学习内容" --body "说明本次新增的知识点和 demo"
```

合并后：

```bash
gh pr merge --squash --delete-branch
git checkout main
git pull
```
