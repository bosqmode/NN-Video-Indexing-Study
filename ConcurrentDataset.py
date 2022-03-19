import os
import random
from itertools import cycle
import numpy as np
from threading import Thread
import time
from collections import deque
from queue import Queue
import cv2
from tensorflow.keras.utils import to_categorical
from timeit import default_timer as timer

class ConcurrentDataset:
    def __init__(self, dir: str, val_split: float=0.1, labels=None):
        self.dir = dir
        self.labels = labels if labels is not None else os.listdir(self.dir)
        self.val_split = val_split
        self.data = {'train':{}, 'val':{}}
        self.ques = {'train': Queue(maxsize=1024), 'val':Queue(maxsize=512)}
        self.__load()
        self.__start_prefetch_threads()

    def preprocess(self, img):
        img = img / 255.0
        return img

    def __load(self):
        for c in self.labels:
            imgs = os.listdir(os.path.join(self.dir, c))
            count = len(imgs)
            traincount = (int)(count*(1-self.val_split))
            valcount = count-traincount
            self.data['train'][c] = imgs[:traincount]
            self.data['val'][c] = imgs[-valcount:]

    def __start_prefetch_threads(self, train_threads: int=8, val_threads: int=1):
        for i in range(train_threads):
            t = Thread(target=self.__prefetch_thread, args=('train',))
            t.daemon = True
            t.start()

        for y in range(val_threads):
            t = Thread(target=self.__prefetch_thread, args=('val',))
            t.daemon = True
            t.start()

    def __prefetch_thread(self, dataSet):
        class_iter = cycle(self.labels)
        while True:
            c = next(class_iter)
            if len(self.data[dataSet][c]) == 0:
                continue

            file = random.choice(self.data[dataSet][c])
            img = self.preprocess(cv2.imread(f'{self.dir}/{c}/{file}'))
            lbl = to_categorical(self.labels.index(c), len(self.labels))
            self.ques[dataSet].put((img, lbl))

    def get_batch(self, batch_size=32, dataSet='train'):
        imgs = []
        lbls = []
        while len(imgs) < batch_size:
            img, lbl = self.ques[dataSet].get()
            imgs.append(img)
            lbls.append(lbl)

        p = np.random.permutation(len(lbls))
        imgs = np.array(imgs, dtype=np.float16)[p]
        lbls = np.array(lbls, dtype=np.int8)[p]
        return imgs, lbls

if __name__ == '__main__':
    c = ConcurrentDataset('coco_singlehot_rescaled')

    start = timer()
    for i in range(5):
        imgs, labels = c.get_batch(16)
        imgs, labels = c.get_batch(16, dataSet='val')
        print(imgs[0])
        print(labels[0])
    end = timer()
    print(end-start)