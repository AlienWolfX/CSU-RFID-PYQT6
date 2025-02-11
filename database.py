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
        query.prepare("""
            INSERT INTO drivers 
            (driver_code, first_name, last_name, driver_type, driver_photo, cr_expiry_date, or_expiry_date, driver_license_no)
            VALUES 
            ($1, $2, $3, $4, $5, $6::date, $7::date, $8)
        """)
        
        # Add values in order
        query.addBindValue(driver_code)
        query.addBindValue(first_name)
        query.addBindValue(last_name)
        query.addBindValue(driver_type)
        query.addBindValue(driver_photo)
        query.addBindValue(cr_expiry_date.strftime('%Y-%m-%d'))  # Format date as string
        query.addBindValue(or_expiry_date.strftime('%Y-%m-%d'))  # Format date as string
        query.addBindValue(driver_license_no)
        
        success = query.exec()
        if not success:
            print(f"Database Error: {query.lastError().text()}")
            print(f"Query: {query.lastQuery()}")  # Debug: print the actual query
            print(f"Values: {[driver_code, first_name, last_name, driver_type, driver_photo, cr_expiry_date, or_expiry_date, driver_license_no]}")  # Debug: print values
        return success

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

    def add_proprietor(self, first_name, last_name):
        query = QSqlQuery()
        query.prepare("""
            INSERT INTO proprietors 
            (first_name, last_name)
            VALUES 
            ($1, $2)
            RETURNING proprietor_id
        """)
        
        query.addBindValue(first_name)
        query.addBindValue(last_name)
        
        success = query.exec()
        if success and query.next():
            return query.value(0)  # Return the new proprietor_id
        print(f"Database Error: {query.lastError().text()}")
        return None

    def add_vehicle_with_relations(self, plate_id, plate_number, model, proprietor_first_name, 
                                 proprietor_last_name, driver_code):
        # Start transaction
        self.db.transaction()
        try:
            # First add proprietor and get ID
            proprietor_id = self.add_proprietor(proprietor_first_name, proprietor_last_name)
            if not proprietor_id:
                raise Exception("Failed to add proprietor")

            # Get driver ID from driver_code
            driver_query = QSqlQuery()
            driver_query.prepare("SELECT driver_id FROM drivers WHERE driver_code = $1")
            driver_query.addBindValue(driver_code)
            if not driver_query.exec() or not driver_query.next():
                raise Exception("Driver not found")
            driver_id = driver_query.value(0)

            # Add vehicle with relations
            vehicle_query = QSqlQuery()
            vehicle_query.prepare("""
                INSERT INTO vehicles 
                (plate_id, plate_number, model, proprietor_id, driver_id)
                VALUES 
                ($1, $2, $3, $4, $5)
            """)
            
            vehicle_query.addBindValue(plate_id)
            vehicle_query.addBindValue(plate_number)
            vehicle_query.addBindValue(model)
            vehicle_query.addBindValue(proprietor_id)
            vehicle_query.addBindValue(driver_id)
            
            if not vehicle_query.exec():
                raise Exception("Failed to add vehicle")

            self.db.commit()
            return True
            
        except Exception as e:
            self.db.rollback()
            print(f"Transaction failed: {str(e)}")
            return False

    def close(self):
        self.db.close()