import sys
from PyQt5 import QtCore
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtWebEngineWidgets import *
from PyQt5.QtGui import *

import subprocess
import os
import signal
import psutil

# CSS styles
buttonStyle = '''padding: 10px;
			font-size: 18px;
			border: none;
			background-color: #333;
			color: #fff;
			border-radius: 4px;'''

headingStyle = '''font-size: 50px;
			font-weight: bold;
            font-family: sans-serif;
			color: #000;'''


class VideoWindow(QMainWindow):
    def __init__(self, video_path):
        super().__init__()
        self.setWindowTitle("Video Viewer")
        self.setGeometry(100, 100, 800, 600)

        # create the web view widget
        self.webview = QWebEngineView(self)
        self.webview.setGeometry(0, 0, 800, 600)

        # load the video file
        self.webview.load(QUrl.fromLocalFile(os.path.abspath(video_path)))


    def closeEvent(self, event):
        event.ignore()
        self.hide()


class HistoryPage(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self): 
        self.videoButtons = []

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
        for filename in os.listdir(video_folder):
            if filename.endswith(".ogv"):
                video_path = os.path.join(video_folder, filename)
                button = QPushButton(filename, self) 
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

        self.setCentralWidget(MainWindow())



class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):        
        self.setWindowTitle('SenseEye Desktop Application')

        # calculate the width and height of the window in percentages
        width_percent = 80
        height_percent = 80
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

        # create a "end" button
        self.buttonEnd = QPushButton('End', self)
        self.buttonEnd.clicked.connect(self.end_process)
        self.buttonEnd.setFixedSize(200, 50)
        self.buttonEnd.setCursor(QCursor(QtCore.Qt.PointingHandCursor))
        self.buttonEnd.setStyleSheet(buttonStyle)

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

    
    def show_history_page(self):
        self.heading.hide()
        self.buttonStart.hide()
        self.buttonEnd.hide()
        self.buttonHistory.hide()

        self.setCentralWidget(HistoryPage())

        
    def start_process(self):
        self.process1 = subprocess.Popen(['sudo', 'python3','main.py'],cwd='../')
        self.process2 = subprocess.Popen(['npm','run','dev'],cwd='../RecommendationsUnit/')
        self.process3 = subprocess.Popen(['sudo', 'python3','main.py'],cwd='../ImageProcessingUnit/')


    def end_process(self):
        print("1-->", self.process1, "2-->" , self.process2,"3-->",self.process3)

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
                thread_obj = psutil._psplatform.Thread(thread.id, process.pid)
                thread_obj.terminate()

            # Finally, terminate the main process
            process.terminate()

        self.process1 = None
        self.process2 = None
        self.process3 = None

        print("All subprocesses terminated.")


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
