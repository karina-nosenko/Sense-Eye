from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtWebEngineWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtMultimedia import QMediaContent, QMediaPlayer
from PyQt5.QtMultimediaWidgets import QVideoWidget
import os


class VideoWindow(QMainWindow):
    def __init__(self, video_path):
        super().__init__()
        self.initUI(video_path)

    def initUI(self, video_path):
        self.setWindowTitle("Video Viewer")

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

        # load the video file
        self.webview.load(QUrl.fromLocalFile(os.path.abspath(video_path)))


    def closeEvent(self, event):
        event.ignore()
        self.hide()