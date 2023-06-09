from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton
import sqlite3

connection = sqlite3.connect('session_data.db')
cursor = connection.cursor()
cursor.execute('''CREATE TABLE IF NOT EXISTS session (key TEXT PRIMARY KEY, value TEXT)''')
connection.commit()

def save_session_data(key, value):
    cursor.execute('''INSERT OR REPLACE INTO session (key, value) VALUES (?, ?)''', (key, value))
    connection.commit()

def get_session_data(key):
    cursor.execute('''SELECT value FROM session WHERE key=?''', (key,))
    result = cursor.fetchone()
    return result[0] if result else None
