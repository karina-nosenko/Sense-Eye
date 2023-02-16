import sys
import math
import cv2
import torch
import numpy as np
import torch.backends.cudnn as cudnn
import itertools
from numpy import random

MODE = 'video'   # realtime/video
CAMERA_INDEX = 1 # Relevant for realtime only. 0-webcam, 4/0 - camera
APPEND_PATH = 'yolov7'
sys.path.append(APPEND_PATH)

from yolov7.models.experimental import attempt_load
from yolov7.utils.general import check_img_size, non_max_suppression, scale_coords, set_logging
from yolov7.utils.plots import plot_one_box
from yolov7.utils.torch_utils import select_device, time_synchronized

def adjust_image_to_desired_shape(img, new_shape=(640, 640), color=(114, 114, 114), auto=True, scaleFill=False, scaleup=True, stride=32):
    # Resize and pad image while meeting stride-multiple constraints
    shape = img.shape[:2]  # current shape [height, width]
    if isinstance(new_shape, int):
        new_shape = (new_shape, new_shape)

    # Scale ratio (new / old)
    scale_ratio = min(new_shape[0] / shape[0], new_shape[1] / shape[1])
    if not scaleup:  # only scale down, do not scale up (for better test mAP)
        scale_ratio = min(scale_ratio, 1.0)

    # Compute padding
    ratio = scale_ratio, scale_ratio  # width, height ratios
    new_unpad = int(round(shape[1] * scale_ratio)), int(round(shape[0] * scale_ratio))
    width_padding, height_padding = new_shape[1] - new_unpad[0], new_shape[0] - new_unpad[1]
    if auto:  # minimum rectangle
        width_padding, height_padding = np.mod(width_padding, stride), np.mod(height_padding, stride)
    elif scaleFill:  # stretch
        width_padding, height_padding = 0.0, 0.0
        new_unpad = (new_shape[1], new_shape[0])
        ratio = new_shape[1] / shape[1], new_shape[0] / shape[0]  # width, height ratios

    # divide padding into 2 sides
    width_padding /= 2
    height_padding /= 2

    # resize
    if shape[::-1] != new_unpad:
        img = cv2.resize(img, new_unpad, interpolation=cv2.INTER_LINEAR)

    top, bottom = int(round(height_padding - 0.1)), int(round(height_padding + 0.1))
    left, right = int(round(width_padding - 0.1)), int(round(width_padding + 0.1))
    img = cv2.copyMakeBorder(img, top, bottom, left, right, cv2.BORDER_CONSTANT, value=color)  # add border
    return img, ratio, (width_padding, height_padding)

classes_to_filter = ['bench','train', 'car', 'bicycle', 'truck', 'baseball glove', 'tennis racket', 'boat'] #You can give list of classes to filter by name, Be happy you don't have to put class number. ['train','person' ]

options  = {
    "weights": APPEND_PATH + "/weights/yolov7.pt", # path to weights file, default weights are for nano model
    "yaml"   : APPEND_PATH + "/data/coco.yaml", # path to yaml file
    "img-size": 640, # default image size
    "conf-thres": 0.25, # confidence threshold for inference
    "iou-thres" : 0.45, # NMS IoU threshold for inference
    "device" : '0',  # device to run our model i.e. 0 or 0,1,2,3 or cpu
    "classes" : classes_to_filter  # list of classes to filter or None
}

# Initializing video object
if (MODE == 'video'):
    video_path = APPEND_PATH + '/videos/soccer_video.mp4'   # the full path to video
    video = cv2.VideoCapture(video_path)
    fps = video.get(cv2.CAP_PROP_FPS)   # frames per second
    w = int(video.get(cv2.CAP_PROP_FRAME_WIDTH))
    h = int(video.get(cv2.CAP_PROP_FRAME_HEIGHT))
    nframes = int(video.get(cv2.CAP_PROP_FRAME_COUNT))

    # Initialzing object for writing video output
    output = cv2.VideoWriter('output.mp4', cv2.VideoWriter_fourcc(*'DIVX'), fps , (w,h))
else:   # realtime
    video = cv2.VideoCapture(CAMERA_INDEX)
    video.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc('M', 'J', 'P', 'G'))

torch.cuda.empty_cache()

# Initializing model and setting it for inference
with torch.no_grad():
    weights, img_size = options['weights'], options['img-size']
    set_logging()
    device = select_device(options['device'])
    use_half_precision = device.type != 'cpu'
    model = attempt_load(weights, map_location=device)  # load FP32 model
    stride = int(model.stride.max())  # model stride
    img_size = check_img_size(img_size, s=stride)  # check img_size
    if use_half_precision:
        model.half()

    names = model.module.names if hasattr(model, 'module') else model.names
    colors = [[random.randint(0, 255) for _ in range(3)] for _ in names]
    if device.type != 'cpu':
        print(model)
        model(torch.zeros(1, 3, img_size, img_size).to(device).type_as(next(model.parameters())))

    # determine the classes to exclude from detection
    classes = None
    if options['classes']:
        classes = []
        for class_name in options['classes']:
            classes.append(names.index(class_name))      
    if classes:  
        classes = [i for i in range(len(names)) if i not in classes]

    range = range(nframes) if (MODE == 'video') else itertools.count()
    for j in range:
        ret, frame = video.read()
        
        if not ret:
            break

        img = adjust_image_to_desired_shape(frame, img_size, stride=stride)[0]
        img = img[:, :, ::-1].transpose(2, 0, 1)  # BGR to RGB, to 3x416x416
        img = np.ascontiguousarray(img)
        img = torch.from_numpy(img).to(device)
        img = img.half() if use_half_precision else img.float()  # uint8 to fp16/32
        img /= 255.0  # 0 - 255 to 0.0 - 1.0

        if img.ndimension() == 3:
            img = img.unsqueeze(0)

        # Inference
        t1 = time_synchronized()
        detection_results = model(img, augment= False)[0]        
        detection_results = non_max_suppression(detection_results, options['conf-thres'], options['iou-thres'], classes= classes, agnostic= False)
        t2 = time_synchronized()

        # Plotting the detections
        for i, det in enumerate(detection_results):
            img_shape_dimensions = torch.tensor(frame.shape)[[1, 0, 1, 0]]
            if len(det):
                det[:, :4] = scale_coords(img.shape[2:], det[:, :4], frame.shape).round()

                for class_index in det[:, -1].unique():
                    number_of_detections = (det[:, -1] == class_index).sum()  # detections per class

                # Draw the class name label and center point for each object
                for *xyxy, conf, class_id in reversed(det): 
                    center_point = ((xyxy[0] + xyxy[2]) // 2, (xyxy[1] + xyxy[3]) // 2)

                    # Class name and center point coordinates label
                    center_point_coordinates_label = f"({center_point[0]}, {center_point[1]})"
                    class_name_label = names[int(class_id)]
                    text_label = f'{class_name_label} {center_point_coordinates_label}'
                    cv2.putText(frame, text_label, tuple(map(int, (center_point[0], center_point[1] - 10))), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)

                    # Center point circle
                    cv2.circle(frame, tuple(map(int, center_point)), 3, (0, 0, 255), -1)

                # Output the result
                if MODE == 'video':
                    print(f"{j+1}/{nframes} frames processed")
                    output.write(frame)
                else:
                    cv2.imshow("Frame", frame)
                    key = cv2.waitKey(1)
                    if key == 27:
                        break
    
output.release() if (MODE == video) else cv2.destroyAllWindows()
video.release()