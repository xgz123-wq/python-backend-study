-- ============================================================
-- Demo 3: 索引原理与优化
-- 对应理论：3.索引原理与优化.md
-- 运行方式：逐段复制到 MySQL 命令行执行
--   docker exec -it mysql-study mysql -u root -p123456 mysql_study
-- ============================================================

-- ============================================================
-- 第一部分：查看现有索引
-- ============================================================

-- 1. 查看 users 表现有索引（主键 + UNIQUE 约束自动创建）
SHOW INDEX FROM users\G

-- 2. 查看 orders 表现有索引（主键 + UNIQUE + 外键自动创建）
SHOW INDEX FROM orders\G

-- 3. 查看 products 表现有索引
SHOW INDEX FROM products\G

-- ============================================================
-- 第二部分：EXPLAIN 分析（有索引 vs 无索引对比）
-- ============================================================

-- 4. 分析：按主键查询（type=const，最优）
EXPLAIN SELECT * FROM users WHERE id = 1\G

-- 5. 分析：按 email 查询（email 有 UNIQUE 索引，type=const）
EXPLAIN SELECT * FROM users WHERE email = 'zhangsan@example.com'\G

-- 6. 分析：按 username 查询（username 有 UNIQUE 索引，type=const）
EXPLAIN SELECT * FROM users WHERE username = '张三'\G

-- 7. 分析：按 status 查询（status 无索引，type=ALL，全表扫描！）
EXPLAIN SELECT * FROM users WHERE status = 'active'\G
-- 注意 type=ALL，rows 等于总行数 → 全表扫描

-- 8. 分析：查询订单按 user_id（外键自动创建索引，type=ref）
EXPLAIN SELECT * FROM orders WHERE user_id = 1\G

-- ============================================================
-- 第三部分：创建索引
-- ============================================================

-- 9. 给 users.status 创建普通索引（优化按状态筛选用户的查询）
CREATE INDEX idx_users_status ON users(status);

-- 再次分析（type 应从 ALL 变为 ref）
EXPLAIN SELECT * FROM users WHERE status = 'active'\G

-- 10. 给 products 创建联合索引（优化商品列表查询）
-- 场景：电商前台最常见：按分类+状态筛选商品，再按价格排序
CREATE INDEX idx_products_cat_status_price ON products(category_id, status, price);

-- 分析联合索引效果
EXPLAIN SELECT id, title, price
FROM products
WHERE category_id = 1 AND status = 'on_sale'
ORDER BY price\G
-- 理想情况：type=ref，Extra=Using index（覆盖索引，不回表）

-- 11. 给 orders 创建联合索引（优化用户查订单历史）
-- 场景：用户中心最常见：查某用户的所有订单，按时间排序
CREATE INDEX idx_orders_user_created ON orders(user_id, created_at);

-- 分析效果
EXPLAIN SELECT order_no, total_amount, status, created_at
FROM orders
WHERE user_id = 4
ORDER BY created_at DESC\G

-- ============================================================
-- 第四部分：索引失效演示
-- ============================================================

-- 12. 失效场景 1：函数包裹索引字段
-- ❌ 对 created_at 使用函数，索引失效
EXPLAIN SELECT * FROM orders WHERE YEAR(created_at) = 2026\G

-- ✅ 改写为范围查询，索引生效
EXPLAIN SELECT * FROM orders
WHERE created_at >= '2026-01-01' AND created_at < '2027-01-01'\G

-- 13. 失效场景 2：隐式类型转换
-- ❌ phone 是 VARCHAR，传入数字触发类型转换，索引失效
EXPLAIN SELECT * FROM users WHERE phone = 13800001001\G

-- ✅ 传入字符串，索引生效
EXPLAIN SELECT * FROM users WHERE phone = '13800001001'\G

-- 14. 失效场景 3：LIKE 前缀通配符
-- ❌ % 在前面，无法利用 B+ 树的有序性
EXPLAIN SELECT * FROM products WHERE title LIKE '%手机%'\G

-- ✅ 前缀匹配，可以用索引（但我们的 title 没有单独索引，所以仍是 ALL）
-- 若 title 有索引：LIKE 'iPhone%' 可以用索引
EXPLAIN SELECT * FROM products WHERE title LIKE 'iPhone%'\G

-- 15. 失效场景 4：联合索引违反最左前缀
-- 联合索引：idx_products_cat_status_price(category_id, status, price)

-- ✅ 使用最左字段 category_id，索引生效
EXPLAIN SELECT * FROM products WHERE category_id = 1\G

