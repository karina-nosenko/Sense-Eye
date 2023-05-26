from PyQt5 import QtCore
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtWebEngineWidgets import *
from PyQt5.QtGui import *
from pymongo import MongoClient
import subprocess
import os
import signal
import psutil
import time
import subprocess
import platform
import json
import cv2
import itertools

from videoWindow import *
from styles import *
from desktop import start_sending_materials_process, start_creating_frames_process

from dotenv import load_dotenv
import os

# Load the .env file
load_dotenv()

# Access the environment variables
# DB_HOST = os.getenv('DB_HOST')

inputStyle = """
    QLineEdit {
        background-color: #f2f2f2;
        border: none;
        border-radius: 10px;
        font-size: 16px;
        padding: 10px;
    }
"""

selectorStyle = """
    QComboBox {
                background-color: #F0F0F0;
                color: #000000;
                border: 1px solid #CCCCCC;
                border-radius: 5px;
                padding: 5px;
    }
    
    QComboBox::drop-down {
        subcontrol-origin: padding;
        subcontrol-position: top right;
        width: 20px;
        
        border-left-width: 1px;
        border-left-color: #CCCCCC;
        border-left-style: solid;
        border-top-right-radius: 5px;
        border-bottom-right-radius: 5px;
    }
    
    QComboBox::down-arrow {
        image: url(icons/down_arrow.png);
        background-position: center;
        background-repeat: no-repeat;
        background-size: 5px 5px;
    }
"""

# == Login Page ==#
class LoginPage(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('SenseEye Login')
        self.setStyleSheet("background-color: #f7f7f7;")

        # get screen size
        screen_size = QDesktopWidget().screenGeometry()

        # set the geometry of the window
        width_percent = 60
        height_percent = 60
        width = int(screen_size.width() * width_percent / 100)
        height = int(screen_size.height() * height_percent / 100)
        self.setGeometry(0, 0, width, height)

        # create a logo label
        self.logoLabel = QLabel(self)
        self.logoLabel.setGeometry(QRect(0, 0, width, height * 0.2))
        self.logoLabel.setPixmap(QPixmap("logo.jfif"))
        self.logoLabel.setScaledContents(True)

        # create organization name input
        self.organizationLabel = QLabel(self)
        self.organizationLabel.setText('Organization Name:')
        self.organizationLabel.setStyleSheet(labelStyle)
        self.organizationLabel.setAlignment(Qt.AlignVCenter)

        self.organizationInput = QLineEdit(self)
        self.organizationInput.setStyleSheet(inputStyle + "background-color: white;")
        self.organizationInput.setFixedWidth(width * 0.3)
        self.organizationInput.setFixedHeight(height * 0.05)
        self.organizationInput.setAlignment(Qt.AlignVCenter)

        # create password input
        self.passwordLabel = QLabel(self)
        self.passwordLabel.setText('Password:')
        self.passwordLabel.setStyleSheet(labelStyle)
        self.passwordLabel.setAlignment(Qt.AlignVCenter)

        self.passwordInput = QLineEdit(self)
        self.passwordInput.setStyleSheet(inputStyle + "background-color: white;")
        self.passwordInput.setFixedWidth(width * 0.3)
        self.passwordInput.setFixedHeight(height * 0.05)
        self.passwordInput.setEchoMode(QLineEdit.Password)
        self.passwordInput.setAlignment(Qt.AlignVCenter)

        # create a "login" button
        self.buttonLogin = QPushButton('Login', self)
        self.buttonLogin.clicked.connect(self.login)
        self.buttonLogin.setFixedWidth(width * 0.3)
        self.buttonLogin.setFixedHeight(height * 0.05)
        self.buttonLogin.setCursor(QCursor(QtCore.Qt.PointingHandCursor))
        self.buttonLogin.setStyleSheet(buttonStyle)

        # create a vertical layout and add the widgets to it
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.logoLabel)
        layout.addStretch()
        layout.addWidget(self.organizationLabel)
        layout.addWidget(self.organizationInput)
        layout.addWidget(self.passwordLabel)
        layout.addWidget(self.passwordInput)
        layout.addWidget(self.buttonLogin)
        layout.addStretch()

        # create a central widget and set the layout on it
        central_widget = QWidget()
        central_widget.setLayout(layout)

        # set the central widget on the main window
        self.setCentralWidget(central_widget)

    def login(self):
        # get organization name and password from inputs
        org_name = self.organizationInput.text()
        password = self.passwordInput.text()

        # connect to MongoDB
        # client = MongoClient('mongodb+srv://yosef:sense111@cluster0.bmxfx.mongodb.net/sense-eye')
        # db = client["sense-eye"]
        # collection = db["organizations"]
        # query = {"name": org_name, "password": password}
        # result = collection.find_one(query)

        # close the MongoDB connection
        # client.close()

        self.main_window = MainPage()
        self.main_window.show()
        self.close()

        # # if result is not None, the organization name and password are valid
        # if result is not None:
        #     # connect to main window or do something else
        #     print("Valid organization name and password")
        #     # Connect the user to the main window
        #     self.main_window = MainPage()
        #     self.main_window.show()
        #     self.close()
        # else:
        #     # display error message or do something else
        #     print("Invalid organization name or password")
        #     QMessageBox.warning(self, "Error", "Invalid organization name or password.")

