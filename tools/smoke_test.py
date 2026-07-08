import requests
import os

API = 'http://127.0.0.1:8000/api'

# 1. register a temp company (if exists, ignore)
reg = requests.post(API + '/auth/register', json={'company_name':'smoke_test_company','password':'testpass'})
print('register', reg.status_code, reg.text[:200])

# 2. login
login = requests.post(API + '/auth/login', data={'username':'smoke_test_company','password':'testpass'})
print('login', login.status_code, login.text[:200])
if login.status_code != 200:
    raise SystemExit('Login failed')

token = login.json().get('access_token')
headers = {'Authorization': 'Bearer ' + token}

# 3. create a project
p = requests.post(API + '/projects/', json={'name':'Smoke Project'}, headers=headers)
print('create project', p.status_code, p.text[:200])
project_id = p.json().get('id') if p.ok else None

# 4. add a worker
w = requests.post(API + '/labour/workers', json={'name':'Test Worker','role':'Worker','project_id':project_id}, headers=headers)
print('add worker', w.status_code, w.text[:200])
worker_id = w.json().get('id')

# 5. upload a small text file as image/pdf (use a tiny png)
from io import BytesIO
fp = BytesIO(b"hello")
files = {'file': ('test.txt', fp, 'text/plain')}
fd = {'project_id': str(project_id)}
up = requests.post(API + '/uploads/', files=files, data=fd, headers=headers)
print('upload', up.status_code, up.text[:200])

# 6. mark attendance for the worker
att = requests.post(API + '/labour/attendance', json={'entries':[{'worker_id': worker_id, 'status':'present'}]}, headers=headers)
print('attendance', att.status_code, att.text[:200])

# 7. list uploads (public file_url should be present)
list_u = requests.get(API + '/uploads/', headers=headers)
print('list uploads', list_u.status_code, list_u.text[:200])

print('Done')
