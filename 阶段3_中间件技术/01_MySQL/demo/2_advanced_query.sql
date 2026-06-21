-- ============================================================
-- Demo 2: 多表联查与子查询
-- 对应理论：2.多表联查与子查询.md
-- 运行方式：逐段复制到 MySQL 命令行执行
--   docker exec -it mysql-study mysql -u root -p123456 mysql_study
-- ============================================================

-- ============================================================
-- 第一部分：INNER JOIN 内连接
-- ============================================================

-- 1. 查询订单详情（订单 + 用户名）
SELECT
    o.order_no    AS 订单编号,
    u.username    AS 买家姓名,
    o.total_amount AS 订单金额,
    o.status      AS 状态,
    o.created_at  AS 下单时间
FROM orders o
INNER JOIN users u ON o.user_id = u.id
ORDER BY o.created_at DESC
LIMIT 10;

-- 2. 三表联查：订单 + 用户名 + 商品名（最完整的订单视图）
SELECT
    o.order_no    AS 订单编号,
    u.username    AS 买家,
    p.title       AS 商品名称,
    o.quantity    AS 数量,
    p.price       AS 单价,
    o.total_amount AS 实付金额,
    o.status      AS 订单状态
FROM orders o
JOIN users    u ON o.user_id    = u.id
JOIN products p ON o.product_id = p.id
ORDER BY o.created_at DESC;

-- 3. 查询商品及其所属分类名
SELECT
    p.id,
    p.title      AS 商品名,
    c.name       AS 分类,
    p.price      AS 价格,
    p.stock      AS 库存
FROM products p
JOIN categories c ON p.category_id = c.id
WHERE p.status = 'on_sale'
ORDER BY c.name, p.price;

-- ============================================================
-- 第二部分：LEFT JOIN 左连接
-- ============================================================

-- 4. 统计每个用户的订单数（含没有下单的用户）
SELECT
    u.id,
    u.username,
    u.status AS 用户状态,
    COUNT(o.id) AS 订单总数
FROM users u
LEFT JOIN orders o ON u.id = o.user_id
GROUP BY u.id, u.username, u.status
ORDER BY 订单总数 DESC;

-- 5. 找出从未下过单的用户（LEFT JOIN + IS NULL 技巧）
SELECT u.id, u.username, u.email, u.status
FROM users u
LEFT JOIN orders o ON u.id = o.user_id
WHERE o.id IS NULL;

-- 6. 统计每种分类的商品数（含没有商品的分类）
SELECT
    c.name   AS 分类名,
    COUNT(p.id) AS 商品数
FROM categories c
LEFT JOIN products p ON c.id = p.category_id
GROUP BY c.id, c.name
ORDER BY 商品数 DESC;

-- ============================================================
-- 第三部分：聚合函数
-- ============================================================

-- 7. 统计已付款订单的整体指标
SELECT
    COUNT(*)              AS 订单总数,
    SUM(total_amount)     AS 总收入,
    ROUND(AVG(total_amount), 2) AS 平均客单价,
    MAX(total_amount)     AS 最大单笔,
    MIN(total_amount)     AS 最小单笔
FROM orders
WHERE status = 'paid';

-- 8. 按订单状态统计数量和金额
SELECT
    status        AS 状态,
    COUNT(*)      AS 订单数,
    SUM(total_amount) AS 总金额
FROM orders
GROUP BY status
ORDER BY 总金额 DESC;

-- ============================================================
-- 第四部分：GROUP BY + HAVING
-- ============================================================

-- 9. 统计每个用户的消费情况（只统计 paid 订单）
SELECT
    u.username           AS 用户名,
    COUNT(o.id)          AS 付款订单数,
    SUM(o.total_amount)  AS 消费总额,
    MAX(o.total_amount)  AS 最大单笔
FROM users u
JOIN orders o ON u.id = o.user_id
WHERE o.status = 'paid'         -- 分组前过滤：只看已付款
GROUP BY u.id, u.username
HAVING COUNT(o.id) >= 2         -- 分组后过滤：下单 2 次以上
ORDER BY 消费总额 DESC;

-- 10. 找出平均价格超过 500 元的商品分类
SELECT
    c.name       AS 分类,
    COUNT(p.id)  AS 商品数,
    ROUND(AVG(p.price), 2) AS 平均售价
FROM categories c
JOIN products p ON c.id = p.category_id
GROUP BY c.id, c.name
HAVING AVG(p.price) > 500
ORDER BY 平均售价 DESC;

