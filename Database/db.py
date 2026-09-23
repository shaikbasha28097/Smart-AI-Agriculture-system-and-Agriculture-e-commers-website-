import os
import sqlite3
import pymysql
from pymysql.cursors import DictCursor
from config import Config

class Database:
    def __init__(self):
        self.use_mysql = False
        self.test_connection()

    def test_connection(self):
        """Attempts to connect to MySQL; falls back to SQLite if unreachable."""
        try:
            conn = pymysql.connect(
                host=Config.MYSQL_HOST,
                port=Config.MYSQL_PORT,
                user=Config.MYSQL_USER,
                password=Config.MYSQL_PASSWORD,
                cursorclass=DictCursor,
                connect_timeout=2
            )
            # Check/create database
            with conn.cursor() as cursor:
                cursor.execute(f"CREATE DATABASE IF NOT EXISTS `{Config.MYSQL_DB}` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
            conn.select_db(Config.MYSQL_DB)
            conn.close()
            self.use_mysql = True
            print(" Connected to MySQL Database successfully.")
        except Exception as e:
            print(f" MySQL not reachable ({e}). Using robust SQLite Database fallback.")
            self.use_mysql = False
            self.init_sqlite()

    def get_connection(self):
        """Returns a database connection object."""
        if self.use_mysql:
            try:
                return pymysql.connect(
                    host=Config.MYSQL_HOST,
                    port=Config.MYSQL_PORT,
                    user=Config.MYSQL_USER,
                    password=Config.MYSQL_PASSWORD,
                    database=Config.MYSQL_DB,
                    cursorclass=DictCursor,
                    autocommit=True
                )
            except Exception:
                self.use_mysql = False
                return self.get_sqlite_connection()
        else:
            return self.get_sqlite_connection()

    def get_sqlite_connection(self):
        os.makedirs(os.path.dirname(Config.SQLITE_DB_PATH), exist_ok=True)
        conn = sqlite3.connect(Config.SQLITE_DB_PATH)
        conn.row_factory = sqlite3.Row
        return conn

    def query(self, sql, params=None, fetchone=False, fetchall=True, insert=False):
        """Universal query executor supporting both MySQL & SQLite dialect differences."""
        conn = self.get_connection()
        params = params or ()
        try:
            if self.use_mysql:
                with conn.cursor() as cursor:
                    # Convert ? placeholders to %s for MySQL if needed
                    sql_converted = sql.replace('?', '%s')
                    cursor.execute(sql_converted, params)
                    if insert:
                        last_id = cursor.lastrowid
                        conn.close()
                        return last_id
                    if fetchone:
                        res = cursor.fetchone()
                        conn.close()
                        return res
                    if fetchall:
                        res = cursor.fetchall()
                        conn.close()
                        return res
                    conn.close()
                    return cursor.rowcount
            else:
                # SQLite execution
                cursor = conn.cursor()
                sql_converted = sql.replace('%s', '?')
                cursor.execute(sql_converted, params)
                if insert:
                    conn.commit()
                    last_id = cursor.lastrowid
                    conn.close()
                    return last_id
                if fetchone:
                    row = cursor.fetchone()
                    conn.close()
                    return dict(row) if row else None
                if fetchall:
                    rows = cursor.fetchall()
                    conn.close()
                    return [dict(r) for r in rows]
                conn.commit()
                rowcount = cursor.rowcount
                conn.close()
                return rowcount
        except Exception as e:
            if conn:
                conn.close()
            print(f" Database query error: {e} in query [{sql}]")
            raise e

    def init_sqlite(self):
        """Initializes SQLite tables and seed data if not present."""
        conn = self.get_sqlite_connection()
        cursor = conn.cursor()
        
        # Create Tables for SQLite
        cursor.executescript('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            phone TEXT,
            password_hash TEXT NOT NULL,
            role TEXT NOT NULL DEFAULT 'farmer',
            avatar TEXT DEFAULT '/static/img/default-avatar.png',
            address TEXT,
            city TEXT,
            state TEXT,
            pincode TEXT,
            is_active INTEGER DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS farmer_profiles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            farm_size_acres REAL DEFAULT 2.5,
            soil_type TEXT DEFAULT 'Loamy',
            primary_crops TEXT DEFAULT 'Rice, Wheat, Tomato',
            irrigation_source TEXT DEFAULT 'Borewell / Drip',
            experience_years INTEGER DEFAULT 5,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        );

        CREATE TABLE IF NOT EXISTS seller_profiles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            business_name TEXT NOT NULL,
            license_number TEXT,
            gst_number TEXT,
            warehouse_location TEXT,
            rating REAL DEFAULT 4.8,
            total_sales REAL DEFAULT 0.00,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        );

        CREATE TABLE IF NOT EXISTS buyer_profiles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            buyer_type TEXT DEFAULT 'individual',
            delivery_address TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        );

        CREATE TABLE IF NOT EXISTS product_categories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            slug TEXT NOT NULL UNIQUE,
            icon TEXT DEFAULT 'fa-leaf',
            description TEXT
        );

        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            seller_id INTEGER,
            farmer_id INTEGER,
            category_id INTEGER NOT NULL,
            name TEXT NOT NULL,
            slug TEXT,
            short_description TEXT,
            description TEXT,
            price REAL NOT NULL,
            unit TEXT DEFAULT 'kg',
            stock_quantity REAL NOT NULL DEFAULT 100,
            image_url TEXT NOT NULL,
            is_organic INTEGER DEFAULT 0,
            rating REAL DEFAULT 4.5,
            remedy_for_disease TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (seller_id) REFERENCES users(id) ON DELETE SET NULL,
            FOREIGN KEY (category_id) REFERENCES product_categories(id)
        );

        CREATE TABLE IF NOT EXISTS harvests (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            farmer_id INTEGER NOT NULL,
            crop_name TEXT NOT NULL,
            variety TEXT,
            quantity REAL NOT NULL,
            unit TEXT DEFAULT 'KG',
            expected_price_per_unit REAL NOT NULL,
            harvest_date TEXT NOT NULL,
            quality TEXT DEFAULT 'Premium',
            location TEXT NOT NULL,
            description TEXT,
            image_url TEXT,
            status TEXT DEFAULT 'available',
            purchased_by_seller_id INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (farmer_id) REFERENCES users(id) ON DELETE CASCADE
        );

        CREATE TABLE IF NOT EXISTS cart_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            product_id INTEGER NOT NULL,
            quantity REAL DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
            FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE
        );

        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            order_number TEXT UNIQUE NOT NULL,
            buyer_id INTEGER NOT NULL,
            total_amount REAL NOT NULL,
            discount_amount REAL DEFAULT 0.00,
            delivery_fee REAL DEFAULT 0.00,
            payment_method TEXT DEFAULT 'upi',
            payment_status TEXT DEFAULT 'paid',
            order_status TEXT DEFAULT 'placed',
            shipping_address TEXT NOT NULL,
            contact_phone TEXT NOT NULL,
            tracking_number TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (buyer_id) REFERENCES users(id) ON DELETE CASCADE
        );

        CREATE TABLE IF NOT EXISTS order_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            order_id INTEGER NOT NULL,
            product_id INTEGER NOT NULL,
            quantity REAL NOT NULL,
            unit_price REAL NOT NULL,
            total_price REAL NOT NULL,
            FOREIGN KEY (order_id) REFERENCES orders(id) ON DELETE CASCADE,
            FOREIGN KEY (product_id) REFERENCES products(id)
        );

        CREATE TABLE IF NOT EXISTS disease_records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            farmer_id INTEGER,
            crop_name TEXT NOT NULL,
            disease_name TEXT NOT NULL,
            confidence_score REAL NOT NULL,
            image_url TEXT,
            organic_treatment TEXT,
            chemical_treatment TEXT,
            recommended_product_id INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (farmer_id) REFERENCES users(id) ON DELETE SET NULL
        );

        CREATE TABLE IF NOT EXISTS crop_predictions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            farmer_id INTEGER,
            nitrogen REAL,
            phosphorus REAL,
            potassium REAL,
            ph_level REAL,
            temperature REAL,
            humidity REAL,
            rainfall REAL,
            recommended_crop TEXT NOT NULL,
            expected_yield_per_acre TEXT,
            estimated_roi_percent INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (farmer_id) REFERENCES users(id) ON DELETE SET NULL
        );

        CREATE TABLE IF NOT EXISTS notifications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            title TEXT NOT NULL,
            message TEXT NOT NULL,
            type TEXT DEFAULT 'general',
            link_url TEXT,
            is_read INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        );
        ''')
        
        # Check seed categories
        cursor.execute("SELECT COUNT(*) FROM product_categories")
        if cursor.fetchone()[0] == 0:
            cursor.executescript('''
            INSERT INTO product_categories (id, name, slug, icon, description) VALUES
            (1, 'Organic Fertilizers & Remedies', 'organic-fertilizers', 'fa-seedling', 'Bio-fertilizers, neem cake, vermicompost, and organic treatments'),
            (2, 'Chemical Fertilizers & Fungicides', 'chemical-fertilizers', 'fa-flask', 'NPK, DAP, Urea, Copper Oxychloride, and disease control sprays'),
            (3, 'Fresh Farm Harvest', 'fresh-harvest', 'fa-carrot', 'Direct from farmer grains, vegetables, and seasonal fruits'),
            (4, 'Certified Hybrid Seeds', 'seeds', 'fa-spa', 'High-yield drought-tolerant certified seeds'),
            (5, 'Smart Farming Tools', 'tools', 'fa-tools', 'Soil testing meters, drip kits, sprayers, and sensors');

            INSERT INTO users (id, name, email, phone, password_hash, role, city, state) VALUES
            (1, 'Shaik Basha (Farmer)', 'farmer@smartagri.com', '9876543210', 'pbkdf2:sha256:600000$farmer123$ef4827018c1e7a6f9f303274dfd38a0bc985a190b2984a92c0fa168a2bf19416', 'farmer', 'Hyderabad', 'Telangana'),
            (2, 'ABC Agro Traders (Seller)', 'seller@smartagri.com', '9876543211', 'pbkdf2:sha256:600000$seller123$ef4827018c1e7a6f9f303274dfd38a0bc985a190b2984a92c0fa168a2bf19416', 'seller', 'Warangal', 'Telangana'),
            (3, 'Ramesh Kumar (Buyer)', 'buyer@smartagri.com', '9876543212', 'pbkdf2:sha256:600000$buyer123$ef4827018c1e7a6f9f303274dfd38a0bc985a190b2984a92c0fa168a2bf19416', 'buyer', 'Hyderabad', 'Telangana');

            INSERT INTO farmer_profiles (user_id, farm_size_acres, soil_type, primary_crops, irrigation_source) VALUES
            (1, 5.0, 'Red Loamy', 'Rice, Tomato, Cotton', 'Drip & Borewell');

            INSERT INTO seller_profiles (user_id, business_name, license_number, warehouse_location, rating, total_sales) VALUES
            (2, 'ABC Agro Trading Corp', 'AGRI-TS-2026-998', 'Central Mandi Yard, Warangal', 4.9, 154200.00);

            INSERT INTO buyer_profiles (user_id, buyer_type, delivery_address) VALUES
            (3, 'individual', 'Flat 402, Green Meadows, Madhapur, Hyderabad');

            INSERT INTO products (id, seller_id, category_id, name, slug, short_description, description, price, unit, stock_quantity, image_url, is_organic, rating, remedy_for_disease) VALUES
            (1, 2, 1, 'Organic Copper Oxychloride Fungicide 50% WP', 'organic-copper-fungicide', 'Broad spectrum bio-fungicide for Early & Late Blight, Leaf Spot', 'Protects tomato, potato, and vegetable crops from early blight, late blight, and bacterial spots. Certified organic composition.', 350.00, '500g Pack', 120, 'https://images.unsplash.com/photo-1585314062340-f1a5a7c9328d?w=500&auto=format&fit=crop&q=60', 1, 4.9, 'Early Blight'),
            (2, 2, 1, 'Pure Cold-Pressed Neem Oil Spray (10,000 PPM)', 'pure-neem-oil-spray', 'Natural organic repellent for pests, aphids, and powdery mildew', '100% pure organic neem oil with azadirachtin 10000 PPM. Ideal for eco-friendly pest control and foliar fungal prevention.', 280.00, '1 Litre Bottle', 200, 'https://images.unsplash.com/photo-1615485290382-441e4d049cb5?w=500&auto=format&fit=crop&q=60', 1, 4.8, 'Powdery Mildew'),
            (3, 2, 2, 'Mancozeb 75% WP Contact Fungicide', 'mancozeb-75-wp', 'Powerful protective fungicide against fungal blast and leaf blight', 'High-grade protective contact fungicide effective on a wide range of field crops, fruits, and vegetables against blast, rust, and blight.', 420.00, '1 KG Pack', 85, 'https://images.unsplash.com/photo-1592417817098-8f3d6eb22509?w=500&auto=format&fit=crop&q=60', 0, 4.7, 'Late Blight'),
            (4, 2, 2, 'Water Soluble NPK 19-19-19 Fertilizer', 'npk-19-19-19', 'Balanced plant nutrition for rapid vegetative and fruit development', '100% water-soluble specialty fertilizer supplying balanced Nitrogen, Phosphorus, and Potassium for drip and foliar applications.', 180.00, '1 KG Pack', 350, 'https://images.unsplash.com/photo-1574943320219-553eb213f72d?w=500&auto=format&fit=crop&q=60', 0, 4.9, 'Nutrient Deficiency'),
            (5, 2, 3, 'Premium Sona Masoori Rice (Farm Fresh)', 'premium-sona-masoori-rice', 'Aged, naturally aromatic unpolished rice straight from farm harvest', 'Grown with minimal chemical intervention, clean harvested, aged 12 months for fluffiness and nutritional value.', 55.00, 'KG', 1500, 'https://images.unsplash.com/photo-1586201375761-83865001e31c?w=500&auto=format&fit=crop&q=60', 1, 4.9, NULL),
            (6, 2, 3, 'Organic Farm Fresh Tomatoes', 'organic-farm-fresh-tomatoes', 'Vine-ripened, juicy red farm fresh hybrid tomatoes', 'Freshly picked daily from local organic farmer fields. Rich in lycopene, firm texture.', 35.00, 'KG', 400, 'https://images.unsplash.com/photo-1592924357228-91a4daadcfea?w=500&auto=format&fit=crop&q=60', 1, 4.8, NULL),
            (7, 2, 4, 'High Yield Certified Tomato F1 Hybrid Seeds', 'tomato-f1-hybrid-seeds', 'Disease-resistant high yield tomato seeds (10g pack)', 'Germination rate 95%, resistant to bacterial wilt and tomato mosaic virus. High yield potential up to 35 tons/acre.', 199.00, 'Pack of 10g', 150, 'https://images.unsplash.com/photo-1530595467537-0b5996c41f2d?w=500&auto=format&fit=crop&q=60', 1, 4.9, NULL),
            (8, 2, 5, 'Digital 4-in-1 Soil Tester (pH, Moisture, Temp, Sunlight)', 'digital-soil-tester', 'Precision probe meter for instant field soil testing', 'Measure soil pH, moisture levels, soil temperature, and sunlight intensity without batteries.', 899.00, 'Piece', 50, 'https://images.unsplash.com/photo-1523348837708-15d4a09cfac2?w=500&auto=format&fit=crop&q=60', 0, 4.9, NULL);

            INSERT INTO harvests (id, farmer_id, crop_name, variety, quantity, unit, expected_price_per_unit, harvest_date, quality, location, description, status) VALUES
            (1, 1, 'Rice', 'Sona Masoori', 500.00, 'KG', 42.00, '2026-09-23', 'Premium', 'Hyderabad, Telangana', 'Freshly harvested, sun-dried, moisture under 12%, premium golden grain quality.', 'available'),
            (2, 1, 'Tomatoes', 'Hybrid Red', 200.00, 'KG', 25.00, '2026-09-22', 'Grade A', 'Rangareddy, Telangana', 'Firm, ripe organic farm tomatoes ready for immediate pickup.', 'available');

            INSERT INTO notifications (user_id, title, message, type, link_url) VALUES
            (1, 'Welcome to Smart AI Farming', 'Explore AI Crop Recommendation and Leaf Disease Scanner on your dashboard!', 'general', '/farmer#ai-tools'),
            (2, 'New Farmer Harvest Available', 'Farmer Shaik Basha posted 500 KG Rice at ₹42/kg in Hyderabad.', 'harvest', '/seller#farmer-harvests'),
            (3, 'Fresh Farm Harvest Arrived', 'Explore freshly harvested Sona Masoori Rice and Organic Tomatoes in E-Mart.', 'order', '/buyer#catalog');
            ''')
            conn.commit()
        conn.close()

db = Database()

