import sqlite3
import bcrypt
from PyQt5.QtWidgets import QMessageBox

class Auth:
    def __init__(self, db_name='project_management.db'):
        self.conn = sqlite3.connect(db_name)
        self.cursor = self.conn.cursor()
        self.create_users_table()

    def create_users_table(self):
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
        ''')
        self.conn.commit()

    def register(self, username, password):
        try:
            hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
            self.cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)",
                                (username, hashed))
            self.conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False

    def login(self, username, password):
        self.cursor.execute("SELECT * FROM users WHERE username=?", (username,))
        user = self.cursor.fetchone()
        if user and bcrypt.checkpw(password.encode('utf-8'), user[2]):
            return user[0]  # Return user ID
        return None

    def close(self):
        self.conn.close()