-- ============================================================
-- 第五部分：子查询
-- ============================================================

-- 11. 查询购买了最贵商品的订单（单值子查询）
SELECT
    o.order_no,
    u.username,
    p.title AS 商品,
    o.total_amount
FROM orders o
JOIN users    u ON o.user_id    = u.id
JOIN products p ON o.product_id = p.id
WHERE o.product_id = (
    SELECT id FROM products ORDER BY price DESC LIMIT 1
);

-- 12. 查询有未支付订单的用户（IN 子查询）
SELECT id, username, email, balance
FROM users
WHERE id IN (
    SELECT DISTINCT user_id
    FROM orders
    WHERE status = 'unpaid'
);

-- 13. 找出从未被购买的商品（NOT IN 子查询）
SELECT id, title, price, stock
FROM products
WHERE id NOT IN (
    SELECT DISTINCT product_id FROM orders
);

-- 14. 消费总额排名前 3 的用户（FROM 子查询/派生表）
SELECT username, ROUND(消费总额, 2) AS 消费总额
FROM (
    SELECT
        u.username,
        SUM(o.total_amount) AS 消费总额
    FROM users u
    JOIN orders o ON u.id = o.user_id
    WHERE o.status = 'paid'
    GROUP BY u.id, u.username
) AS user_stats
ORDER BY 消费总额 DESC
LIMIT 3;

-- 15. 每个分类中最贵的商品（相关子查询）
SELECT
    p.title      AS 商品名,
    c.name       AS 分类,
    p.price      AS 价格
FROM products p
JOIN categories c ON p.category_id = c.id
WHERE p.price = (
    SELECT MAX(price)
    FROM products
    WHERE category_id = p.category_id  -- 与外层查询关联
)
ORDER BY p.price DESC;

-- ============================================================
-- 🏋️ 动手练习
-- ============================================================

-- 练习 1（⭐ 基础）：
-- 查询所有"图书"分类的商品，显示商品名、价格、库存
-- 提示：用 JOIN 连接 products 和 categories

-- 练习 2（⭐⭐ 进阶）：
-- 统计每种订单状态（unpaid/paid/cancelled/refunded）各有多少笔，
-- 总金额是多少？按订单数从多到少排序

-- 练习 3（⭐⭐ 进阶）：
-- 查询用户"赵六"（id=4）的所有订单，显示订单编号、商品名称、数量、金额、状态
-- 提示：三表 JOIN

-- 练习 4（⭐⭐⭐ 挑战）：
-- 找出下单次数最多的用户（含下单 0 次的用户也要展示）
-- 显示：用户名、订单总数，按订单数降序

-- 练习 5（⭐⭐⭐ 挑战）：
-- 查询 2026 年 1 月份消费总额最高的用户是谁？消费了多少？
-- 提示：WHERE 过滤时间范围 + GROUP BY + ORDER BY + LIMIT

-- ============================================================
-- 📝 参考答案
-- ============================================================

-- 答案 1：
SELECT p.title, p.price, p.stock
FROM products p
JOIN categories c ON p.category_id = c.id
WHERE c.name = '图书'
ORDER BY p.price;

-- 答案 2：
SELECT
    status       AS 订单状态,
    COUNT(*)     AS 订单数,
    SUM(total_amount) AS 总金额
FROM orders
GROUP BY status
ORDER BY 订单数 DESC;

-- 答案 3：
SELECT
    o.order_no    AS 订单编号,
    p.title       AS 商品名称,
    o.quantity    AS 数量,
    o.total_amount AS 金额,
    o.status      AS 状态
FROM orders o
JOIN users    u ON o.user_id    = u.id
JOIN products p ON o.product_id = p.id
WHERE u.username = '赵六'
ORDER BY o.created_at;

-- 答案 4：
SELECT
    u.username    AS 用户名,
    COUNT(o.id)   AS 订单总数
FROM users u
LEFT JOIN orders o ON u.id = o.user_id
GROUP BY u.id, u.username
ORDER BY 订单总数 DESC;

-- 答案 5：
SELECT
    u.username        AS 用户名,
    SUM(o.total_amount) AS 一月消费总额
FROM users u
JOIN orders o ON u.id = o.user_id
WHERE o.status = 'paid'
  AND o.created_at BETWEEN '2026-01-01 00:00:00' AND '2026-01-31 23:59:59'
GROUP BY u.id, u.username
ORDER BY 一月消费总额 DESC
LIMIT 1;
