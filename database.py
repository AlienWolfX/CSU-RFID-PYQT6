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
        print("Database connected successfully.")

    def verify_login(self, username, password):
        query = QSqlQuery()
        query.prepare('''
            SELECT username FROM users
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

    def get_user_id(self, username):
        query = QSqlQuery()
        query.prepare('''
            SELECT user_id FROM users WHERE username = ?
        ''')
        query.addBindValue(username)
        if query.exec() and query.next():
            return query.value(0)
        return None

    def get_user_role(self, user_id):
        query = QSqlQuery()
        query.prepare('''
            SELECT role_id FROM users WHERE role_id = ?
        ''')
        query.addBindValue(user_id)
        if query.exec() and query.next():
            return query.value(0)
        return None

    def log_entry(self, rfid_tag):
        query = QSqlQuery()
        query.prepare('INSERT INTO logs (rfid_tag) VALUES (?)')
        query.addBindValue(rfid_tag)
        return query.exec()

    def log_login_attempt(self, user_id, success):
        query = QSqlQuery()
        query.prepare('''
            INSERT INTO login_log (user_id, success) VALUES (?, ?)
        ''')
        query.addBindValue(user_id)
        query.addBindValue(success)
        return query.exec()

    def add_driver(self, driver_code, first_name, last_name, driver_type, driver_photo, cr_expiry_date, or_expiry_date, driver_license_no):
        query = QSqlQuery()
        query.prepare('''
            INSERT INTO drivers (driver_code, first_name, last_name, driver_type, driver_photo, cr_expiry_date, or_expiry_date, driver_license_no)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''')
        query.addBindValue(driver_code)
        query.addBindValue(first_name)
        query.addBindValue(last_name)
        query.addBindValue(driver_type)
        query.addBindValue(driver_photo)
        query.addBindValue(cr_expiry_date)
        query.addBindValue(or_expiry_date)
        query.addBindValue(driver_license_no)
        return query.exec()

    def get_driver(self, driver_id):
        query = QSqlQuery()
        query.prepare('''
            SELECT * FROM drivers WHERE driver_id = ?
        ''')
        query.addBindValue(driver_id)
        if query.exec() and query.next():
            return {
                'driver_id': query.value(0),
                'driver_code': query.value(1),
                'first_name': query.value(2),
                'last_name': query.value(3),
                'driver_type': query.value(4),
                'driver_photo': query.value(5),
                'cr_expiry_date': query.value(6),
                'or_expiry_date': query.value(7),
                'driver_license_no': query.value(8)
            }
        return None

    def add_vehicle(self, plate_id, plate_number, model, proprietor_id, driver_id):
        query = QSqlQuery()
        query.prepare('''
            INSERT INTO vehicles (plate_id, plate_number, model, proprietor_id, driver_id)
            VALUES (?, ?, ?, ?, ?)
        ''')
        query.addBindValue(plate_id)
        query.addBindValue(plate_number)
        query.addBindValue(model)
        query.addBindValue(proprietor_id)
        query.addBindValue(driver_id)
        return query.exec()

    def log_vehicle_action(self, vehicle_id, action, changed_by, details):
        query = QSqlQuery()
        query.prepare('''
            INSERT INTO vehicle_logs (vehicle_id, action, changed_by, details)
            VALUES (?, ?, ?, ?)
        ''')
        query.addBindValue(vehicle_id)
        query.addBindValue(action)
        query.addBindValue(changed_by)
        query.addBindValue(details)
        return query.exec()

    def close(self):
        self.db.close()