#== Main Page ==#
class MainPage(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()    

    def initUI(self):        
        self.setWindowTitle('SenseEye Desktop Application')
        self.setStyleSheet("background-color: #f7f7f7;")

        # calculate the width and height of the window in percentages
        width_percent = 60
        height_percent = 60
        screen_size = QDesktopWidget().screenGeometry()
        width = int(screen_size.width() * width_percent / 100)
        height = int(screen_size.height() * height_percent / 100)

        # set the geometry of the window
        self.setGeometry(0, 0, width, height)
        
        # create the web view widget
        self.webview = QWebEngineView(self)
        self.webview.setGeometry(0, 0, width, height)
        
        # create the heading
        self.heading = QLabel(self)
        self.heading.setText('My Camera Feed')
        self.heading.setAlignment(Qt.AlignVCenter) 
        self.heading.setStyleSheet(headingStyle)  

        # create the mode selector
        self.modeSelector = QComboBox()
        self.modeSelector.addItems(["Single Player", "Two Players Same Team", "Two Players Different Teams"])
        self.modeSelector.currentIndexChanged.connect( self.change_mode )
        self.modeSelector.setStyleSheet(selectorStyle)

        # set the current selected mode as the last that was selected
        with open('../configs.json') as json_file:
            data = json.load(json_file)
        self.modeSelector.setCurrentIndex(data["game_mode"] - 1)
  
        # create a "start" button
        self.buttonStart = QPushButton('Start', self) 
        self.buttonStart.clicked.connect(self.start_process)
        self.buttonStart.setFixedSize(200, 50)
        self.buttonStart.setCursor(QCursor(QtCore.Qt.PointingHandCursor))
        self.buttonStart.setStyleSheet(buttonStyle)

        # create a "status" label
        self.statusLabel = QLabel()
        self.statusLabel.setText('Connecting...')
        self.statusLabel.setAlignment(Qt.AlignVCenter)
        self.statusLabel.setStyleSheet(labelStyle)
        self.statusLabel.hide()   

        # create a "end" button
        self.buttonEnd = QPushButton('End', self)
        self.buttonEnd.clicked.connect(self.end_process)
        self.buttonEnd.setFixedSize(200, 50)
        self.buttonEnd.setCursor(QCursor(QtCore.Qt.PointingHandCursor))
        self.buttonEnd.setStyleSheet(buttonStyle)
        self.buttonEnd.hide()

        # create a "customize field" button
        self.buttonField = QPushButton('Customize Field', self)
        self.buttonField.clicked.connect(self.show_field_page)
        self.buttonField.setFixedSize(200, 50)
        self.buttonField.setCursor(QCursor(QtCore.Qt.PointingHandCursor))
        self.buttonField.setStyleSheet(buttonStyle)

        # create a "view history" button
        self.buttonHistory = QPushButton('View History', self)
        self.buttonHistory.clicked.connect(self.show_history_page)
        self.buttonHistory.setFixedSize(200, 50)
        self.buttonHistory.setCursor(QCursor(QtCore.Qt.PointingHandCursor))
        self.buttonHistory.setStyleSheet(buttonStyle)

        # create a vertical layout and add the widgets to it
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.heading)
        layout.addSpacing(40)
        layout.addWidget(self.modeSelector)
        layout.addSpacing(20)
        layout.addWidget(self.buttonStart)
        layout.addSpacing(20)
        layout.addWidget(self.statusLabel)
        layout.addSpacing(20)
        layout.addWidget(self.buttonEnd)
        layout.addSpacing(20)
        layout.addWidget(self.buttonField)
        layout.addSpacing(20)
        layout.addWidget(self.buttonHistory)
        
        # create a central widget and set the layout on it
        central_widget = QWidget()
        central_widget.setLayout(layout)
        
        # set the central widget on the main window
        self.setCentralWidget(central_widget)

        # initialize subprocess variables to None
        self.process1 = None
        self.process2 = None
        self.process3 = None  

    def change_mode(self, mode):
        with open('../configs.json') as json_file:
            data = json.load(json_file)

        new_mode = int(mode) + 1
        data["game_mode"] = new_mode
        if new_mode == 1:
            data["video_path"] = "yolov7/videos/single_player_yellow.mp4"
        else:
            data["video_path"] = "yolov7/videos/two_players_orange_yellow.mp4"

        with open('../configs.json', 'w') as json_file:
            json.dump(data, json_file, indent=4)

    def start_process(self):
        self.buttonStart.hide()
        self.statusLabel.show()
        self.buttonEnd.show()

        # release ports
        subprocess.run("fuser -k 5000/tcp", shell=True)
        subprocess.run("fuser -k 8080/tcp", shell=True)
        # give the user 10 seconds to connect the components
        self.statusLabel.setText('Attempting to connect to the components...')
        QApplication.processEvents()
        self.process1 = subprocess.Popen(['python3','main.py'],cwd='../', shell=True) 
        time.sleep(10)
        self.statusLabel.setText('Please wait! The video window will pop up in a minute.')

        self.process2 = subprocess.Popen(['npm','run','dev'],cwd='../RecommendationsUnit/', shell=True)
        self.process3 = subprocess.Popen(['python3','main.py'],cwd='../ImageProcessingUnit/', shell=True)
        if platform.system() == "Linux":
            # release ports
            os.system("sudo fuser -k 5000/tcp")
            os.system("sudo fuser -k 8080/tcp")

            # give the user 10 seconds to connect the components
            self.statusLabel.setText('Attempting to connect to the components...')
            QApplication.processEvents()
            self.process1 = subprocess.Popen(['sudo', 'python3','main.py'],cwd='../') 
            time.sleep(10)
            self.statusLabel.setText('Please wait! The video window will pop up in a minute.')

            self.process2 = subprocess.Popen(['npm','run','dev'],cwd='../RecommendationsUnit/')
            self.process3 = subprocess.Popen(['sudo', 'python3','main.py'],cwd='../ImageProcessingUnit/')
        else:
            # TODO: make sure it works on Windows
            # release ports
            os.system("fuser -k 5000/tcp")
            os.system("fuser -k 8080/tcp")

            # give the user 10 seconds to connect the components
            self.statusLabel.setText('Attempting to connect to the components...')
            QApplication.processEvents()
            self.process1 = subprocess.Popen(['python','main.py'],cwd='../', shell=True) 
            time.sleep(10)
            self.statusLabel.setText('Please wait! The video window will pop up in a minute.')

            self.process2 = subprocess.Popen(['npm','run','dev'],cwd='../RecommendationsUnit/', shell=True)
            self.process3 = subprocess.Popen(['python','main.py'],cwd='../ImageProcessingUnit/', shell=True)
        
    def end_process(self):
        self.buttonStart.show()
        self.statusLabel.hide()
        self.buttonEnd.hide()

        # terminate all subprocesses
        if self.process1:
            os.kill(self.process1.pid, signal.SIGKILL)
            self.process1.wait()  # Wait for the process to exit
            self.process1 = None 

        if self.process2:
            os.kill(self.process2.pid, signal.SIGKILL)
            self.process2.wait()  # Wait for the process to exit
            self.process2 = None 

        if self.process3:
            process = psutil.Process(pid=self.process3.pid)
            
            # Get a list of all child processes and terminate them
            child_processes = process.children(recursive=True)
            for child in child_processes:
                child.terminate()

            # Terminate any threads in the process
            for thread in process.threads():
                if getattr(psutil._psplatform, "Thread", None):
                    thread_obj = psutil._psplatform.Thread(thread.id, process.pid)
                    thread_obj.terminate()

            # Finally, terminate the main process
            process.terminate()

        self.process1 = None
        self.process2 = None
        self.process3 = None

        print("All subprocesses terminated.")
 
        start_sending_materials_process()
        start_creating_frames_process()

    def show_history_page(self):
        self.heading.hide()
        self.buttonStart.hide()
        self.buttonEnd.hide()
        self.buttonField.hide()
        self.buttonHistory.hide()
        self.statusLabel.hide()

        self.setCentralWidget(HistoryPage())

    def show_field_page(self):
        self.heading.hide()
        self.buttonStart.hide()
        self.buttonEnd.hide()
        self.buttonField.hide()
        self.buttonHistory.hide()
        self.statusLabel.hide()

        self.setCentralWidget(FieldPage())


