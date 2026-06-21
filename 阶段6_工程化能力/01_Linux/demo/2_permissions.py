"""
Demo 2: 权限与用户管理 - 用 Python 操作文件权限
对应理论文档: 2.权限与用户管理.md

本 Demo 用 Python 的 os 模块和 stat 模块演示 Linux 权限的核心概念：
- 查看和修改文件权限（chmod 的 Python 等效操作）
- 权限的数字表示法（755、644 等的计算原理）
- 获取当前用户信息
- os.stat 获取文件详细元信息

注意: 文件权限操作在 Windows 上有限制，本 Demo 会尽量演示可运行的部分，
      并在 Linux 特有功能处给出说明。
"""

import os
import sys
import stat
import platform
import tempfile
import getpass
# grp 和 pwd 是 Linux 专有模块，Windows 上不存在
# 使用 try/except 实现跨平台兼容
try:
    import grp as grp_module
    HAS_GRP = True
except ImportError:
    grp_module = None
    HAS_GRP = False

try:
    import pwd as pwd_module
    HAS_PWD = True
except ImportError:
    pwd_module = None
    HAS_PWD = False

# ============================================================
# 工具函数
# ============================================================

def print_section(title):
    """打印分隔线和标题"""
    print(f"\n{'=' * 60}")
    print(f"  {title}")
    print(f"{'=' * 60}")


# 检测操作系统
IS_LINUX = platform.system() == "Linux"
IS_WINDOWS = platform.system() == "Windows"

# 创建临时工作目录
work_dir = tempfile.mkdtemp(prefix="perm_demo_")
print(f"临时工作目录: {work_dir}")


# ============================================================
# 第一部分：权限数字表示法详解
# ============================================================

print_section("第一部分：权限数字表示法详解")

def permission_to_octal(perm_bits):
    """
    将 stat 权限位转换为八进制数字表示（如 755、644）。

    参数:
        perm_bits: os.stat().st_mode 的值

    返回:
        三位八进制数字，如 755
    """
    # 提取 owner/group/other 的 rwx 位
    owner = ((perm_bits & stat.S_IRUSR) >> 6) | \
            ((perm_bits & stat.S_IWUSR) >> 5) | \
            ((perm_bits & stat.S_IXUSR) >> 4)
    group = ((perm_bits & stat.S_IRGRP) >> 3) | \
            ((perm_bits & stat.S_IWGRP) >> 2) | \
            ((perm_bits & stat.S_IXGRP) >> 1)
    other = (perm_bits & stat.S_IROTH) | \
            ((perm_bits & stat.S_IWOTH) << 1) | \
            ((perm_bits & stat.S_IXOTH) << 2)

    # 更简洁的方式：直接用八进制
    owner = (perm_bits >> 6) & 0o7
    group = (perm_bits >> 3) & 0o7
    other = perm_bits & 0o7

    return owner, group, other


def octal_to_rwx(octal_digit):
    """
    将单个八进制数字转换为 rwx 字符串。

    例如:
        7 -> 'rwx'
        5 -> 'r-x'
        4 -> 'r--'
        0 -> '---'
    """
    r = 'r' if octal_digit & 4 else '-'
    w = 'w' if octal_digit & 2 else '-'
    x = 'x' if octal_digit & 1 else '-'
    return f"{r}{w}{x}"


def mode_to_string(mode):
    """
    将 st_mode 转换为类似 ls -l 的权限字符串。

    例如: '-rwxr-xr-x'
    """
    # 文件类型
    if stat.S_ISDIR(mode):
        ftype = 'd'
    elif stat.S_ISLNK(mode):
        ftype = 'l'
    else:
        ftype = '-'

    owner, group, other = permission_to_octal(mode)
    return ftype + octal_to_rwx(owner) + octal_to_rwx(group) + octal_to_rwx(other)


# 演示数字表示法的计算过程
print("""
权限数字表示法原理:
  r = 4 (读)    w = 2 (写)    x = 1 (执行)    - = 0 (无权限)

  每组权限 = r + w + x 的和

  例如 755:
    owner: r(4) + w(2) + x(1) = 7  → rwx
    group: r(4) + -(0) + x(1) = 5  → r-x
    other: r(4) + -(0) + x(1) = 5  → r-x
    结果: rwxr-xr-x
""")

