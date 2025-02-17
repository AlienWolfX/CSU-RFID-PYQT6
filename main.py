import sys
import serial
import time
from PyQt6.QtWidgets import QApplication, QDialog, QMainWindow, QTableWidgetItem, QMessageBox, QFileDialog, QHeaderView
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QDate
from PyQt6.QtGui import QPixmap
from forms.LoginForm import Ui_LoginDialog
from forms.Main import Ui_MainWindow
from forms.AdminMain import Ui_AdminMainWindow
from datetime import datetime
from database import Database

READ_TIMEOUT = 2

class RFIDReader(QThread):
    rfid_tag_signal = pyqtSignal(str)

    def __init__(self, port='COM7', baud_rate=9600):
        super().__init__()
        self.port = port
        self.baud_rate = baud_rate
        self.ser = None
        self.running = True

    def run(self):
        try:
            self.ser = serial.Serial(self.port, self.baud_rate, timeout=1)
            print(f"Listening on {self.port} at {self.baud_rate} baud rate...")
        except serial.SerialException as e:
            print(f"Error opening serial port {self.port}: {e}")
            return

        while self.running:
            try:
                rfid_tag = self.read_rfid_tag()
                if rfid_tag:
                    self.rfid_tag_signal.emit(rfid_tag)
            except Exception as e:
                print(f"Error reading RFID tag: {e}")
                time.sleep(1)  # Prevent rapid error messages

        if self.ser and self.ser.is_open:
            self.ser.close()

    def read_rfid_tag(self):
        """Reads an RFID tag and returns a hexadecimal string."""
        BUFFER_SIZE = 3  # Get 3 bytes from 6 hex characters
        start_time = time.time()
        byte_data = bytearray(BUFFER_SIZE)  # Pre-allocate buffer
        bytes_read = 0

        while time.time() - start_time < READ_TIMEOUT:
            if self.ser.in_waiting >= BUFFER_SIZE - bytes_read:
                try:
                    # Read remaining bytes needed
                    chunk = self.ser.read(BUFFER_SIZE - bytes_read)
                    byte_data[bytes_read:bytes_read + len(chunk)] = chunk
                    bytes_read += len(chunk)
                    
                    if bytes_read >= BUFFER_SIZE:
                        # Use faster hex conversion
                        return bytes(byte_data).hex().upper()
                except serial.SerialException:
                    return None

        return None if bytes_read < BUFFER_SIZE else None

    def stop(self):
        self.running = False
        self.wait()

class LoginDialog(QDialog, Ui_LoginDialog):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.loginButton.clicked.connect(self.verify_credentials)
        self.db = Database()
        self.role_id = None

    def verify_credentials(self):
        username = self.usernameField.text()
        password = self.passwordField.text()
        
        if self.db.verify_login(username, password):
            user_id = self.db.get_user_id(username)
            self.role_id = self.db.get_user_role(user_id)  # Get user role
            self.db.log_login_attempt(user_id, True)
            self.accept()
        else:
            user_id = self.db.get_user_id(username)
            if user_id:
                self.db.log_login_attempt(user_id, False)
            self.statusLabel.setText("Invalid credentials")
            self.passwordField.clear()

