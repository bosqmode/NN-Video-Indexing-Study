import requests

URL = "http://localhost:5000"

# payload = {'filepath':'directory1/test1.mp4', 'modified':192000}
# r = requests.post(url=f'{URL}/file/status', json=payload)
# print(r)

# payload = {'filepath':'directory1/test2.mp4', 'modified':0}
# r = requests.post(url=f'{URL}/file/status', json=payload)
# print(r)

payload = {'filepath':'jep/juu.mp4', 'modified':0}
r = requests.post(url=f'{URL}/file/status', json=payload)
print(r)

# payload = {'file_id':1}
# r = requests.get(url=f'{URL}/file/status', json=payload)
# print(r.json())

# payload = {'id':1, 'model':'TestNet99'}
# r = requests.post(url=f'{URL}/detection/finished', json=payload)
# print(r)

payload = {'filepath':'jep/juu.mp4'}
r = requests.post(url=f'{URL}/file/removed', json=payload)
print(r)