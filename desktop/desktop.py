import sys
from PyQt5 import QtCore
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtWebEngineWidgets import *
from PyQt5.QtGui import *
from multiprocessing import Process

from mainWindow import *


def is_internet_connection():
    ping_process = subprocess.run(['ping', '-c', '1', 'google.com'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    if '1 received' in ping_process.stdout.decode():
        return True
    else:
        return False
    
def syncronize():
    while True:
        if is_internet_connection():
            # TODO: send all contents of /materials to the DB
            print('Ping to Google successful!')
        else:
            print('No ping response from Google.')
        time.sleep(10) # wait for 10 seconds before checking again

if __name__ == '__main__':
    # Keep sending materials to the internet each time there's an internet connection
    # in a separate process
    p = Process(target=syncronize)
    p.daemon = True
    p.start()

    # Start the application
    app = QApplication(sys.argv)
    window = MainPage()
    window.show()
    sys.exit(app.exec_())