class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.rfidReader = RFIDReader()
        self.rfidReader.rfid_tag_signal.connect(self.update_rfid_value)
        self.rfidReader.start()
        
        self.buttonLogout.clicked.connect(self.logout)
        self.db = Database()
        
        self.tableLogs.setSortingEnabled(True)
        self.tableLogs.sortItems(3, Qt.SortOrder.DescendingOrder)
        self.last_log_times = {}
        self.LOG_TIMEOUT = 300

    def logout(self):
        """Handle logout button click"""
        self.rfidReader.stop()
        self.close()

    def add_table_entry(self, rfid, name, plate):
        current_time = datetime.now()
        
        # Check if RFID was logged recently
        if rfid in self.last_log_times:
            time_diff = (current_time - self.last_log_times[rfid]).total_seconds()
            if time_diff < self.LOG_TIMEOUT:
                return  # Skip logging if timeout hasn't passed
        
        # Update last log time and add entry
        self.last_log_times[rfid] = current_time
        time_str = current_time.strftime("%Y-%m-%d %H:%M:%S")
        
        row = self.tableLogs.rowCount()
        self.tableLogs.insertRow(row)
        
        # Add items to row
        self.tableLogs.setItem(row, 0, QTableWidgetItem(rfid))
        self.tableLogs.setItem(row, 1, QTableWidgetItem(name))
        self.tableLogs.setItem(row, 2, QTableWidgetItem(plate))
        self.tableLogs.setItem(row, 3, QTableWidgetItem(time_str))
        
        # Resort table 
        self.tableLogs.sortItems(3, Qt.SortOrder.DescendingOrder)

    def update_rfid_value(self, code):
        driver = self.db.get_driver_by_code(code)
        if driver:
            name_str = f"{driver['first_name']} {driver['last_name']}"
            self.userPhoto.setPixmap(QPixmap(driver['driver_photo']))
            plate_no = self.db.get_plate_by_driver_code(driver["driver_code"]) or "Unknown"
        else:
            name_str = "Unknown"
            plate_no = "Unknown"
            self.userPhoto.setPixmap(QPixmap("media/unknown.jpg"))

        self.rfidValue.setText(code)
        self.nameValue.setText(name_str)

        # Add to logs
        self.add_table_entry(code, name_str, plate_no)

    def closeEvent(self, event):
        """Handles the window close event to stop the RFID reader thread."""
        self.rfidReader.stop()
        self.db.close()
        event.accept()

