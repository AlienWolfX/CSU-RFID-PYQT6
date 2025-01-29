from PyQt6.QtSql import QSqlDatabase, QSqlQuery, QSqlError
from PyQt6.QtCore import QObject
import os
from dotenv import load_dotenv
load_dotenv()

class Database(QObject):
    def __init__(self):
        super().__init__()
        # Switch from QMYSQL to QPSQL
        self.db = QSqlDatabase.addDatabase('QPSQL')
        self.db.setHostName(os.getenv("DB_HOST"))
        self.db.setDatabaseName(os.getenv("DB_NAME"))
        self.db.setUserName(os.getenv("DB_USERNAME"))
        self.db.setPassword(os.getenv("DB_PASSWORD"))
        
        if not self.db.open():
            print(f"Database Error: {self.db.lastError().text()}")
            return
        
        self.setup_tables()

    def setup_tables(self):
        query = QSqlQuery()
        
        # Create admin_users table
        # Use SERIAL for auto-increment in PostgreSQL if needed
        query.exec('''
            CREATE TABLE IF NOT EXISTS admin_users (
                username VARCHAR(50) PRIMARY KEY,
                password VARCHAR(100) NOT NULL
            )
        ''')
        
        # Create users table
        query.exec('''
            CREATE TABLE IF NOT EXISTS users (
                rfid_tag VARCHAR(50) PRIMARY KEY,
                name VARCHAR(100) NOT NULL,
                plate VARCHAR(50) NOT NULL,
                photo_path VARCHAR(255)
            )
        ''')
        
        # Create logs table
        query.exec('''
            CREATE TABLE IF NOT EXISTS logs (
                id SERIAL PRIMARY KEY,
                rfid_tag VARCHAR(50),
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (rfid_tag) REFERENCES users(rfid_tag)
            )
        ''')

    def verify_login(self, username, password):
        query = QSqlQuery()
        query.prepare('''
            SELECT username FROM admin_users 
            WHERE username = ? AND password = ?
        ''')
        query.addBindValue(username)
        query.addBindValue(password)
        query.exec()
        return query.next()

    def get_user(self, rfid_tag):
        query = QSqlQuery()
        query.prepare('''
            SELECT name, plate, photo_path 
            FROM users 
            WHERE rfid_tag = ?
        ''')
        query.addBindValue(rfid_tag)
        if query.exec() and query.next():
            return (query.value(0), query.value(1), query.value(2))
        return None

    def log_entry(self, rfid_tag):
        query = QSqlQuery()
        query.prepare('INSERT INTO logs (rfid_tag) VALUES (?)')
        query.addBindValue(rfid_tag)
        return query.exec()

    def close(self):
        self.db.close()