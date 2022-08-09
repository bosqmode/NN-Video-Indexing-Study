import cv2
import numpy as np
from tensorflow.keras.models import Model
from tensorflow.keras.layers import *
from tensorflow.keras.optimizers import Adam
import tensorflow as tf
import cv2
import os
import tensorflow_datasets as tfds
import datetime
from coco import COCO
from coco_final_labels import labels as coco_labels
from coco_final_labels_transfer import labels as coco_labels_transfer
import shutil
from tensorflow.keras.utils import to_categorical
from tensorflow import keras
import random
import tensorflow_addons as tfa
import io
from scipy.spatial import distance
import time

def crop(cvimg, bbox):
    left = int(bbox[0])
    right = int(bbox[0]+bbox[2])
    top = int(bbox[1])
    bottom = int(bbox[1]+bbox[3])
    newimg = cvimg[top:bottom, left:right]
    return newimg

gpus = tf.config.experimental.list_physical_devices('GPU')
for gpu in gpus: 
    tf.config.experimental.set_memory_growth(gpu, True)

def load_image(filename):
    image = tf.io.read_file(filename)
    image = tf.image.decode_jpeg(image, channels=3)
    image = tf.image.resize(image, (224,224))
    image = tf.cast(image, tf.float32) / 255.
    return image

model = tf.keras.models.load_model('weights/siamese_tripletloss/transfer-20220805-201928/final_embedding_transferred')

print("model loaded")

from sklearn.neighbors import NearestNeighbors

transfer_anchor_averages = []
transfer_anchor_weights = []

for i,c in enumerate(coco_labels_transfer):
    anchs = []

    for image in os.listdir(f'data/siamese_anchors_tripletloss_transfer/{c}'):
        img = load_image(f'data/siamese_anchors_tripletloss_transfer/{c}/{image}')
        anchs.append(img)

    preds = model.predict(np.array(anchs).reshape(len(anchs),224,224,3))
    transfer_anchor_averages.append(np.average(preds, axis=0))
    transfer_anchor_weights.append(1-np.std(preds))
    print(f"{c} : {transfer_anchor_weights[-1]}")

print("anchor averages loaded")

MAX_RESOLUTION = 224*3
WINDOW_SIZE = 224
STRIDE = WINDOW_SIZE * 0.5

print(MAX_RESOLUTION)
print(STRIDE)

cap = cv2.VideoCapture("data/testvideos/cycling_in_city.mp4")
frame_counter = 0


while True:
    ret, frame = cap.read()

    height, width, channel = frame.shape

    if height > width:
        frame = cv2.resize(frame, (int(MAX_RESOLUTION*(width/height)), MAX_RESOLUTION))
    else:
        frame = cv2.resize(frame, (MAX_RESOLUTION, int(MAX_RESOLUTION*(height/width))))

    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    frame = frame/255.0

    grid = []
    for y in range(0, int(frame.shape[0] - WINDOW_SIZE), int(STRIDE)):
        for x in range(0, int(frame.shape[1] - WINDOW_SIZE), int(STRIDE)):
            grid.append(frame[y:y + WINDOW_SIZE, x:x + WINDOW_SIZE])
    

    matches = []
    grid_preds = model.predict(np.array(grid).reshape(-1,224,224,3))
    for i,v in enumerate(grid_preds):
        #pred = model.predict(v.reshape(-1,224,224,3))[0]

        distances = []
        for i2,anchor in enumerate(transfer_anchor_averages):
            dist = distance.cosine(anchor, v)
            distances.append(dist)

        guess = np.argmin(np.array(distances))
        if distances[guess] < 0.2 * transfer_anchor_weights[guess]:
            matches.append(f"{coco_labels_transfer[guess]} : {distances[guess]}")

    print(matches)

    cv2.imshow("window", frame)
    cv2.waitKey(10)
