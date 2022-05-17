import VideoScanner.imagenet_labels as lbl
import VideoScanner.frame_scanner as sc
import os
import requests
import shutil

URL = os.environ['DB_ENDPOINT']
FILE_ID = -1
MODEL = int(os.environ['MODEL'])

def detection_callback(detection, timestamp):
    global FILE_ID
    global MODEL
    print(f'{detection} : {timestamp}')
    #(video_ts, category, model, file_id) 
    payload = {'file_id':FILE_ID, 'category':detection, 'video_ts':int(timestamp), 'model':MODEL}
    r = requests.post(url=f'{URL}/detections/add', json=payload)
    print(r)

unlabelled_files = requests.get(url=f'{URL}/files/unlabelled')
unlabelled_files = unlabelled_files.json()

if len(unlabelled_files['results']) > 0:
    scanner = sc.ResNet50Scanner(lbl.labels, 'VideoScanner/model')
    player = sc.OpencvVideoPlayer(scanner, detection_callback)

    file = unlabelled_files['results'][0]['filepath']
    FILE_ID = unlabelled_files['results'][0]['id']
    file_split = file.split('/')
    file_name = file_split[len(file_split)-1]
    shutil.copyfile(file, file_name)
    print(file)
    player.play(file_name)

    # player.play(file)
    # print("done")

    payload = {'id':FILE_ID}
    r = requests.post(url=f'{URL}/detections/finished', json=payload)

    os.remove(file_name)

    print(r)