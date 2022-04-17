from abc import ABC, abstractmethod
from matplotlib.pyplot import step
import numpy as np
from tensorflow.keras.models import Model, load_model
import tensorflow as tf
import cv2
import os
from tensorflow import keras
from collections import defaultdict

from imagenet_labels import labels as imagenet_lbl
import argparse



class FrameScanner(ABC):
    """
    Input a frame (cv2)
    Return a list of detected classes (str)
    """
    @abstractmethod
    def scan_frame(self, frame):
        pass

class VideoPlayer(ABC):
    """
    Video player abstraction
    for example, cv2
    """
    def __init__(self, framescanner: FrameScanner):
        self.scanner = framescanner

    @abstractmethod
    def play(self, path):
        pass

class OpencvVideoPlayer(VideoPlayer):
    def play(self, path):
        print(path)
        cap = cv2.VideoCapture(path)
        frame_counter = 0

        while True:
            ret, frame = cap.read()
            if not ret:
                break

            frame_counter += 1

            if frame_counter % 8 == 0:
                #frame = cv2.rotate(frame, cv2.cv2.ROTATE_90_CLOCKWISE)
                frame = cv2.resize(frame, (224, 224), interpolation=cv2.INTER_AREA)
                frame = frame/255.0

                res = self.scanner.scan_frame(frame.reshape(-1, 224, 224, 3))

                if np.max(res) > 0.8:
                    print(f'{frame_counter} - {imagenet_lbl[np.argmax(res)]} : {np.max(res)}')

                cv2.imshow('frame', frame)
                cv2.waitKey(1)


class SiameseScanner(FrameScanner):
    def __init__(self, modelpath):
        self.model = load_model(modelpath)
        self.anchor_count = 5
        self.anchors = self.load_anchors()
        print(self.anchors)

    def load_anchors(self):
        anchors = defaultdict(list)
        for dir in os.listdir('data/siamese_anchors'):
            for file in os.listdir(f'data/siamese_anchors/{dir}'):
                anchors[dir].append(cv2.imread(f'data/siamese_anchors/{dir}/{file}').reshape(-1, 224,224,3)/255.0)
        return anchors

    def scan_frame(self, frame):
        preds = []
        feed1 = []
        feed2 = []
        classnames = []

        for k in self.anchors:
            for img in self.anchors[k]:
                feed1.append(img.reshape(224,224,3))
                feed2.append(frame.reshape(224,224,3))
                classnames.append(k)

        pred = self.model.predict([np.array(feed1), np.array(feed2)])
        print(len(pred))
        best_avg = 0
        best_class = ""
        for x in range(0, len(pred), self.anchor_count):
            avg = (np.sum(pred[x:x+self.anchor_count])) / self.anchor_count
            preds.append((avg, classnames[x]))
            if avg > best_avg:
                best_avg = avg
                cv2.imshow("anchor", feed1[x])
                best_class = classnames[x]

        print(f'{best_class} : {best_avg}')
        return 0

class ResNet50Scanner(FrameScanner):
    def __init__(self):
        self.model = keras.applications.ResNet50(include_top=True, weights="imagenet", input_shape=(224,224,3))

    def scan_frame(self, frame):
        return self.model.predict(frame)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--path', type=str, help="video file path")
    args = parser.parse_args()

    #scanner = ResNet50Scanner()
    scanner = SiameseScanner('weights/siamese_pretrained/siamesev3')
    player = OpencvVideoPlayer(scanner)
    file = args.path
    player.play(file)

    print("done")


    # model = load_model('weights/siamese_pretrained/siamesev3')
    # img1 = cv2.imread('data/testdir/test390.jpg')/255.0
    # img2 = cv2.imread('data/siamese_anchors/dog/1650027806433000000423201.jpg')/255.0
    # img3 = cv2.imread('data/siamese_anchors/dog/1650027788015000000337274.jpg')/255.0
    # img1 = img1.reshape(-1,224,224,3)
    # img2 = img2.reshape(-1,224,224,3)
    # img3 = img3.reshape(-1,224,224,3)
    # print(model.predict([img1, img2]))
    # print(model.predict([img1, img3]))
