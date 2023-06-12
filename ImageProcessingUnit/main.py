import sys
import cv2
import torch
import itertools
import os
from configs import APPEND_PATH, PINK_COLOR, SHOW_RECOMMENDATION_ARROW, MAX_PLAYERS_NUMBER
import colors_detection as cd
from datetime import datetime
import math
import json
ret = True
# Settings
sys.path.append(APPEND_PATH)
os.environ['CUDA_VISIBLE_DEVICES'] = '1'

from image_functions import rescale_frame
from recommendation_api_helpers import recommendation_single_player, recommendation_two_players_same_team, recommendation_two_players_different_teams, find_indexes_of_two_players, alert
from objects_detection import initialize_player_detection_model, detect_objects

# Read parameters from the configs
with open('../configs.json') as json_file:
    data = json.load(json_file)
GAME_MODE = data["game_mode"]
VIDEO_PATH = data["video_path"]
EXTERNAL_CAMERA = data["external_camera"]
CAMERA_INDEX = data["camera_index"]
MODE = data["mode"]
FIELD_COORDINATES = data["field_coordinates"]
GOALS = data["goals"]
SINGLE_ALERT_LINES = data["single_alert_lines"]
DOUBLE_ALERT_LINES = data["double_alert_lines"]

# Some constants
CURRENT_TIMESTAMP = datetime.now()
FIRST_FRAME_SAVED = False
PLAYERS_GOT_ALERT = MAX_PLAYERS_NUMBER * [False]

def save_traces_records(players_list, ball_indexes):
    # Get the path to the traces file
    path = '../materials/traces/' + CURRENT_TIMESTAMP.strftime('%Y-%m-%d_%H-%M-%S')
    
    traces_path = os.path.join(path, "traces.json")
    
    # Create the directory for the traces file
    os.makedirs(os.path.dirname(traces_path), exist_ok=True)

    # Load the data from the traces file, or create a new list if the file doesn't exist
    if os.path.exists(traces_path):
        with open(traces_path, 'r') as f:
            data = json.load(f)
    else:
        data = []
    
    # Create a new ball object and add it to the data list
    if ball_indexes:
        ball = {
            "gameId": CURRENT_TIMESTAMP.strftime('%Y-%m-%d_%H:%M:%S'),
            "class": "ball",
            "properties": ball_indexes[0]
        }
        data.append(ball)
    
    # Create a new player object for each player, add a color attribute, and add it to the data list
    for player in players_list:
        player_obj = {
            "gameId": CURRENT_TIMESTAMP.strftime('%Y-%m-%d_%H:%M:%S'),
            "class": "person",
            "properties": player
        }
        data.append(player_obj)
    
    # Save the updated data list to the traces file
    with open(traces_path, 'w') as f:
        json.dump(data, f)

def initialize_capture():
        if (MODE == 'video'):
            capture = cv2.VideoCapture(VIDEO_PATH) 
        elif (MODE == 'realtime'):
            # capture = cv2.VideoCapture(-1, cv2.CAP_V4L2)

            capture = None
            for i in range(10):  # assuming maximum 10 camera devices
                cap = cv2.VideoCapture(i, cv2.CAP_V4L2)
                if cap.isOpened():
                    capture = cap
                    break
            if capture is None:
                raise Exception("No valid camera index found")       
            # capture.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*'H264'))
            capture.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc('M', 'J', 'P', 'G'))

            if (EXTERNAL_CAMERA):
                capture.set(3, 1280)  # width (max - 3840)
                capture.set(4, 720)  # height (max - 2160)
        else: 
            raise ValueError('MODE constant must contain "realtime" or "video" value')
        
        return capture

def initialize_output(capture):
    fps = int(capture.get(cv2.CAP_PROP_FPS))
    print(fps)
    w = int(capture.get(cv2.CAP_PROP_FRAME_WIDTH))
    h = int(capture.get(cv2.CAP_PROP_FRAME_HEIGHT))
    CURRENT_TIMESTAMP = datetime.now()
    formatted_timestamp = CURRENT_TIMESTAMP.strftime('%Y-%m-%d %H:%M:%S')
    return cv2.VideoWriter(f'../output_videos/{formatted_timestamp}.ogv', cv2.VideoWriter_fourcc(*'THEO'), fps , (w,h))

capture = initialize_capture()

output = initialize_output(capture)

# Add a new game record to the materials
file_path = os.path.join("../materials", "games.txt")
with open(file_path, "a") as f:
    f.write(f"{CURRENT_TIMESTAMP.strftime('%Y-%m-%d_%H-%M-%S')} {GAME_MODE}\n")

if (MODE == 'video'):
    nframes = int(capture.get(cv2.CAP_PROP_FRAME_COUNT))

