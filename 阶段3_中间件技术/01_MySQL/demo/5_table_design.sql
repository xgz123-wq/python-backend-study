-- ============================================================
-- Demo 5: 表设计与慢查询优化
-- 对应理论：5.表设计与慢查询优化.md
-- 运行方式：逐段复制到 MySQL 命令行执行
--   docker exec -it mysql-study mysql -u root -p123456 mysql_study
-- ============================================================

-- ============================================================
-- 第一部分：列类型最佳实践验证
-- ============================================================

-- 1. 验证 DECIMAL 精度（金额必用）
SELECT 0.1 + 0.2 AS float_result;        -- 可能显示 0.30000000000000004（取决于客户端）
SELECT 0.1 + 0.2 = 0.3 AS float_equal;   -- 结果：0（不等于！）

-- DECIMAL 精确计算
SELECT CAST(0.1 AS DECIMAL(10,2)) + CAST(0.2 AS DECIMAL(10,2)) AS decimal_result;
SELECT CAST(0.1 AS DECIMAL(10,2)) + CAST(0.2 AS DECIMAL(10,2)) = 0.3 AS decimal_equal;  -- 1

-- 2. 查看 products 表使用了 DECIMAL 的字段
DESCRIBE products;
-- price DECIMAL(10,2) → 最多 10 位数字，2 位小数，最大 99999999.99

-- 3. CHAR vs VARCHAR 空间差异（固定 vs 可变）
-- 手机号固定 11 位，用 CHAR(11) 更合适
SELECT LENGTH('13800001001') AS 手机号长度;  -- 11

-- ============================================================
-- 第二部分：逻辑删除演示
-- ============================================================

-- 4. 为 products 添加逻辑删除字段（生产中建表时就应该有）
ALTER TABLE products ADD COLUMN is_deleted TINYINT(1) NOT NULL DEFAULT 0 COMMENT '0:正常 1:已删除';

-- 5. 逻辑删除一个商品（下架的商品，不物理删除）
UPDATE products SET is_deleted = 1 WHERE id = 18;  -- 《高性能MySQL第4版》

-- 6. 正常查询（必须加 is_deleted = 0 过滤已删除的）
SELECT id, title, price, status, is_deleted
FROM products
WHERE is_deleted = 0
ORDER BY id;

-- 7. 查看已被逻辑删除的商品（管理后台可以看到）
SELECT id, title, price, is_deleted
FROM products
WHERE is_deleted = 1;

-- 8. 恢复商品（取消逻辑删除）
UPDATE products SET is_deleted = 0 WHERE id = 18;

-- ============================================================
-- 第三部分：深分页优化
-- ============================================================

-- 9. 先插入更多商品数据，模拟分页场景
-- （我们的 Demo 数据只有 20 条，用已有数据演示原理）

-- ❌ 传统分页：LIMIT offset, count（offset 越大越慢）
-- 第 1 页（快）
EXPLAIN SELECT id, title, price
FROM products
WHERE is_deleted = 0
ORDER BY id
LIMIT 0, 5\G

-- 第 3 页（小数据集看不出差异，但百万级数据时 LIMIT 99990,10 极慢）
EXPLAIN SELECT id, title, price
FROM products
WHERE is_deleted = 0
ORDER BY id
LIMIT 10, 5\G

-- ✅ 游标分页：记住上次的最后一个 id（大数据量时性能恒定）
-- 假设上次返回的最后一个 id=10，下次请求：
EXPLAIN SELECT id, title, price
FROM products
WHERE id > 10             -- 直接走主键索引，不需要跳过前 10 条
  AND is_deleted = 0
ORDER BY id
LIMIT 5\G
-- 对比：type=range（范围扫描），比 LIMIT offset 更高效

-- ✅ 延迟关联：先用覆盖索引取 id，再 JOIN 取完整数据
EXPLAIN SELECT p.id, p.title, p.price, p.stock
FROM products p
JOIN (
    SELECT id FROM products
    WHERE is_deleted = 0
    ORDER BY id
    LIMIT 10, 5
) AS ids ON p.id = ids.id\G

