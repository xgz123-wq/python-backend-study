# Git 与 gh 工作流速查笔记

> 目标：记录本项目如何用 Git 管本地版本，用 gh 管 GitHub 仓库和 PR。

---

## 1. 工具分工

| 工具 | 负责什么 | 常用命令 |
|---|---|---|
| `git` | 本地版本管理 | `add` / `commit` / `push` / `pull` / `branch` |
| `gh` | GitHub 平台操作 | `repo create` / `pr create` / `pr merge` |

一句话：

```text
git 管代码历史，gh 管 GitHub 协作。
```

---

## 2. 本项目当前状态

| 项目 | 内容 |
|---|---|
| 远程仓库 | `https://github.com/xgz123-wq/python-backend-study` |
| 默认分支 | `main` |
| 仓库类型 | Public |
| 当前用途 | Python 后端学习仓库 |
| 首次提交 | `c09cbad chore: 初始化学习阶段内容` |
| PR 演示 | `#1 docs: 新增 git 与 gh 全流程实操笔记` |

---

## 3. 第一次初始化流程

### 3.1 初始化本地仓库

```bash
git init -b main
```

### 3.2 排除本地工具目录

不改 `.gitignore` 时，可以写入本机专用排除文件：

```bash
printf '\n# Local tool state\n.codegraph/\n.claude/\n' >> .git/info/exclude
```

| 文件 | 是否提交 | 作用 |
|---|---:|---|
| `.gitignore` | 会提交 | 团队共享忽略规则 |
| `.git/info/exclude` | 不提交 | 只影响当前电脑 |

### 3.3 首次提交范围

本项目第一次只提交：

```text
README.md
阶段1_Python基础/
阶段2_后端前置知识/
阶段3_中间件技术/
阶段4_FastAPI框架/
阶段5_项目实战/
阶段6_工程化能力/
```

命令：

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

### 3.4 创建 GitHub 仓库并推送

```bash
gh repo create python-backend-study --public --source=. --remote=origin --push
```

参数说明：

| 参数 | 含义 |
|---|---|
| `--public` | 创建公开仓库 |
| `--source=.` | 当前目录作为本地仓库 |
| `--remote=origin` | 远程仓库别名叫 `origin` |
| `--push` | 创建后立刻推送 |

---

## 4. 日常开发流程

推荐不要直接在 `main` 上改。

```text
main 拉最新 → 新建分支 → 修改文件 → commit → push → PR → merge
```

命令模板：

```bash
git checkout main
git pull

git checkout -b docs/add-new-chapter

# 修改文件后
git status
git add "具体文件路径"
git commit -m "docs: 新增 XXX 内容"
git push -u origin docs/add-new-chapter
```

---

## 5. PR 流程

### 5.1 创建 PR

```bash
gh pr create \
  --title "docs: 新增 XXX 内容" \
  --body "说明本次改了什么、为什么改、如何验证"
```

### 5.2 查看 PR

```bash
gh pr list
gh pr view
```

### 5.3 合并 PR

```bash
gh pr merge --squash --delete-branch
```

含义：

| 参数 | 作用 |
|---|---|
| `--squash` | 多个 commit 压成一个再合并 |
| `--delete-branch` | 合并后删除远程分支 |

### 5.4 合并后同步本地

```bash
git checkout main
git pull
```

---

## 6. 常用命令

### git

| 命令 | 作用 |
|---|---|
| `git status` | 看当前改了什么 |
| `git add <file>` | 暂存指定文件 |
| `git commit -m "..."` | 本地提交 |
| `git log --oneline` | 看提交历史 |
| `git branch` | 看分支 |
| `git checkout -b <branch>` | 新建并切换分支 |
| `git push` | 推送到远程 |
| `git pull` | 拉取远程更新 |
| `git remote -v` | 看远程地址 |

### gh

| 命令 | 作用 |
|---|---|
| `gh auth status` | 查看登录状态 |
| `gh repo create` | 创建 GitHub 仓库 |
| `gh repo view --web` | 浏览器打开仓库 |
| `gh pr create` | 创建 PR |
| `gh pr list` | 查看 PR 列表 |
| `gh pr merge` | 合并 PR |

---

## 7. Commit 信息建议

格式：

```text
类型: 简短说明
```

常用类型：

| 类型 | 场景 |
|---|---|
| `docs:` | 文档 |
| `demo:` | Demo 示例 |
| `fix:` | 修复错误 |
| `chore:` | 项目维护 |
| `refactor:` | 重构 |

示例：

```bash
git commit -m "docs: 完善 README"
git commit -m "demo: 新增 Redis 缓存示例"
git commit -m "fix: 修正 MySQL 命令说明"
```

---

## 8. 本项目下一步提交建议

当前建议走轻量开源学习仓库方案。

优先提交：

```text
README.md
.gitignore
LICENSE
docs/Git与gh工作流笔记.md
```

命令：

```bash
git add README.md .gitignore LICENSE "docs/Git与gh工作流笔记.md"
git commit -m "docs: 完善项目 README 与基础说明"
git push
```

暂缓提交，先审查：

```text
AGENTS.md
CLAUDE.md
.vscode/
docs/ai-coding-tutorial/
docs/项目对照笔记/
```

可选提交：

```text
CONTRIBUTING.md
CHANGELOG.md
```

如果只是个人学习展示，它们不是必须。

---

## 9. 开源与 MIT 简短说明

MIT 不是流程，只是授权声明。

```text
别人可以使用、复制、修改、分发、商用；
但要保留版权和许可证；
代码出问题，作者默认不负责。
```

个人学习仓库最小维护：

```text
README.md + LICENSE + .gitignore
```

---

## 10. 避坑清单

| 场景 | 建议 |
|---|---|
| 不确定提交什么 | 先 `git status` |
| 文件很多 | 用 `git add 指定文件`，少用 `git add .` |
| 有 `.env` / token | 不提交 |
| 有本地工具目录 | 放 `.git/info/exclude` 或 `.gitignore` |
| 想回退或强推 | 不要随便用 `reset --hard` / `push --force` |
| 改完文档 | 单独 commit，别混入无关文件 |

---

## 11. 一句话工作流

```text
改文件 → git status → git add 指定文件 → git commit → git push → gh pr create → gh pr merge
```
