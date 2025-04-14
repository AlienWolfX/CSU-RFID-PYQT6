import serial
import time
from typing import Optional
import sys
import re

class RFIDTagReader:
    def __init__(self, port='COM7', baud_rate=9600):
        """Initialize the RFID tag reader"""
        self.port = port
        self.baud_rate = baud_rate
        self.ser = None
        self.last_read_tag = None
        self.last_read_time = 0
        self.READ_TIMEOUT = 2  # Seconds between identical tag reads
        
        # Target pattern in different formats for robust detection
        self.target_hex = "4819E948"
        self.target_bytes = bytes.fromhex("4819E948")
        
        # Buffer for accumulating data between reads
        self.read_buffer = bytearray()
        self.buffer_max_size = 64  # Max buffer size to prevent memory issues
    
    def connect(self):
        """Connect to the serial port"""
        try:
            self.ser = serial.Serial(self.port, self.baud_rate, timeout=1)
            print(f"Connected to {self.port} at {self.baud_rate} baud rate")
            return True
        except serial.SerialException as e:
            print(f"Error connecting to serial port {self.port}: {e}")
            return False
    
    def disconnect(self):
        """Disconnect from the serial port"""
        if self.ser and self.ser.is_open:
            self.ser.close()
            print(f"Disconnected from {self.port}")
    
    def read_rfid_tag(self) -> Optional[str]:
        """Read RFID tag focusing ONLY on the 4819E948 pattern"""
        try:
            if not self.ser or not self.ser.is_open:
                return None
                
            if self.ser.in_waiting > 0:
                # Read new data
                new_data = self.ser.read(self.ser.in_waiting)
                
                # Add to buffer
                self.read_buffer.extend(new_data)
                
                # Trim buffer if it gets too large
                if len(self.read_buffer) > self.buffer_max_size:
                    self.read_buffer = self.read_buffer[-self.buffer_max_size:]
                
                # Debug output: show what we received
                print(f"\nData received: {len(new_data)} bytes")
                print(f"Buffer size: {len(self.read_buffer)} bytes")
                print(f"Raw HEX: {new_data.hex().upper()}")
                
                # Approach 1: Direct pattern match on the full buffer
                tag = self._extract_target_pattern(self.read_buffer)
                if tag:
                    # Clear the buffer after a successful read
                    self.read_buffer.clear()
                    return tag
            
            return None
            
        except serial.SerialException as e:
            print(f"Serial error: {e}")
            return None
        except Exception as e:
            print(f"Unexpected error: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def _extract_target_pattern(self, data):
        """Extract our target pattern using multiple methods for reliability"""
        # Method 1: Direct binary search (most reliable)
        idx = data.find(self.target_bytes)
        if idx >= 0:
            print(f"Found target pattern at position {idx}")
            return self.target_hex
            
        # Method 2: Look for the pattern across H...H boundaries
        if b'H' in data:
            # Use regex to find "H" followed by any bytes then "H"
            h_pattern = re.compile(b'H.{1,10}H')  # H followed by 1-10 bytes then H
            matches = h_pattern.findall(data)
            
            for match in matches:
                # Convert to hex and check if it contains our target
                match_hex = match.hex().upper()
                if "4819E9" in match_hex:
                    print(f"Found target in H...H pattern: {match_hex}")
                    return match_hex
        
        # Method 3: Check for partial matches at the end of buffer 
        # (in case the pattern is split across reads)
        for i in range(1, min(len(self.target_bytes), len(data))):
            if data[-i:] == self.target_bytes[:i]:
                print(f"Partial match at end of buffer ({i} bytes)")
                # Don't return, wait for complete match
                break
                
        return None
    
    def run(self):
        """Run the reader in a loop"""
        if not self.connect():
            return
        
        try:
            print("Waiting for RFID tags (Ctrl+C to exit)...")
            print("=" * 50)
            print(f"Looking for pattern: {self.target_hex}")
            print("=" * 50)
            
            while True:
                tag = self.read_rfid_tag()
                
                if tag:
                    current_time = time.time()
                    
                    # Only process if it's a new tag or the same tag after timeout
                    if tag != self.last_read_tag or (current_time - self.last_read_time) > self.READ_TIMEOUT:
                        self.last_read_tag = tag
                        self.last_read_time = current_time
                        
                        print("=" * 50)
                        print(f"RFID Tag Detected: {tag}")
                        print("=" * 50)
                
                time.sleep(0.1)  # Small delay to reduce CPU usage
                
        except KeyboardInterrupt:
            print("\nExiting...")
        finally:
            self.disconnect()


def list_available_ports():
    """List all available serial ports"""
    try:
        import serial.tools.list_ports
        ports = serial.tools.list_ports.comports()
        
        if not ports:
            print("No serial ports found")
            return
        
        print("\nAvailable serial ports:")
        for port in ports:
            print(f"  {port.device}: {port.description}")
        print()
    except Exception as e:
        print(f"Error listing serial ports: {e}")


if __name__ == "__main__":
    print("RFID Tag Reader Test Script")
    print("=" * 50)
    
    # List available ports
    list_available_ports()
    
    # Get port from command line or use default
    port = sys.argv[1] if len(sys.argv) > 1 else 'COM7'
    
    # Initialize and run the reader
    reader = RFIDTagReader(port=port)
    reader.run()