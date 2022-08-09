import numpy as np
import tensorflow as tf
import os
from coco_final_labels_transfer import labels as coco_labels_transfer
import shutil
from tensorflow import keras

MODEL_PATH = 'weights/siamese_tripletloss/transfer-20220805-201928/final_embedding_transferred'
VIDEOSCANNER_PATH = 'MappingService/images/labelling/VideoScanner'

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

model = tf.keras.models.load_model(MODEL_PATH)

print("model loaded")

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

np.save(f"{VIDEOSCANNER_PATH}/anchor_averages", np.array(transfer_anchor_averages))
np.save(f"{VIDEOSCANNER_PATH}/anchor_weights", np.array(transfer_anchor_weights))

shutil.copytree(MODEL_PATH, 'MappingService/images/labelling/VideoScanner/siamesemodel')