-- ============================================================
-- 第四部分：慢查询分析
-- ============================================================

-- 10. 查看慢查询日志配置
SHOW VARIABLES LIKE 'slow_query%';
SHOW VARIABLES LIKE 'long_query_time';

-- 11. 查看当前全局状态中的慢查询次数
SHOW GLOBAL STATUS LIKE 'Slow_queries';

-- 12. 找出 products 表上最"贵"的查询（无索引的场景）
-- 先删除我们在 Demo3 创建的索引（如果存在）
-- DROP INDEX idx_products_cat_status_price ON products;

-- 全表扫描 + 排序（最慢的模式）
EXPLAIN SELECT id, title, price, stock
FROM products
WHERE is_deleted = 0
  AND status = 'on_sale'
ORDER BY price DESC\G
-- type=ALL → 全表扫描

-- 创建针对性索引后对比
CREATE INDEX idx_products_design ON products(is_deleted, status, price);

EXPLAIN SELECT id, title, price, stock
FROM products
WHERE is_deleted = 0
  AND status = 'on_sale'
ORDER BY price DESC\G
-- type 应变为 ref，rows 大幅减少

-- ============================================================
-- 第五部分：查看表设计全貌
-- ============================================================

-- 13. 查看完整的电商系统表设计（验证字段类型选择）
SHOW CREATE TABLE users\G
SHOW CREATE TABLE products\G
SHOW CREATE TABLE orders\G

-- 14. 统计各表的存储空间
SELECT
    TABLE_NAME                                   AS 表名,
    TABLE_ROWS                                   AS 估算行数,
    ROUND(DATA_LENGTH / 1024, 2)                 AS 数据大小KB,
    ROUND(INDEX_LENGTH / 1024, 2)                AS 索引大小KB,
    ROUND((DATA_LENGTH + INDEX_LENGTH) / 1024, 2) AS 总大小KB
FROM information_schema.TABLES
WHERE TABLE_SCHEMA = 'mysql_study'
ORDER BY 总大小KB DESC;

-- ============================================================
-- 第六部分：SQL 改写优化示例
-- ============================================================

-- 15. 优化：避免 SELECT *，只取需要的字段
-- ❌ 低效：取所有字段（包括不需要的 password_hash 等）
-- SELECT * FROM users WHERE status = 'active';

-- ✅ 高效：只取需要展示的字段
SELECT id, username, email, balance
FROM users
WHERE status = 'active'
  AND is_deleted = 0
ORDER BY id;

-- 等等，users 表还没有 is_deleted，这是为后续扩展说明
-- 当前查询：
SELECT id, username, email, balance
FROM users
WHERE status = 'active'
ORDER BY balance DESC;

-- 16. 优化：用 EXISTS 替代 IN（当子查询结果集很大时）
-- ❌ IN 子查询（子查询结果集大时性能差）
SELECT id, username
FROM users
WHERE id IN (SELECT DISTINCT user_id FROM orders WHERE status = 'paid');

-- ✅ EXISTS（找到匹配行立即停止，更高效）
SELECT id, username
FROM users u
WHERE EXISTS (
    SELECT 1
    FROM orders o
    WHERE o.user_id = u.id AND o.status = 'paid'
);

-- ============================================================
-- 清理演示创建的索引和字段
-- ============================================================

-- 清理逻辑删除字段（保持 Demo 数据干净）
ALTER TABLE products DROP COLUMN is_deleted;

-- 清理 Demo 5 创建的索引
DROP INDEX idx_products_design ON products;

-- ============================================================
-- 🏋️ 动手练习
-- ============================================================

-- 练习 1（⭐ 基础）：
-- 查看 orders 表的完整建表语句（SHOW CREATE TABLE）
-- 找出哪些字段类型选择合理？哪些可以优化？

