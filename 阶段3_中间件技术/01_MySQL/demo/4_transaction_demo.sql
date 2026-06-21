-- ============================================================
-- Demo 4: 事务与隔离级别
-- 对应理论：4.事务与隔离级别.md
-- 运行方式：需要开两个终端模拟并发场景
--   终端1: docker exec -it mysql-study mysql -u root -p123456 mysql_study
--   终端2: docker exec -it mysql-study mysql -u root -p123456 mysql_study
-- ============================================================

-- ============================================================
-- 第一部分：基础事务操作
-- ============================================================

-- 1. 查看当前隔离级别（MySQL 8.0 默认 REPEATABLE-READ）
SELECT @@transaction_isolation;

-- 2. 查看自动提交状态（默认 ON）
SHOW VARIABLES LIKE 'autocommit';

-- ============================================================
-- 场景一：成功的事务——电商下单流程
-- 模拟：用户张三（id=1）购买《MySQL必知必会》（id=15，价格59元）
-- ============================================================

-- 查看下单前的状态
SELECT id, username, balance FROM users WHERE id = 1;
SELECT id, title, stock FROM products WHERE id = 15;

-- 开始事务
BEGIN;

-- 步骤 1：扣减库存
UPDATE products
SET stock = stock - 1
WHERE id = 15 AND stock > 0;   -- 加 stock > 0 防止超卖

-- 步骤 2：创建订单
INSERT INTO orders (order_no, user_id, product_id, quantity, total_amount, status)
VALUES ('ORD_DEMO_001', 1, 15, 1, 59.00, 'unpaid');

-- 步骤 3：扣减余额
UPDATE users
SET balance = balance - 59.00
WHERE id = 1 AND balance >= 59.00;  -- 加余额校验

-- 步骤 4：将订单状态改为已付款
UPDATE orders
SET status = 'paid'
WHERE order_no = 'ORD_DEMO_001';

-- 提交事务
COMMIT;

-- 验证结果（库存减1，余额减59）
SELECT id, username, balance FROM users WHERE id = 1;
SELECT id, title, stock FROM products WHERE id = 15;
SELECT order_no, status, total_amount FROM orders WHERE order_no = 'ORD_DEMO_001';

-- ============================================================
-- 场景二：失败的事务——余额不足，全部回滚
-- ============================================================

-- 查看郑十（id=8）余额（只有 60 元，不够买 iPhone）
SELECT id, username, balance FROM users WHERE id = 8;
SELECT id, title, price, stock FROM products WHERE id = 1;  -- iPhone 9999元

BEGIN;

-- 步骤 1：扣减库存
UPDATE products SET stock = stock - 1 WHERE id = 1 AND stock > 0;

-- 步骤 2：创建订单
INSERT INTO orders (order_no, user_id, product_id, quantity, total_amount, status)
VALUES ('ORD_DEMO_002', 8, 1, 1, 9999.00, 'unpaid');

-- 步骤 3：尝试扣减余额（余额 60 < 9999，扣减失败）
-- 注意：MySQL UPDATE 不会报错，但 affected rows = 0
UPDATE users
SET balance = balance - 9999.00
WHERE id = 8 AND balance >= 9999.00;

-- 检查受影响行数（应该是 0）
SELECT ROW_COUNT() AS 受影响行数;   -- 0 表示余额不足，扣减失败

-- 模拟应用层检测到扣减失败，执行回滚
ROLLBACK;

-- 验证：库存和余额都没有变化
SELECT id, username, balance FROM users WHERE id = 8;         -- 仍为 60
SELECT id, title, stock FROM products WHERE id = 1;           -- 库存未变
SELECT order_no FROM orders WHERE order_no = 'ORD_DEMO_002'; -- 空（订单未创建）

-- ============================================================
-- 第三部分：SAVEPOINT 部分回滚
-- ============================================================

-- 3. SAVEPOINT：在事务内设置保存点，允许部分回滚
BEGIN;

UPDATE users SET balance = balance + 100 WHERE id = 2;  -- 给李四充值 100

SAVEPOINT after_recharge;  -- 设置保存点

UPDATE products SET stock = 0 WHERE id = 10;  -- 标记商品售罄（测试操作）

-- 反悔，只回滚到保存点（充值保留，售罄操作撤销）
ROLLBACK TO SAVEPOINT after_recharge;

COMMIT;

-- 验证：李四余额增加 100，商品 10 库存未变
SELECT id, username, balance FROM users WHERE id = 2;
SELECT id, title, stock FROM products WHERE id = 10;

-- ============================================================
-- 第四部分：隔离级别演示（需要两个终端）
-- ============================================================

-- 【演示脚本】将以下内容分别在终端 1 和终端 2 中执行

-- === 演示：READ COMMITTED 下的不可重复读 ===

-- 终端 1（先执行）：
-- SET SESSION TRANSACTION ISOLATION LEVEL READ COMMITTED;
-- BEGIN;
-- SELECT balance FROM users WHERE id = 1;  -- 记录结果（例如 1521）

-- 终端 2（终端 1 事务未结束时执行）：
-- UPDATE users SET balance = 999 WHERE id = 1;
-- COMMIT;

-- 终端 1（再次查询）：
-- SELECT balance FROM users WHERE id = 1;  -- 结果变了！不可重复读
-- ROLLBACK;


-- === 演示：REPEATABLE READ（MySQL 默认）下的可重复读 ===

