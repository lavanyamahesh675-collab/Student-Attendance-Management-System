import mysql.connector
from werkzeug.security import generate_password_hash
from config import Config
import db_adapter
import os
import sqlite3

admin_hash = generate_password_hash('admin123')
faculty_hash = generate_password_hash('faculty123')

print("Admin hash len:", len(admin_hash))
print("Faculty hash len:", len(faculty_hash))

# Update SQLite
sqlite_path = os.path.join(os.path.dirname(__file__), 'attendance.db')
if os.path.exists(sqlite_path):
    conn_sq = sqlite3.connect(sqlite_path)
    cur_sq = conn_sq.cursor()
    cur_sq.execute("UPDATE users SET password = ? WHERE email = 'admin@attendance.com'", (admin_hash,))
    cur_sq.execute("UPDATE users SET password = ? WHERE email = 'faculty@attendance.com'", (faculty_hash,))
    cur_sq.execute("UPDATE users SET password = ? WHERE email = 'prof.sharma@attendance.com'", (faculty_hash,))
    conn_sq.commit()
    conn_sq.close()
    print("Updated SQLite passwords!")

# Update MySQL
try:
    conn_my = mysql.connector.connect(host=Config.DB_HOST, user=Config.DB_USER, password=Config.DB_PASSWORD, database=Config.DB_NAME)
    cur_my = conn_my.cursor()
    cur_my.execute("UPDATE users SET password = %s WHERE email = 'admin@attendance.com'", (admin_hash,))
    cur_my.execute("UPDATE users SET password = %s WHERE email = 'faculty@attendance.com'", (faculty_hash,))
    cur_my.execute("UPDATE users SET password = %s WHERE email = 'prof.sharma@attendance.com'", (faculty_hash,))
    conn_my.commit()
    conn_my.close()
    print("Updated MySQL passwords!")
except Exception as e:
    print("MySQL error:", e)
