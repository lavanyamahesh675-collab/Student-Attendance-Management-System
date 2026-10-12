import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'attendance_management_secret_key_dbms_2026'
    
    # Database Configuration
    DB_HOST = os.environ.get('DB_HOST', 'localhost')
    DB_USER = os.environ.get('DB_USER', 'root')
    DB_PASSWORD = os.environ.get('DB_PASSWORD', 'root')  # Change your MySQL password here
    DB_NAME = os.environ.get('DB_NAME', 'attendance_db')
    DB_PORT = int(os.environ.get('DB_PORT', 3306))
