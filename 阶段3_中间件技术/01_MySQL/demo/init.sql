-- ============================================================
-- 迷你电商系统 - 初始化脚本
-- 数据库：mysql_study
-- 运行方式：docker exec -i mysql-study mysql -u root -p123456 mysql_study < init.sql
-- ============================================================

-- 清理旧表（按外键依赖顺序删除）
DROP TABLE IF EXISTS orders;
DROP TABLE IF EXISTS products;
DROP TABLE IF EXISTS categories;
DROP TABLE IF EXISTS users;

-- ============================================================
-- 1. 用户表
-- ============================================================
CREATE TABLE users (
    id          INT UNSIGNED AUTO_INCREMENT PRIMARY KEY COMMENT '用户ID',
    username    VARCHAR(50)  NOT NULL UNIQUE COMMENT '用户名',
    email       VARCHAR(100) NOT NULL UNIQUE COMMENT '邮箱',
    phone       CHAR(11)     NOT NULL COMMENT '手机号',
    password_hash VARCHAR(255) NOT NULL COMMENT '密码哈希（bcrypt）',
    balance     DECIMAL(10, 2) NOT NULL DEFAULT 0.00 COMMENT '账户余额（元）',
    status      ENUM('active', 'disabled', 'inactive') NOT NULL DEFAULT 'active' COMMENT '账户状态',
    created_at  DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '注册时间',
    updated_at  DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '最后更新'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='用户表';

-- ============================================================
-- 2. 商品分类表
-- ============================================================
CREATE TABLE categories (
    id          INT UNSIGNED AUTO_INCREMENT PRIMARY KEY COMMENT '分类ID',
    name        VARCHAR(50)  NOT NULL UNIQUE COMMENT '分类名称',
    description VARCHAR(200) COMMENT '分类描述',
    created_at  DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='商品分类表';

-- ============================================================
-- 3. 商品表
-- ============================================================
CREATE TABLE products (
    id          INT UNSIGNED AUTO_INCREMENT PRIMARY KEY COMMENT '商品ID',
    title       VARCHAR(100) NOT NULL COMMENT '商品名称',
    category_id INT UNSIGNED NOT NULL COMMENT '所属分类',
    price       DECIMAL(10, 2) NOT NULL COMMENT '售价（元）',
    stock       INT NOT NULL DEFAULT 0 COMMENT '库存数量',
    status      ENUM('on_sale', 'off_sale', 'sold_out') NOT NULL DEFAULT 'on_sale' COMMENT '商品状态',
    created_at  DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at  DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT fk_product_category FOREIGN KEY (category_id) REFERENCES categories(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='商品表';

-- ============================================================
-- 4. 订单表
-- ============================================================
CREATE TABLE orders (
    id           INT UNSIGNED AUTO_INCREMENT PRIMARY KEY COMMENT '订单ID',
    order_no     VARCHAR(32)  NOT NULL UNIQUE COMMENT '订单编号（唯一）',
    user_id      INT UNSIGNED NOT NULL COMMENT '下单用户',
    product_id   INT UNSIGNED NOT NULL COMMENT '购买商品',
    quantity     INT NOT NULL DEFAULT 1 COMMENT '购买数量',
    total_amount DECIMAL(10, 2) NOT NULL COMMENT '订单总金额',
    status       ENUM('unpaid', 'paid', 'cancelled', 'refunded') NOT NULL DEFAULT 'unpaid' COMMENT '订单状态',
    created_at   DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '下单时间',
    updated_at   DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT fk_order_user    FOREIGN KEY (user_id)    REFERENCES users(id),
    CONSTRAINT fk_order_product FOREIGN KEY (product_id) REFERENCES products(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='订单表';

-- ============================================================
-- Mock 数据：用户（10 条）
-- ============================================================
INSERT INTO users (username, email, phone, password_hash, balance, status) VALUES
('张三',   'zhangsan@example.com', '13800001001', '$2b$12$hash_zhangsan', 1580.00, 'active'),
('李四',   'lisi@example.com',     '13800001002', '$2b$12$hash_lisi',     320.50,  'active'),
('王五',   'wangwu@example.com',   '13800001003', '$2b$12$hash_wangwu',   0.00,    'inactive'),
('赵六',   'zhaoliu@example.com',  '13800001004', '$2b$12$hash_zhaoliu',  9999.99, 'active'),
('孙七',   'sunqi@example.com',    '13800001005', '$2b$12$hash_sunqi',    88.00,   'disabled'),
('周八',   'zhouba@example.com',   '13800001006', '$2b$12$hash_zhouba',   450.00,  'active'),
('吴九',   'wujiu@example.com',    '13800001007', '$2b$12$hash_wujiu',    2100.00, 'active'),
('郑十',   'zhengshi@example.com', '13800001008', '$2b$12$hash_zhengshi', 60.00,   'active'),
('陈一一', 'chenyiyi@example.com', '13800001009', '$2b$12$hash_chenyiyi', 780.00,  'active'),
('林二二', 'linoror@example.com',  '13800001010', '$2b$12$hash_linerer',  0.00,    'inactive');

-- ============================================================
-- Mock 数据：商品分类（5 条）
-- ============================================================
INSERT INTO categories (name, description) VALUES
('电子产品', '手机、平板、电脑等数码设备'),
('服装',     '男装、女装、童装'),
('食品',     '零食、生鲜、饮料'),
('图书',     '技术书籍、文学、教辅'),
('家居',     '家具、厨具、装饰品');

-- ============================================================
-- Mock 数据：商品（20 条）
-- ============================================================
INSERT INTO products (title, category_id, price, stock, status) VALUES
-- 电子产品（category_id=1）
('iPhone 16 Pro 256G',       1, 9999.00, 50,  'on_sale'),
('华为 Mate 70 Pro',         1, 6999.00, 80,  'on_sale'),
('小米平板 7 Pro',            1, 2999.00, 120, 'on_sale'),
('AirPods Pro 第3代',        1, 1799.00, 200, 'on_sale'),
('戴尔 XPS 15 笔记本',       1, 12999.00, 20, 'on_sale'),
-- 服装（category_id=2）
('优衣库摇粒绒外套',          2, 299.00, 500,  'on_sale'),
('耐克Air Max 2024',         2, 899.00, 150,  'on_sale'),
('Levi\'s 501 牛仔裤',       2, 599.00, 300,  'on_sale'),
('无印良品纯棉T恤',           2, 129.00, 800,  'on_sale'),
('阿迪达斯三叶草卫衣',        2, 499.00, 0,    'sold_out'),
-- 食品（category_id=3）
('三只松鼠混合坚果1kg',       3, 89.90,  1000, 'on_sale'),
('蒙牛纯牛奶整箱24盒',        3, 69.90,  500,  'on_sale'),
('农夫山泉矿泉水24瓶',        3, 29.90,  2000, 'on_sale'),
('海天老抽酱油500ml',         3, 15.90,  800,  'on_sale'),
-- 图书（category_id=4）
('MySQL必知必会',             4, 59.00,  300,  'on_sale'),
('Redis实战',                4, 79.00,  200,  'on_sale'),
('Python编程：从入门到实践',  4, 89.00,  400,  'on_sale'),
('高性能MySQL第4版',          4, 139.00, 150,  'off_sale'),
-- 家居（category_id=5）
('宜家BEKANT升降桌',          5, 4999.00, 30,  'on_sale'),
('飞利浦LED护眼台灯',         5, 199.00, 600,  'on_sale');

-- ============================================================
-- Mock 数据：订单（28 条）
-- ============================================================
INSERT INTO orders (order_no, user_id, product_id, quantity, total_amount, status, created_at) VALUES
-- 张三的订单（user_id=1）
('ORD20260101001', 1, 1,  1, 9999.00, 'paid',      '2026-01-15 10:30:00'),
('ORD20260102001', 1, 15, 2, 118.00,  'paid',      '2026-01-22 14:00:00'),
('ORD20260103001', 1, 11, 1, 89.90,   'unpaid',    '2026-03-01 09:00:00'),
-- 李四的订单（user_id=2）
('ORD20260201001', 2, 7,  1, 899.00,  'paid',      '2026-02-05 11:00:00'),
('ORD20260202001', 2, 12, 2, 139.80,  'paid',      '2026-02-10 16:30:00'),
('ORD20260203001', 2, 20, 1, 199.00,  'cancelled', '2026-02-28 08:00:00'),
-- 赵六的订单（user_id=4）
('ORD20260301001', 4, 5,  1, 12999.00,'paid',      '2026-01-08 20:00:00'),
('ORD20260302001', 4, 2,  2, 13998.00,'paid',      '2026-02-14 12:00:00'),
('ORD20260303001', 4, 19, 1, 4999.00, 'refunded',  '2026-03-05 15:00:00'),
('ORD20260304001', 4, 4,  3, 5397.00, 'paid',      '2026-03-10 10:00:00'),
-- 周八的订单（user_id=6）
('ORD20260401001', 6, 6,  2, 598.00,  'paid',      '2026-01-20 13:00:00'),
('ORD20260402001', 6, 9,  3, 387.00,  'paid',      '2026-02-01 09:30:00'),
('ORD20260403001', 6, 13, 5, 149.50,  'unpaid',    '2026-03-15 17:00:00'),
-- 吴九的订单（user_id=7）
('ORD20260501001', 7, 3,  1, 2999.00, 'paid',      '2026-01-25 10:00:00'),
('ORD20260502001', 7, 16, 1, 79.00,   'paid',      '2026-02-03 14:00:00'),
('ORD20260503001', 7, 17, 2, 178.00,  'paid',      '2026-02-20 11:00:00'),
('ORD20260504001', 7, 1,  1, 9999.00, 'unpaid',    '2026-03-18 16:00:00'),
-- 郑十的订单（user_id=8）
('ORD20260601001', 8, 14, 2, 31.80,   'paid',      '2026-02-08 10:00:00'),
('ORD20260602001', 8, 11, 1, 89.90,   'cancelled', '2026-02-25 12:00:00'),
-- 陈一一的订单（user_id=9）
('ORD20260701001', 9, 8,  1, 599.00,  'paid',      '2026-01-30 15:00:00'),
('ORD20260702001', 9, 2,  1, 6999.00, 'paid',      '2026-02-12 09:00:00'),
('ORD20260703001', 9, 15, 3, 177.00,  'refunded',  '2026-03-02 14:00:00'),
('ORD20260704001', 9, 20, 2, 398.00,  'paid',      '2026-03-20 10:30:00'),
-- 林二二（user_id=10，inactive 状态仍有历史订单）
('ORD20251201001', 10, 6, 1, 299.00,  'paid',      '2025-12-01 10:00:00'),
('ORD20251202001', 10, 9, 2, 258.00,  'cancelled', '2025-12-15 14:00:00'),
-- 补充：跨月大额订单
('ORD20260801001', 4, 5,  2, 25998.00,'paid',      '2026-04-01 10:00:00'),
('ORD20260802001', 7, 4,  5, 8995.00, 'paid',      '2026-04-05 11:00:00'),
('ORD20260803001', 1, 19, 1, 4999.00, 'unpaid',    '2026-04-10 09:00:00');

-- ============================================================
-- 验证：查看各表数据量
-- ============================================================
SELECT '=== 数据初始化完成 ===' AS message;
SELECT CONCAT('users: ',     COUNT(*), ' rows') AS table_stats FROM users
UNION ALL
SELECT CONCAT('categories: ', COUNT(*), ' rows') FROM categories
UNION ALL
SELECT CONCAT('products: ',   COUNT(*), ' rows') FROM products
UNION ALL
SELECT CONCAT('orders: ',     COUNT(*), ' rows') FROM orders;
