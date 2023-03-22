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


class HistoryPage(QWidget):
    def __init__(self):
        super().__init__()

        # create a vertical layout for the buttons
        self.layout = QVBoxLayout()

        # add a button for each video file in the output_videos folder
        video_folder = "../output_videos"
        for filename in os.listdir(video_folder):
            if filename.endswith(".ogv"):
                video_path = os.path.join(video_folder, filename)
                button = QPushButton(filename, self)
                button.clicked.connect(lambda checked, path=video_path: self.open_video_window(path))
                self.layout.addWidget(button)

        self.setLayout(self.layout)


    def open_video_window(self, video_path):
        self.w = VideoWindow(video_path)
        self.w.show()


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        
        self.setWindowTitle('SenseEye Desktop Application')
        self.setGeometry(100, 100, 800, 600)
        
        # create the web view widget
        self.webview = QWebEngineView(self)
        self.webview.setGeometry(0, 0, 800, 600)
        
        # load the HTML file
        # self.webview.load(QUrl.fromLocalFile(os.path.abspath('camera.html')))
        
        # create a "show history" button
        self.button = QPushButton('Show History', self)
        self.button.move(50, 500)
        self.button.clicked.connect(self.show_history_page)

        # create a "start" button
        self.button = QPushButton('Start', self)
        self.button.move(350, 500)
        self.button.clicked.connect(self.start_process)

        # create a "end" button
        self.buttonEnd = QPushButton('End', self)
        self.buttonEnd.move(650, 500)
        self.buttonEnd.clicked.connect(self.end_process)

        # initialize subprocess variables to None
        self.process1 = None
        self.process2 = None
        self.process3 = None

    
    def show_history_page(self):
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
