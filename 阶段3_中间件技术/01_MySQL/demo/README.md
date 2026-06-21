# Demo 目录 - MySQL 电商系统实战

> 所有 Demo 均基于「迷你电商系统」，包含 users/categories/products/orders 四张核心表。

---

## 环境准备

```bash
# 0. 首次使用：创建并启动容器（只需执行一次）
docker-compose up -d

# 等待 healthy 后继续（约 30 秒）
docker-compose ps

# 1. 确认 Docker 容器运行
docker ps | grep mysql-study

# 2. 启动容器（如果未运行）
docker start mysql-study

# 3. 导入初始化数据（首次使用，或需要重置数据时）
#    在 demo/ 目录下执行：
docker exec -i mysql-study mysql -u root -p123456 mysql_study < init.sql

# 4. 验证数据是否正常
docker exec -it mysql-study mysql -u root -p123456 mysql_study -e "SHOW TABLES; SELECT COUNT(*) FROM orders;"
```

---

## 学习顺序

| 顺序 | 文件 | 对应理论 | 定位 | 前置依赖 |
|------|------|---------|------|---------|
| 0 | `init.sql` | - | 数据初始化（必须先执行！） | 无 |
| 1 | `0_mysql_basics.sql` | `0.MySQL环境与基础操作.md` | 环境操作、查表结构 | init.sql |
| 2 | `1_basic_crud.sql` | `1.SQL基础与CRUD.md` | INSERT/SELECT/UPDATE/DELETE | init.sql |
| 3 | `2_advanced_query.sql` | `2.多表联查与子查询.md` | JOIN、聚合、子查询 | init.sql |
| 4 | `3_index_demo.sql` | `3.索引原理与优化.md` | 索引创建、EXPLAIN 分析 | init.sql |
| 5 | `4_transaction_demo.sql` | `4.事务与隔离级别.md` | 事务控制、隔离级别演示 | init.sql |
| 6 | `5_table_design.sql` | `5.表设计与慢查询优化.md` | 类型选择、逻辑删除、分页优化 | init.sql |

---

## Demo 详情

### Demo 0: MySQL 环境操作（`0_mysql_basics.sql`）
**文件**：`0_mysql_basics.sql`

熟悉 MySQL 命令行操作、查看数据库/表结构、字符集配置。帮助初学者在开始学 SQL 语法之前，先建立操控 MySQL 的基本手感。

**运行方式**：进入 MySQL 后逐条执行

```bash
docker exec -it mysql-study mysql -u root -p123456 mysql_study
```

**前置依赖**：需要先执行 `init.sql`

---

### Demo 1: SQL 基础与 CRUD（`1_basic_crud.sql`）
**文件**：`1_basic_crud.sql`

覆盖电商场景下的增删改查：查询在售商品、搜索书名、分页列表、给用户充值、逻辑删除等。每个操作都有真实业务含义，不是枯燥的 test 表。

**运行方式**：进入 MySQL 后逐段执行  
**注意**：Demo 中有 INSERT/UPDATE/DELETE 操作，执行后数据会变化。最后有清理语句恢复原始状态。

---

### Demo 2: 多表联查与子查询（`2_advanced_query.sql`）
**文件**：`2_advanced_query.sql`

电商最核心的查询：订单详情（三表 JOIN）、统计用户消费、找从未下单的用户、每类商品的最高价。包含 INNER JOIN、LEFT JOIN、GROUP BY + HAVING、子查询等核心技能。

**运行方式**：进入 MySQL 后逐段执行  
**核心练习**：统计 2026 年 1 月份消费最多的用户（综合应用）

---

### Demo 3: 索引原理与优化（`3_index_demo.sql`）
**文件**：`3_index_demo.sql`

通过 EXPLAIN 亲眼看到有索引 vs 无索引的 type 从 `ALL` 变为 `ref` 的过程。演示 6 大索引失效场景，以及覆盖索引带来的性能提升。

**运行方式**：进入 MySQL 后逐段执行  
**关键实验**：对比 `WHERE YEAR(created_at)=2026`（失效）和 `WHERE created_at >= ...`（生效）的 EXPLAIN 差异  
**注意**：Demo 会创建一些索引，末尾有清理语句（可选执行）

---

### Demo 4: 事务与隔离级别（`4_transaction_demo.sql`）
**文件**：`4_transaction_demo.sql`

演示完整的下单事务（扣库存→创建订单→扣余额→更新状态）和回滚场景（余额不足时全部撤销）。隔离级别的并发演示需要**同时打开两个终端**。

**运行方式**：场景一/二在单个终端执行；隔离级别演示需两个终端  
**两终端模式**：
```bash
# 终端 1
docker exec -it mysql-study mysql -u root -p123456 mysql_study
# 终端 2
docker exec -it mysql-study mysql -u root -p123456 mysql_study
```
**注意**：Demo 末尾有清理语句，执行后恢复原始数据

---

### Demo 5: 表设计与慢查询优化（`5_table_design.sql`）
**文件**：`5_table_design.sql`

验证 DECIMAL 精度问题、演示逻辑删除、对比深分页的两种优化方案（游标分页 vs 延迟关联）、用 EXPLAIN 验证函数导致索引失效。

**运行方式**：进入 MySQL 后逐段执行  
**核心练习**：自己设计一张"商品评价表"，应用本章所有最佳实践  
**注意**：Demo 会临时 ALTER TABLE，末尾有清理语句恢复原始结构

---

## 对应理论文档

| Demo 文件 | 理论文档 | 核心知识点 |
|----------|---------|----------|
| `0_mysql_basics.sql` | `0.MySQL环境与基础操作.md` | Docker、命令行、字符集、SQL 规范 |
| `1_basic_crud.sql` | `1.SQL基础与CRUD.md` | INSERT、SELECT、UPDATE、DELETE、NULL、防注入 |
| `2_advanced_query.sql` | `2.多表联查与子查询.md` | INNER/LEFT JOIN、GROUP BY、HAVING、子查询、执行顺序 |
| `3_index_demo.sql` | `3.索引原理与优化.md` | B+树、聚簇/二级索引、联合索引、EXPLAIN、索引失效 |
| `4_transaction_demo.sql` | `4.事务与隔离级别.md` | ACID、BEGIN/COMMIT/ROLLBACK、隔离级别、MVCC、死锁 |
| `5_table_design.sql` | `5.表设计与慢查询优化.md` | 三范式、DECIMAL、DATETIME、逻辑删除、深分页 |

---

## 电商数据模型

```
users(10条)          categories(5条)
id / username        id / name
email / phone        description
balance / status
     │                    │
     │              ┌─────┘
     │              ▼
     │         products(20条)
     │         id / title / price
     │         stock / status / category_id
     │              │
     └──────────────┘
           orders(28条)
           id / order_no
           user_id / product_id
           quantity / total_amount / status
```

---

## 常见问题

**Q: 执行 init.sql 报错 "ERROR 1215: Cannot add foreign key constraint"**  
A: 通常是表删除顺序问题，init.sql 已按 `orders → products → categories → users` 顺序 DROP，重新执行即可。

**Q: 中文乱码**  
A: 确保终端字符集为 UTF-8。Docker 容器已配置 utf8mb4，如果显示乱码检查终端编码设置。

**Q: "TABLE DOESN'T EXIST" 错误**  
A: 先执行 `USE mysql_study;` 切换到正确数据库。

**Q: Demo 执行一半想重置数据**  
A: 重新执行 `init.sql` 即可（脚本会先 DROP 所有表再重建）。
