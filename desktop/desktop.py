import sys
import os
import pymongo
from PIL import Image
import base64
from PyQt5 import QtCore
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtWebEngineWidgets import *
from PyQt5.QtGui import *
from multiprocessing import Process

from mainWindow import *
from personalized_frames import create_personalized_frames

def create_games():
    client = pymongo.MongoClient("mongodb+srv://yosef:sense111@cluster0.bmxfx.mongodb.net/sense-eye")
    db = client["sense-eye"]
    collection = db["games"]

    path = os.path.join("../materials", "games.txt")
    if not os.path.exists(path):
        return
    
    with open(path, "r+") as f:
        d = f.readlines()
        f.seek(0)
        for i in d:
            game_id, game_mode = i.strip().split()
            document = {
                "timestamp": game_id,
                "mode": game_mode,
                "orgName": "shenkar"
            }

            result = collection.insert_one(document)
            if result.inserted_id:
                # Erase the current row from the file by overwriting it with an empty string
                f.write(i)
                f.truncate()
            else:
                # Unsuccessful insert - stop iterating
                return
            
        os.remove(path)

def send_recommendations_to_db():
    client = pymongo.MongoClient("mongodb+srv://yosef:sense111@cluster0.bmxfx.mongodb.net/sense-eye")
    db = client["sense-eye"]
    collection = db["recomendations"]

    # Uncomment to delete all the recommendations from db
    # collection.delete_many({})

    # Send the recommendations
    path = "../materials/recommendations"
    for foldername in os.listdir(path):
        for filename in os.listdir(os.path.join(path, foldername)):
            with open(os.path.join(path, foldername, filename), "rb") as f:
                encoded_string = base64.b64encode(f.read())
                data = {
                    "status": 0,
                    "frame": encoded_string,
                    "orgName": "shenkar",
                    "gameID": foldername
                }

                result = collection.insert_one(data)
                if result.inserted_id:
                    # Successful insert - delete the frame locally
                    os.remove(os.path.join(path, foldername, filename))
                else:
                    # Unsuccessful insert - stop iterating
                    return
        
        # Delete the folder after sending its contents
        os.rmdir(os.path.join(path, foldername))

def is_internet_connection():
    ping_process = subprocess.run(['ping', '-c', '1', 'google.com'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    if '1 received' in ping_process.stdout.decode():
        return True
    else:
        return False
    
def syncronize():
    while True:
        if is_internet_connection():
            print('Ping to Google successful!')

            create_games() 
            send_recommendations_to_db()

        else:
            print('No ping response from Google.')
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

    # Start the application
    app = QApplication(sys.argv)
    window = MainPage()
    window.show()
    sys.exit(app.exec_())
