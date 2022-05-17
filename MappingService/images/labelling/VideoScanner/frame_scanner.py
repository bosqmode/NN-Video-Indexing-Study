from abc import ABC, abstractmethod
import numpy as np
from tensorflow.keras.models import Model, load_model
import tensorflow as tf
import cv2
import os
from tensorflow import keras
from collections import defaultdict
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
    def __init__(self, framescanner: FrameScanner, detection_callback):
        self.scanner = framescanner
        self.callback = detection_callback

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

            if frame_counter % 8 == 0:
                #frame = cv2.rotate(frame, cv2.cv2.ROTATE_90_CLOCKWISE)
                frame = cv2.resize(frame, (224, 224), interpolation=cv2.INTER_AREA)
                frame = frame/255.0

                res = self.scanner.scan_frame(frame.reshape(-1, 224, 224, 3))

                if res is not None:
                    self.callback(res, time)


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
    def __init__(self, labels, pretrained_model_path=None):
        self.labels = labels
        if pretrained_model_path is None:
            self.model = keras.applications.ResNet50(include_top=True, weights="imagenet", input_shape=(224,224,3))
        else:
            self.model = tf.keras.models.load_model(pretrained_model_path)

    def scan_frame(self, frame):
        res = self.model.predict(frame)
        if np.max(res) > 0.8:
            return self.labels[np.argmax(res)]
        return None


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