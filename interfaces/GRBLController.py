import serial
import serial.tools.list_ports
import time
import subprocess

from misc.Logger import Logger

class GRBL:
    """A class to connect to an Arduino with custom GRBL MEGA-5x software"""
    
    def __init__(self, debug=False, ui_output=True):
        self.debug = debug
        self.ui_output = ui_output
        self.vid = 0x2A03
        self.pid = 0x0042
        self.baud_rate = 115200
        self.port = None
        self.connection = None
        self.source = "Arduino"
    
    def output_message(self, message, level="info"):
        """Output Messages to cmdline and UI Terminal"""
        if(self.debug):
            Logger.console(message, source=self.source, level=level) 
                       
        if(self.ui_output):
            Logger.ui(message, source=self.source, level=level)
        
    def find_port(self):
        """Find a port with an Arduino Mega connected"""
        ports = serial.tools.list_ports.comports()
        for port in ports:
            if port.vid == self.vid and port.pid == self.pid:
                self.port = port.device
        
        if (self.port):
            self.output_message(f"Port found on: {self.port}")
            
        else:
            self.output_message("No Port found", level="error")
            
            
    def setup_connection(self):
        """Establish connection to the GRBL Arduino device."""
        try:
            grbl = serial.Serial(self.port, self.baud_rate)
            self.connection = grbl
            self.output_message(f"Connected")
            
        except serial.SerialException as e:
            self.output_message(f"Unable to connect: {e}", level="error")
            self.connection = None
            
    def close_connection(self):
        """Close connection the the Arduino"""
        if self.connection:
            self.connection.close()
            print("GRBL connection closed")
    
    def upload_firmware(self, hex_file_path):
        """
        Uploads firmware to the connected Arduino using avrdude.
        """
        if not self.port:
            self.output_message("No port found for firmware upload", level="error")
            return False
        
        self.output_message(f"Uploading firmware to {self.port}...", level="info")

        command = [
            "avrdude",
            "-v",
            "-patmega2560",             # Chip type for Arduino Mega 2560
            "-cwiring",                 # Programmer type for Mega 2560
            f"-P{self.port}",
            "-b115200",
            "-D",                        # Disable auto erase for flash memory
            f"-Uflash:w:{hex_file_path}:i"
        ]

        try:
            result = subprocess.run(command, capture_output=True, text=True)

            if result.returncode == 0:
                self.output_message("Firmware uploaded successfully.", level="info")
                return True
            else:
                self.output_message(f"Firmware upload failed:\n{result.stderr}", level="error")
                return False

        except FileNotFoundError:
            self.output_message("avrdude not found. Make sure it is installed and in PATH.", level="error")
            return False
    
    def wake_GRBL(self):
        """Wake up GRBL so it is ready to recieve commands"""
        self.output_message(f"Waking GRBL")
        self.connection.write(b"\r\n\r\n")
        time.sleep(1)
        self.connection.flushInput()
        
    #Needs to output whats happening to terminal
    def send_instruction(self, instruction, print_instruction=False):
        """Send a single instruction to GRBL"""
        if self.connection:
            waiting = True
            response = ""
            self.connection.write(instruction.encode())
            self.connection.flush()
            time.sleep(0.05) #Test Removing this
            
            while waiting :
                if self.connection.in_waiting > 0:
                    response += self.connection.readline().decode()
                else :
                    break
            if(print_instruction):
                self.output_message(f"Sent: '{instruction.strip()}'\nRecieved:\n{response}")
                
            return response

    def reset(self):
        if self.connection:
            self.connection.write(b'\x18')
            self.output_message('Sent GRBL x18')
        else:
            self.output_message("Not connected to Arduino")
            
    def get_status(self):
        """Get the status of GRBL"""
        response = self.send_instruction('?')
        if "Idle" in response:
            status = "Idle"
        elif "ALARM" in response:
            status = "Alarm"
        elif "HOLD" in response:
            status = "Hold"
        elif "FAULT" in response:
            status = "Fault"
        elif "Run" in response:
            status = "Run"
        return status
    
    def initialize(self):
        """Initialize, connection to Arduino, and GRBL software to recieve instructions"""
        self.find_port() #Find Port
        
        if self.port: 
            self.setup_connection() #Connect to grbl
            
        if self.connection :
            self.wake_GRBL() #Wake up GRBL
            self.send_instruction("?\n") #clear output buffer
            self.output_message("GRBL is ready")