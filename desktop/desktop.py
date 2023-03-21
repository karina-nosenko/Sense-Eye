import sys
from PyQt5.QtCore import QUrl
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton
from PyQt5.QtWebEngineWidgets import QWebEngineView
import subprocess
import os
import signal
import psutil


class MyWindow(QWidget):
    def __init__(self):
        super().__init__()
        
        self.setWindowTitle('My Desktop Application')
        self.setGeometry(100, 100, 800, 600)
        
        # create the web view widget
        self.webview = QWebEngineView(self)
        self.webview.setGeometry(0, 0, 800, 600)
        
        # load the HTML file
        self.webview.load(QUrl.fromLocalFile('/home/karina/FinalProject/SenseEye/desktop/camera.html'))
        
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
        self.process1 = subprocess.Popen(['sudo', 'python3','main.py'],cwd='../')
        self.process2 = subprocess.Popen(['npm','run','dev'],cwd='../RecommendationsUnit/')
        print(self.process3)
        self.process3 = subprocess.Popen(['sudo', 'python3','main.py'],cwd='../ImageProcessingUnit/')
    
    def end_process(self):
        print("1-->", self.process1, "2-->" , self.process2,"3-->",self.process3)
        # terminate all subprocesses
        if self.process1:
            # self.process1.terminate()
            # pid1 = self.process1.pid

            # os.kill(self.process1.pid, signal.SIGTERM)

            os.kill(self.process1.pid, signal.SIGKILL)
            self.process1.wait()  # Wait for the process to exit
            self.process1 = None 

            # subprocess.Popen("taskkill /F /T /PID %i"%pid1 , shell=True)
            # os.kill(pid1, signal.SIGTERM)
        if self.process2:
            # os.kill(self.process2.pid, signal.SIGTERM) 

            os.kill(self.process2.pid, signal.SIGKILL)
            self.process2.wait()  # Wait for the process to exit
            self.process2 = None 
            # self.process2.terminate()
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
    window = MyWindow()
    window.show()
    sys.exit(app.exec_())
