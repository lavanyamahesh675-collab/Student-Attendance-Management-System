import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'attendance_management_secret_key_dbms_2026'
    
    # Auto-detect PythonAnywhere environment vs Local
    if 'PYTHONANYWHERE_DOMAIN' in os.environ or os.path.exists('/home/LavanyaChalla09'):
        DB_HOST = os.environ.get('DB_HOST') or 'lavanyachalla09.mysql.pythonanywhere-services.com'
        DB_USER = os.environ.get('DB_USER') or 'LavanyaChalla09'
        DB_PASSWORD = os.environ.get('DB_PASSWORD') or 'root123'
        DB_NAME = os.environ.get('DB_NAME') or 'LavanyaChalla09$attendance_db'
        DB_PORT = 3306
    else:
        DB_HOST = os.environ.get('DB_HOST', 'localhost')
        DB_USER = os.environ.get('DB_USER', 'root')
        DB_PASSWORD = os.environ.get('DB_PASSWORD', 'root')
        DB_NAME = os.environ.get('DB_NAME', 'attendance_db')
        DB_PORT = int(os.environ.get('DB_PORT', 3306))
