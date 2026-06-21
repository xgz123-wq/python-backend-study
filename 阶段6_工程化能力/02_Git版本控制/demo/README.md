# demo 目录说明

本目录包含「Git 版本控制」章节的可运行演示脚本。

## 运行方式

每个脚本均为独立可执行的 Python 文件，直接在终端运行即可：

```bash
python demo/1_git_basics.py
python demo/2_branch_flow.py
```

> **前置要求**：系统已安装 Git 并可通过命令行调用（`git --version` 能正常输出版本号）。

## 脚本列表与运行顺序

| 序号 | 文件名 | 演示内容 | 对应理论文件 |
|------|--------|---------|-------------|
| 1 | `1_git_basics.py` | Git 基础操作：init、add、commit、log、diff、.gitignore | `1.Git基础操作.md` |
| 2 | `2_branch_flow.py` | 分支管理：branch、merge、冲突解决、rebase、Git Flow | `2.分支管理与Git_Flow.md` |

## 注意事项

- 每个脚本都会创建**临时目录**来演示 Git 操作，运行结束后会询问是否删除
- 脚本使用 `subprocess` 调用系统 Git 命令，不依赖任何第三方 Python 库
- 如果 Git 未安装或不在 PATH 中，脚本会给出安装提示并退出
- 所有输出均为中文，方便理解每一步在做什么
