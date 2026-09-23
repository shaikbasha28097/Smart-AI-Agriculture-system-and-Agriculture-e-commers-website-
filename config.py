import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

class Config:
    BASE_DIR = BASE_DIR
    SECRET_KEY = os.environ.get('SECRET_KEY', 'smart-agri-ai-ecosystem-secret-key-2026')
    
    # MySQL Database Configuration
    MYSQL_HOST = os.environ.get('MYSQL_HOST', 'localhost')
    MYSQL_PORT = int(os.environ.get('MYSQL_PORT', 3306))
    MYSQL_USER = os.environ.get('MYSQL_USER', 'root')
    MYSQL_PASSWORD = os.environ.get('MYSQL_PASSWORD', '')
    MYSQL_DB = os.environ.get('MYSQL_DB', 'smart_agri_db')
    
    # SQLite fallback database file
    SQLITE_DB_PATH = os.path.join(BASE_DIR, 'Database', 'smart_agri.db')
    
    # Upload Storage Folders
    UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads')
    DISEASE_UPLOAD_FOLDER = os.path.join(UPLOAD_FOLDER, 'disease_images')
    CROP_UPLOAD_FOLDER = os.path.join(UPLOAD_FOLDER, 'crop_images')
    PRODUCT_UPLOAD_FOLDER = os.path.join(UPLOAD_FOLDER, 'product_images')
    
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16 MB max upload
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'webp', 'gif'}
    
    # Server URLs / Ports for unified ecosystem
    BASE_URL = os.environ.get('BASE_URL', 'http://127.0.0.1:5000')
    FARMER_URL = os.environ.get('FARMER_URL', 'http://127.0.0.1:5000/farmer')
    SELLER_URL = os.environ.get('SELLER_URL', 'http://127.0.0.1:5000/seller')
    BUYER_URL = os.environ.get('BUYER_URL', 'http://127.0.0.1:5000/buyer')