# 常见权限对照表
print("常见权限速查表:")
print(f"{'数字':<8}{'rwx 表示':<14}{'含义':<30}{'典型用途'}")
print("-" * 75)
common_perms = [
    (755, "rwxr-xr-x", "所有者全部权限，其他人只读+执行", "目录、可执行脚本"),
    (644, "rw-r--r--", "所有者读写，其他人只读", "普通文件"),
    (700, "rwx------", "仅所有者有全部权限", "私密目录（如 .ssh/）"),
    (600, "rw-------", "仅所有者可读写", "SSH 私钥、敏感配置"),
    (777, "rwxrwxrwx", "所有人全部权限", "⚠️ 极其危险，禁止在生产使用"),
]
for num, rwx, desc, usage in common_perms:
    print(f"  {num:<6}{rwx:<14}{desc:<30}{usage}")


# ============================================================
# 第二部分：用 Python 查看文件权限
# ============================================================

print_section("第二部分：用 Python 查看文件权限")

# 创建测试文件
test_files = {
    "public.txt": 0o644,      # rw-r--r--
    "script.sh": 0o755,       # rwxr-xr-x
    "secret.key": 0o600,      # rw-------
    "config.ini": 0o640,      # rw-r-----
}

print("\n创建测试文件并设置权限:")
for fname, perm in test_files.items():
    filepath = os.path.join(work_dir, fname)
    # 创建文件
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(f"# {fname} - 权限应为 {oct(perm)}\n")

    # 设置权限（Linux 上完整支持，Windows 上部分支持）
    if IS_LINUX:
        os.chmod(filepath, perm)

    # 读取文件信息
    file_stat = os.stat(filepath)
    mode = file_stat.st_mode
    perm_str = mode_to_string(mode)

    # 获取八进制权限数字
    owner, group, other = permission_to_octal(mode)
    octal_perm = f"{owner}{group}{other}"

    print(f"\n  文件: {fname}")
    print(f"    权限字符串: {perm_str}")
    print(f"    八进制数字: {octal_perm}")
    print(f"    文件大小:   {file_stat.st_size} bytes")

    if IS_LINUX:
        # 在 Linux 上可以获取更多信息
        print(f"    st_mode 原始值: {oct(file_stat.st_mode)}")
        print(f"    inode 编号:     {file_stat.st_ino}")
        print(f"    硬链接数:       {file_stat.st_nlink}")


# ============================================================
# 第三部分：用 Python 修改文件权限（chmod）
# ============================================================

print_section("第三部分：用 Python 修改文件权限 (chmod)")

if IS_LINUX:
    demo_file = os.path.join(work_dir, "demo_chmod.txt")
    with open(demo_file, 'w', encoding='utf-8') as f:
        f.write("chmod demo\n")

    # 查看初始权限
    initial_mode = os.stat(demo_file).st_mode
    print(f"  初始权限: {mode_to_string(initial_mode)}")

    # 使用数字模式修改（等价于 chmod 755）
    os.chmod(demo_file, 0o755)
    new_mode = os.stat(demo_file).st_mode
    print(f"  chmod 755 后: {mode_to_string(new_mode)}")

    # 等价于 chmod 644
    os.chmod(demo_file, 0o644)
    new_mode = os.stat(demo_file).st_mode
    print(f"  chmod 644 后: {mode_to_string(new_mode)}")

    # 等价于 chmod 600
    os.chmod(demo_file, 0o600)
    new_mode = os.stat(demo_file).st_mode
    print(f"  chmod 600 后: {mode_to_string(new_mode)}")

    # 使用 stat 模块的常量（等价于符号模式）
    # 等价于 chmod u+x（给 owner 添加执行权限）
    current_mode = os.stat(demo_file).st_mode
    os.chmod(demo_file, current_mode | stat.S_IXUSR)
    new_mode = os.stat(demo_file).st_mode
    print(f"  chmod u+x 后: {mode_to_string(new_mode)}")

    # 等价于 chmod o-r（移除 other 的读权限）
    current_mode = os.stat(demo_file).st_mode
    os.chmod(demo_file, current_mode & ~stat.S_IROTH)
    new_mode = os.stat(demo_file).st_mode
    print(f"  chmod o-r 后: {mode_to_string(new_mode)}")

    print("\n  位运算说明:")
    print("    | (OR)  = 添加权限位   例: mode | stat.S_IXUSR  添加 owner 执行权限")
    print("    & ~ (AND NOT) = 移除权限位  例: mode & ~stat.S_IROTH  移除 other 读权限")
