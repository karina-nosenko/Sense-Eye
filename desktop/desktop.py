import sys
from PyQt5.QtCore import QUrl
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton
from PyQt5.QtWebEngineWidgets import QWebEngineView

from PyQt5 import QtGui
from PyQt5.QtWidgets import (QMainWindow, QToolTip, QMessageBox, QLabel, QVBoxLayout)

import subprocess
import os
import signal
import psutil


class VideoWindow(QMainWindow):
    def __init__(self, main_window, video_path):
        super().__init__()
        self.main_window = main_window
        self.setWindowTitle("Video Viewer")
        self.setGeometry(main_window.geometry())
        self.video_path = video_path

        # create the web view widget
        self.webview = QWebEngineView(self)
        self.webview.setGeometry(0, 0, 800, 600)

        # load the video file
        self.webview.load(QUrl.fromLocalFile(os.path.abspath(self.video_path)))


    def closeEvent(self, event):
        event.ignore()
        self.hide()

# class VideoWindow(QWidget):
#     def __init__(self, main_vindow):
#         super().__init__()
#         self.main_window = main_window
#         self.setWindowTitle("Video Viewer")
#         self.setGeometry(main_window.geometry())
#         self.video_path = video_path

        # # create the web view widget
        # self.webview = QWebEngineView(self)
        # self.webview.setGeometry(0, 0, 800, 600)

        # # load the video file
        # self.webview.load(QUrl.fromLocalFile(self.video_path))


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        
        self.setWindowTitle('SenseEye Desktop Application')
        self.setGeometry(100, 100, 800, 600)
        
        # create the web view widget
        self.webview = QWebEngineView(self)
        self.webview.setGeometry(0, 0, 800, 600)
        
        # load the HTML file
        self.webview.load(QUrl.fromLocalFile(os.path.abspath('camera.html')))
        
        # create a vertical layout for the buttons
        self.layout = QVBoxLayout()

        # add a button for each video file in the output_videos folder
        # video_folder = "../output_videos"
        # for filename in os.listdir(video_folder):
        #     if filename.endswith(".ogv"):
        #         video_path = os.path.join(video_folder, self)
        #         button = self.QPushButton(filename, self)
        #         button.clicked.connect(self.open_video_window(video_path))
        #         self.layout.addWidget(button)

        # add a button for each video file in the output_videos folder
        video_folder = "../output_videos"
        for filename in os.listdir(video_folder):
            if filename.endswith(".ogv"):
                video_path = os.path.join(video_folder, filename)
                button = QPushButton(filename, self)
                button.clicked.connect(lambda checked, path=video_path: self.open_video_window(path))
                self.layout.addWidget(button)

        # self.pushButton = QPushButton("window", self)
        # self.pushButton.move(275, 200)
        # self.pushButton.setToolTip("<h3>Start the Session</h3>")
        # self.pushButton.clicked.connect(self.window2)

        self.setLayout(self.layout)

        # create a "start" button
        self.button = QPushButton('Start', self)
        self.button.move(300, 500)
        self.button.clicked.connect(self.start_process)

        # create a "end" button
        self.buttonEnd = QPushButton('End', self)
        self.buttonEnd.move(600, 500)
        self.buttonEnd.clicked.connect(self.end_process)

        # initialize subprocess variables to None
        self.process1 = None
        self.process2 = None
        self.process3 = None


    # def open_video_window(self, video_path):
    #     self.window = VideoWindow(self, video_path)
    #     self.window.show()

    def main_window(self):
        self.label = QLabel("Manager", self)
        self.label.move(285, 175)
        self.setWindowTitle(self.title)
        self.setGeometry(self.top, self.left, self.width, self.height)
        self.show()

    
    def open_video_window(self, video_path):
        self.w = VideoWindow(self, video_path)
        self.w.show()

        
    def start_process(self):
        # execute "python main.py" command
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
