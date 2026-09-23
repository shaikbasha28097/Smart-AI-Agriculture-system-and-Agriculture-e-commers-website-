-- Smart AI Agriculture Ecosystem Database Schema
-- Compatible with MySQL (XAMPP/MariaDB) and SQLite

CREATE DATABASE IF NOT EXISTS smart_agri_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE smart_agri_db;

-- 1. Users Table (Common Authentication)
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(120) NOT NULL,
    email VARCHAR(150) UNIQUE NOT NULL,
    phone VARCHAR(20),
    password_hash VARCHAR(255) NOT NULL,
    role ENUM('farmer', 'seller', 'buyer', 'admin') NOT NULL DEFAULT 'farmer',
    avatar VARCHAR(255) DEFAULT '/static/img/default-avatar.png',
    address TEXT,
    city VARCHAR(100),
    state VARCHAR(100),
    pincode VARCHAR(20),
    is_active TINYINT(1) DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- 2. Farmer Profiles
CREATE TABLE IF NOT EXISTS farmer_profiles (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    farm_size_acres DECIMAL(8, 2) DEFAULT 2.5,
    soil_type VARCHAR(100) DEFAULT 'Loamy',
    primary_crops VARCHAR(255) DEFAULT 'Rice, Wheat, Tomato',
    irrigation_source VARCHAR(100) DEFAULT 'Borewell / Drip',
    experience_years INT DEFAULT 5,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- 3. Seller Profiles
CREATE TABLE IF NOT EXISTS seller_profiles (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    business_name VARCHAR(150) NOT NULL,
    license_number VARCHAR(100),
    gst_number VARCHAR(50),
    warehouse_location VARCHAR(200),
    rating DECIMAL(3, 2) DEFAULT 4.8,
    total_sales DECIMAL(12, 2) DEFAULT 0.00,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- 4. Buyer Profiles
CREATE TABLE IF NOT EXISTS buyer_profiles (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    buyer_type ENUM('individual', 'retailer', 'wholesaler', 'restaurant') DEFAULT 'individual',
    delivery_address TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- 5. Product Categories
CREATE TABLE IF NOT EXISTS product_categories (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE,
    slug VARCHAR(100) NOT NULL UNIQUE,
    icon VARCHAR(50) DEFAULT 'fa-leaf',
    description TEXT
);

-- 6. Marketplace Products (Agri-Inputs, Fertilizers, Seeds, Fresh Produce)
CREATE TABLE IF NOT EXISTS products (
    id INT AUTO_INCREMENT PRIMARY KEY,
    seller_id INT,
    farmer_id INT,
    category_id INT NOT NULL,
    name VARCHAR(200) NOT NULL,
    slug VARCHAR(200),
    short_description VARCHAR(255),
    description TEXT,
    price DECIMAL(10, 2) NOT NULL,
    unit VARCHAR(50) DEFAULT 'kg', -- kg, litre, packet, piece
    stock_quantity DECIMAL(10, 2) NOT NULL DEFAULT 100,
    image_url VARCHAR(255) NOT NULL,
    is_organic TINYINT(1) DEFAULT 0,
    rating DECIMAL(3, 2) DEFAULT 4.5,
    remedy_for_disease VARCHAR(150), -- Links disease recommendations to product
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (seller_id) REFERENCES users(id) ON DELETE SET NULL,
    FOREIGN KEY (farmer_id) REFERENCES users(id) ON DELETE SET NULL,
    FOREIGN KEY (category_id) REFERENCES product_categories(id)
);

-- 7. Farmer Harvests (Sell My Crop workflow -> Seller picks up)
CREATE TABLE IF NOT EXISTS harvests (
    id INT AUTO_INCREMENT PRIMARY KEY,
    farmer_id INT NOT NULL,
    crop_name VARCHAR(100) NOT NULL,
    variety VARCHAR(100),
    quantity DECIMAL(10, 2) NOT NULL,
    unit VARCHAR(20) DEFAULT 'KG',
    expected_price_per_unit DECIMAL(10, 2) NOT NULL,
    harvest_date DATE NOT NULL,
    quality ENUM('Premium', 'Grade A', 'Standard', 'Organic Certified') DEFAULT 'Premium',
    location VARCHAR(150) NOT NULL,
    description TEXT,
    image_url VARCHAR(255),
    status ENUM('available', 'purchased_by_seller', 'in_negotiation', 'completed') DEFAULT 'available',
    purchased_by_seller_id INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (farmer_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (purchased_by_seller_id) REFERENCES users(id) ON DELETE SET NULL
);

-- 8. Cart Items
CREATE TABLE IF NOT EXISTS cart_items (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    product_id INT NOT NULL,
    quantity DECIMAL(8, 2) DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE
);

-- 9. Orders
CREATE TABLE IF NOT EXISTS orders (
    id INT AUTO_INCREMENT PRIMARY KEY,
    order_number VARCHAR(50) UNIQUE NOT NULL,
    buyer_id INT NOT NULL,
    total_amount DECIMAL(10, 2) NOT NULL,
    discount_amount DECIMAL(10, 2) DEFAULT 0.00,
    delivery_fee DECIMAL(10, 2) DEFAULT 0.00,
    payment_method ENUM('cod', 'upi', 'card', 'netbanking') DEFAULT 'upi',
    payment_status ENUM('pending', 'paid', 'failed') DEFAULT 'paid',
    order_status ENUM('placed', 'processing', 'shipped', 'out_for_delivery', 'delivered', 'cancelled') DEFAULT 'placed',
    shipping_address TEXT NOT NULL,
    contact_phone VARCHAR(20) NOT NULL,
    tracking_number VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (buyer_id) REFERENCES users(id) ON DELETE CASCADE
);

-- 10. Order Items
CREATE TABLE IF NOT EXISTS order_items (
    id INT AUTO_INCREMENT PRIMARY KEY,
    order_id INT NOT NULL,
    product_id INT NOT NULL,
    quantity DECIMAL(8, 2) NOT NULL,
    unit_price DECIMAL(10, 2) NOT NULL,
    total_price DECIMAL(10, 2) NOT NULL,
    FOREIGN KEY (order_id) REFERENCES orders(id) ON DELETE CASCADE,
    FOREIGN KEY (product_id) REFERENCES products(id)
);

-- 11. Disease Detection History
CREATE TABLE IF NOT EXISTS disease_records (
    id INT AUTO_INCREMENT PRIMARY KEY,
    farmer_id INT,
    crop_name VARCHAR(100) NOT NULL,
    disease_name VARCHAR(150) NOT NULL,
    confidence_score DECIMAL(5, 2) NOT NULL,
    image_url VARCHAR(255),
    organic_treatment TEXT,
    chemical_treatment TEXT,
    recommended_product_id INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (farmer_id) REFERENCES users(id) ON DELETE SET NULL,
    FOREIGN KEY (recommended_product_id) REFERENCES products(id) ON DELETE SET NULL
);

-- 12. Soil & AI Crop Predictions
CREATE TABLE IF NOT EXISTS crop_predictions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    farmer_id INT,
    nitrogen DECIMAL(6, 2),
    phosphorus DECIMAL(6, 2),
    potassium DECIMAL(6, 2),
    ph_level DECIMAL(4, 2),
    temperature DECIMAL(5, 2),
    humidity DECIMAL(5, 2),
    rainfall DECIMAL(6, 2),
    recommended_crop VARCHAR(100) NOT NULL,
    expected_yield_per_acre VARCHAR(100),
    estimated_roi_percent INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (farmer_id) REFERENCES users(id) ON DELETE SET NULL
);

-- 13. Notifications
CREATE TABLE IF NOT EXISTS notifications (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    title VARCHAR(150) NOT NULL,
    message TEXT NOT NULL,
    type ENUM('harvest', 'order', 'disease', 'weather', 'general') DEFAULT 'general',
    link_url VARCHAR(255),
    is_read TINYINT(1) DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- 14. Product Reviews
CREATE TABLE IF NOT EXISTS reviews (
    id INT AUTO_INCREMENT PRIMARY KEY,
    product_id INT NOT NULL,
    user_id INT NOT NULL,
    rating INT DEFAULT 5,
    comment TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- =======================================================
-- INITIAL SEED DATA
-- =======================================================

-- Categories
INSERT INTO product_categories (id, name, slug, icon, description) VALUES
(1, 'Organic Fertilizers & Remedies', 'organic-fertilizers', 'fa-seedling', 'Bio-fertilizers, neem cake, vermicompost, and organic treatments'),
(2, 'Chemical Fertilizers & Fungicides', 'chemical-fertilizers', 'fa-flask', 'NPK, DAP, Urea, Copper Oxychloride, and disease control sprays'),
(3, 'Fresh Farm Harvest', 'fresh-harvest', 'fa-carrot', 'Direct from farmer grains, vegetables, and seasonal fruits'),
(4, 'Certified Hybrid Seeds', 'seeds', 'fa-spa', 'High-yield drought-tolerant certified seeds'),
(5, 'Smart Farming Tools', 'tools', 'fa-tools', 'Soil testing meters, drip kits, sprayers, and sensors')
ON DUPLICATE KEY UPDATE name=VALUES(name);

-- Default Users (Password for all demo accounts: 'password123')
-- Hash for password123 with sha256 or werkzeug
INSERT INTO users (id, name, email, phone, password_hash, role, city, state) VALUES
(1, 'Shaik Basha (Farmer)', 'farmer@smartagri.com', '9876543210', 'pbkdf2:sha256:600000$farmer123$ef4827018c1e7a6f9f303274dfd38a0bc985a190b2984a92c0fa168a2bf19416', 'farmer', 'Hyderabad', 'Telangana'),
(2, 'ABC Agro Traders (Seller)', 'seller@smartagri.com', '9876543211', 'pbkdf2:sha256:600000$seller123$ef4827018c1e7a6f9f303274dfd38a0bc985a190b2984a92c0fa168a2bf19416', 'seller', 'Warangal', 'Telangana'),
(3, 'Ramesh Kumar (Buyer)', 'buyer@smartagri.com', '9876543212', 'pbkdf2:sha256:600000$buyer123$ef4827018c1e7a6f9f303274dfd38a0bc985a190b2984a92c0fa168a2bf19416', 'buyer', 'Hyderabad', 'Telangana')
ON DUPLICATE KEY UPDATE name=VALUES(name);

-- Profiles
INSERT INTO farmer_profiles (user_id, farm_size_acres, soil_type, primary_crops, irrigation_source) VALUES
(1, 5.0, 'Red Loamy', 'Rice, Tomato, Cotton', 'Drip & Borewell')
ON DUPLICATE KEY UPDATE farm_size_acres=VALUES(farm_size_acres);

INSERT INTO seller_profiles (user_id, business_name, license_number, warehouse_location, rating, total_sales) VALUES
(2, 'ABC Agro Trading Corp', 'AGRI-TS-2026-998', 'Central Mandi Yard, Warangal', 4.9, 154200.00)
ON DUPLICATE KEY UPDATE business_name=VALUES(business_name);

INSERT INTO buyer_profiles (user_id, buyer_type, delivery_address) VALUES
(3, 'individual', 'Flat 402, Green Meadows, Madhapur, Hyderabad')
ON DUPLICATE KEY UPDATE buyer_type=VALUES(buyer_type);

-- Products Seed Data (Featuring remedies for AI Disease Detection workflow!)
INSERT INTO products (id, seller_id, category_id, name, slug, short_description, description, price, unit, stock_quantity, image_url, is_organic, rating, remedy_for_disease) VALUES
(1, 2, 1, 'Organic Copper Oxychloride Fungicide 50% WP', 'organic-copper-fungicide', 'Broad spectrum bio-fungicide for Early & Late Blight, Leaf Spot', 'Protects tomato, potato, and vegetable crops from early blight, late blight, and bacterial spots. Certified organic composition.', 350.00, '500g Pack', 120, 'https://images.unsplash.com/photo-1585314062340-f1a5a7c9328d?w=500&auto=format&fit=crop&q=60', 1, 4.9, 'Early Blight'),
(2, 2, 1, 'Pure Cold-Pressed Neem Oil Spray (10,000 PPM)', 'pure-neem-oil-spray', 'Natural organic repellent for pests, aphids, and powdery mildew', '100% pure organic neem oil with azadirachtin 10000 PPM. Ideal for eco-friendly pest control and foliar fungal prevention.', 280.00, '1 Litre Bottle', 200, 'https://images.unsplash.com/photo-1615485290382-441e4d049cb5?w=500&auto=format&fit=crop&q=60', 1, 4.8, 'Powdery Mildew'),
(3, 2, 2, 'Mancozeb 75% WP Contact Fungicide', 'mancozeb-75-wp', 'Powerful protective fungicide against fungal blast and leaf blight', 'High-grade protective contact fungicide effective on a wide range of field crops, fruits, and vegetables against blast, rust, and blight.', 420.00, '1 KG Pack', 85, 'https://images.unsplash.com/photo-1592417817098-8f3d6eb22509?w=500&auto=format&fit=crop&q=60', 0, 4.7, 'Late Blight'),
(4, 2, 2, 'Water Soluble NPK 19-19-19 Fertilizer', 'npk-19-19-19', 'Balanced plant nutrition for rapid vegetative and fruit development', '100% water-soluble specialty fertilizer supplying balanced Nitrogen, Phosphorus, and Potassium for drip and foliar applications.', 180.00, '1 KG Pack', 350, 'https://images.unsplash.com/photo-1574943320219-553eb213f72d?w=500&auto=format&fit=crop&q=60', 0, 4.9, 'Nutrient Deficiency'),
(5, 2, 3, 'Premium Sona Masoori Rice (Farm Fresh)', 'premium-sona-masoori-rice', 'Aged, naturally aromatic unpolished rice straight from farm harvest', 'Grown with minimal chemical intervention, clean harvested, aged 12 months for fluffiness and nutritional value.', 55.00, 'KG', 1500, 'https://images.unsplash.com/photo-1586201375761-83865001e31c?w=500&auto=format&fit=crop&q=60', 1, 4.9, NULL),
(6, 2, 3, 'Organic Farm Fresh Tomatoes', 'organic-farm-fresh-tomatoes', 'Vine-ripened, juicy red farm fresh hybrid tomatoes', 'Freshly picked daily from local organic farmer fields. Rich in lycopene, firm texture.', 35.00, 'KG', 400, 'https://images.unsplash.com/photo-1592924357228-91a4daadcfea?w=500&auto=format&fit=crop&q=60', 1, 4.8, NULL),
(7, 2, 4, 'High Yield Certified Tomato F1 Hybrid Seeds', 'tomato-f1-hybrid-seeds', 'Disease-resistant high yield tomato seeds (10g pack)', 'Germination rate 95%, resistant to bacterial wilt and tomato mosaic virus. High yield potential up to 35 tons/acre.', 199.00, 'Pack of 10g', 150, 'https://images.unsplash.com/photo-1530595467537-0b5996c41f2d?w=500&auto=format&fit=crop&q=60', 1, 4.9, NULL),
(8, 2, 5, 'Digital 4-in-1 Soil Tester (pH, Moisture, Temp, Sunlight)', 'digital-soil-tester', 'Precision probe meter for instant field soil testing', 'Measure soil pH, moisture levels, soil temperature, and sunlight intensity without batteries.', 899.00, 'Piece', 50, 'https://images.unsplash.com/photo-1523348837708-15d4a09cfac2?w=500&auto=format&fit=crop&q=60', 0, 4.9, NULL)
ON DUPLICATE KEY UPDATE name=VALUES(name);

-- Sample Harvest posted by Farmer
INSERT INTO harvests (id, farmer_id, crop_name, variety, quantity, unit, expected_price_per_unit, harvest_date, quality, location, description, status) VALUES
(1, 1, 'Rice', 'Sona Masoori', 500.00, 'KG', 42.00, '2026-09-23', 'Premium', 'Hyderabad, Telangana', 'Freshly harvested, sun-dried, moisture under 12%, premium golden grain quality.', 'available'),
(2, 1, 'Tomatoes', 'Hybrid Red', 200.00, 'KG', 25.00, '2026-09-22', 'Grade A', 'Rangareddy, Telangana', 'Firm, ripe organic farm tomatoes ready for immediate pickup.', 'available')
ON DUPLICATE KEY UPDATE crop_name=VALUES(crop_name);

-- Sample Notifications
INSERT INTO notifications (user_id, title, message, type, link_url) VALUES
(1, 'Welcome to Smart AI Farming', 'Explore AI Crop Recommendation and Leaf Disease Scanner on your dashboard!', 'general', '/farmer#ai-tools'),
(2, 'New Farmer Harvest Available', 'Farmer Shaik Basha posted 500 KG Rice at ₹42/kg in Hyderabad.', 'harvest', '/seller#farmer-harvests'),
(3, 'Fresh Farm Harvest Arrived', 'Explore freshly harvested Sona Masoori Rice and Organic Tomatoes in E-Mart.', 'order', '/buyer#catalog');

