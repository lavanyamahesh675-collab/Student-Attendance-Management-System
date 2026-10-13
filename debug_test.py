import app

client = app.app.test_client()
res = client.post('/login', data={'email': 'admin@attendance.com', 'password': 'admin123'})
print("Login status:", res.status_code)
if b"alert" in res.data:
    import re
    print("Alerts:", re.findall(r'<div class="alert[^"]*">\s*<span>(.*?)</span>', res.data.decode('utf-8')))

conn = app.get_db_connection()
cursor = conn.cursor(dictionary=True)
cursor.execute("SELECT email, password, role FROM users")
print("Users in DB:", cursor.fetchall())
