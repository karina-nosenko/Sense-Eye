import requests
import json
import math

RECOMMENDATIONS_API_ADDRESS = "http://localhost:8080/api/mode"

def recommendation_single_player(color_id, player_x, player_y, holds_ball, direction, ball_x, ball_y, goals):
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
    - goals (list): Coordinates of the goals.
    
    Returns:
    - dict: The JSON response from the API call containing the recommendation.

    Raises:
        None
    """
    api_url = RECOMMENDATIONS_API_ADDRESS + "/singlePlayerMode"
    data = {
        "goals": goals,
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

    headers = {"Content-Type":"application/json"}
    response = requests.post(api_url, data=json.dumps(data), headers=headers)
    return response.json()

def recommendation_two_players_same_team(player1, player2, ball_x, ball_y, goals):
    """
    Calls an API endpoint with player data and returns a recommendation for a same team mode.

    Args:
    - player1 (dict): A dictionary containing the x and y positions, whether they hold the ball or not,
                      the color_id and direction of the first player.
    - player2 (dict): A dictionary containing the x and y positions, whether they hold the ball or not,
                      the color_id and direction of the second player.
    - ball_x (int): The x position of the ball.
    - ball_y (int): The y position of the ball.
    - goals (list): Coordinates of the goals.
    
    Returns:
    - dict: The JSON response from the API call containing the recommendation for the player that holds the ball.

    Raises:
        None
    """
    api_url = RECOMMENDATIONS_API_ADDRESS + "/sameTeamModeA"
    data = {
        "goals": goals,
        "players": [
            player1,
            player2
        ],
        "ball": {
            "x": ball_x,
            "y": ball_y
        }
    }
    
    headers =  {"Content-Type":"application/json"}
    response = requests.post(api_url, data=json.dumps(data), headers=headers)
    return response.json()

def recommendation_two_players_different_teams(player1, player2, ball_x, ball_y, goals):
    """
    Calls an API endpoint with player data and returns a recommendation for a different team mode.

    Args:
    - player1 (dict): A dictionary containing the x and y positions, whether they hold the ball or not,
                      the color_id and direction of the first player.
    - player2 (dict): A dictionary containing the x and y positions, whether they hold the ball or not,
                      the color_id and direction of the second player.
    - ball_x (int): The x position of the ball.
    - ball_y (int): The y position of the ball.
    - goals (list): Coordinates of the goals.
    
    Returns:
    - dict: The JSON response from the API call containing the recommendation for the player that holds the ball.

    Raises:
        None
    """
    api_url = RECOMMENDATIONS_API_ADDRESS + "/differentTeamsModeA"
    data = {
        "goals": goals,
        "players": [
            player1,
            player2
        ],
        "ball": {
            "x": ball_x,
            "y": ball_y
        }
    }
    
    headers =  {"Content-Type":"application/json"}
    response = requests.post(api_url, data=json.dumps(data), headers=headers)
    return response.json()

def alert(players, ball_x, ball_y, goals, single_alert_lines, double_alert_lines):
    api_url = RECOMMENDATIONS_API_ADDRESS + "/alertCloseToGate"
    data = {
        "goals": goals,
        "singleAlertLines": single_alert_lines,
        "doubleAlertLines": double_alert_lines,
        "players": players,
        "ball": {
            "x": ball_x,
            "y": ball_y
        }
    }

    headers =  {"Content-Type":"application/json"}
    response = requests.post(api_url, data=json.dumps(data), headers=headers)
    return response.json()

def find_indexes_of_two_players(player_caps_index, playersList):
    pink_player = {}
    orange_player = {}
    result = _find_closest_objects(playersList, player_caps_index)
    if(len(result)==2):
        if(result[0]['id'] == 1):
            pink_player = result[0]
            orange_player = result[1]
        else:
            pink_player = result[1]
            orange_player = result[0]

    return pink_player, orange_player

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