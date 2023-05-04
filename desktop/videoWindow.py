from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
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
        
        # create the video widget
        self.video_widget = QVideoWidget(self)
        self.setCentralWidget(self.video_widget)

        # create the media player
        self.media_player = QMediaPlayer(self)
        self.media_player.setVideoOutput(self.video_widget)

        # create the play/pause button
        self.play_button = QPushButton(self)
        self.play_button.setIcon(QIcon('icons/pause.png'))
        self.play_button.setFixedSize(30, 30)
        self.play_button.clicked.connect(self.play_pause)

        # create the slider to display the video timeline
        self.timeline_slider = QSlider(Qt.Horizontal, self)
        self.timeline_slider.setRange(0, 0)
        self.timeline_slider.sliderMoved.connect(self.set_position)
        self.media_player.durationChanged.connect(self.set_duration)

        # create the label to display the current time
        self.time_label = QLabel(self)
        self.time_label.setText("00:00")

        # create a horizontal layout for the controls
        control_layout = QHBoxLayout()
        control_layout.addWidget(self.play_button)
        control_layout.addWidget(self.timeline_slider)
        control_layout.addWidget(self.time_label)

        # create a widget to hold the controls
        control_widget = QWidget(self)
        control_widget.setLayout(control_layout)

        # add the controls to the bottom of the main window
        self.setCentralWidget(self.video_widget)
        self.setStatusBar(None)

        # create a toolbar and add the control widget to it
        toolbar = QToolBar(self)
        toolbar.addWidget(control_widget)

        # add the toolbar to the bottom of the main window
        self.addToolBar(Qt.BottomToolBarArea, toolbar)

        # load the video file
        self.media_player.setMedia(QMediaContent(QUrl.fromLocalFile(os.path.abspath(video_path))))

        # start playing the video
        self.media_player.play()

        # connect signals to slots
        self.media_player.durationChanged.connect(self.set_duration)
        self.media_player.positionChanged.connect(self.update_position)

        # set the window to be shown
        self.show()

    def set_duration(self, duration):
        # update the slider range and time label when the duration changes
        self.timeline_slider.setRange(0, duration)
        self.time_label.setText(self.format_time(0) + '/' + self.format_time(duration))

    def set_position(self, position):
        # set the position of the media player to the position of the slider
        self.media_player.setPosition(position)

    def update_position(self, position):
        # update the slider position and time label when the position changes
        self.timeline_slider.setValue(position)
        self.time_label.setText(self.format_time(position) + '/' + self.format_time(self.media_player.duration()))

    def format_time(self, time):
        # format the time as mm:ss
        minutes = int(time / 60000)
        seconds = int((time - minutes * 60000) / 1000)
        return '{:02d}:{:02d}'.format(minutes, seconds)

    def play_pause(self):
        if self.media_player.state() == QMediaPlayer.PlayingState:
            self.media_player.pause()
            self.play_button.setIcon(QIcon('icons/play.png'))
        else:
            self.media_player.play()
            self.play_button.setIcon(QIcon('icons/pause.png'))

    def closeEvent(self, event):
        event.ignore()
        self.hide()

