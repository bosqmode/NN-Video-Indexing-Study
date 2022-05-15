import os
import requests
import time
import random

URL = os.environ['DB_ENDPOINT']
ROOT_DIR = os.environ['SEARCH_ROOT']
ALLOWED_FILES = ['mp4']

abs_filepaths = []

#Add new discovered files, and update last_modified times
for (root, dirs, files) in os.walk(ROOT_DIR, topdown=True):
    print(root)
    print(files)

    for file in files:
        if file.lower()[-3:] in ALLOWED_FILES:
            abs_path = f'{root}/{file}'
            modified_time = int(os.path.getmtime(abs_path))
            payload = {'filepath':abs_path, 'last_modified': modified_time}
            r = requests.post(url=f'{URL}/file/status', json=payload)
            abs_filepaths.append(abs_path)


#Remove files found in DB, but not in search
db_files = requests.get(url=f'{URL}/files')
db_files = db_files.json()

for obj in db_files['results']:
    if obj['filepath'] not in abs_filepaths:
        print(f'Removing: {obj["filepath"]}')
        payload = {'filepath':obj["filepath"]}
        r = requests.delete(url=f'{URL}/file/removed', json=payload)