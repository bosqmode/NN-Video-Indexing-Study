from abc import ABC, abstractmethod
import numpy as np
from tensorflow.keras.models import Model, load_model
import tensorflow as tf
import cv2
import os
from tensorflow import keras
from collections import defaultdict
import argparse
import io
from scipy.spatial import distance
import time


class FrameScanner(ABC):
    """
    Input a frame (cv2)
    Return a list of detected classes (str)
    """


    @abstractmethod
    def scan_frame(self, frame) -> list:
        pass

class VideoPlayer(ABC):
    """
    Video player abstraction
    for example, cv2
    """
    def __init__(self, framescanner: FrameScanner, detection_callback, max_resolution: int=224*3):
        self.scanner = framescanner
        self.callback = detection_callback
        self.max_resolution = max_resolution

    @abstractmethod
    def play(self, path):
        pass

class OpencvVideoPlayer(VideoPlayer):
    def play(self, path):
        print(path)
        cap = cv2.VideoCapture(path)
        fps = cap.get(cv2.CAP_PROP_FPS)
        time = 0.0
        frame_counter = 0

        while True:
            ret, frame = cap.read()
            if not ret:
                break
            
            time += 1000.0/fps
            frame_counter += 1

            height, width, channel = frame.shape

            if height > width:
                frame = cv2.resize(frame, (int(self.max_resolution*(width/height)), self.max_resolution))
            else:
                frame = cv2.resize(frame, (self.max_resolution, int(self.max_resolution*(height/width))))

            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            frame = frame/255.0

            res = self.scanner.scan_frame(frame)

            if res is not None:
                self.callback(res, time)


class SiameseScanner(FrameScanner):
    def __init__(self, modelpath, labels):
        self.model = tf.keras.models.load_model(modelpath)
        self.anchors = self.load_anchors()
        self.anchor_weights = self.load_anchor_weights()
        self.window_size = 224
        self.stride = self.window_size * 0.5
        self.labels = labels

    def load_anchor_weights(self):
        return np.load("VideoScanner/anchor_weights.npy")

    def load_anchors(self):
        return np.load("VideoScanner/anchor_averages.npy")

    def scan_frame(self, frame):
        grid = []
        for y in range(0, int(frame.shape[0] - self.window_size), int(self.stride)):
            for x in range(0, int(frame.shape[1] - self.window_size), int(self.stride)):
                grid.append(frame[y:y + self.window_size, x:x + self.window_size])

        matches = []
        grid_preds = self.model.predict(np.array(grid).reshape(-1,224,224,3))
        for i,v in enumerate(grid_preds):
            #pred = model.predict(v.reshape(-1,224,224,3))[0]

            distances = []
            for i2,anchor in enumerate(self.anchors):
                dist = distance.cosine(anchor, v)
                distances.append(dist)

            guess = np.argmin(np.array(distances))
            if distances[guess] < 0.2 * self.anchor_weights[guess]:
                matches.append((self.labels[guess],distances[guess]))
        return matches

class ResNet50Scanner(FrameScanner):
    def __init__(self, labels, pretrained_model_path=None):
        self.labels = labels
        if pretrained_model_path is None:
            self.model = keras.applications.ResNet50(include_top=True, weights="imagenet", input_shape=(224,224,3))
        else:
            self.model = tf.keras.models.load_model(pretrained_model_path)

    def scan_frame(self, frame):
        matches = []
        frame = cv2.resize(frame, (224, 224), interpolation=cv2.INTER_AREA)
        res = self.model.predict(frame.reshape(-1, 224, 224, 3))
        if np.max(res) > 0.8:
            matches.append((self.labels[np.argmax(res)], -1))
        return matches


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--path', type=str, help="video file path")
    args = parser.parse_args()

    scanner = ResNet50Scanner()
    #scanner = SiameseScanner('weights/siamese_pretrained/siamesev3')
    player = OpencvVideoPlayer(scanner)
    file = args.path
    player.play(file)

    print("done")