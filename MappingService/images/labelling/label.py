import VideoScanner.imagenet_labels as imagenet_labels
import VideoScanner.coco_final_labels_transfer as coco_labels
import VideoScanner.frame_scanner as sc
import os
import requests
import shutil

URL = os.environ['DB_ENDPOINT']
FILE_ID = -1
MODEL = int(os.environ['MODEL'])

def detection_callback(detections, timestamp):
    global FILE_ID
    global MODEL
    for detectiontuple in detections:
        payload = {'file_id':FILE_ID, 'category':detectiontuple[0], 'video_ts':int(timestamp), 'model':MODEL, 'confidence':float(detectiontuple[1])}
        r = requests.post(url=f'{URL}/detections/add', json=payload)
        print(r)

unlabelled_files = requests.get(url=f'{URL}/files/unlabelled')
unlabelled_files = unlabelled_files.json()

if len(unlabelled_files['results']) > 0:
    #scanner = sc.ResNet50Scanner(imagenet_labels.labels, 'VideoScanner/resnetmodel')
    scanner = sc.SiameseScanner('VideoScanner/siamesemodel', coco_labels.labels)
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