from PyQt6.QtSql import QSqlDatabase, QSqlQuery, QSqlError
from PyQt6.QtCore import QObject
import os
from dotenv import load_dotenv
load_dotenv()

class Database(QObject):
    def __init__(self):
        super().__init__()
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

    def log_entry(self, rfid_tag, remarks):
        """Log an entry with remarks and driver reference"""
        query = QSqlQuery()
        
        # First get driver_id from rfid_tag
        driver_query = QSqlQuery()
        driver_query.prepare("""
            SELECT driver_id 
            FROM drivers 
            WHERE driver_code = $1
        """)
        driver_query.addBindValue(rfid_tag)
        
        driver_id = None
        if driver_query.exec() and driver_query.next():
            driver_id = driver_query.value(0)
        
        # Insert log entry
        query.prepare("""
            INSERT INTO logs (rfid_tag, driver_id, remarks) 
            VALUES ($1, $2, $3)
        """)
        query.addBindValue(rfid_tag)
        query.addBindValue(driver_id)
        query.addBindValue(remarks)
        
        success = query.exec()
        if not success:
            print(f"Log entry error: {query.lastError().text()}")
        return success

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
        query.addBindValue(cr_expiry_date.strftime('%Y-%m-%d')) 
        query.addBindValue(or_expiry_date.strftime('%Y-%m-%d'))
        query.addBindValue(driver_license_no)
        
        success = query.exec()
        if not success:
            print(f"Database Error: {query.lastError().text()}")
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

    def get_driver_by_code(self, driver_code):
        query = QSqlQuery()
        query.prepare("""
            SELECT driver_code, first_name, last_name, driver_photo
            FROM drivers
            WHERE driver_code = $1
        """)
        query.addBindValue(driver_code)
        if query.exec() and query.next():
            return {
                'driver_code': query.value(0),
                'first_name': query.value(1),
                'last_name': query.value(2),
                'driver_photo': query.value(3)
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
            return query.value(0) 
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

    def get_plate_by_driver_code(self, driver_code):
        query = QSqlQuery()
        query.prepare("""
            SELECT v.plate_number
            FROM vehicles v
            JOIN drivers d ON v.driver_id = d.driver_id
            WHERE d.driver_code = $1
        """)
        query.addBindValue(driver_code)
        if query.exec() and query.next():
            return query.value(0)
        return None

    def get_all_drivers(self):
        """Fetch all active drivers with their vehicle information"""
        query = QSqlQuery()
        query.prepare("""
            SELECT 
                d.driver_code,
                d.first_name || ' ' || d.last_name as full_name,
                v.plate_number
            FROM drivers d
            LEFT JOIN vehicles v ON v.driver_id = d.driver_id
            WHERE d.is_active = TRUE
            ORDER BY d.first_name, d.last_name
        """)
        
        drivers = []
        if query.exec():
            while query.next():
                drivers.append({
                    'driver_code': query.value(0),
                    'full_name': query.value(1),
                    'plate_number': query.value(2) or "No vehicle"
                })
        return drivers

    def get_driver_details(self, driver_code):
        """Get complete driver details including vehicle and proprietor info"""
        query = QSqlQuery()
        query.prepare("""
            SELECT 
                d.*,
                TO_CHAR(d.cr_expiry_date, 'YYYY-MM-DD') as cr_expiry_date_str,
                TO_CHAR(d.or_expiry_date, 'YYYY-MM-DD') as or_expiry_date_str,
                v.plate_id,
                v.plate_number,
                v.model,
                p.first_name as p_first_name,
                p.last_name as p_last_name
            FROM drivers d
            LEFT JOIN vehicles v ON v.driver_id = d.driver_id
            LEFT JOIN proprietors p ON v.proprietor_id = p.proprietor_id
            WHERE d.driver_code = ?
        """)
        query.addBindValue(driver_code)
        
        if query.exec() and query.next():
            driver = {
                'driver_code': query.value('driver_code'),
                'first_name': query.value('first_name'),
                'last_name': query.value('last_name'),
                'driver_type': query.value('driver_type'),
                'driver_photo': query.value('driver_photo'),
                'driver_license_no': query.value('driver_license_no'),
                'cr_expiry_date': query.value('cr_expiry_date_str'),
                'or_expiry_date': query.value('or_expiry_date_str'),
                'vehicle': {
                    'plate_id': query.value('plate_id'),
                    'plate_number': query.value('plate_number'),
                    'model': query.value('model')
                } if query.value('plate_id') else None,
                'proprietor': {
                    'first_name': query.value('p_first_name'),
                    'last_name': query.value('p_last_name')
                } if query.value('p_first_name') else None
            }
            return driver
        return None

    def update_driver(self, driver_code, first_name, last_name, driver_type, driver_photo, cr_expiry_date, or_expiry_date, driver_license_no):
        """Update driver information"""
        query = QSqlQuery()
        query.prepare("""
            UPDATE drivers 
            SET first_name = $1, 
                last_name = $2, 
                driver_type = $3,
                driver_photo = $4, 
                cr_expiry_date = $5::date, 
                or_expiry_date = $6::date,
                driver_license_no = $7
            WHERE driver_code = $8
            RETURNING driver_id
        """)
        
        # Format dates as strings
        cr_date_str = cr_expiry_date.strftime('%Y-%m-%d')
        or_date_str = or_expiry_date.strftime('%Y-%m-%d')
        
        query.addBindValue(first_name)
        query.addBindValue(last_name)
        query.addBindValue(driver_type)
        query.addBindValue(driver_photo)
        query.addBindValue(cr_date_str)
        query.addBindValue(or_date_str)
        query.addBindValue(driver_license_no)
        query.addBindValue(driver_code)
        
        success = query.exec()
        if not success:
            print(f"Driver update error: {query.lastError().text()}")
        return success

    def update_vehicle_with_relations(self, driver_code, plate_id, plate_number, model, proprietor_first_name, proprietor_last_name):
        """Update vehicle and proprietor information"""
        self.db.transaction()
        try:
            # Get driver_id first
            driver_id_query = QSqlQuery()
            driver_id_query.prepare("SELECT driver_id FROM drivers WHERE driver_code = $1")
            driver_id_query.addBindValue(driver_code)
            
            if not driver_id_query.exec():
                raise Exception(f"Driver query failed: {driver_id_query.lastError().text()}")
            if not driver_id_query.next():
                raise Exception("Driver not found")
                
            driver_id = driver_id_query.value(0)

            # Get or create proprietor
            proprietor_id = self.update_or_create_proprietor(
                proprietor_first_name, 
                proprietor_last_name
            )
            if not proprietor_id:
                raise Exception("Failed to update/create proprietor")

            # Update vehicle
            vehicle_query = QSqlQuery()
            vehicle_query.prepare("""
                UPDATE vehicles 
                SET plate_number = $1,
                    model = $2,
                    proprietor_id = $3
                WHERE driver_id = $4 AND plate_id = $5
                RETURNING vehicle_id
            """)
            
            vehicle_query.addBindValue(plate_number)
            vehicle_query.addBindValue(model)
            vehicle_query.addBindValue(proprietor_id)
            vehicle_query.addBindValue(driver_id)
            vehicle_query.addBindValue(plate_id)

            if not vehicle_query.exec():
                raise Exception(f"Vehicle update failed: {vehicle_query.lastError().text()}")
            
            if not vehicle_query.next():
                # If update failed because vehicle doesn't exist, try to insert
                vehicle_query.prepare("""
                    INSERT INTO vehicles (plate_id, plate_number, model, proprietor_id, driver_id)
                    VALUES ($1, $2, $3, $4, $5)
                    RETURNING vehicle_id
                """)
                
                vehicle_query.addBindValue(plate_id)
                vehicle_query.addBindValue(plate_number)
                vehicle_query.addBindValue(model)
                vehicle_query.addBindValue(proprietor_id)
                vehicle_query.addBindValue(driver_id)
                
                if not vehicle_query.exec():
                    raise Exception(f"Vehicle insert failed: {vehicle_query.lastError().text()}")

            self.db.commit()
            return True

        except Exception as e:
            self.db.rollback()
            print(f"Error updating vehicle with relations: {str(e)}")
            return False

    def update_or_create_proprietor(self, first_name, last_name):
        """Update proprietor if exists, create if not"""
        query = QSqlQuery()
        
        # First try to find existing proprietor
        query.prepare("""
            SELECT proprietor_id 
            FROM proprietors 
            WHERE first_name = $1 AND last_name = $2
        """)
        query.addBindValue(first_name)
        query.addBindValue(last_name)
        
        if query.exec() and query.next():
            return query.value(0)
        
        # If not found, create new proprietor
        query.prepare("""
            INSERT INTO proprietors (first_name, last_name)
            VALUES ($1, $2)
            RETURNING proprietor_id
        """)
        query.addBindValue(first_name)
        query.addBindValue(last_name)
        
        if query.exec() and query.next():
            return query.value(0)
        
        print(f"Proprietor error: {query.lastError().text()}")
        return None

    def delete_driver(self, driver_code):
        """Soft delete driver by setting is_active to FALSE"""
        query = QSqlQuery()
        query.prepare("""
            UPDATE drivers 
            SET is_active = FALSE 
            WHERE driver_code = $1
            RETURNING driver_id
        """)
        query.addBindValue(driver_code)
        
        success = query.exec()
        if not success:
            print(f"Soft delete error: {query.lastError().text()}")
        return success

    def search_drivers(self, search_text):
        """Search active drivers by name, RFID code, or plate number"""
        query = QSqlQuery()
        query.prepare("""
            SELECT DISTINCT
                d.driver_code,
                d.first_name || ' ' || d.last_name as full_name,
                v.plate_number
            FROM drivers d
            LEFT JOIN vehicles v ON v.driver_id = d.driver_id
            WHERE 
                d.is_active = TRUE AND
                (d.driver_code ILIKE $1 OR
                LOWER(d.first_name || ' ' || d.last_name) LIKE LOWER($1) OR
                v.plate_number ILIKE $1)
            ORDER BY full_name
        """)
        
        search_pattern = f"%{search_text}%"
        query.addBindValue(search_pattern)
        
        drivers = []
        if query.exec():
            while query.next():
                drivers.append({
                    'driver_code': query.value(0),
                    'full_name': query.value(1),
                    'plate_number': query.value(2) or "No vehicle"
                })
        else:
            print(f"Search error: {query.lastError().text()}")
        return drivers

    def get_last_log(self, rfid_tag):
        """Get the last log entry for a given RFID tag"""
        query = QSqlQuery()
        query.prepare("""
            SELECT 
                TO_CHAR(time_logged, 'HH12:MI AM') as time_logged,
                remarks
            FROM logs 
            WHERE rfid_tag = $1
            ORDER BY time_logged DESC
            LIMIT 1
        """)
        query.addBindValue(rfid_tag)
        
        if query.exec() and query.next():
            return {
                'time_logged': query.value(0),
                'remarks': query.value(1)
            }
        return None

    def get_all_logs(self):
        """Get all logs with driver names and plate numbers"""
        query = QSqlQuery()
        query.prepare("""
            SELECT 
                l.rfid_tag,
                COALESCE(d.first_name || ' ' || d.last_name, 'Unknown') as name,
                COALESCE(v.plate_number, 'Unknown') as plate_no,
                TO_CHAR(l.time_logged, 'YYYY-MM-DD') as log_date,
                TO_CHAR(l.time_logged, 'HH12:MI AM') as time_logged,
                l.remarks
            FROM logs l
            LEFT JOIN drivers d ON l.driver_id = d.driver_id
            LEFT JOIN vehicles v ON d.driver_id = v.driver_id
            ORDER BY l.time_logged DESC
        """)
        
        logs = []
        if query.exec():
            while query.next():
                logs.append({
                    'rfid_tag': query.value(0),
                    'name': query.value(1),
                    'plate_no': query.value(2),
                    'log_date': query.value(3),
                    'time_logged': query.value(4),
                    'remarks': query.value(5)
                })
        return logs

    def close(self):
        self.db.close()