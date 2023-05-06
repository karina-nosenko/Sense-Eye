import cv2
import json
import os

def create_personalized_frames():
    create_players_traces()
    create_holds_the_ball_traces()
    create_heatmap()

def create_players_traces():
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
            trace_data = json.load(trace_file)

        # Read the first frame image for this game
        frame_file_path = os.path.join(game_path, "first_frame.jpg")
        if not os.path.exists(frame_file_path):
            continue
        frame_img = cv2.imread(frame_file_path)

        # Iterate over all the objects in the trace file
        for trace_obj in trace_data:
            if trace_obj["class"] == "person":
                # Extract the x and y coordinates for this person
                x = trace_obj["properties"]["x"]
                y = trace_obj["properties"]["y"]

                # Draw a circle on the image at this location
                cv2.circle(frame_img, (x, y), 1, (0, 0, 255))

        # Save the image with the traces drawn
        output_file_path = os.path.join(game_path, "traces.jpg")
        cv2.imwrite(output_file_path, frame_img)

def create_holds_the_ball_traces():
    #TODO
    return

def create_heatmap():
    #TODO
    return