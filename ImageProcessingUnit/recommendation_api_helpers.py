import requests
import json
import math

RECOMMENDATIONS_API_ADDRESS = "http://localhost:8080/api/mode"

def recommendation_single_player(color_id, player_x, player_y, holds_ball, direction,ball_x, ball_y):
    """
    Calls an API endpoint with player data and returns a recommendation for a single player mode.

    Args:
    - color_id (str): The color identifier of the player.
    - player_x (float): The x-coordinate of the player.
    - player_y (float): The y-coordinate of the player.
    - holds_ball (bool): Whether the player is holding the ball or not.
    - direction (float): The direction the player is facing (in degrees).
    - ball_x (float): The x-coordinate of the ball.
    - ball_y (float): The y-coordinate of the ball.
    
    Returns:
    - dict: The JSON response from the API call containing the recommendation.

    Raises:
        None
    """
    api_url = RECOMMENDATIONS_API_ADDRESS + "/singlePlayerMode"
    todo = {
        "goals": [
            {
                "x1": 530,
                "y1": 60,
                "x2": 625,
                "y2": 60
            },
            {
                "x1": 473,
                "y1": 428,
                "x2": 573,
                "y2": 428
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


def recommendation_two_players_same_team(playersList, player_caps_index, ball_x, ball_y):
    """
    Calls an API endpoint with player data and returns a recommendation for a same team mode.

    Args:
    - playersList (list): A list of player dictionaries containing the player's x and y positions,
      whether they hold the ball or not, their color_id and direction.
    - player_caps_index (int): Coordinates of the caps of the players
    - ball_x (int): The x position of the ball.
    - ball_y (int): The y position of the ball.
    
    Returns:
    - dict: The JSON response from the API call containing the recommendation for the player that holds the ball.

    Raises:
        None
    """
    yellow_player, orange_player = _find_indexes_of_two_players(playersList, player_caps_index)
    # yellow_group = json.loads({"group":0})
    # orange_group = json.loads({"group":0})
    yellow_player.update({"team":0})
    yellow_player['id'] = 0
    orange_player.update({"team":0})
    orange_player['id'] = 1
    print(yellow_player)
    print(yellow_player)
    api_url = RECOMMENDATIONS_API_ADDRESS + "/sameTeamModeA"
    todo = {
        "goals": [
            {
                "x1": 530,
                "y1": 60,
                "x2": 625,
                "y2": 60
            },
            {
                "x1": 473,
                "y1": 428,
                "x2": 573,
                "y2": 428
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


def _find_indexes_of_two_players(player_caps_index,playersList):
    yellow_player = {}
    orange_player = {}
    # print(playersList)
    # print(player_caps_index)
    result = _find_closest_objects(playersList, player_caps_index)
    # print(result)
    # print("--------------------------------------")
    if(len(result)==2):
        if(result[0]['id']=='yellow'):
            yellow_player = result[0]
            orange_player = result[1]
        else:
            yellow_player = result[1]
            orange_player = result[0]

    return yellow_player, orange_player


def _find_closest_objects(arr1, arr2):
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