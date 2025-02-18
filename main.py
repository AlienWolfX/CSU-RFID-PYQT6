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
                time.sleep(1) 

        if self.ser and self.ser.is_open:
            self.ser.close()

    def read_rfid_tag(self):
        """Reads an RFID tag and returns a hexadecimal string."""
        BUFFER_SIZE = 3  # Get 3 bytes from 6 hex characters
        start_time = time.time()
        byte_data = bytearray(BUFFER_SIZE) 
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
        self.LOG_TIMEOUT = 120  # 2 minutes

        # Setup table columns
        self.tableLogs.setColumnCount(5)
        self.tableLogs.setHorizontalHeaderLabels([
            "RFID", "Name", "Plate No.", "Time", "Remarks"
        ])
        header = self.tableLogs.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)

    def logout(self):
        """Handle logout button click"""
        self.rfidReader.stop()
        self.close()

    def add_table_entry(self, rfid, name, plate):
        current_time = datetime.now()
        
        # Get last log for this RFID
        last_log = self.db.get_last_log(rfid)
        remarks = "Time In"
        
        if last_log:
            last_time = datetime.strptime(last_log['time_logged'], "%I:%M %p")
            time_diff = (current_time - last_time.replace(year=current_time.year, 
                                                        month=current_time.month, 
                                                        day=current_time.day)).total_seconds()
            
            if time_diff < self.LOG_TIMEOUT:
                return
            else:
                remarks = "Time Out" if last_log['remarks'] == "Time In" else "Time In"
        
        self.last_log_times[rfid] = current_time
        time_str = current_time.strftime("%I:%M %p")
        
        self.db.log_entry(rfid, remarks)
        
        row = self.tableLogs.rowCount()
        self.tableLogs.insertRow(row)
        
        self.tableLogs.setItem(row, 0, QTableWidgetItem(rfid))
        self.tableLogs.setItem(row, 1, QTableWidgetItem(name))
        self.tableLogs.setItem(row, 2, QTableWidgetItem(plate))
        self.tableLogs.setItem(row, 3, QTableWidgetItem(time_str))
        self.tableLogs.setItem(row, 4, QTableWidgetItem(remarks))
        
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
        self.plateValue.setText(plate_no)

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
        self.updateButton.clicked.connect(self.update_driver)  
        self.deleteButton.clicked.connect(self.delete_driver)
        self.searchButton.clicked.connect(self.search_drivers)  

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

        # Connect table selection signal
        self.detailsTable.itemClicked.connect(self.on_table_row_clicked)

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

    def on_table_row_clicked(self, item):
        """Handle row click in details table"""
        row = item.row()
        driver_code = self.detailsTable.item(row, 0).text()
        
        # Fetch full driver details from database
        driver = self.db.get_driver_details(driver_code)
        if driver:
            # Set driver fields
            self.driver_codeValue.setText(driver['driver_code'])
            self.dfirst_nameValue.setText(driver['first_name'])
            self.dlast_nameValue.setText(driver['last_name'])
            
            # Set driver type in combo box
            index = self.driverTypeComboBox.findText(driver['driver_type'])
            if index >= 0:
                self.driverTypeComboBox.setCurrentIndex(index)
                
            self.license_noValue.setText(driver['driver_license_no'])
            
            try:
                if isinstance(driver['cr_expiry_date'], str):
                    cr_date = QDate.fromString(driver['cr_expiry_date'], "yyyy-MM-dd")
                    or_date = QDate.fromString(driver['or_expiry_date'], "yyyy-MM-dd")
                else:
                    cr_date = QDate(driver['cr_expiry_date'])
                    or_date = QDate(driver['or_expiry_date'])
                    
                if cr_date.isValid():
                    self.crExpiry.setDate(cr_date)
                if or_date.isValid():
                    self.orExpiry.setDate(or_date)
            except Exception as e:
                print(f"Error setting dates: {e}")
                self.crExpiry.setDate(QDate.currentDate())
                self.orExpiry.setDate(QDate.currentDate())
            
            self.driver_photo_path = driver['driver_photo']
            self.userPhoto.setPixmap(QPixmap(driver['driver_photo']))
            
            # Set vehicle fields
            if driver.get('vehicle'):
                self.plate_idValue.setText(driver['vehicle']['plate_id'])
                self.plate_noValue.setText(driver['vehicle']['plate_number'])
                self.modelValue.setText(driver['vehicle']['model'])
            
            # Set proprietor fields
            if driver.get('proprietor'):
                self.pfirst_nameValue.setText(driver['proprietor']['first_name'])
                self.plast_nameValue.setText(driver['proprietor']['last_name'])

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

    def update_driver(self):
        """Handle driver update"""
        # Get driver values
        driver_code = self.driver_codeValue.text()
        if not driver_code:
            QMessageBox.warning(
                self,
                "Validation Error",
                "Please select a driver to update by clicking on a row in the table."
            )
            return

        # Get updated values from form
        first_name = self.dfirst_nameValue.text()
        last_name = self.dlast_nameValue.text()
        driver_type = self.driverTypeComboBox.currentText()
        license_no = self.license_noValue.text()
        cr_expiry = self.crExpiry.date().toPyDate()
        or_expiry = self.orExpiry.date().toPyDate()

        # Get updated vehicle values
        plate_id = self.plate_idValue.text()
        plate_no = self.plate_noValue.text()
        model = self.modelValue.text()

        # Get updated proprietor values
        proprietor_first_name = self.pfirst_nameValue.text()
        proprietor_last_name = self.plast_nameValue.text()

        # Basic validation
        if not all([first_name, last_name, driver_type, license_no,
                   plate_id, plate_no, model,
                   proprietor_first_name, proprietor_last_name]):
            QMessageBox.warning(
                self,
                "Validation Error",
                "Please fill in all required fields."
            )
            return

        # Update driver
        driver_success = self.db.update_driver(
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
                "Failed to update driver information"
            )
            return

        # Update vehicle and proprietor
        vehicle_success = self.db.update_vehicle_with_relations(
            driver_code=driver_code,
            plate_id=plate_id,
            plate_number=plate_no,
            model=model,
            proprietor_first_name=proprietor_first_name,
            proprietor_last_name=proprietor_last_name
        )

        if vehicle_success:
            QMessageBox.information(
                self,
                "Success",
                "Driver, vehicle, and proprietor information updated successfully!"
            )
            self.load_drivers_table()  # Refresh the table
        else:
            QMessageBox.critical(
                self,
                "Error",
                "Failed to update vehicle information"
            )

    def delete_driver(self):
        """Handle driver deletion"""
        # Get selected row
        current_row = self.detailsTable.currentRow()
        if current_row < 0:
            QMessageBox.warning(
                self,
                "Selection Error",
                "Please select a driver to delete by clicking on a row in the table."
            )
            return

        # Get driver code from selected row
        driver_code = self.detailsTable.item(current_row, 0).text()

        # Show confirmation dialog
        reply = QMessageBox.question(
            self,
            'Confirm Deletion',
            'Do you wish to delete this driver?',
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            # Delete the driver
            if self.db.delete_driver(driver_code):
                QMessageBox.information(
                    self,
                    "Success",
                    "Driver deleted successfully!"
                )
                self.load_drivers_table()  # Refresh the table
                self.clear_form()  # Clear the form
            else:
                QMessageBox.critical(
                    self,
                    "Error",
                    "Failed to delete driver"
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

    def search_drivers(self):
        """Handle search button click"""
        search_text = self.searchValue.text().strip()
        
        if not search_text:
            # If search is empty, show all drivers
            self.load_drivers_table()
            return
        
        # Perform search
        drivers = self.db.search_drivers(search_text)
        
        # Update table with search results
        self.detailsTable.setRowCount(0)  # Clear existing rows
        
        for driver in drivers:
            row = self.detailsTable.rowCount()
            self.detailsTable.insertRow(row)
            
            # Add items to row
            self.detailsTable.setItem(row, 0, QTableWidgetItem(driver['driver_code']))
            self.detailsTable.setItem(row, 1, QTableWidgetItem(driver['full_name']))
            self.detailsTable.setItem(row, 2, QTableWidgetItem(driver['plate_number']))

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