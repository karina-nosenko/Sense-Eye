import sys
from PyQt5.QtCore import QUrl
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton
from PyQt5.QtWebEngineWidgets import QWebEngineView
import subprocess
import os
import signal
class MyWindow(QWidget):
    def __init__(self):
        super().__init__()
        
        self.setWindowTitle('My Desktop Application')
        self.setGeometry(100, 100, 800, 600)
        
        # create the web view widget
        self.webview = QWebEngineView(self)
        self.webview.setGeometry(0, 0, 800, 600)
        
        # load the HTML file
        self.webview.load(QUrl.fromLocalFile('C:\Sense-Eye\desktop\camera.html'))
        
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
        
    def start_process(self):
        # execute "python main.py" command
        self.process1 = subprocess.Popen(['python','main.py'],cwd='../',shell=True)
        self.process2 = subprocess.Popen(['npm','run','dev'],cwd='../RecommendationsUnit/', shell=True)
        print(self.process3)
        self.process3 = subprocess.Popen(['python','main.py'],cwd='../ImageProcessingUnit/',shell=True)
    
    def end_process(self):
        print("1-->", self.process1, "2-->" , self.process2,"3-->",self.process3)
        # terminate all subprocesses
        if self.process1:
            self.process1.terminate()
            pid1 = self.process1.pid
            # subprocess.Popen("taskkill /F /T /PID %i"%pid1 , shell=True)
            # os.kill(pid1, signal.SIGTERM)
        if self.process2:
            self.process2.terminate()
        if self.process3:
            self.process3.terminate()
        self.process1 = None
        self.process2 = None
        self.process3 = None
        print("All subprocesses terminated.")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MyWindow()
    window.show()
    sys.exit(app.exec_())