else:
    print("""
  [Windows 环境说明]

  Windows 不使用 Linux 的 rwx 权限模型，os.chmod() 功能有限。
  在 Windows 上 os.chmod() 只能设置：
    - stat.S_IREAD  (只读)
    - stat.S_IWRITE (可写)

  演示:
""")
    demo_file = os.path.join(work_dir, "demo_chmod.txt")
    with open(demo_file, 'w', encoding='utf-8') as f:
        f.write("chmod demo (Windows)\n")

    # Windows 上设置只读
    os.chmod(demo_file, stat.S_IREAD)
    print(f"  设置只读后: 可写={os.access(demo_file, os.W_OK)}")

    # Windows 上设置可写
    os.chmod(demo_file, stat.S_IREAD | stat.S_IWRITE)
    print(f"  设置可写后: 可写={os.access(demo_file, os.W_OK)}")

    print("\n  [提示] 要体验完整的 Linux 权限操作，请使用 WSL 或 Linux 虚拟机。")


# ============================================================
# 第四部分：当前用户信息
# ============================================================

print_section("第四部分：当前用户信息")

# 跨平台获取用户名
username = getpass.getuser()
print(f"  当前用户名: {username}")

if IS_LINUX:
    # Linux 上可以获取详细的用户信息
    try:
        user_info = pwd_module.getpwnam(username)
        print(f"  UID:        {user_info.pw_uid}")
        print(f"  GID:        {user_info.pw_gid}")
        print(f"  家目录:     {user_info.pw_dir}")
        print(f"  默认 Shell: {user_info.pw_shell}")
        print(f"  描述信息:   {user_info.pw_gecos}")
    except (KeyError, AttributeError):
        print("  无法获取详细用户信息")

    # 获取用户所属的组
    try:
        user_id = os.getuid()
        group_ids = os.getgroups()
        print(f"\n  用户所属的组:")
        for gid in group_ids:
            try:
                group_info = grp_module.getgrgid(gid)
                print(f"    GID {gid}: {group_info.gr_name}")
            except KeyError:
                print(f"    GID {gid}: (未知组)")
    except AttributeError:
        print("  无法获取组信息")
else:
    print(f"\n  [Windows] 用户信息:")
    print(f"  用户名: {os.getlogin()}")
    print(f"  UID 等价: (Windows 不使用 UID/GID)")

# 获取进程相关 ID
print(f"\n  当前进程 PID: {os.getpid()}")
if IS_LINUX:
    print(f"  父进程 PPID:  {os.getppid()}")
    print(f"  用户 ID (UID):  {os.getuid()}")
    print(f"  组 ID (GID):  {os.getgid()}")
    print(f"  有效 UID:      {os.geteuid()}")
    print(f"  有效 GID:      {os.getegid()}")


# ============================================================
# 第五部分：os.stat 文件详细信息
# ============================================================

print_section("第五部分：os.stat 获取文件详细信息")

# 使用当前 Python 脚本自身作为演示文件
script_path = os.path.abspath(__file__)
file_stat = os.stat(script_path)

import time

print(f"  文件路径: {script_path}")
print(f"\n  os.stat() 返回的所有信息:")
print(f"  {'字段':<20}{'值':<30}{'说明'}")
print(f"  {'-'*70}")

stat_fields = [
    ('st_mode',   file_stat.st_mode,                    '文件类型和权限'),
    ('st_ino',    file_stat.st_ino,                     'inode 编号'),
    ('st_dev',    file_stat.st_dev,                     '设备编号'),
    ('st_nlink',  file_stat.st_nlink,                   '硬链接数'),
    ('st_uid',    file_stat.st_uid,                     '所有者 UID'),
    ('st_gid',    file_stat.st_gid,                     '所属组 GID'),
    ('st_size',   file_stat.st_size,                    '文件大小（字节）'),
    ('st_atime',  time.ctime(file_stat.st_atime),       '最后访问时间'),
    ('st_mtime',  time.ctime(file_stat.st_mtime),       '最后修改时间'),
    ('st_ctime',  time.ctime(file_stat.st_ctime),       '状态变更时间'),
]

for field, value, desc in stat_fields:
    print(f"  {field:<20}{str(value):<30}{desc}")

