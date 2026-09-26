import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from Database.db import db

def run_migration():
    print("Running Groceries category and seed migration...")
    
    # 1. Insert Groceries category (ID 9)
    db.query("""
        INSERT INTO product_categories (id, name, slug, icon, description)
        VALUES (9, 'Groceries', 'groceries', 'fa-basket-shopping', 'Organic staples, unpolished pulses, aged grains, pure wood-pressed oils & spices')
        ON DUPLICATE KEY UPDATE name=VALUES(name), slug=VALUES(slug), icon=VALUES(icon), description=VALUES(description)
    """)
    print("Category 9 'Groceries' inserted/updated.")

    # 2. Insert Grocery Products
    grocery_products = [
        (131, 2, 9, 'Organic Royal Basmati Rice (Aged 2 Years)', 'organic-royal-basmati-rice', 
         'Long grain aromatic aged organic basmati rice with exquisite aroma', 
         'Traditional Himalayan foothills harvest aged for 24 months. Non-sticky, fluffy long grains rich in natural aroma and zero chemical polish.', 
         135.00, '1 KG Pack', 200, 'https://images.unsplash.com/photo-1586201375761-83865001e31c?w=500&auto=format&fit=crop&q=60', 1, 4.9, None),
        
        (132, 2, 9, 'Farm Fresh Organic Sharbati Whole Wheat Grain', 'organic-sharbati-whole-wheat', 
         'Golden heavy grains with high dietary fiber and natural sweetness', 
         '100% organic rainfed Sharbati wheat grown in rich black soils of Sehore. High zinc, iron and protein content for soft rotis.', 
         52.00, '1 KG Pack', 350, 'https://images.unsplash.com/photo-1574323347407-f5e1ad6d020b?w=500&auto=format&fit=crop&q=60', 1, 4.8, None),
        
        (133, 2, 9, 'Pure Cold-Pressed Wood Churned Groundnut Oil', 'cold-pressed-groundnut-oil', 
         'Unrefined traditional wood-churned (Kachi Ghani / Mara Chekku) peanut oil', 
         'Extracted at low temperatures from high-grade organic peanuts. Rich in natural plant phytosterols, Vitamin E and authentic nutty aroma.', 
         240.00, '1 Litre Bottle', 120, 'https://images.unsplash.com/photo-1474979266404-7eaacbcd87c5?w=500&auto=format&fit=crop&q=60', 1, 4.9, None),
        
        (134, 2, 9, 'Organic Unpolished Desi Toor Dal (Pigeon Pea)', 'organic-desi-toor-dal', 
         'High-protein unpolished organic yellow lentils without artificial water/oil polish', 
         'Naturally grown pulses retaining all essential micronutrients and dietary fiber. Zero chemical polish, cooks easily with delicious rich flavor.', 
         165.00, '1 KG Pack', 180, 'https://images.unsplash.com/photo-1585994192701-f1a505c8574a?w=500&auto=format&fit=crop&q=60', 1, 4.8, None)
    ]

    for p in grocery_products:
        db.query("""
            INSERT INTO products (id, seller_id, category_id, name, slug, short_description, description, price, unit, stock_quantity, image_url, is_organic, rating, remedy_for_disease)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE name=VALUES(name), price=VALUES(price), unit=VALUES(unit), image_url=VALUES(image_url), category_id=VALUES(category_id)
        """, p)
        print(f"Product {p[0]} '{p[3]}' inserted/updated.")

    # Verify all categories
    categories = db.query("SELECT id, name, slug FROM product_categories ORDER BY id ASC")
    print("Updated categories in DB:", categories)

if __name__ == '__main__':
    run_migration()
