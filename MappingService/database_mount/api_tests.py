import requests

URL = "http://localhost:5000"

payload = {'filepath':'//ip/test4.mp4', 'modified':192000}
r = requests.post(url=f'{URL}/file/status', json=payload)