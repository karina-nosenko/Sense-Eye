import sys
import os
import pymongo
import platform
import base64
import requests
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtWebEngineWidgets import *
from PyQt5.QtGui import *
from multiprocessing import Process

from mainWindow import *
from personalized_frames import create_personalized_frames

def create_games():
    api_url = "https://sense-eye-backend.onrender.com/api/games"

    # Uncomment to delete all the games from db
    # client = pymongo.MongoClient("mongodb+srv://yosef:sense111@cluster0.bmxfx.mongodb.net/sense-eye")
    # db = client["sense-eye"]
    # collection = db["games"]
    # collection.delete_many({})

    path = os.path.join("../materials", "games.txt")
    if not os.path.exists(path):
        return
    
    with open(path, "r+") as f:
        d = f.readlines()
        f.seek(0)
        for i in d:
            game_id, game_mode = i.strip().split()
            request_body = {
                "timestamp": game_id,
                "mode": game_mode,
                "orgName": "shenkar"
            }

            response = requests.post(api_url, json=request_body)
            if response.status_code >= 200 or response.status_code < 300:
                # Erase the current row from the file by overwriting it with an empty string
                f.write(i)
                f.truncate()
            else:
                # Unsuccessful insert - stop iterating
                return
            
        os.remove(path)

def send_recommendations_to_db():
    api_url = "https://sense-eye-backend.onrender.com/api/rec"

    # Uncomment to delete all the recommendations from db
    # client = pymongo.MongoClient("mongodb+srv://yosef:sense111@cluster0.bmxfx.mongodb.net/sense-eye")
    # db = client["sense-eye"]
    # collection = db["recomendations"]
    # collection.delete_many({})

    # Send the recommendations
    path = "../materials/recommendations"
    for foldername in os.listdir(path):
        full_path = os.path.join(path, foldername)
        if not os.path.isdir(full_path):
            continue
        
        for filename in os.listdir(full_path):
            with open(os.path.join(full_path, filename), "rb") as f:
                encoded_string = base64.b64encode(f.read())
                request_body = {
                    "status": 0,
                    "frame": encoded_string,
                    "orgName": "shenkar",
                    "gameID": foldername
                }

                response = requests.post(api_url, json=request_body)
                if response.status_code >= 200 or response.status_code < 300:
                    # Successful insert - delete the frame locally
                    os.remove(os.path.join(full_path, filename))
                else:
                    # Unsuccessful insert - stop iterating
                    return
        
        # Delete the folder after sending its contents (if the folder is empty)
        if len(os.listdir(os.path.join(path, foldername))) == 0:
            os.rmdir(os.path.join(path, foldername))

def is_internet_connection():
    ping_process = None
    if platform.system() == "Linux":
        ping_process = subprocess.run(['ping', '-c', '1', '216.24.57.253'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    else:
        # TODO: make sure it works on Windows
        ping_process = subprocess.run(['ping', '-n', '1', '216.24.57.253'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)

    if '1 received' in ping_process.stdout.decode():
        return True
    else:
        return False
    
def syncronize():
    while True:
        if is_internet_connection():
            print('Ping to server successful!')

            create_games() 
            send_recommendations_to_db()
            # TODO: send traces

        else:
            print('No ping response from the server.')
        time.sleep(10) # wait for 10 seconds before checking again

def start_sending_materials_process():
    # Keep sending materials to the internet each time
    # there's an internet connection (in a separate process)
    p = Process(target=syncronize)
    p.daemon = True
    p.start()

def start_creating_frames_process():
    p = Process(target=create_personalized_frames)
    p.daemon = True
    p.start()

if __name__ == '__main__':
    start_sending_materials_process()
    start_creating_frames_process()

    # Start the application
    app = QApplication(sys.argv)
    window = MainPage()
    window.show()
    sys.exit(app.exec_())