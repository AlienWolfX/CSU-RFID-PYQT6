import sys
import os
import csv
import serial
import time
import shutil
from datetime import datetime, timedelta
from typing import Optional
from collections import deque
import queue
import threading

from PyQt6.QtWidgets import (
    QApplication, 
    QDialog, 
    QMainWindow, 
    QTableWidgetItem, 
    QMessageBox, 
    QFileDialog, 
    QHeaderView,
    QLabel,
    QVBoxLayout,
    QWidget
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QDate, QTimer
from PyQt6.QtGui import QPixmap

from forms.LoginForm import Ui_LoginDialog
from forms.Main import Ui_MainWindow
from forms.AdminMain import Ui_AdminMainWindow
from database import Database


READ_TIMEOUT = 30

class RFIDReader(QThread):
    rfid_tag_signal = pyqtSignal(str)
    
    def __init__(self, port='COM7', baud_rate=9600):
        super().__init__()
        self.port = port
        self.baud_rate = baud_rate
        self.ser = None
        self.running = True
        self.last_read_time = {}  
        self.READ_TIMEOUT = 30  
        self.read_buffer = queue.Queue()  
        self.tag_cache = {}  

    def run(self):
        try:
            self.ser = serial.Serial(self.port, self.baud_rate, timeout=1)
            print(f"Listening on {self.port} at {self.baud_rate} baud rate...")
            
            
            read_thread = threading.Thread(target=self._read_serial)
            read_thread.daemon = True
            read_thread.start()
            
            
            while self.running:
                try:
                    rfid_tag = self.read_buffer.get(timeout=1)
                    if rfid_tag:
                        current_time = time.time()
                        if self._should_process_tag(rfid_tag, current_time):
                            self.last_read_time[rfid_tag] = current_time
                            self.rfid_tag_signal.emit(rfid_tag)
                except queue.Empty:
                    continue
                    
        except serial.SerialException as e:
            print(f"Error opening serial port {self.port}: {e}")
        finally:
            if self.ser and self.ser.is_open:
                self.ser.close()

    def _read_serial(self):
        """Background thread to read from serial port"""
        while self.running:
            try:
                rfid_tag = self._read_rfid_tag()
                if rfid_tag:
                    self.read_buffer.put(rfid_tag)
            except Exception as e:
                print(f"Error reading RFID tag: {e}")
                time.sleep(0.1)

    def _should_process_tag(self, tag: str, current_time: float) -> bool:
        """Check if tag should be processed based on timeout"""
        if tag in self.last_read_time:
            time_diff = current_time - self.last_read_time[tag]
            return time_diff >= self.READ_TIMEOUT
        return True

    def _read_rfid_tag(self) -> Optional[str]:
        """Read RFID tag with specific pattern starting and ending with H"""
        try:
            buffer = bytearray()
            
            # Read available data
            if self.ser.in_waiting > 0:
                chunk = self.ser.read(self.ser.in_waiting)
                buffer += chunk
                
                # Look for pattern starting with 'H' (0x48)
                if buffer and 0x48 in buffer:
                    # Find the first 'H'
                    start_index = buffer.find(b'H')
                    
                    # Check if we have at least 3 bytes after finding 'H'
                    if start_index >= 0 and len(buffer) >= start_index + 3:
                        # Extract exactly 3 bytes (H and 2 bytes after it)
                        tag_data = buffer[start_index:start_index+3]
                        
                        if len(tag_data) == 3:
                            # Convert to hex
                            tag = tag_data.hex().upper()
                            return tag
            
            return None
        except serial.SerialException:
            print("Serial error in _read_rfid_tag")
            return None

    def stop(self):
        """Clean shutdown"""
        self.running = False
        if self.ser and self.ser.is_open:
            self.ser.close()
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
            self.role_id = self.db.get_user_role(user_id)  
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
        self.LOG_TIMEOUT = 30 # Grace period in seconds for every vehicle to be logged

        
        self.tableLogs.setColumnCount(5)
        self.tableLogs.setHorizontalHeaderLabels([
            "RFID", "Name", "Plate No.", "Time", "Remarks"
        ])
        header = self.tableLogs.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.Stretch)

        
        self.driver_cache = {}  
        self.log_cache = deque(maxlen=100)  
        
        
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.process_updates)
        self.update_timer.start(100)  
        
        self.pending_updates = queue.Queue()

    def logout(self):
        """Handle logout button click"""
        self.rfidReader.stop()
        self.close()

    def add_table_entry(self, rfid, name, plate):
        """Add new entry to the logs table with proper remarks handling"""
        current_time = datetime.now()
        
        
        if rfid in self.last_log_times:
            time_diff = (current_time - self.last_log_times[rfid]).total_seconds()
            if time_diff < self.LOG_TIMEOUT:
                return 
        
        
        last_log = self.db.get_last_log(rfid)
        remarks = "Time In"  
        
        if last_log:
            last_time = datetime.strptime(last_log['time_logged'], "%I:%M %p")
            time_since_last = (current_time - last_time).total_seconds()
            
            if time_since_last >= self.LOG_TIMEOUT:
                remarks = "Time Out" if last_log['remarks'] == "Time In" else "Time In"
            else:
                return  
        
        
        self.last_log_times[rfid] = current_time
        time_str = current_time.strftime("%I:%M %p")
        
        
        self.db.log_entry(rfid, remarks)
        
        
        self.tableLogs.insertRow(0)
        
        
        self.tableLogs.setItem(0, 0, QTableWidgetItem(rfid))
        self.tableLogs.setItem(0, 1, QTableWidgetItem(name))
        self.tableLogs.setItem(0, 2, QTableWidgetItem(plate))
        self.tableLogs.setItem(0, 3, QTableWidgetItem(time_str))
        self.tableLogs.setItem(0, 4, QTableWidgetItem(remarks))
        
        
        self.tableLogs.sortItems(3, Qt.SortOrder.DescendingOrder)

    def update_rfid_value(self, code):
        """Queue updates instead of processing immediately"""
        self.pending_updates.put(code)

    def process_updates(self):
        """Process queued updates in batch"""
        try:
            while True:
                code = self.pending_updates.get_nowait()
                self._process_single_update(code)
        except queue.Empty:
            pass

    def _process_single_update(self, code):
        """Process a single RFID update"""
        if code in self.driver_cache:
            driver = self.driver_cache[code]
        else:
            driver = self.db.get_driver_by_code(code)
            self.driver_cache[code] = driver

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

class AboutDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("About CSU VeMon")
        self.setFixedSize(400, 300)
        
        layout = QVBoxLayout()
        
        # Add about information
        about_text = """
        <h2>CSU VeMon - Vehicle Monitoring System</h2>
        <p>Author: AlienWolfX</p>
        <p>GitHub: <a href="https://github.com/AlienWolfX">https://github.com/AlienWolfX</a></p>
        <br>
        """
        
        about_label = QLabel(about_text)
        about_label.setOpenExternalLinks(True)
        about_label.setWordWrap(True)
        layout.addWidget(about_label)
        
        self.setLayout(layout)

class AdminMainWindow(QMainWindow, Ui_AdminMainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.db = Database()
        from datetime import timedelta
        
        # Track current view state
        self.showing_inactive = False
        
        # Connect toolbar actions
        self.actionviewDriverStatus.triggered.connect(self.toggle_driver_view)
        self.actionLogout.triggered.connect(self.logout)
        self.actionClear.triggered.connect(self.clear_form)
        
        # ...existing initialization code...
        self.actionExit.triggered.connect(self.close)
        self.uploadButton.clicked.connect(self.upload_photo)
        self.submitButton.clicked.connect(self.register_driver)
        self.updateButton.clicked.connect(self.update_driver)
        self.deleteButton.clicked.connect(self.delete_driver)
        self.searchButton.clicked.connect(self.search_drivers)
        
        # Remove this line since we're using the toolbar action instead
        # self.clearButton.clicked.connect(self.clear_form)

        
        self.userPhoto.setPixmap(QPixmap("media/unknown.jpg"))
        self.driver_photo_path = "media/unknown.jpg"
        
        
        self.crExpiry.setDisplayFormat("yyyy-MM-dd")
        self.orExpiry.setDisplayFormat("yyyy-MM-dd")
        
        
        self.driverTypeComboBox.clear()
        self.driverTypeComboBox.addItems(["professional", "non-professional", "student"])
        
        
        self.setup_details_table()
        self.load_drivers_table()

        
        self.detailsTable.itemClicked.connect(self.on_table_row_clicked)

        self.actionCSV.triggered.connect(self.export_to_csv)
        self.action_txt_2.triggered.connect(self.export_to_txt)

        # Connect toolbar toggle and about actions
        self.actionToolbar.triggered.connect(self.toggle_toolbar)
        self.actionAbout.triggered.connect(self.show_about_dialog)
        
        # Store toolbar visibility state
        self.toolbar_visible = True

    def toggle_driver_view(self):
        """Toggle between active and inactive drivers view"""
        self.showing_inactive = not self.showing_inactive
        
        # Update button text and tooltip
        if self.showing_inactive:
            self.actionviewDriverStatus.setToolTip("View active drivers")
            self.deleteButton.setText("Reactivate Driver")
        else:
            self.actionviewDriverStatus.setToolTip("View inactive drivers")
            self.deleteButton.setText("Delete")
        
        # Reload appropriate driver list
        self.load_drivers_table()

    def setup_details_table(self):
        """Configure the details table"""
        self.detailsTable.setColumnCount(3)
        self.detailsTable.setHorizontalHeaderLabels(["Driver Code", "Name", "Plate No."])
        header = self.detailsTable.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
    
    def clear_form(self):
        
        self.driver_codeValue.clear()
        self.dfirst_nameValue.clear()
        self.dlast_nameValue.clear()
        self.driverTypeComboBox.setCurrentIndex(0)  
        self.license_noValue.clear()
        self.crExpiry.setDate(QDate.currentDate())
        self.orExpiry.setDate(QDate.currentDate())
        self.userPhoto.setPixmap(QPixmap("media/unknown.jpg"))
        self.driver_photo_path = "media/unknown.jpg"
        
        
        self.plate_idValue.clear()
        self.plate_noValue.clear()
        self.modelValue.clear()
        
        
        self.pfirst_nameValue.clear()
        self.plast_nameValue.clear()
    
    def export_to_csv(self):
        """Export logs to CSV file with Philippines timezone"""
        file_name, _ = QFileDialog.getSaveFileName(
            self,
            "Export Logs to CSV",
            "",
            "CSV Files (*.csv)"
        )
        
        if file_name:
            try:
                logs = self.db.get_all_logs()
                
                
                with open(file_name, 'w', newline='') as file:
                    writer = csv.writer(file)
                    writer.writerow(['RFID', 'Name', 'Plate No.', 'Date', 'Time', 'Remarks'])
                    
                    for log in logs:
                        
                        dt = datetime.strptime(f"{log['log_date']} {log['time_logged']}", "%Y-%m-%d %I:%M %p")
                        pht = dt + timedelta(hours=8)
                        
                        
                        rfid = f'="{log["rfid_tag"]}"'
                        
                        writer.writerow([
                            rfid,  
                            log['name'],
                            log['plate_no'],
                            pht.strftime("%Y-%m-%d"),
                            pht.strftime("%I:%M %p"),
                            log['remarks']
                        ])
                
                QMessageBox.information(self, "Success", f"Logs exported successfully to {file_name}")
                
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to export logs: {str(e)}")

    def export_to_txt(self):
        """Export logs to text file with Philippines timezone"""
        file_name, _ = QFileDialog.getSaveFileName(
            self,
            "Export Logs to Text",
            "",
            "Text Files (*.txt)"
        )
        
        if file_name:
            try:
                logs = self.db.get_all_logs()
                
                with open(file_name, 'w') as file:
                    file.write("CSU VeMon Logs\n")
                    file.write("=" * 100 + "\n\n")
                    
                    file.write(f"{'RFID':<15} {'Name':<30} {'Plate No.':<15} {'Date':<12} {'Time':<12} {'Remarks':<10}\n")
                    file.write("-" * 100 + "\n")
                    
                    for log in logs:
                        
                        dt = datetime.strptime(f"{log['log_date']} {log['time_logged']}", "%Y-%m-%d %I:%M %p")
                        pht = dt + timedelta(hours=8)
                        
                        file.write(
                            f"{log['rfid_tag']:<15} "
                            f"{log['name'][:30]:<30} "
                            f"{log['plate_no']:<15} "
                            f"{pht.strftime('%Y-%m-%d'):<12} "
                            f"{pht.strftime('%I:%M %p'):<12} "
                            f"{log['remarks']:<10}\n"
                        )
                
                QMessageBox.information(self, "Success", f"Logs exported successfully to {file_name}")
                
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to export logs: {str(e)}")

    def load_drivers_table(self):
        """Load drivers into the details table based on current view"""
        self.detailsTable.setRowCount(0)
        
        # Get active or inactive drivers based on current view
        drivers = (self.db.get_inactive_drivers() if self.showing_inactive 
                  else self.db.get_all_drivers())
        
        for driver in drivers:
            row = self.detailsTable.rowCount()
            self.detailsTable.insertRow(row)
            
            
            self.detailsTable.setItem(row, 0, QTableWidgetItem(driver['driver_code']))
            self.detailsTable.setItem(row, 1, QTableWidgetItem(driver['full_name']))
            self.detailsTable.setItem(row, 2, QTableWidgetItem(driver['plate_number']))

    def on_table_row_clicked(self, item):
        """Handle row click in details table"""
        row = item.row()
        driver_code = self.detailsTable.item(row, 0).text()
        
        
        driver = self.db.get_driver_details(driver_code)
        if driver:
            
            self.driver_codeValue.setText(driver['driver_code'])
            self.dfirst_nameValue.setText(driver['first_name'])
            self.dlast_nameValue.setText(driver['last_name'])
            
            
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
            
            
            if driver.get('vehicle'):
                self.plate_idValue.setText(driver['vehicle']['plate_id'])
                self.plate_noValue.setText(driver['vehicle']['plate_number'])
                self.modelValue.setText(driver['vehicle']['model'])
            
            
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
            
            
            if not os.path.exists("images"):
                os.makedirs("images")

            extension = os.path.splitext(file_name)[1]

            
            safe_first = self.dfirst_nameValue.text() or "FirstName"
            safe_last = self.dlast_nameValue.text() or "LastName"
            new_filename = f"{safe_first}_{safe_last}{extension}"
            
            new_path = os.path.join("images", new_filename)
            try:
                shutil.copy(file_name, new_path)
                self.driver_photo_path = new_path
            except Exception as e:
                print(f"Error copying file: {e}")
                
                self.driver_photo_path = file_name
            
            
            self.userPhoto.setPixmap(QPixmap(self.driver_photo_path))

    def register_driver(self):
        """Handle driver, vehicle, and proprietor registration"""
        
        driver_code = self.driver_codeValue.text()
        first_name = self.dfirst_nameValue.text()
        last_name = self.dlast_nameValue.text()
        driver_type = self.driverTypeComboBox.currentText()  
        license_no = self.license_noValue.text()
        cr_expiry = self.crExpiry.date().toPyDate()
        or_expiry = self.orExpiry.date().toPyDate()

        
        plate_id = self.plate_idValue.text()
        plate_no = self.plate_noValue.text()
        model = self.modelValue.text()

        
        proprietor_first_name = self.pfirst_nameValue.text()
        proprietor_last_name = self.plast_nameValue.text()

        
        if not all([driver_code, first_name, last_name, driver_type, license_no,
                    plate_id, plate_no, model,
                    proprietor_first_name, proprietor_last_name]):
            QMessageBox.warning(
                self,
                "Validation Error",
                "Please fill in all required fields."
            )
            return

        
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
            self.load_drivers_table()  
            self.clear_form()
        else:
            QMessageBox.critical(
                self,
                "Error",
                "Failed to register vehicle information"
            )

    def update_driver(self):
        """Handle driver update"""
        
        driver_code = self.driver_codeValue.text()
        if not driver_code:
            QMessageBox.warning(
                self,
                "Validation Error",
                "Please select a driver to update by clicking on a row in the table."
            )
            return

        
        first_name = self.dfirst_nameValue.text()
        last_name = self.dlast_nameValue.text()
        driver_type = self.driverTypeComboBox.currentText()
        license_no = self.license_noValue.text()
        cr_expiry = self.crExpiry.date().toPyDate()
        or_expiry = self.orExpiry.date().toPyDate()

        
        plate_id = self.plate_idValue.text()
        plate_no = self.plate_noValue.text()
        model = self.modelValue.text()

        
        proprietor_first_name = self.pfirst_nameValue.text()
        proprietor_last_name = self.plast_nameValue.text()

        
        if not all([first_name, last_name, driver_type, license_no,
                   plate_id, plate_no, model,
                   proprietor_first_name, proprietor_last_name]):
            QMessageBox.warning(
                self,
                "Validation Error",
                "Please fill in all required fields."
            )
            return

        
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
            self.load_drivers_table()  
        else:
            QMessageBox.critical(
                self,
                "Error",
                "Failed to update vehicle information"
            )

    def delete_driver(self):
        """Handle driver deactivation/reactivation"""
        current_row = self.detailsTable.currentRow()
        if current_row < 0:
            action = "reactivate" if self.showing_inactive else "deactivate"
            QMessageBox.warning(
                self,
                "Selection Error",
                f"Please select a driver to {action} by clicking on a row in the table."
            )
            return

        driver_code = self.detailsTable.item(current_row, 0).text()
        action = "reactivate" if self.showing_inactive else "deactivate"

        reply = QMessageBox.question(
            self,
            f'Confirm {action.title()}',
            f'Do you want to {action} this driver?',
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            success = (self.db.reactivate_driver(driver_code) if self.showing_inactive 
                      else self.db.delete_driver(driver_code))
            
            if success:
                QMessageBox.information(
                    self,
                    "Success",
                    f"Driver {action}d successfully!"
                )
                self.load_drivers_table()
                self.clear_form()
            else:
                QMessageBox.critical(
                    self,
                    "Error",
                    f"Failed to {action} driver"
                )

    def clear_form(self):
        """Clear all form fields"""
        
        self.driver_codeValue.clear()
        self.dfirst_nameValue.clear()
        self.dlast_nameValue.clear()
        self.driverTypeComboBox.setCurrentIndex(0)  
        self.license_noValue.clear()
        self.crExpiry.setDate(QDate.currentDate())
        self.orExpiry.setDate(QDate.currentDate())
        self.userPhoto.setPixmap(QPixmap("media/unknown.jpg"))
        self.driver_photo_path = "media/unknown.jpg"
        
        
        self.plate_idValue.clear()
        self.plate_noValue.clear()
        self.modelValue.clear()
        
        
        self.pfirst_nameValue.clear()
        self.plast_nameValue.clear()

    def search_drivers(self):
        """Handle search button click"""
        search_text = self.searchValue.text().strip()
        
        if not search_text:
            
            self.load_drivers_table()
            return
        
        
        drivers = self.db.search_drivers(search_text)
        
        
        self.detailsTable.setRowCount(0)  
        
        if not drivers:
            
            QMessageBox.information(
                self,
                "Search Results",
                "No drivers found matching your search."
            )
            return
        
        
        for driver in drivers:
            row = self.detailsTable.rowCount()
            self.detailsTable.insertRow(row)
            
            
            self.detailsTable.setItem(row, 0, QTableWidgetItem(driver['driver_code']))
            self.detailsTable.setItem(row, 1, QTableWidgetItem(driver['full_name']))
            self.detailsTable.setItem(row, 2, QTableWidgetItem(driver['plate_number']))

    def logout(self):
        """Handle logout action"""
        reply = QMessageBox.question(
            self,
            'Confirm Logout',
            'Are you sure you want to logout?',
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self.close()

    def toggle_toolbar(self):
        """Toggle toolbar visibility"""
        self.toolbar_visible = not self.toolbar_visible
        self.toolBar.setVisible(self.toolbar_visible)

    def show_about_dialog(self):
        """Show about dialog"""
        dialog = AboutDialog(self)
        dialog.exec()

def main():
    app = QApplication(sys.argv)
    
    login = LoginDialog()
    if login.exec() == QDialog.DialogCode.Accepted:
        if login.role_id == 1:  
            window = AdminMainWindow()
        else:  
            window = MainWindow()
        window.show()
        sys.exit(app.exec())

if __name__ == "__main__":
    main()