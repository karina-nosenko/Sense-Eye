import sys
import argparse
import math
import time
import cv2
import torch
import numpy as np
import torch.backends.cudnn as cudnn
from numpy import random
from pathlib import Path

APPEND_PATH = 'yolov7'
sys.path.append(APPEND_PATH)

from yolov7.models.experimental import attempt_load
from yolov7.utils.datasets import LoadStreams, LoadImages
from yolov7.utils.general import check_img_size, check_requirements, check_imshow, non_max_suppression, apply_classifier, scale_coords, xyxy2xywh, strip_optimizer, set_logging, increment_path
from yolov7.utils.plots import plot_one_box
from yolov7.utils.torch_utils import select_device, load_classifier, time_synchronized, TracedModel

from IPython.display import display, Javascript, Image
from base64 import b64decode, b64encode
import PIL
import io
import html

def letterbox(img, new_shape=(640, 640), color=(114, 114, 114), auto=True, scaleFill=False, scaleup=True, stride=32):
    # Resize and pad image while meeting stride-multiple constraints
    shape = img.shape[:2]  # current shape [height, width]
    if isinstance(new_shape, int):
        new_shape = (new_shape, new_shape)

    # Scale ratio (new / old)
    r = min(new_shape[0] / shape[0], new_shape[1] / shape[1])
    if not scaleup:  # only scale down, do not scale up (for better test mAP)
        r = min(r, 1.0)

    # Compute padding
    ratio = r, r  # width, height ratios
    new_unpad = int(round(shape[1] * r)), int(round(shape[0] * r))
    dw, dh = new_shape[1] - new_unpad[0], new_shape[0] - new_unpad[1]  # wh padding
    if auto:  # minimum rectangle
        dw, dh = np.mod(dw, stride), np.mod(dh, stride)  # wh padding
    elif scaleFill:  # stretch
        dw, dh = 0.0, 0.0
        new_unpad = (new_shape[1], new_shape[0])
        ratio = new_shape[1] / shape[1], new_shape[0] / shape[0]  # width, height ratios

    dw /= 2  # divide padding into 2 sides
    dh /= 2

    if shape[::-1] != new_unpad:  # resize
        img = cv2.resize(img, new_unpad, interpolation=cv2.INTER_LINEAR)

    top, bottom = int(round(dh - 0.1)), int(round(dh + 0.1))
    left, right = int(round(dw - 0.1)), int(round(dw + 0.1))
    img = cv2.copyMakeBorder(img, top, bottom, left, right, cv2.BORDER_CONSTANT, value=color)  # add border
    return img, ratio, (dw, dh)

classes_to_filter = ['bench','train', 'car', 'bicycle', 'truck', 'baseball glove', 'tennis racket', 'boat'] #You can give list of classes to filter by name, Be happy you don't have to put class number. ['train','person' ]

opt = {   
    "weights": APPEND_PATH + "/weights/yolov7.pt", # Path to weights file default weights are for nano model
    "yaml"   : APPEND_PATH + "/data/coco.yaml",
    "img-size": 640, # default image size
    "conf-thres": 0.25, # confidence threshold for inference.
    "iou-thres" : 0.45, # NMS IoU threshold for inference.
    "device" : '0',  # device to run our model i.e. 0 or 0,1,2,3 or cpu
    "classes" : classes_to_filter  # list of classes to filter or None
}

cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc('M', 'J', 'P', 'G'))

center_points_current_frame = [] # sense-eye
center_points_previous_frame = []# sense-eye
count = 0
object_exists = False
track_id = 0 #sense eye
tracking_objects = {}

torch.cuda.empty_cache()

with torch.no_grad():
    weights, imgsz = opt['weights'], opt['img-size']
    set_logging()
    device = select_device(opt['device'])
    half = device.type != 'cpu'
    model = attempt_load(weights, map_location=device)  # load FP32 model
    stride = int(model.stride.max())  # model stride
    imgsz = check_img_size(imgsz, s=stride)  # check img_size
    if half:
        model.half()

    names = model.module.names if hasattr(model, 'module') else model.names
    colors = [[random.randint(0, 255) for _ in range(3)] for _ in names]
    if device.type != 'cpu':
        print(model)
        model(torch.zeros(1, 3, imgsz, imgsz).to(device).type_as(next(model.parameters())))

    classes = None
    if opt['classes']:
        classes = []
        for class_name in opt['classes']:
            classes.append(names.index(class_name))
        
    if classes:  
        classes = [i for i in range(len(names)) if i not in classes]

    while True:
        ret, frame = cap.read()

        if ret:
            count +=1
            img = letterbox(frame, imgsz, stride=stride)[0]
            img = img[:, :, ::-1].transpose(2, 0, 1)  # BGR to RGB, to 3x416x416
            img = np.ascontiguousarray(img)
            img = torch.from_numpy(img).to(device)
            img = img.half() if half else img.float()  # uint8 to fp16/32
            img /= 255.0  # 0 - 255 to 0.0 - 1.0
            if img.ndimension() == 3:
                img = img.unsqueeze(0)

            # Inference
            t1 = time_synchronized()
            pred = model(img, augment= False)[0]
            
            pred = non_max_suppression(pred, opt['conf-thres'], opt['iou-thres'], classes= classes, agnostic= False)
            t2 = time_synchronized()
            for i, det in enumerate(pred):
                s = ''
                s += '%gx%g ' % img.shape[2:]  # print string
            
            gn = torch.tensor(frame.shape)[[1, 0, 1, 0]]
            if len(det):
                det[:, :4] = scale_coords(img.shape[2:], det[:, :4], frame.shape).round()

                for c in det[:, -1].unique():
                    n = (det[:, -1] == c).sum()  # detections per class
                    s += f"{n} {names[int(c)]}{'s' * (n > 1)}, "  # add to string

                for *xyxy, conf, cls in reversed(det):
                    label = f'{names[int(cls)]} {conf:.2f}'
                    plot_one_box(xyxy, frame, label=label, color=colors[int(cls)], line_thickness=3,center_points=center_points_current_frame,name=names[int(cls)])

                if count<=1:
                    for pt in center_points_current_frame:
                        for pt2 in center_points_previous_frame:
                            distance = math.hypot(pt2[0]-pt[0], pt2[1]-pt[1])
                            if distance < 52:
                                tracking_objects[track_id] = pt
                                track_id += 1
                else:
                    tracking_objects_copy = tracking_objects.copy()
                    center_points_current_frame_copy = center_points_current_frame.copy()
                    for object_id, pt2 in tracking_objects_copy.items():
                        object_exists = False
                        for pt in center_points_current_frame:
                            distance = math.hypot(pt2[0]-pt[0], pt2[1]-pt[1])
                            if distance < 52:
                                tracking_objects[object_id] = pt
                                object_exists = True
                                center_points_current_frame.remove(pt)
                                continue

                        if not object_exists:
                            tracking_objects.pop(object_id)

                for pt in center_points_current_frame:
                    tracking_objects[track_id] = pt
                    track_id += 1

            for object_id, pt in tracking_objects.items():
                cv2.circle(frame, pt, 5,(0,0,255),-1)
                cv2.putText(frame,str(object_id), (pt[0], pt[1]-7),0,1,(0,0,255),2)
                
            center_points_previous_frame = center_points_current_frame.copy()

            cv2.imshow("Frame", frame)
            key = cv2.waitKey(1)
            if key == 27:
                break
        else:
            break

  
cap.release()
cv2.destroyAllWindows()
