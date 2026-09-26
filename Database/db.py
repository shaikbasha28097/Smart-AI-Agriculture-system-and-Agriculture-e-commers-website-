import os
import sqlite3
import decimal
import pymysql
from pymysql.cursors import DictCursor
from config import Config

class Database:
    def __init__(self):
        self.use_mysql = False
        self.test_connection()

    def _clean_row(self, row):
        if not row or not isinstance(row, dict):
            return row
        cleaned = {}
        for k, v in row.items():
            if isinstance(v, decimal.Decimal):
                cleaned[k] = float(v)
            else:
                cleaned[k] = v
        return cleaned

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
                        return self._clean_row(res)
                    if fetchall:
                        res = cursor.fetchall()
                        conn.close()
                        return [self._clean_row(r) for r in res] if res else []
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
                    return self._clean_row(dict(row)) if row else None
                if fetchall:
                    rows = cursor.fetchall()
                    conn.close()
                    return [self._clean_row(dict(r)) for r in rows] if rows else []
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
            (1, 'Fruits', 'fruits', 'fa-apple-whole', 'Fresh farm-harvested seasonal and organic fruits direct from orchard growers'),
            (2, 'Vegetables', 'vegetables', 'fa-carrot', 'Daily harvested farm-fresh vegetables, roots, and organic leafy greens'),
            (3, 'Seeds', 'seeds', 'fa-spa', 'Certified hybrid, high-germination, disease-resistant & drought-tolerant field seeds'),
            (4, 'Plants', 'plants', 'fa-seedling', 'Live nursery saplings, grafted fruit plants, tissue culture & aromatic herbs'),
            (5, 'Soil', 'soil', 'fa-mountain-sun', 'Nutrient-rich potting mix, fertile red soil, vermi-compost soil & organic cocopeat blocks'),
            (6, 'Organic Fertilizers', 'organic-fertilizers', 'fa-leaf', 'Bio-fertilizers, cold-pressed neem oils, seaweed extracts & certified organic disease remedies'),
            (7, 'Chemical Fertilizers', 'chemical-fertilizers', 'fa-flask', 'High-purity NPK, DAP, Urea, micronutrient complexes & protective fungicides'),
            (8, 'Farming Tools', 'farming-tools', 'fa-screwdriver-wrench', 'Digital soil testing meters, 16L battery sprayers, drip irrigation kits & pruning tools'),
            (9, 'Groceries', 'groceries', 'fa-basket-shopping', 'Organic staples, unpolished pulses, aged grains, pure wood-pressed oils & spices');

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
            (101, 2, 1, 'Fresh Farm Alphonso Mangoes (Ratnagiri Grade A)', 'fresh-farm-alphonso-mangoes', 'Naturally ripened, sweet and aromatic GI-tagged Alphonso mangoes', 'Directly harvested from certified coastal orchards. Chemical-free natural ripening process, rich golden pulp with incomparable sweetness.', 450.00, 'Dozen (12 Pcs)', 80, 'https://images.unsplash.com/photo-1553279768-865429fa0078?w=500&auto=format&fit=crop&q=60', 1, 4.9, NULL),
            (102, 2, 1, 'Organic Farm Fresh Sweet Oranges (Nagpur)', 'organic-sweet-oranges', 'Juicy, vitamin-C rich fresh farm oranges harvested daily', 'Farm fresh citrus with high juice content and natural sweetness. Grown using zero synthetic pesticides, perfect for fresh juicing.', 85.00, '1 KG Pack', 250, 'https://images.unsplash.com/photo-1611080626919-7cf5a9dbab5b?w=500&auto=format&fit=crop&q=60', 1, 4.8, NULL),
            (103, 2, 1, 'Kashmir Royal Delicious Red Apples', 'kashmir-royal-red-apples', 'Crisp, sweet mountain-grown red apples from Himalayan valleys', 'Handpicked grade-A Kashmir apples with exceptional crunch, sweetness, and deep red color. High in dietary fiber and antioxidants.', 150.00, '1 KG Pack', 180, 'https://images.unsplash.com/photo-1560806887-1e4cd0b6cbd6?w=500&auto=format&fit=crop&q=60', 1, 4.9, NULL),
            (104, 2, 1, 'Fresh Farm Robusta Bananas (Pesticide Free)', 'fresh-farm-robusta-bananas', 'Naturally tree-ripened potassium-rich sweet bananas', 'Grown with organic compost and drip irrigation. Sweet, nutrient-dense, and completely free from calcium carbide artificial ripening.', 45.00, 'Dozen (12 Pcs)', 300, 'https://images.unsplash.com/photo-1571771894821-ce9b6c11b08e?w=500&auto=format&fit=crop&q=60', 1, 4.7, NULL),
            (105, 2, 2, 'Organic Farm Fresh Tomatoes (Vine Ripened)', 'organic-farm-fresh-tomatoes', 'Juicy, firm red hybrid tomatoes harvested fresh every morning', 'Picked daily from local farmer fields. Rich in lycopene and natural acidity, perfect for curries, salads, and puree processing.', 35.00, '1 KG Pack', 400, 'https://images.unsplash.com/photo-1592924357228-91a4daadcfea?w=500&auto=format&fit=crop&q=60', 1, 4.8, NULL),
            (106, 2, 2, 'Fresh Farm Yellow Potatoes (Clean Sorted)', 'fresh-farm-yellow-potatoes', 'Medium-to-large sorted low-sugar baking & cooking potatoes', 'Unwashed dry-stored farm potatoes with thin skin and firm flesh. Ideal for daily cooking, roasting, and chips with minimal peeling loss.', 30.00, '1 KG Pack', 600, 'https://images.unsplash.com/photo-1518977676601-b53f82aba655?w=500&auto=format&fit=crop&q=60', 0, 4.7, NULL),
            (107, 2, 2, 'Fresh Green Organic Chillies (G4 Variety)', 'fresh-green-organic-chillies', 'Pungent, glossy green spicy chillies harvested fresh', 'Grown in organic soils with natural bio-sprays. High capsaicin content, strong flavor and excellent shelf life.', 60.00, '500g Pack', 150, 'https://images.unsplash.com/photo-1588252303782-cb80119abd6d?w=500&auto=format&fit=crop&q=60', 1, 4.8, NULL),
            (108, 2, 2, 'Farm Fresh Red Onions (Nashik Grade)', 'farm-fresh-red-onions', 'Firm, pungent high-dry-matter red onions with tight skins', 'Premium sorting from Nashik harvest. High pungent flavor and long storage durability of up to 3 months in dry conditions.', 40.00, '1 KG Pack', 500, 'https://images.unsplash.com/photo-1508747703725-719777637510?w=500&auto=format&fit=crop&q=60', 0, 4.9, NULL),
            (109, 2, 3, 'High Yield Certified Tomato F1 Hybrid Seeds', 'tomato-f1-hybrid-seeds', 'Disease-resistant high yield hybrid tomato seeds (10g pack)', 'Germination rate above 95%, resistant to bacterial wilt, leaf curl virus, and nematodes. Yield potential up to 35 tons/acre.', 199.00, 'Pack of 10g', 150, 'https://images.unsplash.com/photo-1530595467537-0b5996c41f2d?w=500&auto=format&fit=crop&q=60', 1, 4.9, NULL),
            (110, 2, 3, 'Certified BPT-5204 (Samba Mahsuri) Paddy Seeds', 'certified-paddy-seeds', 'Drought-tolerant high-milling-recovery paddy seeds for Kharif & Rabi', 'Certified foundation seeds treated with bio-fungicide. Fine grain quality, excellent aroma, and high consumer market demand.', 850.00, '25 KG Bag', 90, 'https://images.unsplash.com/photo-1586201375761-83865001e31c?w=500&auto=format&fit=crop&q=60', 1, 4.8, NULL),
            (111, 2, 3, 'Hybrid BT Cotton Seeds (Bollgard II)', 'hybrid-bt-cotton-seeds', 'Bollworm-resistant certified hybrid cotton seeds with high lint yield', 'Superior boll weight (4.5 to 5g) with excellent boll bursting and high spinning value. Suitable for rainfed and irrigated fields.', 860.00, '450g Pack', 120, 'https://images.unsplash.com/photo-1606041008023-472dfb5e530f?w=500&auto=format&fit=crop&q=60', 0, 4.9, NULL),
            (112, 2, 3, 'Dwarf Papaya (Red Lady 786) Hybrid Seeds', 'dwarf-papaya-red-lady-seeds', 'High-sugar red-fleshed hermaphrodite hybrid papaya seeds', 'Early bearing dwarf variety fruiting at 80cm plant height. Yields 60-80 kg per tree with thick, sweet red aromatic pulp.', 320.00, 'Pack of 10g', 110, 'https://images.unsplash.com/photo-1517282009859-f000ec3b26fe?w=500&auto=format&fit=crop&q=60', 1, 4.9, NULL),
            (113, 2, 4, 'Grafted Thai All-Time Mango Sapling Plant', 'grafted-thai-mango-sapling', 'Heavy bearing year-round flowering grafted live mango sapling', 'Healthy 2-foot grafted plant in polybag. Starts fruiting within 18 months, suitable for home gardens, terrace pots, and orchard density planting.', 250.00, 'Live Sapling', 75, 'https://images.unsplash.com/photo-1546842931-886c185b4c8c?w=500&auto=format&fit=crop&q=60', 1, 4.9, NULL),
            (114, 2, 4, 'Grand Naine (G9) Tissue Culture Banana Plants', 'g9-tissue-culture-banana', 'Virus-free clonal tissue culture high-density banana sapling', 'Uniform growth cycle with 30-35 kg bunch weight per plant. Matures in 11 months with zero rhizome rot vulnerability.', 45.00, 'Per Plant', 500, 'https://images.unsplash.com/photo-1528825871115-3581a5387919?w=500&auto=format&fit=crop&q=60', 1, 4.8, NULL),
            (115, 2, 4, 'Organic Hybrid Lemon Plant (Baramasi Kagzi)', 'hybrid-lemon-plant-baramasi', 'Perennial thin-skinned juicy lemon live plant with continuous fruiting', 'Well-rooted graft in potting soil. Produces round, seedless lemons rich in juice throughout all 12 months.', 180.00, 'Live Plant', 120, 'https://images.unsplash.com/photo-1534856966150-c832f817a570?w=500&auto=format&fit=crop&q=60', 1, 4.8, NULL),
            (116, 2, 4, 'Ayurvedic Tulsi & Neem Herbal Live Plant Combo', 'tulsi-neem-herbal-plant-combo', 'Set of 2 sacred medicinal live plants for organic farming & air purification', 'Includes Krishna Tulsi and bio-active Neem sapling. Natural insect repellent, medicinal leaves, and resilient growth.', 150.00, 'Pair (2 Plants)', 95, 'https://images.unsplash.com/photo-1509316975850-ff9c5deb0cd9?w=500&auto=format&fit=crop&q=60', 1, 4.9, NULL),
            (117, 2, 5, 'Premium Organic Potting Soil Mix (Vermi-Compost Enriched)', 'premium-organic-potting-soil', 'Sterilized, pH-balanced ready-to-use potting mix for seeds & saplings', 'Enriched with vermicompost, neem cake, perlite, and mycorrhiza. Provides optimal aeration, moisture retention, and zero root rot.', 299.00, '10 KG Bag', 160, 'https://images.unsplash.com/photo-1464226184884-fa280b87c399?w=500&auto=format&fit=crop&q=60', 1, 4.9, NULL),
            (118, 2, 5, 'Natural High-Grade Red Soil for Farm & Garden', 'natural-red-soil-farm-garden', 'Iron-rich, well-draining natural loam soil for agriculture beds', 'Screened red soil free from rocks, weeds, and clay clods. Perfect for fruit orchards, vegetable raised beds, and nursery grafting.', 350.00, '25 KG Bag', 100, 'https://images.unsplash.com/photo-1589923188900-85dae523342b?w=500&auto=format&fit=crop&q=60', 1, 4.8, NULL),
            (119, 2, 5, '100% Organic Low EC Cocopeat Block (Expands to 75L)', 'organic-low-ec-cocopeat-block', 'Washed low-salinity coconut coir substrate for water retention & rooting', 'Triple washed low EC (<0.5 mS/cm). Retains up to 10x its weight in water, promoting fibrous root acceleration.', 199.00, '5 KG Block', 220, 'https://images.unsplash.com/photo-1585314062340-f1a5a7c9328d?w=500&auto=format&fit=crop&q=60', 1, 4.9, NULL),
            (120, 2, 5, 'Sterilized Garden Topsoil + Perlite Aeration Blend', 'sterilized-garden-topsoil-perlite', 'Weed-free heat-treated topsoil mixed with volcanic perlite granules', 'Lightweight, crumbly texture ensuring rapid seed germination and capillary root respiration.', 240.00, '5 KG Bag', 140, 'https://images.unsplash.com/photo-1523348837708-15d4a09cfac2?w=500&auto=format&fit=crop&q=60', 1, 4.7, NULL),
            (1, 2, 6, 'Organic Copper Oxychloride Fungicide 50% WP', 'organic-copper-fungicide', 'Broad spectrum bio-fungicide for Early & Late Blight, Leaf Spot', 'Protects tomato, potato, and vegetable crops from early blight, late blight, and bacterial spots. Certified organic composition.', 350.00, '500g Pack', 120, 'https://images.unsplash.com/photo-1585314062340-f1a5a7c9328d?w=500&auto=format&fit=crop&q=60', 1, 4.9, 'Early Blight'),
            (2, 2, 6, 'Pure Cold-Pressed Neem Oil Spray (10,000 PPM)', 'pure-neem-oil-spray', 'Natural organic repellent for pests, aphids, and powdery mildew', '100% pure organic neem oil with azadirachtin 10000 PPM. Ideal for eco-friendly pest control and foliar fungal prevention.', 280.00, '1 Litre Bottle', 200, 'https://images.unsplash.com/photo-1615485290382-441e4d049cb5?w=500&auto=format&fit=crop&q=60', 1, 4.8, 'Powdery Mildew'),
            (121, 2, 6, 'Premium Bio-Enriched Vermicompost (100% Organic Manure)', 'premium-bio-vermicompost', 'Earthworm-processed nutrient-dense organic humus with beneficial microbes', 'Rich in humic acid, micro-flora, and essential NPK. Improves soil structure and water holding capacity by 40%.', 320.00, '25 KG Bag', 150, 'https://images.unsplash.com/photo-1574943320219-553eb213f72d?w=500&auto=format&fit=crop&q=60', 1, 4.9, 'Nutrient Deficiency'),
            (122, 2, 6, 'Liquid Seaweed Extract Bio-Stimulant Fertilizer', 'liquid-seaweed-extract-fertilizer', 'Cold-processed marine kelp liquid for root vigor, flowering & stress tolerance', 'Natural cytokinins, auxins, and trace minerals. Stimulates lateral root branchings and reduces heat/drought stress.', 420.00, '500ml Bottle', 110, 'https://images.unsplash.com/photo-1530595467537-0b5996c41f2d?w=500&auto=format&fit=crop&q=60', 1, 4.8, 'Leaf Spot'),
            (3, 2, 7, 'Mancozeb 75% WP Contact Fungicide', 'mancozeb-75-wp', 'Powerful protective fungicide against fungal blast and leaf blight', 'High-grade protective contact fungicide effective on a wide range of field crops, fruits, and vegetables against blast, rust, and blight.', 420.00, '1 KG Pack', 85, 'https://images.unsplash.com/photo-1592417817098-8f3d6eb22509?w=500&auto=format&fit=crop&q=60', 0, 4.7, 'Late Blight'),
            (4, 2, 7, 'Water Soluble NPK 19-19-19 Fertilizer', 'npk-19-19-19', 'Balanced plant nutrition for rapid vegetative and fruit development', '100% water-soluble specialty fertilizer supplying balanced Nitrogen, Phosphorus, and Potassium for drip and foliar applications.', 180.00, '1 KG Pack', 350, 'https://images.unsplash.com/photo-1574943320219-553eb213f72d?w=500&auto=format&fit=crop&q=60', 0, 4.9, 'Nutrient Deficiency'),
            (123, 2, 7, 'Urea 46% Nitrogen Prilled Fertilizer', 'urea-46-nitrogen-fertilizer', 'High-concentration fast-release nitrogen granules for vegetative growth', 'Agricultural grade prilled urea for basal and top-dressing applications in paddy, sugarcane, wheat, and cotton.', 267.00, '45 KG Bag', 200, 'https://images.unsplash.com/photo-1586201375761-83865001e31c?w=500&auto=format&fit=crop&q=60', 0, 4.8, NULL),
            (124, 2, 7, 'Di-Ammonium Phosphate (DAP 18-46-0) Fertilizer', 'dap-18-46-0-fertilizer', 'High-phosphorus granular fertilizer for root establishment and tillering', 'Essential basal fertilizer providing starter nitrogen and heavy phosphorus for root elongation and sturdy stalk growth.', 1350.00, '50 KG Bag', 120, 'https://images.unsplash.com/photo-1592417817098-8f3d6eb22509?w=500&auto=format&fit=crop&q=60', 0, 4.9, NULL),
            (8, 2, 8, 'Digital 4-in-1 Soil Tester (pH, Moisture, Temp, Sunlight)', 'digital-soil-tester', 'Precision probe meter for instant field soil testing', 'Measure soil pH, moisture levels, soil temperature, and sunlight intensity without batteries.', 899.00, 'Piece', 50, 'https://images.unsplash.com/photo-1523348837708-15d4a09cfac2?w=500&auto=format&fit=crop&q=60', 0, 4.9, NULL),
            (125, 2, 8, '16L Agriculture 2-in-1 Battery & Manual Knapsack Sprayer', '16l-knapsack-sprayer', 'Dual-mode high-pressure rechargeable battery sprayer with 4 brass nozzles', '12V 8Ah long-lasting lithium battery sprays up to 25 tanks on a single charge. Comfortable padded straps and extendable stainless steel lance.', 2450.00, 'Unit', 45, 'https://images.unsplash.com/photo-1589923188900-85dae523342b?w=500&auto=format&fit=crop&q=60', 0, 4.9, NULL),
            (126, 2, 8, 'Complete DIY Drip Irrigation Starter Kit (100 Plants)', 'drip-irrigation-kit-100-plants', 'Water-saving drip kit with 16mm mainline, micro-tubes & pressure drippers', 'Includes 50m mainline pipe, 100 adjustable drippers, punch tool, connectors, and end-stops. Saves up to 70% irrigation water.', 1299.00, 'Complete Kit', 60, 'https://images.unsplash.com/photo-1464226184884-fa280b87c399?w=500&auto=format&fit=crop&q=60', 0, 4.8, NULL),
            (127, 2, 8, 'Heavy-Duty SK5 Stainless Steel Pruning & Grafting Shears', 'pruning-grafting-shears', 'Ultra-sharp Japanese SK5 steel bypass garden pruner with safety lock', 'Ergonomic anti-slip grip with shock-absorbing spring. Cuts branches up to 25mm clean without crushing plant bark.', 499.00, 'Piece', 110, 'https://images.unsplash.com/photo-1615485290382-441e4d049cb5?w=500&auto=format&fit=crop&q=60', 0, 4.9, NULL),
            (131, 2, 9, 'Organic Royal Basmati Rice (Aged 2 Years)', 'organic-royal-basmati-rice', 'Long grain aromatic aged organic basmati rice with exquisite aroma', 'Traditional Himalayan foothills harvest aged for 24 months. Non-sticky, fluffy long grains rich in natural aroma and zero chemical polish.', 135.00, '1 KG Pack', 200, 'https://images.unsplash.com/photo-1586201375761-83865001e31c?w=500&auto=format&fit=crop&q=60', 1, 4.9, NULL),
            (132, 2, 9, 'Farm Fresh Organic Sharbati Whole Wheat Grain', 'organic-sharbati-whole-wheat', 'Golden heavy grains with high dietary fiber and natural sweetness', '100% organic rainfed Sharbati wheat grown in rich black soils of Sehore. High zinc, iron and protein content for soft rotis.', 52.00, '1 KG Pack', 350, 'https://images.unsplash.com/photo-1574323347407-f5e1ad6d020b?w=500&auto=format&fit=crop&q=60', 1, 4.8, NULL),
            (133, 2, 9, 'Pure Cold-Pressed Wood Churned Groundnut Oil', 'cold-pressed-groundnut-oil', 'Unrefined traditional wood-churned (Kachi Ghani / Mara Chekku) peanut oil', 'Extracted at low temperatures from high-grade organic peanuts. Rich in natural plant phytosterols, Vitamin E and authentic nutty aroma.', 240.00, '1 Litre Bottle', 120, 'https://images.unsplash.com/photo-1474979266404-7eaacbcd87c5?w=500&auto=format&fit=crop&q=60', 1, 4.9, NULL),
            (134, 2, 9, 'Organic Unpolished Desi Toor Dal (Pigeon Pea)', 'organic-desi-toor-dal', 'High-protein unpolished organic yellow lentils without artificial water/oil polish', 'Naturally grown pulses retaining all essential micronutrients and dietary fiber. Zero chemical polish, cooks easily with delicious rich flavor.', 165.00, '1 KG Pack', 180, 'https://images.unsplash.com/photo-1585994192701-f1a505c8574a?w=500&auto=format&fit=crop&q=60', 1, 4.8, NULL);

            INSERT INTO harvests (id, farmer_id, crop_name, variety, quantity, unit, expected_price_per_unit, harvest_date, quality, location, description, status) VALUES
            (1, 1, 'Rice', 'Sona Masoori', 500.00, 'KG', 42.00, '2026-09-23', 'Premium', 'Hyderabad, Telangana', 'Freshly harvested, sun-dried, moisture under 12%, premium golden grain quality.', 'available'),
            (2, 1, 'Tomatoes', 'Hybrid Red', 200.00, 'KG', 25.00, '2026-09-22', 'Grade A', 'Rangareddy, Telangana', 'Firm, ripe organic farm tomatoes ready for immediate pickup.', 'available');

            INSERT INTO notifications (user_id, title, message, type, link_url) VALUES
            (1, 'Welcome to Smart AI Farming', 'Explore AI Crop Recommendation and Leaf Disease Scanner on your dashboard!', 'general', '/farmer#ai-tools'),
            (2, 'New Farmer Harvest Available', 'Farmer Shaik Basha posted 500 KG Rice at ₹42/kg in Hyderabad.', 'harvest', '/seller#farmer-harvests'),
            (3, 'Fresh Farm Harvest Arrived', 'Explore freshly harvested Fruits, Vegetables, Seeds, Plants, Soil, Fertilizers and Tools in Agri E-Mart.', 'order', '/buyer#catalog');
            ''')
            conn.commit()
        conn.close()

db = Database()

