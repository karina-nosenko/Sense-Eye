import sys
import cv2
import torch
import itertools
import os
from configs import APPEND_PATH, MODE, CAMERA_INDEX, VIDEO_PATH, options, GAME_MODE, YELLOW_COLOR, ORANGE_COLOR
import colors_detection as cd
import objects_detection as od

# Settings
sys.path.append(APPEND_PATH)
os.environ['CUDA_VISIBLE_DEVICES'] = '1'

from image_functions import rescale_frame
from recommendation_api_helpers import recommendation_single_player, recommendation_two_players_same_team


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
    weights, img_size, device, use_half_precision, model, stride, names, classes = od.initialize_player_detection_model()
    frames_range = range(nframes) if (MODE == 'video') else itertools.count()  

    for frame_index in frames_range:
        ret, frame = capture.read()  
        if not ret:
            break


        (player_with_the_ball_center_point,
        prev_person_center_points,
        playersList,
        ball_indexes) = od.detect_objects(
            frame,
            prev_person_center_points,
            player_with_the_ball_center_point,
            img_size,
            device,
            use_half_precision,
            model,
            stride,
            names,
            classes
        )

        player_caps_index = cd.detect_colors(frame)

        # Single player
        if (GAME_MODE == 1):
            # print(playersList)
            # print(player_caps_index)
            # print(ball_indexes)
            if(len(ball_indexes)>0 and len(playersList)>0 and len(playersList[0])>3 and playersList[0]['x'] and playersList[0]['y'] and playersList[0]['holdsBall'] and playersList[0]['sightDirection'] and ball_indexes[0]['x'] and ball_indexes[0]['y']):
                print(recommendation_single_player(YELLOW_COLOR, playersList[0]['x'], playersList[0]['y'], playersList[0]['holdsBall'], playersList[0]['sightDirection'], ball_indexes[0]['x'], ball_indexes[0]['y']))

        # Two players
        elif (GAME_MODE == 2):
            if(len(playersList)==2 and len(ball_indexes)>0 and ball_indexes[0]['x'] and ball_indexes[0]['y']):
                print(recommendation_two_players_same_team(playersList, player_caps_index,ball_indexes[0]['x'], ball_indexes[0]['y']))

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