-- ✅ 使用最左两字段，索引生效
EXPLAIN SELECT * FROM products WHERE category_id = 1 AND status = 'on_sale'\G

-- ❌ 跳过 category_id，直接用 status，索引失效（type=ALL）
EXPLAIN SELECT * FROM products WHERE status = 'on_sale'\G

-- ============================================================
-- 第五部分：覆盖索引演示
-- ============================================================

-- 16. 覆盖索引：SELECT 的字段全部在索引中，无需回表
-- 联合索引 idx_products_cat_status_price(category_id, status, price)
-- SELECT 的字段：id（主键）+ price（在索引中）
EXPLAIN SELECT id, price
FROM products
WHERE category_id = 1 AND status = 'on_sale'
ORDER BY price\G
-- Extra 应显示 Using index → 覆盖索引，不回表

-- 17. 非覆盖索引：SELECT 了索引外的字段，需要回表
EXPLAIN SELECT id, title, price, stock   -- title/stock 不在索引中
FROM products
WHERE category_id = 1 AND status = 'on_sale'\G
-- Extra 无 Using index → 需要回表读取 title 和 stock

-- ============================================================
-- 第六部分：清理演示创建的索引
-- ============================================================

-- 如需清理（可选）：
-- DROP INDEX idx_users_status ON users;
-- DROP INDEX idx_products_cat_status_price ON products;
-- DROP INDEX idx_orders_user_created ON orders;

-- 查看 orders 当前所有索引
SHOW INDEX FROM orders;

-- ============================================================
-- 🏋️ 动手练习
-- ============================================================

-- 练习 1（⭐ 基础）：
-- 用 EXPLAIN 分析以下查询：
--   SELECT * FROM orders WHERE order_no = 'ORD20260101001';
-- 查看 type 是什么？key 用了哪个索引？为什么？

-- 练习 2（⭐⭐ 进阶）：
-- 用 EXPLAIN 分析以下两条查询，对比 rows 字段的差异：
--   查询 A：SELECT * FROM orders WHERE user_id = 4;
--   查询 B：SELECT * FROM orders WHERE total_amount > 1000;
-- total_amount 没有索引，rows 有什么不同？

-- 练习 3（⭐⭐ 进阶）：
-- 为 orders 表的 status 字段添加索引，然后再次 EXPLAIN 分析：
--   SELECT * FROM orders WHERE status = 'paid';
-- 对比加索引前后的 type 和 rows 变化

-- 练习 4（⭐⭐⭐ 挑战）：
-- 设计一个联合索引，优化以下查询（思考字段顺序）：
--   SELECT order_no, total_amount, created_at
--   FROM orders
--   WHERE user_id = 4 AND status = 'paid'
--   ORDER BY created_at DESC;
-- 说明：为什么字段顺序要这样排列？
-- 创建后用 EXPLAIN 验证是否达到预期效果

-- ============================================================
-- 📝 参考答案
-- ============================================================

-- 答案 1：
EXPLAIN SELECT * FROM orders WHERE order_no = 'ORD20260101001'\G
-- type=const（order_no 有 UNIQUE 索引，等值查询返回最多一行）
-- key=order_no（使用了 order_no 上的唯一索引）
-- rows=1（只扫描 1 行）

-- 答案 2：
EXPLAIN SELECT * FROM orders WHERE user_id = 4\G
-- type=ref，rows 很少（有外键索引，只扫描 user_id=4 的订单）

EXPLAIN SELECT * FROM orders WHERE total_amount > 1000\G
-- type=ALL，rows=28（全表扫描，total_amount 无索引）

-- 答案 3：
CREATE INDEX idx_orders_status ON orders(status);
EXPLAIN SELECT * FROM orders WHERE status = 'paid'\G
-- 加索引前：type=ALL
-- 加索引后：type=ref，rows 减少为 paid 状态的订单数（约 16 条）

-- 答案 4：
-- 字段顺序应为 (user_id, status, created_at)
-- 原因：
-- 1. user_id 区分度最高（等值查询），放最前面
-- 2. status 次之（等值查询），放第二
-- 3. created_at 用于 ORDER BY，放最后（避免 Using filesort）
CREATE INDEX idx_orders_user_status_created ON orders(user_id, status, created_at);
EXPLAIN SELECT order_no, total_amount, created_at
FROM orders
WHERE user_id = 4 AND status = 'paid'
ORDER BY created_at DESC\G
-- 理想结果：type=ref，Extra 无 Using filesort（排序直接利用索引顺序）
