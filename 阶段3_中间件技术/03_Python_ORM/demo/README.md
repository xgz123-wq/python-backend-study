# Python ORM 章节 Demo 说明

## 学习顺序

| 顺序 | Demo 文件 | 对应理论文档 | 主要内容 |
|------|-----------|-------------|---------|
| 1 | `1_sqlalchemy_demo.py` | `1.SQLAlchemy核心用法.md` | 同步 ORM：Model 定义、CRUD、关联查询、事务 |
| 2 | `2_tortoise_orm_demo.py` | `2.Tortoise_ORM异步.md` | 异步 ORM：async CRUD、预加载、事务 |
| 3 | `3_alembic_demo.py` | `3.Alembic数据库迁移.md` | 迁移工作流：初始化、生成迁移、升级、回滚 |

---

## 环境准备

### Demo 1 & 2（使用 SQLite，无需 MySQL）

两个 Demo 默认使用 SQLite 文件数据库，**无需启动任何服务**，安装依赖后直接运行：

```bash
pip install -r requirements.txt
python 1_sqlalchemy_demo.py
python 2_tortoise_orm_demo.py
```

### 切换为 MySQL（可选）

如需使用 MySQL，先启动 Docker：

```bash
docker-compose up -d
# 等待 MySQL 就绪（约10秒）
docker-compose ps   # 确认 healthy

# 修改 Demo 文件中的 DATABASE_URL（注释 SQLite 行，取消注释 MySQL 行）
# SQLite:  sqlite:///./orm_demo.db
# MySQL:   mysql+pymysql://root:123456@localhost:3306/orm_demo
```

### Demo 3（Alembic 迁移）

```bash
# 先运行初始化脚本（建表 + 插入测试数据）
python 3_alembic_demo.py

# 按下方步骤操作 Alembic 命令行
```

---

## Demo 3 完整迁移操作步骤

```bash
# 步骤1：初始化 Alembic（在 demo/ 目录下执行）
alembic init alembic   # 已有 alembic/ 目录可跳过

# 步骤2：确认 alembic.ini 中数据库连接正确
# sqlalchemy.url = sqlite:///./alembic_demo.db

# 步骤3：确认 alembic/env.py 中 target_metadata 已设置（已配置好）

# 步骤4：生成初始迁移文件
alembic revision --autogenerate -m "initial tables"

# 步骤5：查看生成的文件
# alembic/versions/xxxx_initial_tables.py

# 步骤6：执行迁移（建表）
alembic upgrade head

# 步骤7：查看当前版本
alembic current

# 步骤8：模拟 Model 变更
# 在 3_alembic_demo.py 的 User 类中添加一行：
#   avatar: Mapped[str | None] = mapped_column(String(255), nullable=True)

# 步骤9：生成变更迁移文件
alembic revision --autogenerate -m "add avatar to users"

# 步骤10：执行变更
alembic upgrade head

# 步骤11：查看迁移历史
alembic history

# 步骤12：回滚演示
alembic downgrade -1      # 撤销最近一次（删除 avatar 列）
alembic upgrade head      # 重新执行

# 步骤13：完全回滚
alembic downgrade base    # 删除所有表
```

---

## 各 Demo 预期输出

### Demo 1（SQLAlchemy 同步）
```
【0. 建表】表已创建：users, posts
【1. Create 创建】创建用户: ['zhangsan', 'lisi', 'wangwu']
【2. Read 查询】按 ID 查询, 条件查询, 分页查询...
【3. 关联查询】用户 zhangsan 共 2 篇文章
【4. Update 更新】单条更新, 批量激活...
【5. Delete 删除】删除 wangwu（及其关联文章）
【6. 事务演示】事务回滚成功
```

### Demo 2（Tortoise ORM 异步）
```
【数据库初始化完成】
【1. Create 异步创建】...
【2. Read 异步查询】...
【3. 关联预加载】...
【4/5/6. Update/Delete/事务】...
```

---

## 停止 MySQL

```bash
docker-compose down          # 停止（数据保留）
docker-compose down -v       # 停止并清除数据卷
```

---

## 常用调试命令

```bash
# 连接 MySQL 容器内部
docker exec -it mysql_orm_learn mysql -u root -p123456 orm_demo

# 查看建表 SQL（SQLite）
sqlite3 orm_demo.db ".schema"
sqlite3 orm_demo.db "SELECT * FROM users;"

# Alembic 状态查看
alembic current     # 当前版本
alembic history     # 完整历史
alembic heads       # 最新版本
```
