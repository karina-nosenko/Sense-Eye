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

from videoWindow import *
from styles import *
from desktop import start_sending_materials_process, start_creating_frames_process

from dotenv import load_dotenv
import os

# Load the .env file
load_dotenv()

# Access the environment variables
DB_HOST = os.getenv('DB_HOST')


inputStyle = """
    QLineEdit {
        background-color: #f2f2f2;
        border: none;
        border-radius: 10px;
        font-size: 16px;
        padding: 10px;
    }
"""

# == Login Page ==#
class LoginPage(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('SenseEye Login')

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

    # def login(self):
    #     # Get the organization name and password entered by the user
    #     org_name = self.organizationInput.text()
    #     password = self.passwordInput.text()

    #     # Check if the organization name and password are correct
    #     if org_name == "shenkar" and password == "1234567890":
    #         # Connect the user to the main window
    #         self.main_window = MainPage()
    #         self.main_window.show()
    #         # self.main_window.initUI()
    #         self.close()
    #     else:
    #         # Display an error message
    #         QMessageBox.warning(self, "Error", "Invalid organization name or password.")

    def login(self):
        # get organization name and password from inputs
        org_name = self.organizationInput.text()
        password = self.passwordInput.text()

        # connect to MongoDB
        client = MongoClient(DB_HOST)
        db = client["sense-eye"]
        org_collection = db["organizations"]

        # query the organization collection for the given organization name and password
        query = {"name": org_name, "password": password}
        result = org_collection.find_one(query)

        # close the MongoDB connection
        client.close()

        # if result is not None, the organization name and password are valid
        if result is not None:
            # connect to main window or do something else
            print("Valid organization name and password")
            # Connect the user to the main window
            self.main_window = MainPage()
            self.main_window.show()
            # self.main_window.initUI()
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
    # def __init__(self):
    #     super().__init__()
    #     # create login page and set as central widget
    #     loginPage = LoginPage()
    #     self.setCentralWidget(loginPage)    

    def initUI(self):        
        self.setWindowTitle('SenseEye Desktop Application')

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
        layout.addWidget(self.buttonStart)
        layout.addSpacing(20)
        layout.addWidget(self.statusLabel)
        layout.addSpacing(20)
        layout.addWidget(self.buttonEnd)
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

        
    def start_process(self):
        self.buttonStart.hide()
        self.statusLabel.show()
        self.buttonEnd.show()

        # release ports
        # os.system("fuser -k 5000/tcp")
        # os.system("fuser -k 8080/tcp")
        subprocess.run("fuser -k 5000/tcp", shell=True)
        subprocess.run("fuser -k 8080/tcp", shell=True)
        # give the user 10 seconds to connect the components
        self.statusLabel.setText('Attempting to connect to the components...')
        QApplication.processEvents()
        self.process1 = subprocess.Popen(['python3','main.py'],cwd='../', shell=True) 
        # time.sleep(10)
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
            # time.sleep(10)
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
            # time.sleep(10)
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

        start_creating_frames_process()

        start_sending_materials_process()


    def show_history_page(self):
        self.heading.hide()
        self.buttonStart.hide()
        self.buttonEnd.hide()
        self.buttonHistory.hide()
        self.statusLabel.hide()

        self.setCentralWidget(HistoryPage())


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
        for filename in sorted(os.listdir(video_folder)):
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