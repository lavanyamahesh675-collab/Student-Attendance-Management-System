import requests

BASE = 'https://LavanyaChalla09.pythonanywhere.com'

# 1. Test Faculty Login
s_fac = requests.Session()
res_fac_login = s_fac.post(f'{BASE}/login', data={'email': 'faculty@attendance.com', 'password': 'faculty123'})
print("Faculty Login Final URL:", res_fac_login.url)
print("Faculty Login Status:", res_fac_login.status_code)
assert 'dashboard' in res_fac_login.url or 'Dashboard' in res_fac_login.text, "Faculty login failed!"
print(">>> TEST 1 PASSED: Faculty Login works successfully!")

# 2. Test Admin Login & Manage Faculty (/faculty)
s_adm = requests.Session()
s_adm.post(f'{BASE}/login', data={'email': 'admin@attendance.com', 'password': 'admin123'})
res_manage_fac = s_adm.get(f'{BASE}/faculty')
print("Manage Faculty Status:", res_manage_fac.status_code)
assert res_manage_fac.status_code == 200, f"Manage Faculty failed with status {res_manage_fac.status_code}"
assert "Dr. Ramesh Verma" in res_manage_fac.text, "Dr. Ramesh Verma missing in faculty list!"
print(">>> TEST 2 PASSED: Manage Faculty loads 200 OK without Internal Server Error!")
