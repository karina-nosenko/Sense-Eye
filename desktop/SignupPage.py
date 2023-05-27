from PyQt5.QtCore import Qt, QRect
from PyQt5.QtGui import QCursor, QPixmap
from PyQt5.QtWidgets import QMainWindow, QVBoxLayout, QLabel, QLineEdit, QPushButton, QWidget, QApplication
from PyQt5 import QtCore
from mainWindow import LoginPage
import pymongo

from pymongo import MongoClient
from styles import labelStyle, inputStyle, buttonStyle
# MongoDB connection string
connection_string = "mongodb+srv://yosef:sense111@cluster0.bmxfx.mongodb.net/sense-eye"
# MongoDB database name
db_name = "sense-eye"
# MongoDB collection name
collection_name = "organizations"
class SignupPage(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('SenseEye Signup')
        self.setStyleSheet("background-color: #f7f7f7;")

        # get screen size
        screen_size = QApplication.primaryScreen().availableGeometry()

        # set the geometry of the window
        window_width = int(screen_size.width() * 0.3)
        window_height = int(screen_size.height() * 0.3)
        window_x = int((screen_size.width() - window_width) / 2)
        window_y = int((screen_size.height() - window_height) / 2)
        self.setGeometry(window_x, window_y, window_width, window_height)

        # create a logo label
        self.logoLabel = QLabel(self)
        self.logoLabel.setGeometry(QRect(0, 0, window_width, window_height * 0.2))
        self.logoLabel.setPixmap(QPixmap("logo.jfif"))
        self.logoLabel.setScaledContents(True)

        # create organization name input
        self.organizationLabel = QLabel(self)
        self.organizationLabel.setText('Organization Name:')
        self.organizationLabel.setStyleSheet(labelStyle)
        self.organizationLabel.setAlignment(Qt.AlignVCenter)

        self.organizationInput = QLineEdit(self)
        self.organizationInput.setStyleSheet(inputStyle + "background-color: white;")
        self.organizationInput.setFixedWidth(window_width * 0.3)
        self.organizationInput.setFixedHeight(window_height * 0.15)
        self.organizationInput.setAlignment(Qt.AlignVCenter)

        # create password input
        self.passwordLabel = QLabel(self)
        self.passwordLabel.setText('Password:')
        self.passwordLabel.setStyleSheet(labelStyle)
        self.passwordLabel.setAlignment(Qt.AlignVCenter)

        self.passwordInput = QLineEdit(self)
        self.passwordInput.setStyleSheet(inputStyle + "background-color: white;")
        self.passwordInput.setFixedWidth(window_width * 0.3)
        self.passwordInput.setFixedHeight(window_height * 0.15)
        self.passwordInput.setEchoMode(QLineEdit.Password)
        self.passwordInput.setAlignment(Qt.AlignVCenter)

        # create a "signup" button
        self.buttonSignup = QPushButton('Signup', self)
        self.buttonSignup.clicked.connect(self.signup)
        self.buttonSignup.setFixedWidth(window_width * 0.3)
        self.buttonSignup.setFixedHeight(window_height * 0.15)
        self.buttonSignup.setCursor(QCursor(QtCore.Qt.PointingHandCursor))
        self.buttonSignup.setStyleSheet(buttonStyle)

        # create a vertical layout and add the widgets to it
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.logoLabel)
        layout.addStretch()
        layout.addWidget(self.organizationLabel)
        layout.addWidget(self.organizationInput)
        layout.addWidget(self.passwordLabel)
        layout.addWidget(self.passwordInput)
        layout.addWidget(self.buttonSignup)
        layout.addStretch()

        # create a central widget and set the layout on it
        central_widget = QWidget()
        central_widget.setLayout(layout)

        # set the central widget on the main window
        self.setCentralWidget(central_widget)

    def signup(self):
        # Get organization name and password from inputs
        org_name = self.organizationInput.text()
        password = self.passwordInput.text()

        # Create a dictionary with the data to be inserted
        organization = {"name": org_name, "password": password}

        try:
            # Connect to the MongoDB database
            client = MongoClient(connection_string)
            db = client[db_name]
            collection = db[collection_name]

            # Insert the organization data into the collection
            collection.insert_one(organization)

            # Perform any additional signup functionality

            self.main_window = LoginPage()
            self.main_window.show()
            self.close()

        except pymongo.errors.ConnectionFailure:
            print("Could not connect to MongoDB.")

        except pymongo.errors.ConnectionFailure:
            print("Could not connect to MongoDB.")
if __name__ == '__main__':
    app = QApplication([])
    signup_page = SignupPage()
    signup_page.show()
    app.exec_()
