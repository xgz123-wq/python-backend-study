-- ============================================================
-- Demo 0: MySQL 环境与基础操作
-- 对应理论：0.MySQL环境与基础操作.md
-- 运行方式：在进入 MySQL 后，逐条复制执行
--   docker exec -it mysql-study mysql -u root -p123456 mysql_study
-- ============================================================

-- ============================================================
-- 第一部分：数据库基本操作
-- ============================================================

-- 1. 查看所有数据库
SHOW DATABASES;

-- 2. 确认当前所在数据库
SELECT DATABASE();

-- 3. 查看 MySQL 版本和当前时间
SELECT VERSION(), NOW(), USER();

-- 4. 查看字符集配置（应全部显示 utf8mb4）
SHOW VARIABLES LIKE 'character%';

-- ============================================================
-- 第二部分：查看电商系统表结构
-- ============================================================

-- 5. 查看所有表
SHOW TABLES;

-- 6. 查看 users 表结构（字段、类型、是否可空、默认值）
DESC users;

-- 7. 查看 products 表结构
DESC products;

-- 8. 查看 orders 表结构
DESC orders;

-- 9. 查看完整建表语句（含字符集和外键）
SHOW CREATE TABLE orders\G

-- ============================================================
-- 第三部分：查看 Mock 数据
-- ============================================================

-- 10. 查看所有用户
SELECT id, username, email, balance, status FROM users;

-- 11. 查看所有商品分类
SELECT * FROM categories;

-- 12. 查看前 10 个商品
SELECT id, title, price, stock, status FROM products LIMIT 10;

-- 13. 查看前 10 笔订单
SELECT id, order_no, user_id, product_id, total_amount, status
FROM orders LIMIT 10;

-- 14. 统计各表数据量
SELECT 'users'      AS 表名, COUNT(*) AS 记录数 FROM users
UNION ALL
SELECT 'categories', COUNT(*) FROM categories
UNION ALL
SELECT 'products',   COUNT(*) FROM products
UNION ALL
SELECT 'orders',     COUNT(*) FROM orders;

-- ============================================================
-- 第四部分：表信息查询
-- ============================================================

-- 15. 查看所有表的存储引擎和字符集
SHOW TABLE STATUS\G

-- 16. 通过 information_schema 查询表信息（更灵活）
SELECT
    TABLE_NAME        AS 表名,
    ENGINE            AS 引擎,
    TABLE_COLLATION   AS 字符集排序,
    TABLE_ROWS        AS 估算行数,
    CREATE_TIME       AS 创建时间
FROM information_schema.TABLES
WHERE TABLE_SCHEMA = 'mysql_study';

-- ============================================================
-- 🏋️ 动手练习
-- ============================================================
-- 练习 1（⭐ 基础）：查看 MySQL 当前的最大连接数配置
--   提示：使用 SHOW VARIABLES LIKE 'max_connections';

-- 练习 2（⭐ 基础）：用 DESC 命令查看 categories 表结构，
--   说出每个字段的数据类型

-- 练习 3（⭐⭐ 进阶）：通过 information_schema 查询 mysql_study 库中
--   哪些表有外键约束？外键关联的是哪张表？
--   提示：SELECT * FROM information_schema.KEY_COLUMN_USAGE WHERE TABLE_SCHEMA='mysql_study';

-- ============================================================
-- 📝 参考答案
-- ============================================================

-- 答案 1：
SHOW VARIABLES LIKE 'max_connections';

-- 答案 2：
DESC categories;
-- id: INT UNSIGNED（无符号整数，主键）
-- name: VARCHAR(50)（可变长字符串，最长50字符）
-- description: VARCHAR(200)（可变长字符串，允许为NULL）
-- created_at: DATETIME（日期时间）

-- 答案 3：
SELECT
    TABLE_NAME        AS 表名,
    COLUMN_NAME       AS 字段名,
    REFERENCED_TABLE_NAME  AS 关联表,
    REFERENCED_COLUMN_NAME AS 关联字段
FROM information_schema.KEY_COLUMN_USAGE
WHERE TABLE_SCHEMA = 'mysql_study'
  AND REFERENCED_TABLE_NAME IS NOT NULL;
-- 结果：products.category_id → categories.id
--       orders.user_id       → users.id
--       orders.product_id    → products.id
