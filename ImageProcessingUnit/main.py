import sys
import cv2
import torch
import itertools
import os
from configs import APPEND_PATH, MODE, CAMERA_INDEX, VIDEO_PATH, options, GAME_MODE, YELLOW_COLOR, ORANGE_COLOR
import colors_detection as cd
from datetime import datetime
import uuid

# Settings
sys.path.append(APPEND_PATH)
os.environ['CUDA_VISIBLE_DEVICES'] = '1'

from image_functions import rescale_frame
from recommendation_api_helpers import recommendation_single_player, recommendation_two_players_same_team
from objects_detection import initialize_player_detection_model, detect_objects

CURRENT_TIMESTAMP = datetime.now()

def initialize_capture():
        if (MODE == 'video'):
            capture = cv2.VideoCapture(VIDEO_PATH) 
        elif (MODE == 'realtime'):
            capture = cv2.VideoCapture(CAMERA_INDEX)
            capture.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*'H264'))

        # Relevant when using an external usb camera
        # capture.set(3, 1280)  # width (max - 3840)
        # capture.set(4, 720)  # height (max - 2160)
        else: 
            raise ValueError('MODE constant must contain "realtime" or "video" value')
        
        return capture

def initialize_output(capture):
    fps = int(capture.get(cv2.CAP_PROP_FPS))
    w = int(capture.get(cv2.CAP_PROP_FRAME_WIDTH))
    h = int(capture.get(cv2.CAP_PROP_FRAME_HEIGHT))
    CURRENT_TIMESTAMP = datetime.now()
    formatted_timestamp = CURRENT_TIMESTAMP.strftime('%Y-%m-%d %H:%M:%S')
    return cv2.VideoWriter(f'../output_videos/{formatted_timestamp}.ogv', cv2.VideoWriter_fourcc(*'THEO'), fps , (w,h))


capture = initialize_capture()

output = initialize_output(capture)

if (MODE == 'video'):
    nframes = int(capture.get(cv2.CAP_PROP_FRAME_COUNT))

color_recommendation = ''
output_state_recommendation = ''
state_recommendation = ''
previous_recommendation_label = ''
data = {}

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

        (player_with_the_ball_center_point,
        prev_person_center_points,
        playersList,
        ball_indexes) = detect_objects(
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
        ball_prev_indexes = []
        if(len(ball_indexes)>0):
            ball_prev_indexes = ball_indexes
        player_caps_index = cd.detect_colors(frame)

        # Single player
        if (GAME_MODE == 1):
            if(len(ball_prev_indexes)>0 and len(playersList)>0 and len(playersList[0])>3 and playersList[0]['x'] and playersList[0]['y'] and playersList[0]['holdsBall'] and playersList[0]['sightDirection'] and ball_indexes[0]['x'] and ball_indexes[0]['y']):
                data = recommendation_single_player(YELLOW_COLOR, playersList[0]['x'], playersList[0]['y'], playersList[0]['holdsBall'], playersList[0]['sightDirection'], ball_indexes[0]['x'], ball_indexes[0]['y'])
        # Two players from the same team
        elif (GAME_MODE == 2):
            if(len(playersList)==2 and len(ball_indexes)>0 and ball_indexes[0]['x'] and ball_indexes[0]['y']):
                data = recommendation_two_players_same_team(playersList, player_caps_index, ball_indexes[0]['x'], ball_indexes[0]['y'])

        if "color" in data and "output_state"  in data and "state"  in data:
            color_recommendation = data['color']
            output_state_recommendation = str(data['output_state'])
            state_recommendation = data['state']

        # Output recommendation label
        recommendation_label = color_recommendation + ": " + state_recommendation + " " + output_state_recommendation
        cv2.putText(frame, recommendation_label, 
                            (40, 110), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 1)
        
        # Save the frame with the recommendation to materials
        if recommendation_label != previous_recommendation_label:
            path = '../materials/recommendations/' + CURRENT_TIMESTAMP.strftime('%Y-%m-%d_%H-%M-%S')
            filename = f'{path}/{datetime.now().strftime("%Y-%m-%d_%H-%M-%S")}.jpg'
            os.makedirs(os.path.dirname(filename), exist_ok=True)
            cv2.imwrite(filename, cv2.resize(frame, (1600, 901)))
        
        previous_recommendation_label = recommendation_label

        # Output the result
        if MODE == 'video':
            print(f"{frame_index+1}/{nframes} frames processed")

        output.write(frame)
        cv2.imshow("Frame", rescale_frame(frame, scale=1)) # for usb camera scale=0.6667
        key = cv2.waitKey(1)
        if key == 27:
            break

output.release()
cv2.destroyAllWindows()
capture.release()