# 权限字符串
print(f"\n  权限字符串: {mode_to_string(file_stat.st_mode)}")

# 文件大小的人类可读格式
size = file_stat.st_size
for unit in ['B', 'KB', 'MB', 'GB']:
    if size < 1024:
        print(f"  文件大小:   {size:.1f} {unit}")
        break
    size /= 1024

# 检查各种文件属性
print(f"\n  文件属性检查:")
print(f"  是普通文件?   {stat.S_ISREG(file_stat.st_mode)}")
print(f"  是目录?       {stat.S_ISDIR(file_stat.st_mode)}")
print(f"  是符号链接?   {stat.S_ISLNK(file_stat.st_mode)}")

# os.access 检查权限
print(f"\n  权限检查 (os.access):")
print(f"  可读?  {os.access(script_path, os.R_OK)}")
print(f"  可写?  {os.access(script_path, os.W_OK)}")
print(f"  可执行? {os.access(script_path, os.X_OK)}")


# ============================================================
# 第六部分：权限相关的实用工具函数
# ============================================================

print_section("第六部分：实用工具函数")

def check_ssh_key_permissions(ssh_dir="~/.ssh"):
    """
    检查 SSH 密钥文件权限是否正确（Linux 安全最佳实践）。

    SSH 对权限要求非常严格：
    - ~/.ssh 目录: 700
    - 私钥文件: 600
    - 公钥文件: 644
    - authorized_keys: 600
    """
    ssh_path = os.path.expanduser(ssh_dir)

    if not os.path.exists(ssh_path):
        print(f"  SSH 目录不存在: {ssh_path}")
        return

    print(f"  检查 SSH 目录权限: {ssh_path}")

    expected = {
        'dir': 0o700,
        'private_key': 0o600,
        'public_key': 0o644,
        'authorized_keys': 0o600,
    }

    dir_stat = os.stat(ssh_path)
    dir_perm = stat.S_IMODE(dir_stat.st_mode)
    dir_ok = dir_perm == expected['dir']
    print(f"    目录权限: {oct(dir_perm)} (期望 {oct(expected['dir'])}) {'✅' if dir_ok else '❌'}")

    for item in os.listdir(ssh_path):
        item_path = os.path.join(ssh_path, item)
        if not os.path.isfile(item_path):
            continue

        item_stat = os.stat(item_path)
        item_perm = stat.S_IMODE(item_stat.st_mode)

        if item == "authorized_keys":
            expect = expected['authorized_keys']
        elif item.endswith(".pub"):
            expect = expected['public_key']
        else:
            expect = expected['private_key']

        ok = item_perm == expect
        print(f"    {item}: {oct(item_perm)} (期望 {oct(expect)}) {'✅' if ok else '❌'}")


if IS_LINUX:
    check_ssh_key_permissions()
else:
    print("""
  [SSH 权限检查最佳实践]

  在 Linux 上，SSH 密钥文件的权限必须正确，否则 SSH 会拒绝使用：

  | 文件                | 正确权限 | 命令              |
  |---------------------|---------|-------------------|
  | ~/.ssh/             | 700     | chmod 700 ~/.ssh  |
  | ~/.ssh/id_rsa       | 600     | chmod 600 id_rsa  |
  | ~/.ssh/id_rsa.pub   | 644     | chmod 644 id_rsa.pub |
  | ~/.ssh/authorized_keys | 600  | chmod 600 authorized_keys |

  权限不对时 SSH 会报错:
  @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
  @         WARNING: UNPROTECTED PRIVATE KEY FILE!          @
  @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
""")


# ============================================================
# 清理
# ============================================================

print_section("清理")
import shutil
shutil.rmtree(work_dir, ignore_errors=True)
print(f"  已清理临时目录: {work_dir}")


print(f"\n{'=' * 60}")
print("Demo 2 完成！")
print(f"{'=' * 60}")
print("""
核心收获:
  1. 权限数字表示法: r=4, w=2, x=1，三组求和得到三位数（如 755, 644）
  2. os.stat() 可以获取文件的全部元信息（权限、大小、时间等）
  3. os.chmod() 修改权限，支持数字模式和 stat 常量位运算
  4. os.access() 检查当前进程是否有权限读/写/执行某个文件
  5. SSH 密钥权限必须严格遵守（600/700），否则 SSH 会拒绝工作
""")
