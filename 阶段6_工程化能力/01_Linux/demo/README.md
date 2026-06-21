# Linux 基础 - Demo 学习指南

## 运行环境说明

本章节 Demo 使用 Python 编写，通过 `subprocess`、`os` 等模块演示 Linux 核心概念。
所有 Demo 均可在 **Windows** 上运行（对 Linux 特有功能做了跨平台兼容处理），但建议配合 Linux 虚拟机或 WSL 学习效果更佳。

**运行方式**：

```bash
# 在 demo 目录下依次运行
python 1_basic_commands.py
python 2_permissions.py
python 3_process_management.py
python 4_network_text.py
```

**前置依赖**：无额外依赖，全部使用 Python 标准库。

---

## 学习顺序

按编号顺序依次学习，每个 Demo 对应一个理论知识点。

---

### Demo 1: Linux 基础命令（用 Python 模拟 Shell 操作）
**文件**: `1_basic_commands.py`

通过 Python 的 `subprocess` 模块执行 Shell 命令，演示文件操作（创建/复制/移动/删除）、管道和重定向的 Python 等效操作、文件系统遍历。理解 Python 如何与操作系统交互，这在后端开发中非常常见（如自动化运维脚本）。

**运行方式**: `python 1_basic_commands.py`
**前置依赖**: 无额外依赖

---

### Demo 2: 权限与用户管理（用 Python 操作文件权限）
**文件**: `2_permissions.py`

用 Python `os` 模块查看和修改文件权限，模拟 `chmod` 数字表示法（755、644 等），展示当前用户信息，演示 `os.stat` 获取文件详细信息。理解权限的底层机制。

**运行方式**: `python 2_permissions.py`
**前置依赖**: 无额外依赖

---

### Demo 3: 进程管理（用 Python 管理进程）
**文件**: `3_process_management.py`

用 `subprocess` 启动子进程、获取当前进程 PID、列出系统进程、模拟 `nohup` 后台运行、演示进程信号概念（SIGTERM、SIGKILL）。这是编写守护进程和后台任务的基础。

**运行方式**: `python 3_process_management.py`
**前置依赖**: 无额外依赖

---

### Demo 4: 网络与文本处理（用 Python 实现 Linux 工具）
**文件**: `4_network_text.py`

用 Python 实现类似 `curl` 的 HTTP 请求、用 `socket` 检查端口连通性、用 `re` 模块模拟 `grep` 功能、编写简单日志分析脚本、展示 Shell 脚本的 Python 等效实现。后端开发者日常最常用的技能组合。

**运行方式**: `python 4_network_text.py`
**前置依赖**: 无额外依赖

---

## 对应理论文档

| Demo | 文件 | 对应理论文档 |
|------|------|-------------|
| Demo 1 | `1_basic_commands.py` | `../1.Linux基础命令.md` |
| Demo 2 | `2_permissions.py` | `../2.权限与用户管理.md` |
| Demo 3 | `3_process_management.py` | `../3.进程管理.md` |
| Demo 4 | `4_network_text.py` | `../4.网络与文本处理.md` |

---

## 核心要点

1. **`subprocess` 是 Python 与 Shell 交互的桥梁**：后端自动化脚本、CI/CD 管道中大量使用
2. **权限数字表示法**（755、644 等）：每位是 rwx 的和（r=4, w=2, x=1），部署时必须正确设置
3. **进程管理是运维基础**：PID、信号、后台运行、systemd 服务配置
4. **文本处理三剑客**（grep、sed、awk）的 Python 等效：`re` 模块 + 字符串操作可以实现更灵活的文本处理
5. **跨平台兼容**：Demo 中使用 `platform` 和 `os.name` 判断操作系统，对 Linux 特有功能做降级处理

---

## 常见问题

| 问题 | 解决方案 |
|------|----------|
| Windows 上某些命令不可用 | Demo 已做跨平台处理，会自动跳过 Linux 特有命令并打印说明 |
| `subprocess` 输出乱码 | Windows 终端编码问题，Demo 中使用 `encoding='utf-8'` 解决 |
| `PermissionError` | 某些权限操作需要管理员身份运行 |
| 想实际体验 Linux 命令 | 安装 WSL（Windows Subsystem for Linux）或使用虚拟机 |
| `ModuleNotFoundError` | 所有 Demo 仅使用标准库，无需安装额外包 |