#== History Page ==#
class HistoryPage(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self): 
        # create the heading
        self.heading = QLabel(self)
        self.heading.setText('My Camera History')
        self.heading.setAlignment(Qt.AlignVCenter) 
        self.heading.setStyleSheet(headingStyle)

        # create the videos buttons
        self.videosLayout = QGridLayout()
        self.videosLayout.setSpacing(10)
        row = 0
        column = 0
        video_folder = "../output_videos"

        # delete videos if their number exceeds the specified value
        videos_list = sorted(os.listdir(video_folder))
        if len(videos_list) > 27:
            videos_to_delete = videos_list[:-27]
            for video in videos_to_delete:
                video_path = os.path.join(video_folder, video)
                os.remove(video_path)

        # create the videos
        videos_list = sorted(os.listdir(video_folder))
        for filename in videos_list:
            if filename.endswith(".ogv"):
                video_path = os.path.join(video_folder, filename)
                button = QPushButton(filename[:-4], self) 
                button.clicked.connect(lambda checked, path=video_path: self.open_video_window(path))
                button.setFixedSize(500, 50)
                button.setStyleSheet(buttonStyle)
                self.videosLayout.addWidget(button, row, column)
                column += 1
                if column == 3:
                    row += 1
                    column = 0

        # create a "back" button
        self.buttonBack = QPushButton('Back', self) 
        self.buttonBack.clicked.connect(self.show_main_window_page)
        self.buttonBack.setFixedSize(200, 50)
        self.buttonBack.setCursor(QCursor(QtCore.Qt.PointingHandCursor))
        self.buttonBack.setStyleSheet(buttonStyle)

        # create a vertical layout and add the widgets to it
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.heading)
        layout.addSpacing(40)
        layout.addLayout(self.videosLayout)
        layout.addSpacing(40)
        layout.addWidget(self.buttonBack)

        # create a central widget and set the layout on it
        central_widget = QWidget()
        central_widget.setLayout(layout)
        
        # set the central widget on the main window
        self.setCentralWidget(central_widget)


    def open_video_window(self, video_path):
        self.w = VideoWindow(video_path)
        self.w.show()

    def show_main_window_page(self):
        self.heading.hide()
        self.buttonBack.hide()

        self.setCentralWidget(MainPage())

