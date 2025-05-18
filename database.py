import sqlite3
import hashlib

class Database:
    def __init__(self, db_name="chat_history.db"):
        self.conn = sqlite3.connect(db_name)
        self.create_tables()

    def create_tables(self):
        # Tạo bảng users và chat_history
        cursor = self.conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                username TEXT PRIMARY KEY,
                password_hash TEXT NOT NULL
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS chat_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT,
                message TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        self.conn.commit()

    def register_user(self, username, password):
        cursor = self.conn.cursor()
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        try:
            cursor.execute("INSERT INTO users (username, password_hash) VALUES (?, ?)", 
                           (username, password_hash))
            self.conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False

    def login_user(self, username, password):
        cursor = self.conn.cursor()
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        cursor.execute("SELECT * FROM users WHERE username = ? AND password_hash = ?", 
                       (username, password_hash))
        return cursor.fetchone() is not None

    def save_message(self, username, message):
        cursor = self.conn.cursor()
        cursor.execute("INSERT INTO chat_history (username, message) VALUES (?, ?)", 
                       (username, message))
        self.conn.commit()

    def get_chat_history(self, username):
        cursor = self.conn.cursor()
        cursor.execute("SELECT username, message, timestamp FROM chat_history WHERE username = ?", 
                       (username,))
        return cursor.fetchall()

    def close(self):
        self.conn.close()