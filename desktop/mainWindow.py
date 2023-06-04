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
import datetime
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
        client = MongoClient(os.environ['DB_HOST'])
        db = client["sense-eye"]
        collection = db["organizations"]
        query = {"name": org_name, "password": password}
        result = collection.find_one(query)

        # close the MongoDB connection
        client.close()

        # if result is not None, the organization name and password are valid
        if result is not None:
            # connect to main window or do something else
            print("Valid organization name and password")
            # Connect the user to the main window
            self.main_window = MainPage()
            self.main_window.show()
            self.close()
        else:
            # display error message or do something else
            print("Invalid organization name or password")
            QMessageBox.warning(self, "Error", "Invalid organization name or password.")

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
        self.buttonStart.setStyleSheet(buttonGreenActionStyle)

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
        self.buttonEnd.setStyleSheet(buttonRedActionStyle)
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
        self.buttonBack.setCursor(QCursor(Qt.PointingHandCursor))
        self.buttonBack.setStyleSheet(buttonStyle)

        # create a date range input
        self.dateFromLabel = QLabel("From:", self)
        self.dateFromEdit = QDateEdit(self)
        self.dateFromEdit.setCalendarPopup(True)
        self.dateFromEdit.setDate(datetime.date.today())  # Set default date to today
        self.dateToLabel = QLabel("To:", self)
        self.dateToEdit = QDateEdit(self)
        self.dateToEdit.setCalendarPopup(True)
        self.dateToEdit.setDate(datetime.date.today())  # Set default date to today

        # create a filter button
        self.filterButton = QPushButton("Filter", self)
        self.filterButton.setStyleSheet(buttonStyle)
        self.filterButton.clicked.connect(self.filterVideos)

        # create a layout for the date range input and filter button
        filterLayout = QHBoxLayout()
        filterLayout.addWidget(self.dateFromLabel)
        filterLayout.addWidget(self.dateFromEdit,stretch=1)
        #TODO
        filterLayout.addWidget(self.dateToLabel)
        filterLayout.addWidget(self.dateToEdit,stretch=1)
        filterLayout.addWidget(self.filterButton,stretch=1)

        # create a vertical layout and add the widgets to it
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.heading)
        layout.addSpacing(40)
        layout.addLayout(filterLayout)
        layout.addSpacing(20)
        layout.addLayout(self.videosLayout)
        layout.addSpacing(40)
        layout.addWidget(self.buttonBack)

        # create a central widget and set the layout on it
        central_widget = QWidget()
        central_widget.setLayout(layout)
        
        # set the central widget on the main window
        self.setCentralWidget(central_widget)

    def filterVideos(self):
        # Get the selected date range
        dateFrom = self.dateFromEdit.date().toPyDate()
        dateTo = self.dateToEdit.date().toPyDate()

        # Clear the videos layout
        for i in reversed(range(self.videosLayout.count())): 
            self.videosLayout.itemAt(i).widget().setParent(None)

        # Filter and display videos within the selected date range
        video_folder = "../output_videos"
        videos_list = sorted(os.listdir(video_folder))
        for filename in videos_list:
            if filename.endswith(".ogv"):
                video_date_str = filename.split(".")[0]  # Extract the date portion from the filename
                video_date = datetime.datetime.strptime(video_date_str, "%Y-%m-%d %H_%M_%S").date()
                if dateFrom <= video_date <= dateTo:
                    video_path = os.path.join(video_folder, filename)
                    button = QPushButton(filename[:-4], self)
                    #TODO
                    button.setStyleSheet(buttonStyle)
                    button.clicked.connect(lambda checked, path=video_path: self.open_video_window(path))
                    button.setFixedSize(500, 50)
                    self.videosLayout.addWidget(button)

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
            self.FIELD_COORDINATES = data["field_coordinates"]
            self.SINGLE_ALERT_LINES = data["single_alert_lines"]
            self.DOUBLE_ALERT_LINES = data["double_alert_lines"]

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
        self.draw_single_alert_lines()
        self.draw_double_alert_lines()

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
        self.buttonFieldCorners.setStyleSheet(buttonCustomizeStyle)

        # create an "update gates" button
        self.buttonGatesCorners = QPushButton('Update Gates', self) 
        self.buttonGatesCorners.clicked.connect(self.update_goals)
        self.buttonGatesCorners.setFixedSize(200, 50)
        self.buttonGatesCorners.setCursor(QCursor(QtCore.Qt.PointingHandCursor))
        self.buttonGatesCorners.setStyleSheet(buttonCustomizeStyle)

        # create an "update single alert" button
        self.buttonSingleAlert = QPushButton('Update Single Alert', self) 
        self.buttonSingleAlert.clicked.connect(self.update_single_alert_lines)
        self.buttonSingleAlert.setFixedSize(200, 50)
        self.buttonSingleAlert.setCursor(QCursor(QtCore.Qt.PointingHandCursor))
        self.buttonSingleAlert.setStyleSheet(buttonCustomizeStyle)

        # create an "update double alert" button
        self.buttonDoubleAlert = QPushButton('Update Double Alert', self) 
        self.buttonDoubleAlert.clicked.connect(self.update_double_alert_lines)
        self.buttonDoubleAlert.setFixedSize(200, 50)
        self.buttonDoubleAlert.setCursor(QCursor(QtCore.Qt.PointingHandCursor))
        self.buttonDoubleAlert.setStyleSheet(buttonCustomizeStyle)

        # create a "save" button
        self.buttonSave = QPushButton('Save', self) 
        self.buttonSave.clicked.connect(self.save)
        self.buttonSave.setFixedSize(200, 50)
        self.buttonSave.setCursor(QCursor(QtCore.Qt.PointingHandCursor))
        self.buttonSave.setStyleSheet(buttonGreenActionStyle)

        # create a "back" button
        self.buttonBack = QPushButton('Back', self) 
        self.buttonBack.clicked.connect(self.show_main_window_page)
        self.buttonBack.setFixedSize(200, 50)
        self.buttonBack.setCursor(QCursor(QtCore.Qt.PointingHandCursor))
        self.buttonBack.setStyleSheet(buttonStyle)

        # create a horizontal layout and add customization buttons to it
        horizontal_layout = QHBoxLayout()
        horizontal_layout.setAlignment(Qt.AlignCenter)
        horizontal_layout.addWidget(self.buttonFieldCorners)
        horizontal_layout.addSpacing(10)
        horizontal_layout.addWidget(self.buttonGatesCorners)
        horizontal_layout.addSpacing(10)
        horizontal_layout.addWidget(self.buttonSingleAlert)
        horizontal_layout.addSpacing(10)
        horizontal_layout.addWidget(self.buttonDoubleAlert)

        # create a vertical layout and add the widgets to it
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.heading)
        layout.addSpacing(40)
        layout.addWidget(self.field_image)
        layout.addSpacing(40)
        layout.addLayout(horizontal_layout)
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
        for goal in self.GOALS:
            point1 = (goal['x1'], goal['y1'])
            point2 = (goal['x2'], goal['y2'])
            cv2.line(self.frame, point1, point2, (0, 0, 255), 1)

    def draw_single_alert_lines(self):
        for line in self.SINGLE_ALERT_LINES:
            point1 = (line["x1"], line["y1"])
            point2 = (line["x2"], line["y2"])
            self.draw_dashed_line(point1, point2, (0, 255, 0))

    def draw_double_alert_lines(self):
        for line in self.DOUBLE_ALERT_LINES:
            point1 = (line["x1"], line["y1"])
            point2 = (line["x2"], line["y2"])
            self.draw_dashed_line(point1, point2, (255, 255, 0))

    def draw_dashed_line(self, point1, point2, color, thickness=1, dash_length=5, gap_length=5):
        # Calculate the direction vector of the line
        dx = point2[0] - point1[0]
        dy = point2[1] - point1[1]
        line_length = max(abs(dx), abs(dy))
        dx = dx / line_length
        dy = dy / line_length
        
        # Draw the dashes
        distance = 0
        draw_dash = True
        while distance < line_length:
            if draw_dash:
                x1 = int(point1[0] + distance * dx)
                y1 = int(point1[1] + distance * dy)
                x2 = int(point1[0] + (distance + dash_length) * dx)
                y2 = int(point1[1] + (distance + dash_length) * dy)
                cv2.line(self.frame, (x1, y1), (x2, y2), color, thickness)
            distance += dash_length + gap_length
            draw_dash = not draw_dash

    def update_field(self):
        # clear the field corners
        self.FIELD_COORDINATES = []
        self.frame = cv2.imread(self.initial_field_path)
        self.draw_goals()
        self.draw_single_alert_lines()
        self.draw_double_alert_lines()
        self.unselect_buttons()
        self.buttonFieldCorners.setStyleSheet(buttonSelectedCustomizeStyle)
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
        self.draw_single_alert_lines()
        self.draw_double_alert_lines()
        self.unselect_buttons()
        self.buttonGatesCorners.setStyleSheet(buttonSelectedCustomizeStyle)
        self.update_field_image()

        # handle click events
        self.field_image.mousePressEvent = self.mouse_click_event_update_goals

    def mouse_click_event_update_goals(self, event):
        goals_number = len(self.GOALS)

        if len(self.GOALS) >= 2 and self.isLineComplete(self.GOALS[1]):
            return

        # get mouse click coordinates
        x, y = event.pos().x(), event.pos().y()

        if goals_number == 0:
            self.GOALS.append({"x1": x, "y1": y})
            cv2.circle(self.frame, (x, y), 2, (0, 0, 255), -1)

        elif goals_number == 1 and not self.isLineComplete(self.GOALS[0]):
            self.GOALS[0]["x2"] = x
            self.GOALS[0]["y2"] = y
            goal_point1 = (self.GOALS[0]["x1"], self.GOALS[0]["y1"])
            goal_point2 = (self.GOALS[0]["x2"], self.GOALS[0]["y2"])
            cv2.line(self.frame, goal_point1, goal_point2, (0, 0, 255), 2)

        elif goals_number == 1:
            self.GOALS.append({"x1": x, "y1": y})
            cv2.circle(self.frame, (x, y), 2, (0, 0, 255), -1)

        elif goals_number == 2:
            self.GOALS[1]["x2"] = x
            self.GOALS[1]["y2"] = y
            goal_point1 = (self.GOALS[1]["x1"], self.GOALS[1]["y1"])
            goal_point2 = (self.GOALS[1]["x2"], self.GOALS[1]["y2"])
            cv2.line(self.frame, goal_point1, goal_point2, (0, 0, 255), 2)

        self.update_field_image()

    def update_single_alert_lines(self):
        # clear single alert lines
        self.SINGLE_ALERT_LINES = []
        self.frame = cv2.imread(self.initial_field_path)
        self.draw_field_corners()
        self.draw_goals()
        self.draw_double_alert_lines()
        self.unselect_buttons()
        self.buttonSingleAlert.setStyleSheet(buttonSelectedCustomizeStyle)
        self.update_field_image()

        # handle click events
        self.field_image.mousePressEvent = self.mouse_click_event_update_single_alert_lines

    def mouse_click_event_update_single_alert_lines(self, event):
        # get mouse click coordinates
        x, y = event.pos().x(), event.pos().y()

        if self.SINGLE_ALERT_LINES:
            last_alert_line = self.SINGLE_ALERT_LINES[-1]

            if not self.isLineComplete(last_alert_line):
                self.SINGLE_ALERT_LINES[-1]["x2"] = x
                self.SINGLE_ALERT_LINES[-1]["y2"] = y
                point1 = (self.SINGLE_ALERT_LINES[-1]["x1"], self.SINGLE_ALERT_LINES[-1]["y1"])
                point2 = (self.SINGLE_ALERT_LINES[-1]["x2"], self.SINGLE_ALERT_LINES[-1]["y2"])
                self.draw_dashed_line(point1, point2, (0, 255, 0))
                self.update_field_image()
                return
            
        self.SINGLE_ALERT_LINES.append({"x1": x, "y1": y})
        cv2.circle(self.frame, (x, y), 1, (0, 255, 0), -1)
        self.update_field_image()

    def update_double_alert_lines(self):
        # clear double alert lines
        self.DOUBLE_ALERT_LINES = []
        self.frame = cv2.imread(self.initial_field_path)
        self.draw_field_corners()
        self.draw_goals()
        self.draw_single_alert_lines()
        self.unselect_buttons()
        self.buttonDoubleAlert.setStyleSheet(buttonSelectedCustomizeStyle)
        self.update_field_image()

        # handle click events
        self.field_image.mousePressEvent = self.mouse_click_event_update_double_alert_lines

    def mouse_click_event_update_double_alert_lines(self, event):
        # get mouse click coordinates
        x, y = event.pos().x(), event.pos().y()

        if self.DOUBLE_ALERT_LINES:
            last_alert_line = self.DOUBLE_ALERT_LINES[-1]

            if not self.isLineComplete(last_alert_line):
                self.DOUBLE_ALERT_LINES[-1]["x2"] = x
                self.DOUBLE_ALERT_LINES[-1]["y2"] = y
                point1 = (self.DOUBLE_ALERT_LINES[-1]["x1"], self.DOUBLE_ALERT_LINES[-1]["y1"])
                point2 = (self.DOUBLE_ALERT_LINES[-1]["x2"], self.DOUBLE_ALERT_LINES[-1]["y2"])
                self.draw_dashed_line(point1, point2, (255, 255, 0))
                self.update_field_image()
                return
            
        self.DOUBLE_ALERT_LINES.append({"x1": x, "y1": y})
        cv2.circle(self.frame, (x, y), 1, (255, 255, 0), -1)
        self.update_field_image()

    def isLineComplete(self, line):
        return ("x1" in line) and ("y1" in line) and ("x2" in line) and ("y2" in line)
    
    def save(self):
        self.unselect_buttons()
        self.update_field_image()

        # load the configs file
        with open('../configs.json') as json_file:
            data = json.load(json_file)
        
        # update the values in the data object
        data["goals"] = self.GOALS
        data["field_coordinates"] = self.FIELD_COORDINATES
        data["single_alert_lines"] = self.SINGLE_ALERT_LINES
        data["double_alert_lines"] = self.DOUBLE_ALERT_LINES

        # write the updated data back to the configs file
        with open('../configs.json', 'w') as json_file:
            json.dump(data, json_file, indent=4)

        # Show an alert dialog
        message_box = QMessageBox()
        message_box.setIconPixmap(QIcon("icons/success.png").pixmap(64, 64))
        message_box.setStyleSheet(alertStyle)
        message_box.setText("The new coordinates saved successfully!")
        message_box.setWindowTitle("Success")
        message_box.setStandardButtons(QMessageBox.Ok)
        message_box.exec_()

    def unselect_buttons(self):
        self.buttonFieldCorners.setStyleSheet(buttonCustomizeStyle)
        self.buttonGatesCorners.setStyleSheet(buttonCustomizeStyle)
        self.buttonSingleAlert.setStyleSheet(buttonCustomizeStyle)
        self.buttonDoubleAlert.setStyleSheet(buttonCustomizeStyle)

    def show_main_window_page(self):
        self.heading.hide()
        self.buttonBack.hide()

        self.cleanup()

        self.setCentralWidget(MainPage())

    def cleanup(self):
        if os.path.exists(self.field_path):
            os.remove(self.field_path)

        if os.path.exists(self.initial_field_path):
            os.remove(self.initial_field_path)