import os
import requests

TOKEN = 'b76433712f84bbcf93f2f3c4c28dc75d07b98516'
USERNAME = 'LavanyaChalla09'
headers = {'Authorization': f'Token {TOKEN}'}
domain_name = f'{USERNAME}.pythonanywhere.com'

base_dir = os.path.abspath(os.path.dirname(__file__))

print(f"[*] Starting full deployment to {domain_name}...")

# 1. Upload files
uploaded_count = 0
for root, dirs, files in os.walk(base_dir):
    if '__pycache__' in root or '.git' in root or 'node_modules' in root:
        continue
    for file in files:
        if file.endswith('.pyc') or file == 'cloudflared.exe':
            continue
        local_path = os.path.join(root, file)
        rel_path = os.path.relpath(local_path, base_dir).replace('\\', '/')
        
        remote_url = f"https://www.pythonanywhere.com/api/v0/user/{USERNAME}/files/path/home/{USERNAME}/student_attendance_system/{rel_path}"
        with open(local_path, 'rb') as f:
            content = f.read()
        res = requests.post(remote_url, headers=headers, files={'content': content})
        if res.status_code in [200, 201]:
            print(f"  [OK] Uploaded: {rel_path}")
            uploaded_count += 1
        else:
            print(f"  [FAIL] {rel_path}: {res.status_code}")

print(f"\n[+] Total files uploaded: {uploaded_count}")

# 2. Configure WSGI file
wsgi_content = f"""import sys
path = '/home/{USERNAME}/student_attendance_system'
if path not in sys.path:
    sys.path.append(path)

from app import app as application
"""

wsgi_url = f"https://www.pythonanywhere.com/api/v0/user/{USERNAME}/files/path/var/www/lavanyachalla09_pythonanywhere_com_wsgi.py"
res_wsgi = requests.post(wsgi_url, headers=headers, files={'content': wsgi_content.encode('utf-8')})
print(f"[*] WSGI configured: {res_wsgi.status_code}")

# 3. Reload Webapp
reload_url = f"https://www.pythonanywhere.com/api/v0/user/{USERNAME}/webapps/{domain_name}/reload/"
res_reload = requests.post(reload_url, headers=headers)
print(f"[*] Webapp reload: {res_reload.status_code} {res_reload.text}")

print(f"\n[+] SUCCESS! Webapp is live at: https://{domain_name}")
