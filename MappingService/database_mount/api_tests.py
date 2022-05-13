from random import random
import requests
import time
import random

URL = "http://localhost:5000"

payload = {'filepath':'directory1/test1.mp4', 'last_searched':0, 'last_modified': 19200}
r = requests.post(url=f'{URL}/file/status', json=payload)
print(r)

payload = {'filepath':'directory1/test2.mp4', 'last_searched':0, 'last_modified': 20000}
r = requests.post(url=f'{URL}/file/status', json=payload)
print(r)

payload = {'filepath':'directory2/test3.mp4', 'last_searched':0, 'last_modified': 25000}
r = requests.post(url=f'{URL}/file/status', json=payload)
print(r)

payload = {'filepath':'directory2/test4.mp4', 'last_searched':0, 'last_modified': 30000}
r = requests.post(url=f'{URL}/file/status', json=payload)
print(r)

payload = {'id':2}
r = requests.get(url=f'{URL}/file/id', json=payload)
print(r.json())

payload = {'filepath':'directory1/test2.mp4'}
r = requests.get(url=f'{URL}/file/path', json=payload)
print(r.json())

payload = {'file_id':1}
r = requests.get(url=f'{URL}/detections/fileid', json=payload)
print(r.json())

payload = {'filepath':'jep/juu24.mp4', 'last_searched':0, 'last_modified': 30000}
r = requests.post(url=f'{URL}/file/status', json=payload)
print(r)

payload = {'filepath':'jep/juu24.mp4'}
r = requests.delete(url=f'{URL}/file/removed', json=payload)
print(r)

payload = {'model_name':'ResNet50_test', 'version_string':'v1.0', 'description_text':str(random.random()), 'added_timestamp':int(time.time())}
r = requests.post(url=f'{URL}/model/add', json=payload)
print(r)

payload = {'model_name':'ResNet50_test', 'version_string':'v1.1', 'description_text':str(random.random()), 'added_timestamp':int(time.time())}
r = requests.post(url=f'{URL}/model/add', json=payload)
print(r)

r = requests.get(url=f'{URL}/models')
print(r.json())

# payload = {'model':1, 'category':'car', 'video_ts':int(time.time()), 'file_id':2}
# r = requests.post(url=f'{URL}/detections/add', json=payload)
# print(r)

# payload = {'file_id':2}
# r = requests.get(url=f'{URL}/detections/fileid', json=payload)
# print(r.json())

payload = {'filepath':'directory1/test1.mp4'}
r = requests.get(url=f'{URL}/detections/filepath', json=payload)
print(r.json())