#== Customize Field Page ==#
class FieldPage(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self): 
        # create the heading
        self.heading = QLabel(self)
        self.heading.setText('Customize Field')
        self.heading.setAlignment(Qt.AlignVCenter) 
        self.heading.setStyleSheet(headingStyle)

        # read json configs
        with open('../configs.json') as json_file:
            data = json.load(json_file)
            self.VIDEO_PATH = '../ImageProcessingUnit/' + data["video_path"]
            self.EXTERNAL_CAMERA = data["external_camera"]
            self.CAMERA_INDEX = data["camera_index"]
            self.MODE = data["mode"]
            self.GOALS = data["goals"]
            self.FIELD_DELIMITERS = data["field_delimiters"]
            self.FIELD_COORDINATES = data["field_coordinates"]

        # read a frame
        capture = self.initialize_capture()
        ret, self.frame = capture.read()
        self.initial_field_path = 'initial_field.jpg'
        cv2.imwrite(self.initial_field_path, self.frame)
        capture.release()
        self.field_path = 'field.jpg'

        #TODO: if no field.jpg was created - display a label of "Failed to capture a field" 

        self.draw_goals()
        self.draw_field_corners()

        # update field.jpg
        cv2.imwrite(self.field_path, self.frame)

        # embed a frame to the view
        self.field_image = QLabel(self)
        self.setCentralWidget(self.field_image)
        self.pixmap = QPixmap(self.field_path)
        if not self.pixmap.isNull():
            self.field_image.setPixmap(self.pixmap)
            self.field_image.setScaledContents(True)
        else:
            print(f"Failed to load image from {self.field_path}")

        # create an "update field" button
        self.buttonFieldCorners = QPushButton('Update Field', self) 
        self.buttonFieldCorners.clicked.connect(self.update_field)
        self.buttonFieldCorners.setFixedSize(200, 50)
        self.buttonFieldCorners.setCursor(QCursor(QtCore.Qt.PointingHandCursor))
        self.buttonFieldCorners.setStyleSheet(buttonStyle)

        # create an "update gates" button
        self.buttonGatesCorners = QPushButton('Update Gates', self) 
        self.buttonGatesCorners.clicked.connect(self.update_goals)
        self.buttonGatesCorners.setFixedSize(200, 50)
        self.buttonGatesCorners.setCursor(QCursor(QtCore.Qt.PointingHandCursor))
        self.buttonGatesCorners.setStyleSheet(buttonStyle)

        # create an "update delimeters" button
        self.buttonDelimeters = QPushButton('Update Delimeters', self) 
        self.buttonDelimeters.clicked.connect(self.show_main_window_page)
        self.buttonDelimeters.setFixedSize(200, 50)
        self.buttonDelimeters.setCursor(QCursor(QtCore.Qt.PointingHandCursor))
        self.buttonDelimeters.setStyleSheet(buttonStyle)

        # create a "save" button
        self.buttonSave = QPushButton('Save', self) 
        self.buttonSave.clicked.connect(self.show_main_window_page)
        self.buttonSave.setFixedSize(200, 50)
        self.buttonSave.setCursor(QCursor(QtCore.Qt.PointingHandCursor))
        self.buttonSave.setStyleSheet(buttonStyle)

        # create a "back" button
        self.buttonBack = QPushButton('Back', self) 
        self.buttonBack.clicked.connect(self.show_main_window_page)
        self.buttonBack.setFixedSize(200, 50)
        self.buttonBack.setCursor(QCursor(QtCore.Qt.PointingHandCursor))
        self.buttonBack.setStyleSheet(buttonStyle)

        # create a vertical layout and add the widgets to it
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.heading)
        layout.addSpacing(40)
        layout.addWidget(self.field_image)
        layout.addSpacing(40)
        layout.addWidget(self.buttonFieldCorners)
        layout.addSpacing(10)
        layout.addWidget(self.buttonGatesCorners)
        layout.addSpacing(10)
        layout.addWidget(self.buttonDelimeters)
        layout.addSpacing(40)
        layout.addWidget(self.buttonSave)
        layout.addSpacing(20)
        layout.addWidget(self.buttonBack)

        # create a central widget and set the layout on it
        self.central_widget = QWidget()
        self.central_widget.setLayout(layout)
        
        # set the central widget on the main window
        self.setCentralWidget(self.central_widget)    

    def initialize_capture(self):
        if (self.MODE == 'video'):
            capture = cv2.VideoCapture(self.VIDEO_PATH) 
        elif (self.MODE == 'realtime'):
            capture = cv2.VideoCapture(self.CAMERA_INDEX)
            # capture.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*'H264'))
            capture.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc('M', 'J', 'P', 'G'))

            if (self.EXTERNAL_CAMERA):
                capture.set(3, 1280)  # width (max - 3840)
                capture.set(4, 720)  # height (max - 2160)
        else: 
            raise ValueError('MODE constant must contain "realtime" or "video" value')
        
        return capture
    
    def update_field_image(self):
        cv2.imwrite(self.field_path, self.frame)

        self.pixmap = QPixmap(self.field_path)

        if not self.pixmap.isNull():
            self.field_image.setPixmap(self.pixmap)
            self.field_image.setScaledContents(True)
        else:
            print(f"Failed to load image from {self.field_path}")

    def draw_field_corners(self):
        if len(self.FIELD_COORDINATES) < 4:
            return

        corners = [
            (self.FIELD_COORDINATES[0]['x'], self.FIELD_COORDINATES[0]['y']),
            (self.FIELD_COORDINATES[1]['x'], self.FIELD_COORDINATES[1]['y']),
            (self.FIELD_COORDINATES[2]['x'], self.FIELD_COORDINATES[2]['y']),
            (self.FIELD_COORDINATES[3]['x'], self.FIELD_COORDINATES[3]['y'])
        ]

        for corner in corners:
            cv2.circle(self.frame, corner, 3, (0, 0, 255), -1)

    def draw_goals(self):
        if len(self.GOALS) < 2:
            return

        goals = [
            [(self.GOALS[0]['x1'], self.GOALS[0]['y1']), (self.GOALS[0]['x2'], self.GOALS[0]['y2'])],
            [(self.GOALS[1]['x1'], self.GOALS[1]['y1']), (self.GOALS[1]['x2'], self.GOALS[1]['y2'])]
        ]

        for goal in goals:
            cv2.line(self.frame, goal[0], goal[1], (0, 0, 255), 1)

    def update_field(self):
        # clear the field corners
        self.FIELD_COORDINATES = []
        self.frame = cv2.imread(self.initial_field_path)
        self.draw_goals()
        self.update_field_image()

        # handle click events
        self.field_image.mousePressEvent = self.mouse_click_event_update_field

    def mouse_click_event_update_field(self, event):
        if len(self.FIELD_COORDINATES) >= 4:
            return

        # get mouse click coordinates
        x, y = event.pos().x(), event.pos().y()

        # add the new coordinate to the field corners list
        self.FIELD_COORDINATES.append({"x": x, "y": y})

        # update the coordinate on the image
        cv2.circle(self.frame, (x, y), 3, (0, 0, 255), -1)
        self.update_field_image()

    def update_goals(self):
        # clear the goals
        self.GOALS = []
        self.frame = cv2.imread(self.initial_field_path)
        self.draw_field_corners()
        self.update_field_image()

        # handle click events
        self.field_image.mousePressEvent = self.mouse_click_event_update_goals

    def mouse_click_event_update_goals(self, event):
        goals_number = len(self.GOALS)

        if len(self.GOALS) >= 2 and self.isGoalComplete(self.GOALS[1]):
            return

        # get mouse click coordinates
        x, y = event.pos().x(), event.pos().y()

        if goals_number == 0:
            self.GOALS.append({"x1": x, "y1": y})
            cv2.circle(self.frame, (x, y), 1, (0, 0, 255), -1)

        elif goals_number == 1 and not self.isGoalComplete(self.GOALS[0]):
            self.GOALS[0]["x2"] = x
            self.GOALS[0]["y2"] = y
            goal_point1 = (self.GOALS[0]["x1"], self.GOALS[0]["y1"])
            goal_point2 = (self.GOALS[0]["x2"], self.GOALS[0]["y2"])
            cv2.line(self.frame, goal_point1, goal_point2, (0, 0, 255), 1)

        elif goals_number == 1:
            self.GOALS.append({"x1": x, "y1": y})
            cv2.circle(self.frame, (x, y), 1, (0, 0, 255), -1)

        elif goals_number == 2:
            self.GOALS[1]["x2"] = x
            self.GOALS[1]["y2"] = y
            goal_point1 = (self.GOALS[1]["x1"], self.GOALS[1]["y1"])
            goal_point2 = (self.GOALS[1]["x2"], self.GOALS[1]["y2"])
            cv2.line(self.frame, goal_point1, goal_point2, (0, 0, 255), 1)

        self.update_field_image()

    def isGoalComplete(self, goal):
        return ("x1" in goal) and ("y1" in goal) and ("x2" in goal) and ("y2" in goal)

    def show_main_window_page(self):
        self.heading.hide()
        self.buttonBack.hide()

        self.setCentralWidget(MainPage())

        