color_recommendation = ''
output_state_recommendation = ''
state_recommendation = ''
previous_recommendation_label = ''
frames_counter = 1
data = {}
pink_player = {}
orange_player = {}
angles = []
alert_result = {}

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

        player_caps_index = cd.detect_colors(frame) 

        (player_with_the_ball_center_point,
        prev_person_center_points,
        players_list,
        ball_indexes,
        frames_counter,
        angles,
        FIRST_FRAME_SAVED) = detect_objects(
            frame,
            prev_person_center_points,
            player_with_the_ball_center_point,
            img_size,
            device,
            use_half_precision,
            model,
            stride,
            names,
            classes,
            frames_counter,
            angles,
            FIRST_FRAME_SAVED,
            CURRENT_TIMESTAMP,
            FIELD_COORDINATES,
            GOALS)
        
        ball_prev_indexes = []
        if(len(ball_indexes)>0):
            ball_prev_indexes = ball_indexes

        # Single player
        if (GAME_MODE == 1):
            if len(players_list)>0:
                players_list[0]['id'] = 0
                players_list[0]['team'] = 0
            if(len(ball_prev_indexes)>0 and len(players_list)>0 and len(players_list[0])>3 and players_list[0]['x'] and players_list[0]['y'] and players_list[0]['holdsBall'] and players_list[0]['sightDirection'] and ball_indexes[0]['x'] and ball_indexes[0]['y']):
                data = recommendation_single_player(PINK_COLOR, players_list[0]['x'], players_list[0]['y'], players_list[0]['holdsBall'], players_list[0]['sightDirection'], ball_indexes[0]['x'], ball_indexes[0]['y'], GOALS)

                if not PLAYERS_GOT_ALERT[players_list[0]['id']]:
                    alert_result = alert([players_list[0]], ball_indexes[0]['x'], ball_indexes[0]['y'], GOALS, SINGLE_ALERT_LINES, DOUBLE_ALERT_LINES)
        # Two players from the same team
        elif (GAME_MODE == 2 or GAME_MODE == 3):
            pink_player, orange_player = find_indexes_of_two_players(players_list, player_caps_index)
            pink_player['id'] = 0
            orange_player['id'] = 1
            if(len(players_list)==2 and len(ball_indexes)>0 and ball_indexes[0]['x'] and ball_indexes[0]['y']):
                pink_player, orange_player = find_indexes_of_two_players(players_list, player_caps_index)
                pink_player['id'] = 0
                orange_player['id'] = 1

                pink_player.update({"team":0})
                if GAME_MODE == 2:
                    orange_player.update({"team":0})
                    data = recommendation_two_players_same_team(pink_player, orange_player, ball_indexes[0]['x'], ball_indexes[0]['y'], GOALS)
                else:
                    orange_player.update({"team":1})
                    data = recommendation_two_players_different_teams(pink_player, orange_player, ball_indexes[0]['x'], ball_indexes[0]['y'], GOALS)
                
                playersToAlert = []
                if not PLAYERS_GOT_ALERT[pink_player['id']]:
                    playersToAlert.append(pink_player)
                if not PLAYERS_GOT_ALERT[orange_player['id']]:
                    playersToAlert.append(orange_player)

                alert_result = alert(playersToAlert, ball_indexes[0]['x'], ball_indexes[0]['y'], GOALS, SINGLE_ALERT_LINES, DOUBLE_ALERT_LINES)
                playersToAlert = []

        if "color" in data and "output_state" in data and "state"  in data:
            color_recommendation = data['color']
            output_state_recommendation = str(data['output_state'])
            state_recommendation = data['state']

        save_traces_records(players_list, ball_indexes)

        # Output recommendation label
        recommendation_label = color_recommendation + ": " + state_recommendation + " " + output_state_recommendation
        cv2.putText(frame, recommendation_label, (40, 110), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 1)

        # Output alert label
        PLAYERS_GOT_ALERT = MAX_PLAYERS_NUMBER * [False]
        if 'result' in alert_result and 'idsAlerted' in alert_result:
            alert_label = alert_result['result']
            cv2.putText(frame, alert_label, (40, 160), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 1)

            for id in alert_result['idsAlerted']:
                PLAYERS_GOT_ALERT[id] = True
            
            alert_result = {}

        # Output recommendation arrow
        if SHOW_RECOMMENDATION_ARROW:
            if output_state_recommendation != '':
                arrow_angle = (int(output_state_recommendation) / 12) * 360
                start_arrow = (int(player_with_the_ball_center_point[0]), int(player_with_the_ball_center_point[1]))
                arrow_length = 40
                delta_x = arrow_length * math.cos(math.radians(arrow_angle))
                delta_y = arrow_length * math.sin(math.radians(arrow_angle))
                x2 = int(player_with_the_ball_center_point[0] + delta_x)
                y2 = int(player_with_the_ball_center_point[1] - delta_y)
                end_arrow = (x2, y2)
                color = (255, 191, 0) if color_recommendation == 'pink' else (5, 100, 100)
                cv2.arrowedLine(frame, start_arrow, end_arrow, color, thickness = 2, tipLength = 0.5)

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

        scale = 1
        if (EXTERNAL_CAMERA and MODE == 'realtime'):
            scale = 0.6667

        cv2.imshow("Frame", rescale_frame(frame, scale=scale))
        key = cv2.waitKey(1)
        if key == 27:
            break

# Release resources
output.release()
cv2.destroyAllWindows()
capture.release()