-- 终端 1（先执行）：
-- SET SESSION TRANSACTION ISOLATION LEVEL REPEATABLE READ;
-- BEGIN;
-- SELECT balance FROM users WHERE id = 1;  -- 记录结果

-- 终端 2（终端 1 事务未结束时执行）：
-- UPDATE users SET balance = 888 WHERE id = 1;
-- COMMIT;

-- 终端 1（再次查询，结果不变！）：
-- SELECT balance FROM users WHERE id = 1;  -- 仍是事务开始时的值（MVCC 快照）
-- COMMIT;


-- ============================================================
-- 第五部分：查看活跃事务（生产监控）
-- ============================================================

-- 4. 查看当前所有活跃事务
SELECT
    trx_id           AS 事务ID,
    trx_started      AS 开始时间,
    TIMESTAMPDIFF(SECOND, trx_started, NOW()) AS 已运行秒数,
    trx_state        AS 状态,
    LEFT(trx_query, 80) AS 当前SQL
FROM information_schema.INNODB_TRX;

-- 5. 查看当前锁等待情况（当出现锁等待时）
SELECT * FROM information_schema.INNODB_LOCK_WAITS\G

-- ============================================================
-- 清理演示数据
-- ============================================================

-- 恢复张三的余额（将 DEMO 下单的钱补回去）
UPDATE users SET balance = balance + 59.00 WHERE id = 1;
-- 恢复 MySQL必知必会 库存
UPDATE products SET stock = stock + 1 WHERE id = 15;
-- 删除演示订单
DELETE FROM orders WHERE order_no = 'ORD_DEMO_001';

-- ============================================================
-- 🏋️ 动手练习
-- ============================================================

-- 练习 1（⭐ 基础）：
-- 用一个事务完成：给用户"赵六"（id=4）购买《Redis实战》（id=16，79元）
-- 包括：扣库存、创建订单、扣余额、更新订单状态为 paid
-- 最后 COMMIT，并验证结果

-- 练习 2（⭐⭐ 进阶）：
-- 模拟失败场景：王五（id=3，余额0元）尝试购买《高性能MySQL第4版》（id=18，139元）
-- 检测到余额不足时，执行 ROLLBACK
-- 验证：库存和余额均未变化

-- 练习 3（⭐⭐⭐ 挑战）：
-- 打开两个终端，演示脏读：
--   1. 终端1 设置 READ UNCOMMITTED，开始事务，修改某用户余额但不提交
--   2. 终端2 查询该用户余额（应该能读到未提交的修改）
--   3. 终端1 ROLLBACK
--   4. 终端2 再次查询（余额恢复原值，刚才读到的是脏数据）

-- ============================================================
-- 📝 参考答案
-- ============================================================

-- 答案 1：
SELECT id, username, balance FROM users WHERE id = 4;         -- 赵六余额
SELECT id, title, price, stock FROM products WHERE id = 16;   -- Redis实战库存

BEGIN;
-- 扣库存
UPDATE products SET stock = stock - 1 WHERE id = 16 AND stock > 0;
-- 创建订单
INSERT INTO orders (order_no, user_id, product_id, quantity, total_amount, status)
VALUES ('ORD_EX_001', 4, 16, 1, 79.00, 'unpaid');
-- 扣余额
UPDATE users SET balance = balance - 79.00 WHERE id = 4 AND balance >= 79.00;
-- 更新订单状态
UPDATE orders SET status = 'paid' WHERE order_no = 'ORD_EX_001';
COMMIT;

-- 验证
SELECT id, username, balance FROM users WHERE id = 4;
SELECT id, title, stock FROM products WHERE id = 16;
SELECT order_no, status FROM orders WHERE order_no = 'ORD_EX_001';

-- 清理
DELETE FROM orders WHERE order_no = 'ORD_EX_001';
UPDATE products SET stock = stock + 1 WHERE id = 16;
UPDATE users SET balance = balance + 79.00 WHERE id = 4;

-- 答案 2：
SELECT id, username, balance FROM users WHERE id = 3;  -- 余额 0

BEGIN;
UPDATE products SET stock = stock - 1 WHERE id = 18 AND stock > 0;
INSERT INTO orders (order_no, user_id, product_id, quantity, total_amount, status)
VALUES ('ORD_EX_002', 3, 18, 1, 139.00, 'unpaid');
UPDATE users SET balance = balance - 139.00 WHERE id = 3 AND balance >= 139.00;
SELECT ROW_COUNT();  -- 0，余额不足
ROLLBACK;

-- 验证（库存未变，订单未创建）
SELECT id, title, stock FROM products WHERE id = 18;
SELECT * FROM orders WHERE order_no = 'ORD_EX_002';  -- 空

-- 答案 3（终端操作，写出步骤即可）：
-- 终端1:
-- SET SESSION TRANSACTION ISOLATION LEVEL READ UNCOMMITTED;
-- BEGIN;
-- UPDATE users SET balance = 99999 WHERE id = 1;  -- 不 COMMIT

-- 终端2:
-- SET SESSION TRANSACTION ISOLATION LEVEL READ UNCOMMITTED;
-- SELECT balance FROM users WHERE id = 1;  -- 读到 99999（脏读！）

-- 终端1:
-- ROLLBACK;

-- 终端2:
-- SELECT balance FROM users WHERE id = 1;  -- 恢复原值，脏数据已消失
