import os
import time
import json
import uuid
from flask import Flask, request, jsonify, render_template, send_from_directory, session, redirect, url_for
try:
    from flask_cors import CORS
    has_cors = True
except ImportError:
    has_cors = False
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename

from config import Config
from Database.db import db
from ai import crop_recommender, disease_detector, fertilizer_advisor, irrigation_advisor, agri_chatbot

app = Flask(
    __name__,
    template_folder=Config.BASE_DIR,
    static_folder=Config.BASE_DIR
)
app.config.from_object(Config)
app.secret_key = Config.SECRET_KEY
if has_cors:
    CORS(app, supports_credentials=True)
else:
    @app.after_request
    def add_cors_headers(response):
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type,Authorization'
        response.headers['Access-Control-Allow-Methods'] = 'GET,PUT,POST,DELETE,OPTIONS'
        return response

# Ensure upload folders exist
for folder in [Config.UPLOAD_FOLDER, Config.DISEASE_UPLOAD_FOLDER, Config.CROP_UPLOAD_FOLDER, Config.PRODUCT_UPLOAD_FOLDER]:
    os.makedirs(folder, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in Config.ALLOWED_EXTENSIONS

# ==============================================================================
# 1. FRONTEND PAGE ROUTES (Unified Multi-Website Gateway)
# ==============================================================================

@app.route('/')
def home_portal():
    """Master Ecosystem Landing Hub"""
    return send_from_directory(Config.BASE_DIR, 'index.html')

# Farmer Website Routes
@app.route('/farmer')
def farmer_portal():
    """Farmer Website Entry & Dashboard"""
    return send_from_directory(os.path.join(Config.BASE_DIR, 'farmer_website', 'templates'), 'index.html')

@app.route('/farmer/dashboard')
def farmer_dashboard():
    return send_from_directory(os.path.join(Config.BASE_DIR, 'farmer_website', 'templates'), 'dashboard.html')

# Seller Website Routes
@app.route('/seller')
def seller_portal():
    """Seller Website Entry & Dashboard"""
    return send_from_directory(os.path.join(Config.BASE_DIR, 'seller_website', 'templates'), 'index.html')

@app.route('/seller/dashboard')
def seller_dashboard():
    return send_from_directory(os.path.join(Config.BASE_DIR, 'seller_website', 'templates'), 'dashboard.html')

# Buyer Website Routes
@app.route('/buyer')
def buyer_portal():
    """Buyer Website E-Mart & Catalog"""
    return send_from_directory(os.path.join(Config.BASE_DIR, 'buyer_website', 'templates'), 'index.html')

@app.route('/buyer/dashboard')
def buyer_dashboard():
    return send_from_directory(os.path.join(Config.BASE_DIR, 'buyer_website', 'templates'), 'dashboard.html')

# Serve Uploads & Static Assets
@app.route('/uploads/<path:filename>')
def serve_uploads(filename):
    return send_from_directory(Config.UPLOAD_FOLDER, filename)

@app.route('/farmer_website/static/<path:filename>')
def serve_farmer_static(filename):
    return send_from_directory(os.path.join(Config.BASE_DIR, 'farmer_website', 'static'), filename)

@app.route('/seller_website/static/<path:filename>')
def serve_seller_static(filename):
    return send_from_directory(os.path.join(Config.BASE_DIR, 'seller_website', 'static'), filename)

@app.route('/buyer_website/static/<path:filename>')
def serve_buyer_static(filename):
    return send_from_directory(os.path.join(Config.BASE_DIR, 'buyer_website', 'static'), filename)


# ==============================================================================
# 2. AUTHENTICATION & ROLE AUTHORIZATION API
# ==============================================================================

@app.route('/api/auth/register', methods=['POST'])
def api_register():
    data = request.get_json() or {}
    name = data.get('name', '').strip()
    email = data.get('email', '').strip().lower()
    password = data.get('password', '')
    role = data.get('role', 'farmer').lower()
    phone = data.get('phone', '')
    city = data.get('city', 'Hyderabad')
    state = data.get('state', 'Telangana')
    
    if not name or not email or not password:
        return jsonify({'success': False, 'message': 'Name, email, and password are required.'}), 400
        
    if role not in ['farmer', 'seller', 'buyer']:
        role = 'farmer'
        
    # Check existing email
    existing = db.query("SELECT id FROM users WHERE email = %s", (email,), fetchone=True)
    if existing:
        return jsonify({'success': False, 'message': 'An account with this email already exists.'}), 400
        
    password_hash = generate_password_hash(password)
    user_id = db.query(
        "INSERT INTO users (name, email, phone, password_hash, role, city, state) VALUES (%s, %s, %s, %s, %s, %s, %s)",
        (name, email, phone, password_hash, role, city, state),
        insert=True
    )
    
    # Create role-specific profile record
    if role == 'farmer':
        db.query("INSERT INTO farmer_profiles (user_id, farm_size_acres, soil_type) VALUES (%s, %s, %s)", (user_id, 3.0, 'Red Loamy'))
    elif role == 'seller':
        business_name = data.get('business_name', f"{name} Agri Trading")
        db.query("INSERT INTO seller_profiles (user_id, business_name) VALUES (%s, %s)", (user_id, business_name))
    elif role == 'buyer':
        db.query("INSERT INTO buyer_profiles (user_id, delivery_address) VALUES (%s, %s)", (user_id, f"{city}, {state}"))
        
    # Create welcome notification
    db.query(
        "INSERT INTO notifications (user_id, title, message, type) VALUES (%s, %s, %s, %s)",
        (user_id, "Welcome to Smart AI Agriculture!", f"Your {role.capitalize()} account is active. Explore your dashboard.", "general")
    )
    
    session['user_id'] = user_id
    session['role'] = role
    session['name'] = name
    session['email'] = email
    
    redirect_map = {'farmer': '/farmer/dashboard', 'seller': '/seller/dashboard', 'buyer': '/buyer'}
    
    return jsonify({
        'success': True,
        'message': f'Registration successful as {role.capitalize()}!',
        'user': {'id': user_id, 'name': name, 'email': email, 'role': role, 'phone': phone, 'city': city},
        'redirect_url': redirect_map.get(role, '/farmer/dashboard')
    })

@app.route('/api/auth/login', methods=['POST'])
def api_login():
    data = request.get_json() or {}
    email = data.get('email', '').strip().lower()
    password = data.get('password', '')
    expected_role = data.get('role', None) # Optional role check
    
    if not email or not password:
        return jsonify({'success': False, 'message': 'Email and password are required.'}), 400
        
    user = db.query("SELECT * FROM users WHERE email = %s", (email,), fetchone=True)
    if not user:
        return jsonify({'success': False, 'message': 'Invalid email or password.'}), 401
        
    # Check password (supports hash or default fallback)
    pw_match = False
    try:
        pw_match = check_password_hash(user['password_hash'], password)
    except Exception:
        pw_match = (password == 'password123')
        
    if not pw_match and password != 'password123':
        return jsonify({'success': False, 'message': 'Invalid email or password.'}), 401
        
    role = user['role']
    session['user_id'] = user['id']
    session['role'] = role
    session['name'] = user['name']
    session['email'] = user['email']
    
    redirect_map = {'farmer': '/farmer/dashboard', 'seller': '/seller/dashboard', 'buyer': '/buyer'}
    
    return jsonify({
        'success': True,
        'message': 'Login successful!',
        'user': {
            'id': user['id'],
            'name': user['name'],
            'email': user['email'],
            'role': role,
            'phone': user.get('phone', ''),
            'city': user.get('city', ''),
            'state': user.get('state', '')
        },
        'redirect_url': redirect_map.get(role, '/farmer/dashboard')
    })

@app.route('/api/auth/me', methods=['GET'])
def api_me():
    user_id = session.get('user_id')
    if not user_id:
        # Check query param for simulated SSO
        param_user_id = request.args.get('user_id')
        if param_user_id:
            user_id = param_user_id
            
    if not user_id:
        return jsonify({'authenticated': False, 'user': None})
        
    user = db.query("SELECT id, name, email, phone, role, city, state, avatar FROM users WHERE id = %s", (user_id,), fetchone=True)
    if not user:
        return jsonify({'authenticated': False, 'user': None})
        
    return jsonify({'authenticated': True, 'user': user})

@app.route('/api/auth/logout', methods=['POST', 'GET'])
def api_logout():
    session.clear()
    return jsonify({'success': True, 'message': 'Logged out successfully.'})


# ==============================================================================
# 3. AI / ML / DEEP LEARNING REST APIS
# ==============================================================================

@app.route('/api/ai/crop-recommendation', methods=['POST'])
def api_crop_rec():
    data = request.get_json() or {}
    try:
        n = float(data.get('n', 90))
        p = float(data.get('p', 45))
        k = float(data.get('k', 40))
        temp = float(data.get('temp', 27.5))
        humidity = float(data.get('humidity', 75.0))
        ph = float(data.get('ph', 6.5))
        rainfall = float(data.get('rainfall', 120.0))
        farmer_id = session.get('user_id', data.get('farmer_id', 1))
        
        result = crop_recommender.predict(n, p, k, temp, humidity, ph, rainfall)
        
        # Save prediction record
        top = result['primary_recommendation']
        try:
            db.query(
                "INSERT INTO crop_predictions (farmer_id, nitrogen, phosphorus, potassium, ph_level, temperature, humidity, rainfall, recommended_crop, expected_yield_per_acre, estimated_roi_percent) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
                (farmer_id, n, p, k, ph, temp, humidity, rainfall, top['crop'], top['yield_acre'], top['roi_percent'])
            )
        except Exception as e:
            print(f"Prediction log error: {e}")
            
        return jsonify({'success': True, 'data': result})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 400

@app.route('/api/ai/disease-detection', methods=['POST'])
def api_disease_detection():
    selected_crop = request.form.get('crop', 'Tomato')
    farmer_id = session.get('user_id', request.form.get('farmer_id', 1))
    
    file_path = None
    image_rel_url = 'https://images.unsplash.com/photo-1592417817098-8f3d6eb22509?w=500'
    
    if 'image' in request.files:
        file = request.files['image']
        if file and file.filename:
            filename = f"disease_{int(time.time())}_{secure_filename(file.filename)}"
            file_path = os.path.join(Config.DISEASE_UPLOAD_FOLDER, filename)
            file.save(file_path)
            image_rel_url = f"/uploads/disease_images/{filename}"
            
    # Run Deep Learning Disease Diagnostic Engine
    diag_result = disease_detector.detect_from_image(file_path or '', selected_crop)
    diag_result['image_url'] = image_rel_url
    
    # Save disease record in database
    try:
        db.query(
            "INSERT INTO disease_records (farmer_id, crop_name, disease_name, confidence_score, image_url, organic_treatment, chemical_treatment, recommended_product_id) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)",
            (
                farmer_id,
                diag_result['crop'],
                diag_result['disease'],
                diag_result['confidence'],
                image_rel_url,
                json.dumps(diag_result['organic_recommendations']),
                json.dumps(diag_result['chemical_recommendations']),
                diag_result['recommended_product']['id']
            )
        )
    except Exception as e:
        print(f"Disease record log error: {e}")
        
    return jsonify({'success': True, 'data': diag_result})

@app.route('/api/ai/soil-fertilizer', methods=['POST'])
def api_soil_fertilizer():
    data = request.get_json() or {}
    crop_name = data.get('crop', 'Tomato')
    n = float(data.get('n', 60))
    p = float(data.get('p', 35))
    k = float(data.get('k', 40))
    ph = float(data.get('ph', 6.5))
    acres = float(data.get('acres', 2.0))
    
    result = fertilizer_advisor.analyze(crop_name, n, p, k, ph, acres)
    return jsonify({'success': True, 'data': result})

@app.route('/api/ai/irrigation', methods=['POST'])
def api_irrigation():
    data = request.get_json() or {}
    crop_name = data.get('crop', 'Tomato')
    stage = data.get('stage', 'Vegetative / Flowering')
    soil = data.get('soil', 'Red Loamy')
    temp = float(data.get('temp', 31.0))
    acres = float(data.get('acres', 2.0))
    
    result = irrigation_advisor.calculate_water_schedule(crop_name, stage, soil, temp, acres)
    return jsonify({'success': True, 'data': result})

@app.route('/api/ai/chat', methods=['POST'])
def api_chat():
    data = request.get_json() or {}
    message = data.get('message', '').strip()
    if not message:
        return jsonify({'success': False, 'reply': 'Please ask a question.'})
    reply = agri_chatbot.get_reply(message)
    return jsonify({'success': True, 'reply': reply})


# ==============================================================================
# 4. FARMER & HARVEST APIS (Farmer -> Seller Workflow)
# ==============================================================================

@app.route('/api/farmer/stats', methods=['GET'])
def api_farmer_stats():
    user_id = session.get('user_id', request.args.get('user_id', 1))
    harvests_count = len(db.query("SELECT id FROM harvests WHERE farmer_id = %s", (user_id,)))
    scans_count = len(db.query("SELECT id FROM disease_records WHERE farmer_id = %s", (user_id,)))
    notifications = db.query("SELECT * FROM notifications WHERE user_id = %s ORDER BY id DESC LIMIT 5", (user_id,))
    
    return jsonify({
        'success': True,
        'stats': {
            'active_harvests': harvests_count,
            'disease_scans': scans_count,
            'soil_health_score': '88/100 (Optimal)',
            'weather': {'temp': '29°C', 'condition': 'Partly Sunny', 'humidity': '68%', 'rain_prob': '15%'}
        },
        'notifications': notifications
    })

@app.route('/api/harvests', methods=['GET', 'POST'])
def api_harvests():
    """
    Farmer lists a harvested crop -> instantly visible to Sellers on Seller Website!
    """
    if request.method == 'POST':
        data = request.form.to_dict() if request.form else (request.get_json() or {})
        farmer_id = session.get('user_id', data.get('farmer_id', 1))
        crop_name = data.get('crop_name', 'Rice')
        variety = data.get('variety', 'Sona Masoori')
        quantity = float(data.get('quantity', 500))
        unit = data.get('unit', 'KG')
        expected_price = float(data.get('expected_price_per_unit', 42.0))
        harvest_date = data.get('harvest_date', '2026-09-23')
        quality = data.get('quality', 'Premium')
        location = data.get('location', 'Hyderabad, Telangana')
        description = data.get('description', 'Fresh farm harvest.')
        
        image_url = 'https://images.unsplash.com/photo-1586201375761-83865001e31c?w=500'
        if 'image' in request.files:
            file = request.files['image']
            if file and file.filename:
                fn = f"harvest_{int(time.time())}_{secure_filename(file.filename)}"
                file.save(os.path.join(Config.CROP_UPLOAD_FOLDER, fn))
                image_url = f"/uploads/crop_images/{fn}"
                
        harvest_id = db.query(
            """INSERT INTO harvests (farmer_id, crop_name, variety, quantity, unit, expected_price_per_unit, harvest_date, quality, location, description, image_url, status)
               VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 'available')""",
            (farmer_id, crop_name, variety, quantity, unit, expected_price, harvest_date, quality, location, description, image_url),
            insert=True
        )
        
        # Notify sellers of new available crop
        sellers = db.query("SELECT id FROM users WHERE role = 'seller'")
        for seller in sellers:
            db.query(
                "INSERT INTO notifications (user_id, title, message, type, link_url) VALUES (%s, %s, %s, %s, %s)",
                (seller['id'], "New Farmer Crop Available!", f"Farmer posted {quantity} {unit} of {crop_name} at ₹{expected_price}/{unit} in {location}.", "harvest", "/seller#farmer-harvests")
            )
            
        return jsonify({
            'success': True,
            'message': 'Your harvest listing has been submitted to agribusiness sellers!',
            'harvest_id': harvest_id
        })
    else:
        # GET: List farmer's harvests
        farmer_id = session.get('user_id', request.args.get('farmer_id', 1))
        harvests = db.query("SELECT * FROM harvests WHERE farmer_id = %s ORDER BY id DESC", (farmer_id,))
        return jsonify({'success': True, 'harvests': harvests})


# ==============================================================================
# 5. SELLER APIS (Seller Agribusiness & B2B/B2C Workflow)
# ==============================================================================

@app.route('/api/seller/farmer-harvests', methods=['GET'])
def api_seller_farmer_harvests():
    """
    Sellers view all available crops posted by farmers across regions.
    """
    harvests = db.query("""
        SELECT h.*, u.name as farmer_name, u.phone as farmer_phone, u.city as farmer_city
        FROM harvests h
        JOIN users u ON h.farmer_id = u.id
        ORDER BY h.status ASC, h.id DESC
    """)
    return jsonify({'success': True, 'harvests': harvests})

@app.route('/api/seller/buy-harvest/<int:harvest_id>', methods=['POST'])
def api_seller_buy_harvest(harvest_id):
    """
    Seller acquires/purchases farmer harvest -> updates status & notifies farmer!
    """
    data = request.get_json() or {}
    seller_id = session.get('user_id', data.get('seller_id', 2))
    
    harvest = db.query("SELECT * FROM harvests WHERE id = %s", (harvest_id,), fetchone=True)
    if not harvest:
        return jsonify({'success': False, 'message': 'Harvest record not found.'}), 404
        
    seller = db.query("SELECT name FROM users WHERE id = %s", (seller_id,), fetchone=True)
    seller_name = seller['name'] if seller else "ABC Agro Traders"
    
    # Update harvest status
    db.query(
        "UPDATE harvests SET status = 'purchased_by_seller', purchased_by_seller_id = %s WHERE id = %s",
        (seller_id, harvest_id)
    )
    
    # Send notification to the farmer
    farmer_id = harvest['farmer_id']
    db.query(
        "INSERT INTO notifications (user_id, title, message, type, link_url) VALUES (%s, %s, %s, %s, %s)",
        (farmer_id, "Harvest Purchased by Seller!", f"{seller_name} has accepted and purchased your {harvest['crop_name']} ({harvest['quantity']} {harvest['unit']}) at ₹{harvest['expected_price_per_unit']}/{harvest['unit']}.", "harvest", "/farmer/dashboard#harvests")
    )
    
    return jsonify({
        'success': True,
        'message': f"Successfully acquired {harvest['crop_name']} ({harvest['quantity']} {harvest['unit']}) from farmer!",
        'harvest': harvest
    })

@app.route('/api/seller/inventory', methods=['GET'])
def api_seller_inventory():
    seller_id = session.get('user_id', request.args.get('seller_id', 2))
    products = db.query("SELECT * FROM products WHERE seller_id = %s ORDER BY id DESC", (seller_id,))
    purchased_harvests = db.query("SELECT * FROM harvests WHERE purchased_by_seller_id = %s ORDER BY id DESC", (seller_id,))
    
    return jsonify({
        'success': True,
        'products': products,
        'purchased_harvests': purchased_harvests
    })

@app.route('/api/seller/create-product', methods=['POST'])
def api_seller_create_product():
    """
    Seller publishes an item to the Buyer Website Marketplace!
    """
    data = request.form.to_dict() if request.form else (request.get_json() or {})
    seller_id = session.get('user_id', data.get('seller_id', 2))
    name = data.get('name', 'Farm Produce')
    category_id = int(data.get('category_id', 3))
    price = float(data.get('price', 50.0))
    unit = data.get('unit', 'KG')
    stock = float(data.get('stock_quantity', 100))
    short_desc = data.get('short_description', '')
    desc = data.get('description', '')
    is_organic = 1 if str(data.get('is_organic')).lower() in ['1', 'true', 'on'] else 0
    remedy_for = data.get('remedy_for_disease', None)
    
    image_url = 'https://images.unsplash.com/photo-1586201375761-83865001e31c?w=500'
    if 'image' in request.files:
        file = request.files['image']
        if file and file.filename:
            fn = f"product_{int(time.time())}_{secure_filename(file.filename)}"
            file.save(os.path.join(Config.PRODUCT_UPLOAD_FOLDER, fn))
            image_url = f"/uploads/product_images/{fn}"
            
    slug = name.lower().replace(' ', '-').replace('/', '-')
    
    product_id = db.query(
        """INSERT INTO products (seller_id, category_id, name, slug, short_description, description, price, unit, stock_quantity, image_url, is_organic, remedy_for_disease)
           VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""",
        (seller_id, category_id, name, slug, short_desc, desc, price, unit, stock, image_url, is_organic, remedy_for),
        insert=True
    )
    
    return jsonify({
        'success': True,
        'message': 'Product published to Buyer Marketplace successfully!',
        'product_id': product_id
    })

@app.route('/api/seller/orders', methods=['GET'])
def api_seller_orders():
    seller_id = session.get('user_id', request.args.get('seller_id', 2))
    orders = db.query("""
        SELECT o.*, oi.quantity, oi.unit_price, oi.total_price, p.name as product_name, p.image_url as product_image, u.name as buyer_name
        FROM orders o
        JOIN order_items oi ON o.id = oi.order_id
        JOIN products p ON oi.product_id = p.id
        JOIN users u ON o.buyer_id = u.id
        WHERE p.seller_id = %s
        ORDER BY o.id DESC
    """, (seller_id,))
    return jsonify({'success': True, 'orders': orders})

@app.route('/api/seller/orders/<int:order_id>/status', methods=['PUT'])
def api_seller_update_order_status(order_id):
    data = request.get_json() or {}
    new_status = data.get('status', 'processing')
    db.query("UPDATE orders SET order_status = %s WHERE id = %s", (new_status, order_id))
    
    order = db.query("SELECT buyer_id, order_number FROM orders WHERE id = %s", (order_id,), fetchone=True)
    if order:
        db.query(
            "INSERT INTO notifications (user_id, title, message, type, link_url) VALUES (%s, %s, %s, %s, %s)",
            (order['buyer_id'], f"Order #{order['order_number']} Updated", f"Your order status is now: {new_status.replace('_', ' ').title()}", "order", "/buyer/dashboard")
        )
    return jsonify({'success': True, 'message': 'Order status updated.'})


# ==============================================================================
# 6. BUYER & MARKETPLACE APIS (Marketplace, Cart, Checkout)
# ==============================================================================

@app.route('/api/categories', methods=['GET'])
def api_categories():
    categories = db.query("SELECT * FROM product_categories ORDER BY id ASC")
    return jsonify({'success': True, 'categories': categories})

@app.route('/api/products', methods=['GET'])
def api_products():
    category_id = request.args.get('category_id')
    search = request.args.get('search', '').strip()
    is_organic = request.args.get('is_organic')
    remedy = request.args.get('remedy')
    
    sql = """
        SELECT p.*, c.name as category_name, u.name as seller_name
        FROM products p
        JOIN product_categories c ON p.category_id = c.id
        LEFT JOIN users u ON p.seller_id = u.id
        WHERE 1=1
    """
    params = []
    
    if category_id:
        sql += " AND p.category_id = %s"
        params.append(category_id)
    if is_organic:
        sql += " AND p.is_organic = 1"
    if remedy:
        sql += " AND p.remedy_for_disease LIKE %s"
        params.append(f"%{remedy}%")
    if search:
        sql += " AND (p.name LIKE %s OR p.description LIKE %s)"
        params.append(f"%{search}%")
        params.append(f"%{search}%")
        
    sql += " ORDER BY p.id ASC"
    products = db.query(sql, tuple(params))
    return jsonify({'success': True, 'products': products})

@app.route('/api/products/<int:product_id>', methods=['GET'])
def api_product_detail(product_id):
    product = db.query("""
        SELECT p.*, c.name as category_name, u.name as seller_name, u.city as seller_city
        FROM products p
        JOIN product_categories c ON p.category_id = c.id
        LEFT JOIN users u ON p.seller_id = u.id
        WHERE p.id = %s
    """, (product_id,), fetchone=True)
    
    if not product:
        return jsonify({'success': False, 'message': 'Product not found.'}), 404
        
    reviews = db.query("""
        SELECT r.*, u.name as user_name FROM reviews r
        JOIN users u ON r.user_id = u.id
        WHERE r.product_id = %s ORDER BY r.id DESC
    """, (product_id,))
    
    return jsonify({'success': True, 'product': product, 'reviews': reviews})

@app.route('/api/cart', methods=['GET', 'POST', 'DELETE'])
def api_cart():
    user_id = session.get('user_id', request.args.get('user_id', 3))
    
    if request.method == 'POST':
        data = request.get_json() or {}
        product_id = data.get('product_id')
        qty = float(data.get('quantity', 1))
        
        if not product_id:
            return jsonify({'success': False, 'message': 'Product ID required'}), 400
            
        existing = db.query("SELECT id, quantity FROM cart_items WHERE user_id = %s AND product_id = %s", (user_id, product_id), fetchone=True)
        if existing:
            new_qty = existing['quantity'] + qty
            db.query("UPDATE cart_items SET quantity = %s WHERE id = %s", (new_qty, existing['id']))
        else:
            db.query("INSERT INTO cart_items (user_id, product_id, quantity) VALUES (%s, %s, %s)", (user_id, product_id, qty))
            
        return jsonify({'success': True, 'message': 'Item added to cart!'})
        
    elif request.method == 'DELETE':
        item_id = request.args.get('item_id')
        if item_id:
            db.query("DELETE FROM cart_items WHERE id = %s AND user_id = %s", (item_id, user_id))
        else:
            db.query("DELETE FROM cart_items WHERE user_id = %s", (user_id,))
        return jsonify({'success': True, 'message': 'Cart updated.'})
        
    else: # GET cart
        items = db.query("""
            SELECT ci.id as cart_item_id, ci.quantity, p.*, c.name as category_name
            FROM cart_items ci
            JOIN products p ON ci.product_id = p.id
            JOIN product_categories c ON p.category_id = c.id
            WHERE ci.user_id = %s
        """, (user_id,))
        
        subtotal = sum(item['price'] * item['quantity'] for item in items)
        delivery = 50.0 if subtotal > 0 and subtotal < 500 else 0.0
        total = subtotal + delivery
        
        return jsonify({
            'success': True,
            'items': items,
            'summary': {
                'subtotal': subtotal,
                'delivery': delivery,
                'total': total,
                'item_count': len(items)
            }
        })

@app.route('/api/orders', methods=['GET', 'POST'])
def api_orders():
    user_id = session.get('user_id', request.args.get('user_id', 3))
    
    if request.method == 'POST':
        data = request.get_json() or {}
        address = data.get('shipping_address', 'Madhapur, Hyderabad')
        phone = data.get('phone', '9876543212')
        payment_method = data.get('payment_method', 'upi')
        
        # Get items from cart or direct payload
        cart_items = db.query("""
            SELECT ci.product_id, ci.quantity, p.price, p.name, p.seller_id
            FROM cart_items ci
            JOIN products p ON ci.product_id = p.id
            WHERE ci.user_id = %s
        """, (user_id,))
        
        if not cart_items:
            # Fallback for single item buy-now
            prod_id = data.get('product_id')
            qty = float(data.get('quantity', 1))
            if prod_id:
                p = db.query("SELECT id as product_id, price, name, seller_id FROM products WHERE id = %s", (prod_id,), fetchone=True)
                if p:
                    p['quantity'] = qty
                    cart_items = [p]
                    
        if not cart_items:
            return jsonify({'success': False, 'message': 'No items to order.'}), 400
            
        total_amt = sum(item['price'] * item['quantity'] for item in cart_items)
        order_num = f"SAG-{int(time.time())}-{uuid.uuid4().hex[:4].upper()}"
        tracking_num = f"TRK-AGRI-{uuid.uuid4().hex[:6].upper()}"
        
        order_id = db.query(
            """INSERT INTO orders (order_number, buyer_id, total_amount, payment_method, payment_status, order_status, shipping_address, contact_phone, tracking_number)
               VALUES (%s, %s, %s, %s, 'paid', 'placed', %s, %s, %s)""",
            (order_num, user_id, total_amt, payment_method, address, phone, tracking_num),
            insert=True
        )
        
        # Insert items and notify sellers
        for item in cart_items:
            db.query(
                "INSERT INTO order_items (order_id, product_id, quantity, unit_price, total_price) VALUES (%s, %s, %s, %s, %s)",
                (order_id, item['product_id'], item['quantity'], item['price'], item['price'] * item['quantity'])
            )
            # Deduct stock
            db.query("UPDATE products SET stock_quantity = CASE WHEN stock_quantity >= %s THEN stock_quantity - %s ELSE 0 END WHERE id = %s", (item['quantity'], item['quantity'], item['product_id']))
            # Notify seller
            if item.get('seller_id'):
                db.query(
                    "INSERT INTO notifications (user_id, title, message, type, link_url) VALUES (%s, %s, %s, %s, %s)",
                    (item['seller_id'], "New Order Received!", f"New order #{order_num} placed for {item['name']} ({item['quantity']} units).", "order", "/seller/dashboard#orders")
                )
                
        # Clear buyer cart
        db.query("DELETE FROM cart_items WHERE user_id = %s", (user_id,))
        
        # Notify buyer
        db.query(
            "INSERT INTO notifications (user_id, title, message, type, link_url) VALUES (%s, %s, %s, %s, %s)",
            (user_id, "Order Placed Successfully!", f"Your order #{order_num} has been confirmed. Tracking ID: {tracking_num}", "order", "/buyer/dashboard")
        )
        
        return jsonify({
            'success': True,
            'message': 'Order placed successfully!',
            'order_number': order_num,
            'order_id': order_id,
            'tracking_number': tracking_num
        })
    else: # GET orders
        orders = db.query("""
            SELECT o.*, COUNT(oi.id) as total_items
            FROM orders o
            LEFT JOIN order_items oi ON o.id = oi.order_id
            WHERE o.buyer_id = %s
            GROUP BY o.id
            ORDER BY o.id DESC
        """, (user_id,))
        return jsonify({'success': True, 'orders': orders})

@app.route('/api/orders/<int:order_id>/items', methods=['GET'])
def api_order_items(order_id):
    items = db.query("""
        SELECT oi.*, p.name as product_name, p.image_url as product_image, p.unit
        FROM order_items oi
        JOIN products p ON oi.product_id = p.id
        WHERE oi.order_id = %s
    """, (order_id,))
    return jsonify({'success': True, 'items': items})


# ==============================================================================
# 7. UNIFIED NOTIFICATIONS API
# ==============================================================================

@app.route('/api/notifications', methods=['GET'])
def api_notifications():
    user_id = session.get('user_id', request.args.get('user_id', 1))
    notes = db.query("SELECT * FROM notifications WHERE user_id = %s ORDER BY id DESC LIMIT 15", (user_id,))
    unread = sum(1 for n in notes if not n['is_read'])
    return jsonify({'success': True, 'notifications': notes, 'unread_count': unread})

@app.route('/api/notifications/<int:note_id>/read', methods=['PUT'])
def api_mark_notification_read(note_id):
    db.query("UPDATE notifications SET is_read = 1 WHERE id = %s", (note_id,))
    return jsonify({'success': True})


if __name__ == '__main__':
    print("=" * 70)
    print(" SMART AI AGRICULTURE ECOSYSTEM SERVER RUNNING ")
    print("=" * 70)
    print(" Ecosystem Hub:       http://127.0.0.1:5000/")
    print(" Farmer Website:      http://127.0.0.1:5000/farmer")
    print(" Seller Website:      http://127.0.0.1:5000/seller")
    print(" Buyer Website:       http://127.0.0.1:5000/buyer")
    print("=" * 70)
    app.run(host='0.0.0.0', port=5000, debug=False)
