import requests
import re

s = requests.Session()
res = s.post('https://LavanyaChalla09.pythonanywhere.com/login', data={'email': 'admin@attendance.com', 'password': 'admin123'})
print('Status code:', res.status_code)
print('Final URL:', res.url)

alerts = re.findall(r'<div class="alert[^"]*">\s*<span>(.*?)</span>', res.text)
print('Alerts:', alerts)
