import sys
import math
import cv2
import torch
import numpy as np
import torch.backends.cudnn as cudnn
import itertools
import numpy as np
from scipy.spatial import distance
from numpy import random
import os
import colors_detection as cd
os.environ['CUDA_VISIBLE_DEVICES'] = '1'

MODE = 'realtime'   # realtime/video
CAMERA_INDEX = 0 # Relevant for realtime only. 0-webcam, 4/0 - camera
APPEND_PATH = 'yolov7'
sys.path.append(APPEND_PATH)

from yolov7.models.experimental import attempt_load
from yolov7.utils.general import check_img_size, non_max_suppression, scale_coords, set_logging
from yolov7.utils.plots import plot_one_box
from yolov7.utils.torch_utils import select_device, time_synchronized

def rescale_frame(frame, scale):    # works for image, video, live video
    width = int(frame.shape[1] * scale)
    height = int(frame.shape[0] * scale)
    dimensions = (width, height)
    return cv2.resize(frame, dimensions, interpolation=cv2.INTER_AREA)

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


def find_nearest_player_to_the_ball(ball_center_point, all_detections):
    if not ball_center_point:
        return None

    min_distance_to_ball = float('inf')   # positive infinity
    nearest_player_center_point = None
    for *xyxy, confidence_score, class_id in reversed(all_detections):
        if names[int(class_id)] == 'person':
            player_center_point = ((xyxy[0] + xyxy[2]) // 2, (xyxy[1] + xyxy[3]) // 2)
            ball_coordinates_np = np.array([ball_center_point[0].cpu(), ball_center_point[1].cpu()])
            player_coordinates_np = np.array([player_center_point[0].cpu(),player_center_point[1].cpu()])
            euclidean_distance = distance.euclidean(ball_coordinates_np, player_coordinates_np)

            if euclidean_distance < min_distance_to_ball:
                min_distance_to_ball = euclidean_distance
                nearest_player_center_point = xyxy
    
    return nearest_player_center_point if min_distance_to_ball != float('inf') else None


classes_to_detect = [ 'person', 'sports ball' ]

options  = {
    "weights": APPEND_PATH + "/weights/yolov7.pt", # path to weights file, default weights are for nano model
    "yaml"   : APPEND_PATH + "/data/coco.yaml", # path to yaml file (contains all the class names)
    "img-size": 640, # default image size
    "conf-thres": 0.25, # confidence threshold for inference
    "iou-thres" : 0.45, # NMS IoU threshold for inference
    "device" : 'cpu',  # device to run our model i.e. 0 or 0,1,2,3 or cpu
    "classes" : classes_to_detect  # list of classes to filter or None
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
    video.set(3, 1440)

torch.cuda.empty_cache()

# Initializing model and setting it for inference
with torch.no_grad():
    player_with_the_ball_center_point = None
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

    # Convert class names to class indexes
    classes = []
    for class_name in options['classes']:
        classes.append(names.index(class_name))

    range = range(nframes) if (MODE == 'video') else itertools.count()
    for j in range:
        ret, frame = video.read()
        frame = rescale_frame(frame, scale=1)   # define frame size
        
        if not ret:
            break

        cd.colorsDetections(frame, video)

        img = adjust_image_to_desired_shape(frame, img_size, stride=stride)[0]
        img = img[:, :, ::-1].transpose(2, 0, 1)  # BGR to RGB, to 3x416x416
        img = np.ascontiguousarray(img)
        img = torch.from_numpy(img).to(device)
        img = img.half() if use_half_precision else img.float()  # uint8 to fp16/32
        img /= 255.0  # 0 - 255 to 0.0 - 1.0

        # Add a forth dimention to the image object - batch_size=1
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

                # Detect the player with the ball - the player whose coordinates are
                # the nearest to the found ball.
                ball_found_in_current_frame = False
                for *xyxy, confidence_score, class_id in reversed(det):
                    if (names[int(class_id)] == 'sports ball'):
                        ball_found_in_current_frame = True
                        center_point = ((xyxy[0] + xyxy[2]) // 2, (xyxy[1] + xyxy[3]) // 2)
                        nearest_player_to_the_ball = find_nearest_player_to_the_ball(center_point, det)
                        if nearest_player_to_the_ball:
                            player_with_the_ball_center_point = ((nearest_player_to_the_ball[0] + nearest_player_to_the_ball[2]) // 2, (nearest_player_to_the_ball[1] + nearest_player_to_the_ball[3]) // 2)
                
                # If the ball was not found in the current frame - the 'player with the ball'
                # will be the player whose coordinates are the nearest to the 'player with the ball'
                # in the previous frame.
                if not ball_found_in_current_frame:
                    for *xyxy, confidence_score, class_id in reversed(det):
                        nearest_player_to_the_ball = find_nearest_player_to_the_ball(player_with_the_ball_center_point, det)
                        if nearest_player_to_the_ball:
                            player_with_the_ball_center_point = ((nearest_player_to_the_ball[0] + nearest_player_to_the_ball[2]) // 2, (nearest_player_to_the_ball[1] + nearest_player_to_the_ball[3]) // 2)

                # Draw the class name label and center point for each object
                for *xyxy, confidence_score, class_id in reversed(det):
                    center_point = ((xyxy[0] + xyxy[2]) // 2, (xyxy[1] + xyxy[3]) // 2)

                    # Class name and center point coordinates label
                    center_point_coordinates_label = f"({center_point[0]}, {center_point[1]})"
                    class_name_label = names[int(class_id)]  

                    if center_point == player_with_the_ball_center_point:
                        text_color = (255, 255, 0) # blue for player with the ball
                    elif class_name_label == 'sports ball':
                        text_color = (0, 255, 0) # green for ball
                        class_name_label = 'ball'
                    else:
                        text_color = (0, 0, 255) # red for rest of the players

                    text_label = f'{class_name_label} {center_point_coordinates_label}'
                    cv2.putText(frame, text_label, tuple(map(int, (center_point[0], center_point[1] - 10))), cv2.FONT_HERSHEY_SIMPLEX, 0.5, text_color, 2)

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