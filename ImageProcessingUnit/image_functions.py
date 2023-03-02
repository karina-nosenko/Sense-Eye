import cv2
import requests
import json
import math
def find_closest_objects(arr1, arr2):
    results = []
    used_indexes = []
    for obj1 in arr1:
        closest_dist = math.inf
        closest_obj2 = None
        for i, obj2 in enumerate(arr2):
            if i not in used_indexes:
                dist = math.sqrt((obj1['x'] - obj2['x'])**2 + (obj1['y'] - obj2['y'])**2)
                if dist < closest_dist:
                    closest_dist = dist
                    closest_obj2 = obj2
        if closest_obj2 is not None:
            closest_obj2['id'] = obj1['id']
            results.append(closest_obj2)
            used_indexes.append(arr2.index(closest_obj2))
            obj1['x'] = closest_obj2['x']
            obj1['y'] = closest_obj2['y']
    return results

def find_indexes_of_two_players(player_caps_index,playersList):
    yellow_player = {}
    orange_player = {}
    print(playersList)
    print(player_caps_index)
    result = find_closest_objects(playersList,player_caps_index)
    print(result)
    print("--------------------------------------")
    if(len(result)==2):
        if(result[0]['id']=='yellow'):
            yellow_player = result[0]
            orange_player = result[1]
        else:
            yellow_player = result[1]
            orange_player = result[0]
    return yellow_player,orange_player

def recomendetion_two_players_same_team(playersList,player_caps_index,ball_x,ball_y):
    yellow_player, orange_player = find_indexes_of_two_players(playersList,player_caps_index)
    # yellow_group = json.loads({"group":0})
    # orange_group = json.loads({"group":0})
    yellow_player.update({"team":0})
    yellow_player['id'] = 0
    orange_player.update({"team":0})
    orange_player['id'] = 1
    print(yellow_player)
    api_url = "http://localhost:8080/api/mode/sameTeamModeA"
    todo = {
    "goals": [
        {
            "x1": 1,
            "y1": 15,
            "x2": 1,
            "y2": 10
        },
        {
            "x1": 20,
            "y1": 15,
            "x2": 20,
            "y2": 10
        }
    ],
    "players": [
        yellow_player,
        orange_player
    ],
    "ball": {
        "x": ball_x,
        "y": ball_y
    }
}
    headers =  {"Content-Type":"application/json"}
    response = requests.post(api_url, data=json.dumps(todo), headers=headers)
    return response.json()
   
def recomendetion_single_player(color_id,player_x,player_y,holds_ball,direction,ball_x,ball_y):
    api_url = "http://localhost:8080/api/mode/singlePlayerMode"
    todo = {
    "goals": [
        {
            "x1": 1,
            "y1": 15,
            "x2": 1,
            "y2": 10
        },
        {
            "x1": 20,
            "y1": 15,
            "x2": 20,
            "y2": 10
        }
    ],
    "players": [
        {
            "id": color_id,
            "x": player_x,
            "y": player_y,
            "team": 0,
            "holdsBall": holds_ball,
            "sightDirection":direction 
        }
    ],
    "ball": {
        "x": ball_x,
        "y": ball_y
    }
}
    headers =  {"Content-Type":"application/json"}
    response = requests.post(api_url, data=json.dumps(todo), headers=headers)
    return response.json()
def rescale_frame(frame, scale):
    """
    Rescales the input frame by the specified scale factor.

    Args:
        frame (numpy.ndarray): A numpy array representing a single frame of a video.
        scale (float): A positive floating-point value specifying the scale factor by which to resize the frame.
    
    Returns:
        numpy.ndarray: A numpy array representing the resized frame.

    Raises:
        None
    """
    width = int(frame.shape[1] * scale)
    height = int(frame.shape[0] * scale)
    dimensions = (width, height)
    return cv2.resize(frame, dimensions, interpolation=cv2.INTER_AREA)


def adjust_image_to_desired_shape(img, new_shape=(640, 640), color=(114, 114, 114), auto=True, scaleFill=False, scaleup=True, stride=32):
    """
    Resizes and pads an image, while making sure the size of the image is a multiple of the 'stride' parameter.

    Args:
        img (ndarray): The input image to be resized and padded.
        new_shape (tuple): The desired output shape of the image, defaults to (640, 640).
        color (tuple): The color of the padding, defaults to (114, 114, 114).
        auto (bool): If True, adds padding to ensure the output image has minimum rectangle size, defaults to True.
        scaleFill (bool): If True, stretches the image to fill the desired output shape, defaults to False.
        scaleup (bool): If True, scales the image up to meet the desired output shape, defaults to True.
        stride (int): The stride of the output image, defaults to 32.
    
    Returns:
        tuple: A tuple containing the resized and padded image (ndarray), the scale ratio (tuple), and the amount of padding added to the width and height (tuple).

    Raises:
        None
    """
    # Ensure that new_shape is a tuple with two elements
    current_shape = img.shape[:2]
    if isinstance(new_shape, int):
        new_shape = (new_shape, new_shape)

    # Calculate the scaling ratio for the image
    scale_ratio = min(new_shape[0] / current_shape[0], new_shape[1] / current_shape[1])
    if not scaleup:
        scale_ratio = min(scale_ratio, 1.0)

    # Compute padding
    ratio = scale_ratio, scale_ratio
    new_unpad = int(round(current_shape[1] * scale_ratio)), int(round(current_shape[0] * scale_ratio))
    width_padding = new_shape[1] - new_unpad[0]
    height_padding = new_shape[0] - new_unpad[1]
    if auto:
        width_padding %= stride
        height_padding %= stride
    elif scaleFill:
        width_padding, height_padding = 0.0, 0.0
        new_unpad = (new_shape[1], new_shape[0])
        ratio = new_shape[1] / current_shape[1], new_shape[0] / current_shape[0]

    # divide padding into 2 sides
    width_padding /= 2
    height_padding /= 2

    # resize
    if current_shape[::-1] != new_unpad:
        img = cv2.resize(img, new_unpad, interpolation=cv2.INTER_LINEAR)

    top, bottom = int(round(height_padding - 0.1)), int(round(height_padding + 0.1))
    left, right = int(round(width_padding - 0.1)), int(round(width_padding + 0.1))
    img = cv2.copyMakeBorder(img, top, bottom, left, right, cv2.BORDER_CONSTANT, value=color)
    return img, ratio, (width_padding, height_padding)