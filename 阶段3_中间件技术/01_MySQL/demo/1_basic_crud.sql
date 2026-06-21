-- ============================================================
-- Demo 1: SQL 基础与 CRUD
-- 对应理论：1.SQL基础与CRUD.md
-- 运行方式：逐段复制到 MySQL 命令行执行
--   docker exec -it mysql-study mysql -u root -p123456 mysql_study
-- ============================================================

-- ============================================================
-- 第一部分：SELECT 查询
-- ============================================================

-- 1. 查看所有在售商品（指定字段，不用 *）
SELECT id, title, price, stock, status
FROM products
WHERE status = 'on_sale'
ORDER BY price DESC;

-- 2. 查找余额大于 500 元的活跃用户
SELECT id, username, email, balance
FROM users
WHERE status = 'active'
  AND balance > 500
ORDER BY balance DESC;

-- 3. 搜索书名包含"MySQL"的商品（模糊查询）
SELECT id, title, price, stock
FROM products
WHERE title LIKE '%MySQL%';

-- 4. 查询价格在 100~1000 元之间的商品（含两端）
SELECT id, title, price
FROM products
WHERE price BETWEEN 100 AND 1000
ORDER BY price;

-- 5. 查询分页商品列表（第 2 页，每页 5 条）
SELECT id, title, price
FROM products
ORDER BY id
LIMIT 5 OFFSET 5;    -- 跳过前 5 条，取 5 条

-- 6. 字段别名（给列取中文名）
SELECT
    id        AS 商品ID,
    title     AS 商品名称,
    price     AS 售价,
    stock     AS 库存
FROM products
WHERE status = 'on_sale'
LIMIT 10;

-- ============================================================
-- 第二部分：NULL 处理
-- ============================================================

-- 7. 查看 categories 表中有 description 的分类
SELECT id, name, description
FROM categories
WHERE description IS NOT NULL;

-- 8. 用 IFNULL 设置默认值（description 为 NULL 时显示"暂无描述"）
SELECT id, name, IFNULL(description, '暂无描述') AS 描述
FROM categories;

-- 9. 用 COALESCE 处理多级 NULL（取第一个非 NULL 值）
-- 场景：优先显示 phone，没有则显示 email
SELECT username, COALESCE(phone, email, '无联系方式') AS 联系方式
FROM users;

-- ============================================================
-- 第三部分：INSERT 插入
-- ============================================================

-- 10. 插入一个新用户（指定字段名，推荐写法）
INSERT INTO users (username, email, phone, password_hash, balance, status)
VALUES ('测试用户', 'test@example.com', '13600000001', '$2b$12$test_hash', 0.00, 'inactive');

-- 11. 验证插入结果
SELECT id, username, email, status, created_at
FROM users
WHERE username = '测试用户';

-- 12. 插入一条测试订单
INSERT INTO orders (order_no, user_id, product_id, quantity, total_amount, status)
VALUES ('ORD_TEST_001', 1, 15, 1, 59.00, 'unpaid');

-- ============================================================
-- 第四部分：UPDATE 修改
-- ============================================================

-- 13. 激活刚创建的测试用户
UPDATE users
SET status = 'active'
WHERE username = '测试用户';

-- 14. 给用户 ID=1（张三）充值 500 元（基于原值计算）
UPDATE users
SET balance = balance + 500.00
WHERE id = 1;

-- 验证充值结果
SELECT id, username, balance FROM users WHERE id = 1;

-- 15. 将测试订单状态改为已支付
UPDATE orders
SET status = 'paid', updated_at = NOW()
WHERE order_no = 'ORD_TEST_001';

-- 16. 撤销充值（演示完后恢复原始数据）
UPDATE users SET balance = balance - 500.00 WHERE id = 1;

-- ============================================================
-- 第五部分：DELETE 删除
-- ============================================================

-- 17. 物理删除刚才插入的测试数据（演示用，实际项目用逻辑删除）
-- 注意：有外键关联时，要先删子表数据
DELETE FROM orders WHERE order_no = 'ORD_TEST_001';
DELETE FROM users WHERE username = '测试用户';

-- 18. 验证删除结果
SELECT COUNT(*) AS 剩余用户数 FROM users;

-- ============================================================
-- 第六部分：综合查询练习
-- ============================================================

-- 19. 查询库存不足（stock < 10）且在售的商品（需补货预警）
SELECT id, title, stock, price
FROM products
WHERE status = 'on_sale'
  AND stock < 10
ORDER BY stock;

-- 20. 查询已取消的订单（用于统计流失）
SELECT order_no, user_id, total_amount, created_at
FROM orders
WHERE status = 'cancelled'
ORDER BY created_at DESC;

-- ============================================================
-- 🏋️ 动手练习
-- ============================================================

-- 练习 1（⭐ 基础）：
-- 查询所有状态为 'paid' 的订单，按下单时间从新到旧排序，只显示前 5 条
-- 需要的字段：order_no, user_id, total_amount, created_at

-- 练习 2（⭐ 基础）：
-- 查询单价超过 5000 元的商品，显示商品名称、价格和库存
-- 按价格从高到低排序

-- 练习 3（⭐⭐ 进阶）：
-- 查询 2026 年 2 月份创建的所有订单（2026-02-01 到 2026-02-28）
-- 提示：使用 BETWEEN 或 >= / <=

-- 练习 4（⭐⭐ 进阶）：
-- 将商品 ID=18（高性能MySQL第4版）的状态改回 'on_sale'，并将价格改为 129.00
-- 改完后查询验证

-- 练习 5（⭐⭐⭐ 挑战）：
-- 查询所有用户中，余额为 0 且状态为 'inactive' 的用户
-- 并思考：这些用户是否应该在业务上做清理？（用 SELECT 查出来分析即可，不要删除）

-- ============================================================
-- 📝 参考答案（先自己写，写不出来再看！）
-- ============================================================

-- 答案 1：
SELECT order_no, user_id, total_amount, created_at
FROM orders
WHERE status = 'paid'
ORDER BY created_at DESC
LIMIT 5;

-- 答案 2：
SELECT title, price, stock
FROM products
WHERE price > 5000
ORDER BY price DESC;

-- 答案 3：
SELECT order_no, user_id, total_amount, status, created_at
FROM orders
WHERE created_at BETWEEN '2026-02-01 00:00:00' AND '2026-02-28 23:59:59'
ORDER BY created_at;

-- 答案 4：
UPDATE products
SET status = 'on_sale', price = 129.00
WHERE id = 18;
-- 验证：
SELECT id, title, price, status FROM products WHERE id = 18;

-- 答案 5：
SELECT id, username, email, balance, status, created_at
FROM users
WHERE balance = 0
  AND status = 'inactive';
-- 分析：这些用户注册后从未充值，可能是无效账户
-- 实际处理：不物理删除，设置合理的清理策略（如 180 天未登录后发邮件提醒）
