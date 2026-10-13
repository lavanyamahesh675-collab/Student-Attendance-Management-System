import os
import sys
import requests

def deploy(username, api_token, mysql_password=None):
    base_url = f"https://www.pythonanywhere.com/api/v0/user/{username}"
    headers = {"Authorization": f"Token {api_token}"}
    domain_name = f"{username}.pythonanywhere.com"

    print(f"[*] Deploying Student Attendance System for {username}...")

    # 1. Create or check Web App
    webapps_url = f"{base_url}/webapps/"
    res = requests.get(webapps_url, headers=headers)
    existing_domains = [w['domain_name'] for w in res.json()] if res.status_code == 200 else []

    if domain_name not in existing_domains:
        print(f"[*] Creating web app {domain_name}...")
        create_res = requests.post(webapps_url, headers=headers, json={
            "domain_name": domain_name,
            "python_version": "python310"
        })
        print(f"Webapp creation: {create_res.status_code}")
    else:
        print(f"[*] Web app {domain_name} already exists.")

    # 2. Upload zip file
    zip_path = os.path.join(os.path.dirname(__file__), "..", "student_attendance_system.zip")
    if not os.path.exists(zip_path):
        zip_path = "student_attendance_system.zip"

    if os.path.exists(zip_path):
        print(f"[*] Uploading project zip file...")
        upload_url = f"{base_url}/files/path/home/{username}/student_attendance_system.zip"
        with open(zip_path, "rb") as f:
            upload_res = requests.post(upload_url, headers=headers, files={"content": f})
        print(f"Zip upload: {upload_res.status_code}")

    # 3. Configure WSGI file
    wsgi_content = f"""import sys
path = '/home/{username}/student_attendance_system'
if path not in sys.path:
    sys.path.append(path)

from app import app as application
"""
    wsgi_url = f"{base_url}/files/path/var/www/{username.lower()}_pythonanywhere_com_wsgi.py"
    wsgi_res = requests.post(wsgi_url, headers=headers, files={"content": wsgi_content.encode('utf-8')})
    print(f"WSGI configuration: {wsgi_res.status_code}")

    # 4. Reload webapp
    reload_url = f"{base_url}/webapps/{domain_name}/reload/"
    reload_res = requests.post(reload_url, headers=headers)
    print(f"Reload webapp: {reload_res.status_code}")

    print(f"\n[+] DEPLOYMENT COMPLETED!")
    print(f"Live URL: https://{domain_name}")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python deploy_to_pythonanywhere.py <username> <api_token>")
    else:
        deploy(sys.argv[1], sys.argv[2])
