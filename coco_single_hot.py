from coco import COCO
from coco_labels_paper import labels as coco_labels
import cv2
import os
import time
import random
from itertools import cycle

OUTPUT_DIR = 'coco_onehot_data'

ROTATE_DIR = [cv2.ROTATE_90_CLOCKWISE, cv2.ROTATE_90_COUNTERCLOCKWISE, cv2.ROTATE_180]


def rescale(cvimg):
    newimg = cv2.resize(cvimg, (224, 224))
    return newimg


def rotate(cvimg):
    newimg = cv2.rotate(cvimg, cv2.cv2.ROTATE_90_CLOCKWISE)
    return newimg


def crop(cvimg, ann):
    bbox = ann['bbox']
    left = int(bbox[0])
    right = int(bbox[0]+bbox[2])
    top = int(bbox[1])
    bottom = int(bbox[1]+bbox[3])
    newimg = cvimg[top:bottom, left:right]
    return newimg


def augment(cvimg):
    newimg = cvimg
    (r, g, b) = cv2.split(newimg)
    r = r*random.uniform(0.8, 1.2)
    g = g*random.uniform(0.8, 1.2)
    b = b*random.uniform(0.8, 1.2)
    newimg = cv2.merge([r,g,b])
    if random.random() > 0.25:
        newimg = cv2.rotate(cvimg, random.choice(ROTATE_DIR))

    return newimg


def ts():
    return str(int(round(time.time() * 1000)))


c = COCO("coco2017/annotations/instances_train2017.json")
print(c)

amounts = [len(c.getAnnIds(catIds=[i+1])) for i in range(len(coco_labels))]
print(amounts)


if not os.path.exists(OUTPUT_DIR):
    os.mkdir(OUTPUT_DIR)

    for cn in coco_labels:
        os.mkdir(f"{OUTPUT_DIR}/{cn}")

    for i, val in enumerate(c.anns):
        ann = c.anns[val]
        print(f'{i} : {len(c.anns)}')

        # skip zero area annotations
        if ann['area'] < 2000:
            continue

        class_name = coco_labels[ann['category_id']-1].strip()
        img = c.loadImgs(ann['image_id'])
        file_name = img[0]['file_name']

        cvimg = cv2.imread(os.path.join("coco2017/train2017", file_name))
        cvimg = crop(cvimg, ann)

        height, width, channel = cvimg.shape
        if height > 224 or width > 224:
            cvimg = rescale(cvimg)

        cv2.imwrite("{3}/{0}/{2}{1}".format(class_name, file_name,
                                            ts(), OUTPUT_DIR), cvimg)

max_amount = max(len(os.listdir("coco_onehot_data/{0}".format(c))) for c in os.listdir("coco_onehot_data"))
print(max_amount)

for folder in os.listdir(OUTPUT_DIR):
    print(folder)
    class_amount = len(os.listdir(f'{OUTPUT_DIR}/{folder}'))

    if class_amount == 0:
        continue

    diff = abs(max_amount - class_amount)

    generated = 0
    gen_cycle = cycle(os.listdir(f'{OUTPUT_DIR}/{folder}'))

    while True:
        f = next(gen_cycle)
        cvimg = cv2.imread(f'{OUTPUT_DIR}/{folder}/{f}')
        cvimg = augment(cvimg)
        cv2.imwrite(f'{OUTPUT_DIR}/{folder}/{ts()}{f}', cvimg)
        generated += 1
        print(f'Generated {generated} for class {folder}')
        if generated >= diff:
            break


# if not os.path.exists("coco_singlehot_rescaled"):
#     os.mkdir("coco_singlehot_rescaled")
#     for c in os.listdir("coco_singlehot"):
#         os.mkdir("coco_singlehot_rescaled/{0}".format(c))
#         for f in os.listdir("coco_singlehot/{0}".format(c)):
#             cvimg = cv2.imread("coco_singlehot/{0}/{1}".format(c, f))
#             cvimg = rescale(cvimg)
#             cv2.imwrite("coco_singlehot_rescaled/{0}/{1}".format(c,f), cvimg)