-- 练习 2（⭐⭐ 进阶）：
-- 为 orders 表添加逻辑删除字段 deleted_at（DATETIME 类型，默认 NULL）
-- 然后"逻辑删除"所有 status='cancelled' 的订单
-- 最后查询：未被逻辑删除的订单列表（按创建时间倒序，只显示 5 条）

-- 练习 3（⭐⭐ 进阶）：
-- 用 EXPLAIN 对比以下两种写法的性能差异：
-- 写法 A：SELECT * FROM orders WHERE DATE(created_at) = '2026-02-05'
-- 写法 B：SELECT * FROM orders WHERE created_at >= '2026-02-05' AND created_at < '2026-02-06'
-- 哪种写法能用到索引？为什么？

-- 练习 4（⭐⭐⭐ 挑战）：
-- 设计一张"商品评价表"(product_reviews)，要求：
--   - 关联 users 和 products
--   - 包含评分（1-5分）、评价内容、是否有图片
--   - 支持逻辑删除
--   - 添加合理的索引
--   - 字段类型遵循最佳实践
-- 写出 CREATE TABLE 语句

-- ============================================================
-- 📝 参考答案
-- ============================================================

-- 答案 1：
SHOW CREATE TABLE orders\G
-- 合理的设计：
--   order_no VARCHAR(32) UNIQUE → 业务唯一键，VARCHAR 合适
--   total_amount DECIMAL(10,2) → 金额必须用 DECIMAL ✅
--   status ENUM(...) → 有限枚举值用 ENUM ✅
--   created_at DATETIME → 时间用 DATETIME ✅
-- 可以优化的地方：
--   可以添加 deleted_at 支持逻辑删除

-- 答案 2：
ALTER TABLE orders ADD COLUMN deleted_at DATETIME DEFAULT NULL COMMENT '逻辑删除时间';
UPDATE orders SET deleted_at = NOW() WHERE status = 'cancelled';
SELECT order_no, user_id, total_amount, status, created_at
FROM orders
WHERE deleted_at IS NULL
ORDER BY created_at DESC
LIMIT 5;
-- 恢复
ALTER TABLE orders DROP COLUMN deleted_at;

-- 答案 3：
-- 写法 A（DATE函数包裹字段，索引失效）
EXPLAIN SELECT * FROM orders WHERE DATE(created_at) = '2026-02-05'\G
-- type=ALL → 全表扫描，索引失效！

-- 写法 B（范围查询，索引可用）
EXPLAIN SELECT * FROM orders WHERE created_at >= '2026-02-05' AND created_at < '2026-02-06'\G
-- type=ALL（orders.created_at 目前没有独立索引）
-- 但如果 created_at 有索引，写法 B 会走索引，写法 A 不会
-- 结论：永远不要对索引字段使用函数！

-- 答案 4：
CREATE TABLE product_reviews (
    id          INT UNSIGNED AUTO_INCREMENT PRIMARY KEY COMMENT '评价ID',
    product_id  INT UNSIGNED NOT NULL COMMENT '商品ID',
    user_id     INT UNSIGNED NOT NULL COMMENT '用户ID',
    rating      TINYINT NOT NULL COMMENT '评分（1-5）',
    content     VARCHAR(500) COMMENT '评价内容',
    has_image   TINYINT(1) NOT NULL DEFAULT 0 COMMENT '是否有图片 0:无 1:有',
    deleted_at  DATETIME DEFAULT NULL COMMENT '逻辑删除时间',
    created_at  DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at  DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT fk_review_product FOREIGN KEY (product_id) REFERENCES products(id),
    CONSTRAINT fk_review_user    FOREIGN KEY (user_id)    REFERENCES users(id),
    INDEX idx_reviews_product (product_id, deleted_at),   -- 查看某商品的评价列表
    INDEX idx_reviews_user    (user_id, created_at)       -- 查看某用户的评价历史
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='商品评价表';
