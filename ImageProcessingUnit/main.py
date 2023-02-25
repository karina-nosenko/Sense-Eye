import sys
import cv2
import torch
import itertools
import os
from configs import APPEND_PATH, MODE, CAMERA_INDEX, VIDEO_PATH, options

# Settings
sys.path.append(APPEND_PATH)
os.environ['CUDA_VISIBLE_DEVICES'] = '1'

from image_functions import rescale_frame
from colors_detection import detect_colors
from objects_detection import detect_objects, initialize_player_detection_model

def initialize_capture():
    if (MODE == 'video'):
        capture = cv2.VideoCapture(VIDEO_PATH) 
    elif (MODE == 'realtime'):
        capture = cv2.VideoCapture(CAMERA_INDEX)
        capture.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc('M', 'J', 'P', 'G'))

        # Uncomment when using an external usb camera
        # capture.set(3, 3840)  # width (max - 3840)
        # capture.set(4, 2160)  # height (max - 2160)
    else: 
        raise ValueError('MODE constant must contain "realtime" or "video" value')
    
    return capture

def initialize_output(capture):
    fps = int(capture.get(cv2.CAP_PROP_FPS))
    w = int(capture.get(cv2.CAP_PROP_FRAME_WIDTH))
    h = int(capture.get(cv2.CAP_PROP_FRAME_HEIGHT))
    return cv2.VideoWriter('output.mp4', cv2.VideoWriter_fourcc(*'DIVX'), fps , (w,h))


capture = initialize_capture()

if (MODE == 'video'):
    output = initialize_output(capture)
    nframes = int(capture.get(cv2.CAP_PROP_FRAME_COUNT))

# Initializing model and setting it for inference
torch.cuda.empty_cache()
with torch.no_grad():
    player_with_the_ball_center_point = None
    prev_person_center_points = None
    weights, img_size, device, use_half_precision, model, stride, names, classes = initialize_player_detection_model()
    frames_range = range(nframes) if (MODE == 'video') else itertools.count()  

    for frame_index in frames_range:
        ret, frame = capture.read()  
        if not ret:
            break

        # detect_colors(frame, capture)
        player_with_the_ball_center_point, prev_person_center_points = detect_objects(frame, prev_person_center_points, player_with_the_ball_center_point, img_size, device, use_half_precision, model, stride, names, classes)

        # Output the result
        if MODE == 'video':
            print(f"{frame_index+1}/{nframes} frames processed")
            output.write(frame)
        else:
            cv2.imshow("Frame", rescale_frame(frame, scale=0.6667))
            key = cv2.waitKey(1)
            if key == 27:
                break
 
    
output.release() if (MODE == 'video') else cv2.destroyAllWindows()
capture.release()