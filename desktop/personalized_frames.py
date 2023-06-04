import cv2
import json
import os
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
import pandas as pd
from collections import defaultdict
from PIL import Image

defined_strings = {0: 'orange', 1: 'pink'}

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
   
        # Open the JSON file and load its contents into a Python object
        with open(trace_file_path, 'r') as f:
            data = json.load(f)

        # Create the frames with insights
        create_players_traces(game_path, data)
        create_holds_the_ball_traces(game_path, data)
        create_ball_holders_percentages(data).savefig(game_path + '/ball_holders_percentages.png')
        create_ball_movement_pattern(data).savefig(game_path + '/ball_movement.png')
        create_player_movement_pattern(game_path, data).savefig(game_path + '/players_movement.png')
        create_players_heatmap(game_path, data).savefig(game_path + '/players_heatmap.png')
        create_ball_heatmap(game_path, data).savefig(game_path + '/ball_heatmap.png')

        # Delete unused files
        os.remove(os.path.join(game_path, "traces.json"))
        os.remove(os.path.join(game_path, "first_frame.jpg"))

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
                    circle_color = (140, 50, 180)  # pink
                    cv2.circle(frame_img, (x, y), 1, circle_color, -1)
                elif id == 1:
                    circle_color = (0, 165, 255)  # orange
                    cv2.circle(frame_img, (x, y), 1, circle_color, -1)   

        # Save the image with the traces drawn
        output_file_path = os.path.join(game_path, "traces.png")
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
                    circle_color = (140, 50, 180)  # pink
                    cv2.circle(frame_img, (x, y), 1, circle_color, -1)
                elif id == 1 and holds_ball == True:
                    circle_color = (0, 165, 255)  # orange
                    cv2.circle(frame_img, (x, y), 1, circle_color, -1)   

        # Save the image with the traces drawn
        output_file_path = os.path.join(game_path, "ball_holders_traces.png")
        cv2.imwrite(output_file_path, frame_img)

def create_ball_holders_percentages(data):
    default_color = 'gray'  # Default color for IDs not found in defined_strings
    next_numeric_id = 2  # Start assigning numeric IDs from 3 onwards

    # Load content into dataframe
    df = pd.DataFrame.from_dict(data, orient='columns')
    df = df.dropna(subset=['gameId'])

    # Create a copy of the original DataFrame
    players_df = df.copy()

    if 'properties' in players_df and 'id' in players_df['properties']:
        players_df['properties']['id'] = players_df['properties']['id'].astype(str).apply(lambda x: defined_strings.get(int(x), x))
    
    # Step 1: Group objects by gameId
    game_groups = defaultdict(list)
    for _, row in df.iterrows():
        game_groups[row['gameId']].append(row)

    # Step 2: Calculate holdsBall percentage for each id in each gameId group
    for game_id, group in game_groups.items():
        id_counts = defaultdict(int)
        total_objects = len(group)

        # Step 3: Count occurrences of holdsBall being true for each id
        for row in group:
            properties = row['properties']
            if 'holdsBall' in properties and properties['holdsBall'] and 'id' in properties:
                id_value = properties['id']
                if not isinstance(id_value, int):
                    if id_value not in defined_strings:
                        defined_strings[id_value] = next_numeric_id
                        next_numeric_id += 1
                    id_value = defined_strings[id_value]
                id_counts[id_value] += 1

        hash_map = {}  # Hash map to store ID-percentage associations
        max_percentage = 0
        max_color = None
        for id_value, count in id_counts.items():
            percentage = int(count / total_objects * 100)
            hash_map[id_value] = percentage
            if percentage > max_percentage:
                max_percentage = percentage
                max_color = defined_strings.get(id_value, default_color)

        # Prepare data for plotting
        ids = list(hash_map.keys())
        percentages = list(hash_map.values())

        # Convert numeric IDs to labels
        labels = [defined_strings.get(id_value, str(id_value)) for id_value in ids]

        # Plotting the chart
        plt.figure(figsize=(8, 6))
        plt.bar(labels, percentages, color=[defined_strings.get(id_value, default_color) for id_value in ids])
        plt.xlabel('Cap Color')
        plt.ylabel('Percentage')
        plt.title(f"Percentages of Ball Holders")

        # Display the percentage on top of each bar
        for i, percentage in enumerate(percentages):
            plt.text(i, percentage + 1, f"{percentage}%", ha='center', va='bottom')
        
        # Set the x-axis ticks to display only whole numbers
        plt.xticks(range(min(ids), max(ids) + 1))

        # Adjust the y-axis limit to accommodate the highest bar
        plt.ylim(top=max_percentage + 10)  # Increase the limit by 10 units 

        # Add text at the bottom of the chart
        text = f"The player with the highest percentage of holding the ball is: {max_color}"
        plt.text(0.5, -0.15, text, transform=plt.gca().transAxes, ha='center')

        # Adjust the layout to ensure the text fits within the figure
        plt.tight_layout()

        return plt