class AdminMainWindow(QMainWindow, Ui_AdminMainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.db = Database()
        
        # Connect signals
        self.buttonLogout.clicked.connect(self.logout)
        self.actionExit.triggered.connect(self.close)
        self.uploadButton.clicked.connect(self.upload_photo)
        self.submitButton.clicked.connect(self.register_driver)
        
        # Set default photo and initialize photo path
        self.userPhoto.setPixmap(QPixmap("media/unknown.jpg"))
        self.driver_photo_path = "media/unknown.jpg"
        
        # Set date formats
        self.crExpiry.setDisplayFormat("yyyy-MM-dd")
        self.orExpiry.setDisplayFormat("yyyy-MM-dd")
        
        # Setup driver type combo box
        self.driverTypeComboBox.clear()
        self.driverTypeComboBox.addItems(["professional", "non-professional", "student"])
        
        # Setup details table
        self.setup_details_table()
        self.load_drivers_table()

    def setup_details_table(self):
        """Configure the details table"""
        self.detailsTable.setColumnCount(3)
        self.detailsTable.setHorizontalHeaderLabels(["Driver Code", "Name", "Plate No."])
        header = self.detailsTable.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        
    def load_drivers_table(self):
        """Load all drivers into the details table"""
        self.detailsTable.setRowCount(0)  # Clear existing rows
        drivers = self.db.get_all_drivers()
        
        for driver in drivers:
            row = self.detailsTable.rowCount()
            self.detailsTable.insertRow(row)
            
            # Add items to row
            self.detailsTable.setItem(row, 0, QTableWidgetItem(driver['driver_code']))
            self.detailsTable.setItem(row, 1, QTableWidgetItem(driver['full_name']))
            self.detailsTable.setItem(row, 2, QTableWidgetItem(driver['plate_number']))

    def upload_photo(self):
        file_name, _ = QFileDialog.getOpenFileName(
            self,
            "Select Driver Photo",
            "",
            "Image files (*.jpg *.png *.jpeg)"
        )
        if file_name:
            import shutil, os
            
            # Make sure the "images" folder exists
            if not os.path.exists("images"):
                os.makedirs("images")

            # Get extension from the original file
            extension = os.path.splitext(file_name)[1]

            # Use first and last name for new filename
            safe_first = self.dfirst_nameValue.text() or "FirstName"
            safe_last = self.dlast_nameValue.text() or "LastName"
            new_filename = f"{safe_first}_{safe_last}{extension}"
            
            new_path = os.path.join("images", new_filename)
            try:
                shutil.copy(file_name, new_path)
                self.driver_photo_path = new_path
            except Exception as e:
                print(f"Error copying file: {e}")
                # Fallback
                self.driver_photo_path = file_name
            
            # Update the QPixmap to the new path
            self.userPhoto.setPixmap(QPixmap(self.driver_photo_path))

    def register_driver(self):
        """Handle driver, vehicle, and proprietor registration"""
        # Get driver values
        driver_code = self.driver_codeValue.text()
        first_name = self.dfirst_nameValue.text()
        last_name = self.dlast_nameValue.text()
        driver_type = self.driverTypeComboBox.currentText()  # Get selected type from combo box
        license_no = self.license_noValue.text()
        cr_expiry = self.crExpiry.date().toPyDate()
        or_expiry = self.orExpiry.date().toPyDate()

        # Get vehicle values
        plate_id = self.plate_idValue.text()
        plate_no = self.plate_noValue.text()
        model = self.modelValue.text()

        # Get proprietor values
        proprietor_first_name = self.pfirst_nameValue.text()
        proprietor_last_name = self.plast_nameValue.text()

        # Basic validation
        if not all([driver_code, first_name, last_name, driver_type, license_no,
                    plate_id, plate_no, model,
                    proprietor_first_name, proprietor_last_name]):
            QMessageBox.warning(
                self,
                "Validation Error",
                "Please fill in all required fields."
            )
            return

        # First add driver
        driver_success = self.db.add_driver(
            driver_code=driver_code,
            first_name=first_name,
            last_name=last_name,
            driver_type=driver_type,
            driver_photo=self.driver_photo_path,
            cr_expiry_date=cr_expiry,
            or_expiry_date=or_expiry,
            driver_license_no=license_no
        )

        if not driver_success:
            QMessageBox.critical(
                self,
                "Error",
                "Failed to register driver"
            )
            return

        # Then add vehicle with proprietor
        vehicle_success = self.db.add_vehicle_with_relations(
            plate_id=plate_id,
            plate_number=plate_no,
            model=model,
            proprietor_first_name=proprietor_first_name,
            proprietor_last_name=proprietor_last_name,
            driver_code=driver_code
        )

        if vehicle_success:
            QMessageBox.information(
                self,
                "Success",
                "Driver, vehicle, and proprietor registered successfully!"
            )
            self.load_drivers_table()  # Refresh the table
            self.clear_form()
        else:
            QMessageBox.critical(
                self,
                "Error",
                "Failed to register vehicle information"
            )

    def clear_form(self):
        """Clear all form fields"""
        # Clear driver fields
        self.driver_codeValue.clear()
        self.dfirst_nameValue.clear()
        self.dlast_nameValue.clear()
        self.driverTypeComboBox.setCurrentIndex(0)  # Reset to first item
        self.license_noValue.clear()
        self.crExpiry.setDate(QDate.currentDate())
        self.orExpiry.setDate(QDate.currentDate())
        self.userPhoto.setPixmap(QPixmap("media/unknown.jpg"))
        self.driver_photo_path = "media/unknown.jpg"
        
        # Clear vehicle fields
        self.plate_idValue.clear()
        self.plate_noValue.clear()
        self.modelValue.clear()
        
        # Clear proprietor fields
        self.pfirst_nameValue.clear()
        self.plast_nameValue.clear()

    def logout(self):
        """Handle logout button click"""
        self.close()

def main():
    app = QApplication(sys.argv)
    
    login = LoginDialog()
    if login.exec() == QDialog.DialogCode.Accepted:
        if login.role_id == 1:  # Admin
            window = AdminMainWindow()
        else:  # Regular user
            window = MainWindow()
        window.show()
        sys.exit(app.exec())

if __name__ == "__main__":
    main()