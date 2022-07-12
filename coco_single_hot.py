from coco import COCO
from coco_labels_paper import labels as coco_labels
import cv2
import os
import time
import random
from itertools import cycle

#OUTPUT_DIR = 'data/coco_onehot_data'
TRAIN_ANNOTATIONS = 'data/coco2017/annotations/instances_train2017.json'
TRAIN_IMAGES = 'data/coco2017/train2017'
TRAIN_OUTPUT_DIR = 'data/coco_onehot_train'
VAL_ANNOTATIONS = 'data/coco2017/annotations/instances_val2017.json'
VAL_IMAGES = 'data/coco2017/val2017'
VAL_OUTPUT_DIR = 'data/coco_onehot_val'
TRANSFER_IMAGES = 'data/new_classes'
TRAIN_TRANSFER_OUTPUT_DIR = 'data/transfer_train'
VAL_TRANSFER_OUTPUT_DIR = 'data/transfer_val'

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


def generate_dataset(anns_path: str, imgs_path: str, output_dir: str, augment: bool) -> None:
    c = COCO(anns_path)
    print(c)

    amounts = [len(c.getAnnIds(catIds=[i+1])) for i in range(len(coco_labels))]
    print(amounts)


    if not os.path.exists(output_dir):
        os.mkdir(output_dir)

        for cn in coco_labels:
            os.mkdir(f"{output_dir}/{cn}")

        for i, val in enumerate(c.anns):
            ann = c.anns[val]
            print(f'{i} : {len(c.anns)}')

            # skip zero area annotations
            if ann['area'] < 14400:
                continue

            class_name = coco_labels[ann['category_id']-1].strip()
            img = c.loadImgs(ann['image_id'])
            file_name = img[0]['file_name']

            cvimg = cv2.imread(os.path.join(imgs_path, file_name))
            cvimg = crop(cvimg, ann)

            height, width, channel = cvimg.shape

            if height > width:
                cvimg = cv2.resize(cvimg, (int(224*(width/height)), 224))
            elif width > height:
                cvimg = cv2.resize(cvimg, (224, int(224*(height/width))))

            height, width, channel = cvimg.shape
            height_delta = max(224 - height, 0)
            width_delta = max(224 - width, 0)

            if height_delta > 0 or width_delta > 0:
                cvimg = cv2.copyMakeBorder(cvimg, int(height_delta/2), int(height_delta/2), int(width_delta/2), int(width_delta/2), cv2.BORDER_REPLICATE)
            if height > 224 or width > 224:
                cvimg = rescale(cvimg)

            cv2.imwrite("{3}/{0}/{2}{1}".format(class_name, file_name,
                                                ts(), output_dir), cvimg)

    if not augment:
        return

    max_amount = max(len(os.listdir("{1}/{0}".format(c, output_dir))) for c in os.listdir(output_dir))
    print(max_amount)

    for folder in os.listdir(output_dir):
        print(folder)
        class_amount = len(os.listdir(f'{output_dir}/{folder}'))

        if class_amount == 0:
            continue

        diff = abs(max_amount - class_amount)

        generated = 0
        gen_cycle = cycle(os.listdir(f'{output_dir}/{folder}'))

        while True:
            f = next(gen_cycle)
            cvimg = cv2.imread(f'{output_dir}/{folder}/{f}')
            cvimg = augment(cvimg)
            cv2.imwrite(f'{output_dir}/{folder}/{ts()}{f}', cvimg)
            generated += 1
            print(f'Generated {generated} for class {folder}')
            if generated >= diff:
                break

def get_jpgs(dir):
    jpgs = []
    for root, dirnames, filenames in os.walk(dir):
        for filename in filenames:
            if filename.endswith('.jpg'):
                jpgs.append(filename)

    return jpgs


