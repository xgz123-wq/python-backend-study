# 虚拟环境与包管理 - Demo 学习指南

## 学习顺序

本章建议按编号顺序学习：先理解虚拟环境的作用，再掌握 pip 的核心操作，然后学习 requirements.txt 的规范写法，最后了解现代工具 Poetry/PDM。

> ⚠️ **特别说明**：虚拟环境本身需要在命令行中创建和激活，Demo 文件演示的是用 Python 代码"观察"环境状态的方式。完整的 shell 操作命令在各 Demo 文件末尾和理论文档中均有列出。

---

### Demo 1: venv 虚拟环境（检测与环境信息）
**文件**: `1_venv.py`

演示如何用代码检测当前是否处于虚拟环境中、查看虚拟环境的路径结构和模块搜索路径，以及后端项目启动时做环境检查的最佳实践写法。

**运行方式**: `python 1_venv.py`
**前置依赖**: 无额外依赖
**测试方式**: 分别在激活虚拟环境前后运行，对比"是否在虚拟环境中"的输出

---

### Demo 2: pip 依赖管理（查询与检查）
**文件**: `2_pip.py`

演示如何用 `importlib.metadata` 查询已安装包、检查指定包是否安装及其版本，以及后端项目启动前做依赖检查的代码写法。

**运行方式**: `python 2_pip.py`
**前置依赖**: 无额外依赖
**测试方式**: 观察"依赖检查"部分的输出，对比当前环境是否有 fastapi/pydantic 等包

---

### Demo 3: requirements.txt 规范（解析与生成）
**文件**: `3_requirements.py`

演示如何解析 requirements.txt 文件、对比文件内容与当前环境的差异，以及生成规范的 requirements.txt 示例（包含注释、分组、精确版本号）。

**运行方式**: `python 3_requirements.py`
**前置依赖**: 无额外依赖
**测试方式**: 首次运行会生成 `demo/requirements.txt` 示例文件，查看文件内容

---

### Demo 4: Poetry / PDM（概念对比与命令速查）
**文件**: `4_poetry_pdm.py`

通过对比表格和示例文件格式，理解 Poetry/PDM 相比 pip+requirements.txt 的优势；展示 pyproject.toml 和 poetry.lock 的格式；并提供工具选型建议。

**运行方式**: `python 4_poetry_pdm.py`
**前置依赖**: 无额外依赖（不需要安装 Poetry）
**测试方式**: 观察对比表格和 pyproject.toml 格式示例；如果系统已安装 Poetry，第五部分会显示版本信息

---

## 对应理论文档

| Demo | 文件 | 对应理论文档 | 关键概念 |
|------|------|-------------|---------|
| Demo 1 | `1_venv.py` | `../1.venv虚拟环境.md` | 沙盒隔离、sys.prefix、激活/退出 |
| Demo 2 | `2_pip.py` | `../2.pip依赖管理.md` | install/list/freeze、版本检查 |
| Demo 3 | `3_requirements.py` | `../3.requirements.txt规范.md` | 精确版本、分环境管理、Git 约定 |
| Demo 4 | `4_poetry_pdm.py` | `../4.了解Poetry与PDM.md` | pyproject.toml、lock file、选型建议 |

---

## 核心要点

1. **虚拟环境是强制要求**：任何 Python 项目都应在虚拟环境中开发，不要往全局 Python 装项目依赖。
2. **requirements.txt 精确版本**：用 `==` 锁定版本，保证团队和生产环境完全一致。
3. **三件套工作流**：`python -m venv .venv` → 激活 → `pip install -r requirements.txt`。
4. **不提交 .venv 目录**：在 `.gitignore` 中加入 `.venv/`，靠 requirements.txt 共享依赖信息。
5. **现代工具 Poetry/PDM**：自动管理 lock file，进入项目实战阶段再深入使用。

---

## 常见问题

| 问题 | 解决方案 |
|------|---------|
| PowerShell 无法运行 Activate.ps1 | 运行 `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned` |
| pip install 很慢 | `pip install 包名 -i https://pypi.tuna.tsinghua.edu.cn/simple` |
| 不知道自己在哪个环境 | `python -c "import sys; print(sys.prefix)"` |
| requirements.txt 装完有包冲突 | `pip install -r requirements.txt --use-pep517` 或逐包排查 |
| venv 目录不小心提交到 Git | 删除后在 .gitignore 加 `.venv/`，再 `git rm -r --cached .venv` |

---

## 完整的虚拟环境工作流（速查）

```bash
# 1. 创建
python -m venv .venv

# 2. 激活（Windows PowerShell）
.venv\Scripts\Activate.ps1

# 3. 安装依赖
pip install -r requirements.txt

# 4. 开发过程中添加新包
pip install new-package
pip freeze > requirements.txt   # 更新清单

# 5. 退出
deactivate
```
