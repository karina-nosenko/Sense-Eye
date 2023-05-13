import cv2
import json
import os
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
import pandas as pd
from collections import defaultdict

defined_strings = {0: 'orange', 1: 'pink', 2: 'red', 3: 'yellow'}

def create_personalized_frames():
    # Path to the directory containing the trace files and images
    trace_dir = "../materials/traces"

    # Iterate over all the game directories
    for game_dir in os.listdir(trace_dir):
        game_path = os.path.join(trace_dir, game_dir)

        # Ignore non-directory items in the traces folder
        if not os.path.isdir(game_path):
            continue

        # Read the trace file for this game
        trace_file_path = os.path.join(game_path, "traces.json")
        if not os.path.exists(trace_file_path):
            continue
        
        with open(trace_file_path, "r") as trace_file:
            print(trace_file)
            trace_data = json.load(trace_file)

        create_players_traces(game_path, trace_data)
        create_holds_the_ball_traces(game_path, trace_data)
        create_ball_holders_percentages(game_path, trace_data)
    

def create_players_traces(game_path, trace_data):    
        # Read the first frame image for this game
        frame_file_path = os.path.join(game_path, "first_frame.jpg")
        if not os.path.exists(frame_file_path):
            return
        
        frame_img = cv2.imread(frame_file_path)

        # Iterate over all the objects in the trace file
        for trace_obj in trace_data:
            if trace_obj["class"] == "person":
                # Extract the x and y coordinates for this person
                x = trace_obj["properties"]["x"]
                y = trace_obj["properties"]["center_y"]
                id = trace_obj["properties"].get("id", None)

                # Set the circle color based on the person's ID
                if id == 0:
                    circle_color = (0, 255, 255)  # yellow
                    cv2.circle(frame_img, (x, y), 1, circle_color, -1)
                elif id == 1:
                    circle_color = (0, 165, 255)  # orange
                    cv2.circle(frame_img, (x, y), 1, circle_color, -1)   

        # Save the image with the traces drawn
        output_file_path = os.path.join(game_path, "traces.jpg")
        cv2.imwrite(output_file_path, frame_img)

def create_holds_the_ball_traces(game_path, trace_data):
        # Read the first frame image for this game
        frame_file_path = os.path.join(game_path, "first_frame.jpg")
        if not os.path.exists(frame_file_path):
            return
        
        frame_img = cv2.imread(frame_file_path)

        # Iterate over all the objects in the trace file
        for trace_obj in trace_data:
            if trace_obj["class"] == "person":
                # Extract the x and y coordinates for this person
                x = trace_obj["properties"]["x"]
                y = trace_obj["properties"]["center_y"]
                id = trace_obj["properties"].get("id", None)
                holds_ball = trace_obj["properties"].get("holdsBall", None)

                # Set the circle color based on the person's ID
                if id == 0 and holds_ball == True:
                    circle_color = (0, 255, 255)  # yellow
                    cv2.circle(frame_img, (x, y), 1, circle_color, -1)
                elif id == 1 and holds_ball == True:
                    circle_color = (0, 165, 255)  # orange
                    cv2.circle(frame_img, (x, y), 1, circle_color, -1)   

        # Save the image with the traces drawn
        output_file_path = os.path.join(game_path, "holds_ball.jpg")
        cv2.imwrite(output_file_path, frame_img)

def create_ball_holders_percentages(game_path, trace_data):
    default_color = 'gray'  # Default color for IDs not found in defined_strings
    next_numeric_id = 2  # Start assigning numeric IDs from 4 onwards

    # Step 1: Group objects by gameId
    # game_groups = defaultdict(list)
    # for _, row in df.iterrows():
    #     game_groups[row['gameId']].append(row)
