from abc import ABC, abstractmethod
import numpy as np
from tensorflow.keras.models import Model, load_model
import tensorflow as tf
import cv2
import os
from tensorflow import keras

from imagenet_labels import labels as imagenet_lbl

class FrameScanner(ABC):
    """
    Input a frame (cv2)
    Return a list of detected classes (str)
    """
    @abstractmethod
    def scan_frame(self, frame):
        pass

class SiameseScanner(FrameScanner):
    def __init__(self, modelpath):
        self.model = load_model(modelpath)

    def scan_frame(self, frame):
        pass

class ResNet50Scanner(FrameScanner):
    def __init__(self):
        self.model = keras.applications.ResNet50(include_top=True, weights="imagenet", input_shape=(224,224,3))

    def scan_frame(self, frame):
        return self.model.predict(frame)


scanner = ResNet50Scanner()
file = "D:/Koodit/test.mp4"
cap = cv2.VideoCapture(file)

last_frame = None
frame_counter = 0

while True:
    ret, frame = cap.read()

    if not ret:
        break

    frame_counter += 1

    if frame_counter % 8 == 0:
        frame = cv2.rotate(frame, cv2.cv2.ROTATE_90_CLOCKWISE)
        frame = cv2.resize(frame, (224, 224), interpolation=cv2.INTER_AREA)

        res = scanner.scan_frame(frame.reshape(-1, 224, 224, 3))

        if np.max(res) > 0.5:
            print(f'{frame_counter} - {imagenet_lbl[np.argmax(res)]} : {np.max(res)}')

        cv2.imshow('frame', frame)
        cv2.waitKey(1)

print("done")