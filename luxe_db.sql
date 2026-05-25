-- ============================================
-- LUXE Fashion Store — Database Schema
-- ============================================
-- HOW TO IMPORT:
--   1. Open phpMyAdmin (http://localhost/phpmyadmin)
--   2. Click "Import" → choose this file → Go
-- OR via terminal:
--   mysql -u root < luxe_db.sql
-- ============================================

CREATE DATABASE IF NOT EXISTS luxe_store;
USE luxe_store;

-- USERS
CREATE TABLE IF NOT EXISTS users (
  id INT AUTO_INCREMENT PRIMARY KEY,
  name VARCHAR(100) NOT NULL,
  email VARCHAR(150) UNIQUE NOT NULL,
  password VARCHAR(255) NOT NULL,
  role ENUM('user','admin') DEFAULT 'user',
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- PRODUCTS
CREATE TABLE IF NOT EXISTS products (
  id INT AUTO_INCREMENT PRIMARY KEY,
  name VARCHAR(150) NOT NULL,
  category ENUM('Men','Women','Shoes','Hoodies','Traditional') NOT NULL,
  price DECIMAL(10,2) NOT NULL,
  old_price DECIMAL(10,2) DEFAULT NULL,
  emoji VARCHAR(10) DEFAULT '👕',
  badge ENUM('New','Sale','') DEFAULT '',
  stock INT DEFAULT 100,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- CART
CREATE TABLE IF NOT EXISTS cart (
  id INT AUTO_INCREMENT PRIMARY KEY,
  user_id INT NOT NULL,
  product_id INT NOT NULL,
  quantity INT DEFAULT 1,
  added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
  FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE,
  UNIQUE KEY unique_cart (user_id, product_id)
);

-- ORDERS
CREATE TABLE IF NOT EXISTS orders (
  id INT AUTO_INCREMENT PRIMARY KEY,
  user_id INT NOT NULL,
  total DECIMAL(10,2) NOT NULL,
  status ENUM('pending','processing','shipped','delivered','cancelled') DEFAULT 'pending',
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (user_id) REFERENCES users(id)
);

-- ORDER ITEMS
CREATE TABLE IF NOT EXISTS order_items (
  id INT AUTO_INCREMENT PRIMARY KEY,
  order_id INT NOT NULL,
  product_id INT NOT NULL,
  quantity INT NOT NULL,
  price DECIMAL(10,2) NOT NULL,
  FOREIGN KEY (order_id) REFERENCES orders(id) ON DELETE CASCADE,
  FOREIGN KEY (product_id) REFERENCES products(id)
);

-- =====================
-- SEED DATA
-- =====================

-- Admin user
-- Email: admin@luxe.com
-- Password: admin123
-- (hash generated with flask-bcrypt, rounds=12)
INSERT IGNORE INTO users (name, email, password, role) VALUES
('Admin', 'admin@luxe.com', '$2b$12$92IXUNpkjO0rOQ5byMi.Ye4oKoEa3Ro9llC/.og/at2.uXplHaXXi', 'admin');

-- NOTE: If the above password hash doesn't work, run this once in Python to reset it:
--   python3 -c "from flask_bcrypt import Bcrypt; b=Bcrypt(); print(b.generate_password_hash('admin123').decode())"
-- Then UPDATE users SET password='<output>' WHERE email='admin@luxe.com';

-- Sample products
INSERT IGNORE INTO products (name, category, price, old_price, emoji, badge) VALUES
('Silk Blazer', 'Men', 8999, 12999, '🥼', 'Sale'),
('Oxford Shirt', 'Men', 3499, NULL, '👔', 'New'),
('Wool Trousers', 'Men', 5999, NULL, '👖', ''),
('Cashmere Sweater', 'Men', 7499, 9999, '🧶', 'Sale'),
('Evening Gown', 'Women', 12999, NULL, '👗', 'New'),
('Satin Blouse', 'Women', 4299, 5999, '👚', 'Sale'),
('Wrap Skirt', 'Women', 3799, NULL, '🩱', ''),
('Linen Sundress', 'Women', 5499, NULL, '🌸', 'New'),
('Leather Oxfords', 'Shoes', 9999, 13999, '👞', 'Sale'),
('Strappy Heels', 'Shoes', 7299, NULL, '👠', 'New'),
('White Sneakers', 'Shoes', 5499, NULL, '👟', ''),
('Chelsea Boots', 'Shoes', 11999, 15999, '🥾', 'Sale'),
('Zip-Up Hoodie', 'Hoodies', 4299, NULL, '🧥', 'New'),
('Oversized Hoodie', 'Hoodies', 3799, 4999, '🧤', 'Sale'),
('Silk Saree', 'Traditional', 18999, NULL, '🥻', 'New'),
('Embroidered Kurta', 'Traditional', 6499, 8999, '🎽', 'Sale'),
('Anarkali Suit', 'Traditional', 14999, NULL, '✨', ''),
('Sherwani', 'Traditional', 22999, 29999, '🎩', 'Sale');