def create_ball_movement_pattern(data):
    plt.figure()

    # Extract the x-y coordinates for each ball location
    coords = []
    for d in data:
        if d["class"] == "ball":
            coords.append([d["properties"]["x"], d["properties"]["y"]])

    # Create a heatmap using Matplotlib
    if len(coords) > 0:
        coords = np.array(coords)
        plt.hist2d(coords[:, 0], coords[:, 1], bins=30, cmap=plt.cm.jet)

    plt.colorbar()
    plt.title("Ball Location Heatmap")
    plt.xlabel("X")
    plt.ylabel("Y")

    return plt

def create_player_movement_pattern(game_path, data):
    plt.figure()

    # Load the background image
    img = Image.open(game_path + '/first_frame.jpg')

    # Create a figure and axis objects with the same size as the background image
    fig, ax = plt.subplots(figsize=(img.width/100, img.height/100))

    # Plot the background image
    ax.imshow(img)

    # Set the x and y limits of the axis to match the dimensions of the image
    ax.set_xlim([0, img.width])
    ax.set_ylim([img.height, 0])

    # Group the data by gameId
    groups = {}
    for d in data:
        gameId = d["gameId"]
        if gameId not in groups:
            groups[gameId] = []
        if d["class"] == "person":
            groups[gameId].append([d["properties"]["x"], d["properties"]["y"]])

    # Create a heatmap for each group
    for gameId, coords in groups.items():
        if len(coords) > 0:
            coords = np.array(coords)
            # Set the extent of the heatmap to match the image dimensions
            im = ax.hist2d(coords[:, 0], coords[:, 1], bins=30, cmap=plt.cm.jet)[3]
        plt.colorbar(im, ax=ax)
        ax.set_title(f"Players Location Heatmap")
        ax.set_xlabel("X")
        ax.set_ylabel("Y")

        return plt
    
def create_players_heatmap(game_path, data):
    plt.figure()

    # Load the background image
    img = Image.open(game_path + '/first_frame.jpg')

    # Create a figure and axis objects with a larger size
    fig, ax = plt.subplots(figsize=(16, 8))
    # Set the aspect ratio of the image to match the dimensions of the plot
    aspect = img.width / float(img.height)
    ax.set_aspect(aspect)

    # Plot the background image
    ax.imshow(img)

    # Group the data by gameId
    groups = {}
    for d in data:
        gameId = d["gameId"]
        if gameId not in groups:
            groups[gameId] = []
        if d["class"] == "person":
            groups[gameId].append([d["properties"]["x"], d["properties"]["y"]])

    # Create a heatmap for each group
    for gameId, coords in groups.items():
        if len(coords) > 0:
            coords = np.array(coords)
            # Set the range of the heatmap to match the image dimensions
            im, _, _, _ = ax.hist2d(coords[:, 0], coords[:, 1], bins=30, cmap=plt.cm.Reds, alpha=0.4, range=[[0, img.width], [0, img.height]])
        ax.set_title(f"Players Location Heatmap")
        ax.set_xlabel("X")
        ax.set_ylabel("Y")

        return plt
    
def create_ball_heatmap(game_path, data):
    plt.figure()

    # Load the background image
    img = Image.open(game_path + '/first_frame.jpg')

    # Create a figure and axis objects with a larger size
    fig, ax = plt.subplots(figsize=(16, 8))

    # Set the aspect ratio of the image to match the dimensions of the plot
    aspect = img.width / float(img.height)
    ax.set_aspect(aspect)

    # Plot the background image
    ax.imshow(img)

    # Group the data by gameId
    groups = {}
    for d in data:
        gameId = d["gameId"]
        if gameId not in groups:
            groups[gameId] = []
        if d["class"] == "ball":
            groups[gameId].append([d["properties"]["x"], d["properties"]["y"]])

    # Create a heatmap for each group
    for gameId, coords in groups.items():
        if len(coords) > 0:
            coords = np.array(coords)
            # Set the range of the heatmap to match the image dimensions
            im, _, _, _ = ax.hist2d(coords[:, 0], coords[:, 1], bins=30, cmap=plt.cm.Reds, alpha=0.4, range=[[0, img.width], [0, img.height]])
        ax.set_title(f"Ball's Location Heatmap")
        ax.set_xlabel("X")
        ax.set_ylabel("Y")

        return plt