# -*- coding: utf-8 -*-
'''
@Time          : 20/04/25 15:49
@Author        : huguanghao
@File          : demo.py
@Noice         :
@Modificattion :
    @Author    :
    @Time      :
    @Detail    :
'''

from tool.class_names import COCO_NAMES, VOC_NAMES
from tool.utils import *
from tool.torch_utils import *
from tool.darknet2pytorch import Darknet
from tool.weights import download_weights
import argparse


def detect_cv2(cfgfile, weightfile, imgfile, namesfile=None, use_cuda=False):
    import cv2
    m = Darknet(cfgfile, use_cuda=use_cuda)

    m.print_network()
    m.load_weights(weightfile)
    print('Loading weights from %s... Done!' % (weightfile))

    if namesfile is None:
        num_classes = m.num_classes
        if num_classes == 20:
            namesfile = VOC_NAMES
        elif num_classes == 80:
            namesfile = COCO_NAMES
        else:
            namesfile = 'data/x.names'
    class_names = load_class_names(namesfile)

    img = cv2.imread(imgfile)
    sized = cv2.resize(img, (m.width, m.height))
    sized = cv2.cvtColor(sized, cv2.COLOR_BGR2RGB)

    for i in range(2):
        start = time.time()
        boxes = do_detect(m, sized, 0.4, 0.6, use_cuda=use_cuda)
        finish = time.time()
        if i == 1:
            print('%s: Predicted in %f seconds.' % (imgfile, (finish - start)))

    plot_boxes_cv2(img, boxes[0], savename='predictions.jpg', class_names=class_names)


def detect_cv2_camera(cfgfile, weightfile, namesfile=None, use_cuda=False):
    import cv2
    m = Darknet(cfgfile, use_cuda=use_cuda)

    m.print_network()
    m.load_weights(weightfile)
    print('Loading weights from %s... Done!' % (weightfile))

    cap = cv2.VideoCapture(0)
    # cap = cv2.VideoCapture("./test.mp4")
    cap.set(3, 1280)
    cap.set(4, 720)
    print("Starting the YOLO loop...")

    if namesfile is None:
        num_classes = m.num_classes
        if num_classes == 20:
            namesfile = VOC_NAMES
        elif num_classes == 80:
            namesfile = COCO_NAMES
        else:
            namesfile = 'data/x.names'
    class_names = load_class_names(namesfile)

    while True:
        ret, img = cap.read()
        sized = cv2.resize(img, (m.width, m.height))
        sized = cv2.cvtColor(sized, cv2.COLOR_BGR2RGB)

        start = time.time()
        boxes = do_detect(m, sized, 0.4, 0.6, use_cuda=use_cuda)
        finish = time.time()
        print('Predicted in %f seconds.' % (finish - start))

        result_img = plot_boxes_cv2(img, boxes[0], savename=None, class_names=class_names)

        cv2.imshow('Yolo demo', result_img)
        cv2.waitKey(1)

    cap.release()


def detect_skimage(cfgfile, weightfile, imgfile, namesfiles=None, use_cuda=False):
    from skimage import io
    from skimage.transform import resize
    m = Darknet(cfgfile, use_cuda=use_cuda)

    m.print_network()
    m.load_weights(weightfile)
    print('Loading weights from %s... Done!' % (weightfile))

    if namesfiles is None:
        num_classes = m.num_classes
        if num_classes == 20:
            namesfile = VOC_NAMES
        elif num_classes == 80:
            namesfile = COCO_NAMES
        else:
            namesfile = 'data/x.names'
    class_names = load_class_names(namesfile)

    img = io.imread(imgfile)
    sized = resize(img, (m.width, m.height)) * 255

    for i in range(2):
        start = time.time()
        boxes = do_detect(m, sized, 0.4, 0.4, use_cuda=use_cuda)
        finish = time.time()
        if i == 1:
            print('%s: Predicted in %f seconds.' % (imgfile, (finish - start)))

    plot_boxes_cv2(img, boxes, savename='predictions.jpg', class_names=class_names)


def get_args():
    parser = argparse.ArgumentParser('Test your image or video by trained model.')
    parser.add_argument('-cfgfile', type=str, default='./cfg/yolov4.cfg',
                        help='path of cfg file', dest='cfgfile')
    parser.add_argument('-weightfile', type=str,
                        help='path of trained model.', dest='weightfile')
    parser.add_argument('-namesfile', type=str,
                        help='path of your names file.', dest='namesfile')
    parser.add_argument('-imgfile', type=str,
                        default='./data/mscoco2017/train2017/190109_180343_00154162.jpg',
                        help='path of your image file.', dest='imgfile')
    parser.add_argument('-gpu', type=str, dest='gpu', default="-1",
                        help='choose which cuda device to use by index e.g. 0 (input -1 for cpu only)')
    args = parser.parse_args()
    args.gpu = int(args.gpu) if torch.cuda.device_count() >= 1 else -1
    args.use_cuda = args.gpu != -1
    return args


def main():
    args = get_args()

    if not args.weightfile or not os.path.exists(args.weightfile):
        weightfile = download_weights(dest_path=args.weightfile)
    else:
        weightfile = args.weightfile

    with torch.cuda.device(args.gpu):
        if args.imgfile:
            detect_cv2(args.cfgfile, weightfile, args.imgfile, namesfile=args.namesfile, use_cuda=args.use_cuda)
            # detect_imges(args.cfgfile, args.weightfile, args.use_cuda)
            # detect_cv2(args.cfgfile, args.weightfile, args.imgfile, args.use_cuda)
            # detect_skimage(args.cfgfile, args.weightfile, args.imgfile, args.use_cuda)
        else:
            detect_cv2_camera(args.cfgfile, args.weightfile, namesfile=args.namesfile, use_cuda=args.use_cuda)


if __name__ == '__main__':
    main()