def balance_datasets():
    train_imgs = get_jpgs(TRAIN_OUTPUT_DIR)
    val_imgs = get_jpgs(VAL_OUTPUT_DIR)

    print(len(train_imgs))
    print(len(val_imgs))

    total = len(train_imgs) + len(val_imgs)
    val_split = total*0.1
    diff = int(val_split - len(val_imgs))
    print(diff)

    import shutil
    for c in coco_labels:
        files = os.listdir(f'{TRAIN_OUTPUT_DIR}/{c}')
        amount = len(files) * (diff/total)
        if len(files) > 2:
            amount = max(int(amount), 1)
            movefiles = random.choices(files, k=amount)
            movefiles = list(set(movefiles))
            for movefile in movefiles:
                if not os.path.exists(f'{VAL_OUTPUT_DIR}/{c}'):
                    os.mkdir(f'{VAL_OUTPUT_DIR}/{c}')
                shutil.move(f'{TRAIN_OUTPUT_DIR}/{c}/{movefile}', f'{VAL_OUTPUT_DIR}/{c}/{movefile}')

    print(len(get_jpgs(TRAIN_OUTPUT_DIR)))
    print(len(get_jpgs(VAL_OUTPUT_DIR)))

def generate_transfer_learning_dataset(path):
    if os.path.exists(path):

        newclasses = os.listdir(path)
        print(newclasses)

        os.mkdir(f"{TRAIN_TRANSFER_OUTPUT_DIR}")
        os.mkdir(f"{VAL_TRANSFER_OUTPUT_DIR}")
        for cn in newclasses:
            os.mkdir(f"{TRAIN_TRANSFER_OUTPUT_DIR}/{cn}")
            os.mkdir(f"{VAL_TRANSFER_OUTPUT_DIR}/{cn}")

        for i, val in enumerate(newclasses):
            files = os.listdir(f"{path}/{val}")
            split = int(len(files)*0.9)

            for i2, val2 in enumerate(files):
                print(os.path.join(path, val2))
                cvimg = cv2.imread(os.path.join(path, val, val2))

                height, width, channel = cvimg.shape

                if height > width:
                    cvimg = cv2.resize(cvimg, (int(224*(width/height)), 224))
                elif width > height:
                    cvimg = cv2.resize(cvimg, (224, int(224*(height/width))))

                height, width, channel = cvimg.shape
                height_delta = max(224 - height, 0)
                width_delta = max(224 - width, 0)

                if height_delta > 0 or width_delta > 0:
                    cvimg = cv2.copyMakeBorder(cvimg, int(height_delta/2), int(height_delta/2), int(width_delta/2), int(width_delta/2), cv2.BORDER_REPLICATE)
                if height > 224 or width > 224:
                    cvimg = rescale(cvimg)
                
                cv2.imwrite(f"{TRAIN_TRANSFER_OUTPUT_DIR if i2 < split else VAL_TRANSFER_OUTPUT_DIR}/{val}/{ts()}.jpg", cvimg)    

if __name__ == '__main__':
    generate_dataset(TRAIN_ANNOTATIONS, TRAIN_IMAGES, TRAIN_OUTPUT_DIR, False)
    generate_dataset(VAL_ANNOTATIONS, VAL_IMAGES, VAL_OUTPUT_DIR, False)
    #generate_transfer_learning_dataset(TRANSFER_IMAGES)
    balance_datasets()

    # f = open("final_labels.py", "w")
    # f.write("labels = [\n")
    # for folder in os.listdir(TRAIN_OUTPUT_DIR):
    #     class_amount = len(os.listdir(f'{TRAIN_OUTPUT_DIR}/{folder}'))
    #     print(class_amount)
    #     if class_amount > 0:
    #         f.write(f'"{folder}",\n')
    # f.write("]")

    

# if not os.path.exists("coco_singlehot_rescaled"):
#     os.mkdir("coco_singlehot_rescaled")
#     for c in os.listdir("coco_singlehot"):
#         os.mkdir("coco_singlehot_rescaled/{0}".format(c))
#         for f in os.listdir("coco_singlehot/{0}".format(c)):
#             cvimg = cv2.imread("coco_singlehot/{0}/{1}".format(c, f))
#             cvimg = rescale(cvimg)
#             cv2.imwrite("coco_singlehot_rescaled/{0}/{1}".format(c,f), cvimg)