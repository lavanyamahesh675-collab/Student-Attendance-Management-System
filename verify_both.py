import app

client = app.app.test_client()
res = client.post('/login', data={'email': 'faculty@attendance.com', 'password': 'faculty123'}, follow_redirects=True)
print("Faculty login status:", res.status_code)
assert b"Welcome back" in res.data or b"Dashboard" in res.data, "Faculty login failed!"
print("Faculty Login: SUCCESSFUL!")

# Test manage faculty as admin
client_admin = app.app.test_client()
client_admin.post('/login', data={'email': 'admin@attendance.com', 'password': 'admin123'}, follow_redirects=True)
res_fac = client_admin.get('/faculty')
print("Manage Faculty status:", res_fac.status_code)
assert res_fac.status_code == 200, "Manage Faculty failed!"
print("Manage Faculty: SUCCESSFUL 200 OK!")
