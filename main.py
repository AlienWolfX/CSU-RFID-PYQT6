import sys
import serial
import time
from PyQt6.QtWidgets import QApplication, QDialog, QMainWindow, QTableWidgetItem
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QPixmap
from forms.LoginForm import Ui_LoginDialog
from forms.Main import Ui_MainWindow
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

    def verify_credentials(self):
        username = self.usernameField.text()
        password = self.passwordField.text()
        
        if self.db.verify_login(username, password):
            self.accept()
        else:
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

    def update_rfid_value(self, tag):
        """Updates the rfidValue text field with the read RFID tag and logs entry."""
        self.rfidValue.setText(tag)
        
        result = self.db.get_user(tag)
        if result:
            name, plate, photo_path = result
            self.userPhoto.setPixmap(QPixmap(photo_path))
        else:
            name = "Unknown"
            plate = "Unknown"
            self.userPhoto.setPixmap(QPixmap("media/unknown.jpg"))
            
        self.nameValue.setText(name)
        self.plateValue.setText(plate)
        
        # Log entry in table
        self.add_table_entry(tag, name, plate)
        self.db.log_entry(tag)

    def closeEvent(self, event):
        """Handles the window close event to stop the RFID reader thread."""
        self.rfidReader.stop()
        self.db.close()
        event.accept()

def main():
    app = QApplication(sys.argv)
    login = LoginDialog()
    if login.exec() == QDialog.DialogCode.Accepted:
        main_window = MainWindow()
        main_window.show()
        sys.exit(app.exec())
    sys.exit()
    # app = QApplication(sys.argv)
    # main_window = MainWindow()
    # main_window.show()
    # sys.exit(app.exec())

if __name__ == "__main__":
    main()