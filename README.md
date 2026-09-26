# 🌱 Smart AI Agriculture System & E-Commerce Website

An end-to-end intelligent agricultural ecosystem uniting **Farmers**, **Agribusiness Sellers**, and **Retail Buyers** with **AI Quality & Chemical Scanning**, **Live APMC Mandi Rates**, and a **9-Service E-Mart**.

---

## 🌳 Architectural Tree Structure

See the complete tree design below and in [PROJECT_STRUCTURE.md](file:///c:/xampp/mysql/scripts/Smart%20AI%20Agriculture%20system/PROJECT_STRUCTURE.md).

```
🌱 ROOT: Smart AI Agriculture System
│
├── 🚜 [BRANCH 1] Farmer Website (farmer_website/)
│   ├── 🎨 [SUB-BRANCH] templates/
│   │   ├── 🍃 index.html
│   │   └── 🍃 dashboard.html
│   └── 🎨 [SUB-BRANCH] static/
│       ├── 🍃 css/farmer.css
│       └── 🍃 js/ (farmer.js, voice_multilingual.js)
│
├── 🏪 [BRANCH 2] Seller Agribusiness Website (seller_website/)
│   ├── 🎨 [SUB-BRANCH] templates/
│   │   ├── 🍃 index.html
│   │   └── 🍃 dashboard.html
│   └── 🎨 [SUB-BRANCH] static/
│       ├── 🍃 css/seller.css
│       └── 🍃 js/ (seller.js, voice_multilingual.js)
│
├── 🛒 [BRANCH 3] Buyer E-Mart Website (buyer_website/)
│   ├── 🎨 [SUB-BRANCH] templates/
│   │   ├── 🍃 index.html
│   │   └── 🍃 dashboard.html
│   └── 🎨 [SUB-BRANCH] static/
│       ├── 🍃 css/buyer.css
│       └── 🍃 js/ (buyer.js, voice_multilingual.js)
│
├── 🧠 [BRANCH 4] AI & ML Suite (ai/)
│   ├── 🍃 quality_chemical_scanner.py (<= 30% Chemical Gatekeeper)
│   ├── 🍃 mandi_market_prices.py (Live Agmarknet APMC Rates)
│   ├── 🍃 crop_recommender.py (Soil NPK AI Engine)
│   ├── 🍃 disease_detector.py (Leaf Pathology Vision)
│   ├── 🍃 fertilizer_advisor.py & irrigation_advisor.py
│   └── 🍃 agri_chatbot.py (Multilingual Agronomist Bot)
│
├── 🗄️ [BRANCH 5] Database & Storage (Database/ & uploads/)
│   ├── 🍃 db.py (Dual MySQL/SQLite ORM Connector)
│   ├── 🍃 schema.sql (14 Tables, 9 Categories & Certified Seed Products)
│   └── 🍃 uploads/ (Product Photos, Disease & Crop Scans)
│
└── ⚙️ [BRANCH 6] Backend Server & Gateway
    ├── 🍃 app.py (Unified Flask Routing & REST APIs)
    ├── 🍃 config.py (App & Port Settings)
    ├── 🍃 run_server.bat (Windows 1-Click Launcher)
    └── 🍃 index.html (Master Ecosystem Hub)
```

---

## 🌐 Quick Access URLs (Server Port: 5000)

* **Ecosystem Hub**: [http://127.0.0.1:5000/](http://127.0.0.1:5000/)
* **Buyer E-Mart (9 Services)**: [http://127.0.0.1:5000/buyer](http://127.0.0.1:5000/buyer)
* **Seller Portal Dashboard**: [http://127.0.0.1:5000/seller](http://127.0.0.1:5000/seller)
* **Farmer AI Portal**: [http://127.0.0.1:5000/farmer](http://127.0.0.1:5000/farmer)
