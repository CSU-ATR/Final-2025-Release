from data.PNAConfig import PNAConfig
from misc.Logger import Logger

import socket
import time
import math
import pandas as pd



class PNA:
    """A class to interact with a Network Analyzer using SCPI commands."""

    def __init__(self, ip_address="169.254.123.123", port=5025, ui_output=True):
        self.ip_address = ip_address
        self.port = port
        self.buffer_size = 4096
        self.connection = None
        self.ui_output = ui_output
        self.source = "PNA"
        self.sweep_time = 0
            
    def output_message(self, message, level="info"):
        """Output Messages UI Terminal""" 
        if(self.ui_output):
            Logger.ui(message, source=self.source, level=level)
    
    def get_pna_calsets(self):
        calsets = self.send_command(":SENS:CORR:CSET:CAT? NAME", expect_response=True)
        calsets = calsets[1:-1]
        calsets = calsets.split(',')
        return calsets
        
    def setup_connection(self):
        """Establish a socket connection to the Network Analyzer."""
        self.output_message("Attempting connection")
        try:
            self.connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.connection.settimeout(2)
            self.connection.connect((self.ip_address, self.port))
            self.output_message(f"Connected at {self.ip_address}:{self.port}")
        except socket.timeout:
            self.output_message("Socket Timed Out", level="error")
            self.connection = None
        except Exception as e:
            self.output_message(f"Failed to connect: {e}", level="error")
            self.connection = None

    def close_connection(self):
        """Close the socket connection."""
        if self.connection:
            self.connection.close()
            self.output_message("PNA Connection Closed")

    def send_command(self, command, expect_response=True):
        """Send a SCPI command to the Network Analyzer and optionally receive a response."""
        if self.connection:
            try:
                # Send the command
                self.connection.sendall((command + '\n').encode())
                self.output_message(f"Sent: {command}")

                if not expect_response:
                    return None

                # Initialize an empty response buffer
                response = b""

                while True:
                    # Read in chunks
                    chunk = self.connection.recv(self.buffer_size)
                    if not chunk:  # If no more data is received, stop reading
                        break
                    response += chunk

                    # Optional: Check if response ends with a specific terminator
                    if response.endswith(b'\n'):
                        break

                # Decode and return the complete response
                decoded_response = response.decode().strip()
                self.output_message(f"Received: {decoded_response[:100]}...")  # Print only the first 100 characters for brevity
                return decoded_response if decoded_response else None

            except Exception as e:
                self.output_message(f"{command} caused: {e}", level="error")
                return None

        else:
            self.output_message("Socket is not connected.")
            return None


    def configure_analyzer(self, settings: PNAConfig):
        """Configure the analyzer with user-specified settings."""
        self.send_command("*RST", expect_response=False)
        self.send_command("*CLS", expect_response=False)
        
        self.send_command(f"CALCulate1:PARameter:DEFine 'Meas1', {settings.s_parameter}", expect_response=False)
        self.send_command("DISPlay:WINDow1:TRACe1:FEED 'Meas1'", expect_response=False)

        self.send_command(f"SOURce1:POWer1:LEVel:IMMediate {settings.source_power}", expect_response=False)
        self.send_command(f"SENSe1:FREQuency:STARt {settings.start_frequency}", expect_response=False)
        self.send_command(f"SENSe1:FREQuency:STOP {settings.stop_frequency}", expect_response=False)
        self.send_command(f"SENSe1:BWIDth {settings.if_bandwidth}", expect_response=False)
        self.send_command(f"SENSe1:SWEep:POINts {settings.sweep_points}", expect_response=False)
        
        self.send_command(f"SENSe1:AVERage:COUNt {settings.averaging_points}", expect_response=False)
        self.send_command("SENSe1:AVERage ON", expect_response=False)
        self.send_command("INITiate1:CONTinuous OFF", expect_response=False)
        self.send_command("TRIGger:SEQuence:SINGle", expect_response=False)
        self.send_command("FORMat:DATA ASCii", expect_response=False)
        
        self.sweep_time = self.send_command("SENSe1:SWEEp:TIME?")
        print(f"Sweep time is: {self.sweep_time} seconds")
        self.sweep_time = float(self.sweep_time) #Convert sweep time to a float
        self.sweep_time = self.sweep_time + self.sweep_time*0.1 #add 10% to its time so that a sweep can be garunteed finished
        
        self.send_command(f"SENS:CORR:CSET:ACT '{settings.cal_set}'", expect_response=False)

    def fetch_data(self):
        self.send_command("*CLS", expect_response=False)
        self.send_command("INITiate1:IMMediate", expect_response=False) #Trigger a sweep
        time.sleep(self.sweep_time) #Wait for sweep to finish executing
        data = self.send_command("CALCulate1:DATA? SDATA", expect_response=True) #Get the data from the buffer

        if not data:
            return

        data_list = data.split(',')
        sweep_points = len(data_list) // 2
        freq_start = float(self.send_command("SENSe1:FREQuency:STARt?"))
        freq_stop = float(self.send_command("SENSe1:FREQuency:STOP?"))
        self.output_message("Got start and stop frequencies from PNA")
        freqs = [freq_start + i * (freq_stop - freq_start) / (sweep_points - 1) for i in range(sweep_points)]

        rows = []

        """Save scan data to dataframe"""
        for i in range(sweep_points):
            freq = freqs[i]
            real = float(data_list[2 * i])
            imag = float(data_list[2 * i + 1])
            magnitude = (real**2 + imag**2)**0.5
            phase = math.degrees(math.atan2(imag, real))
            rows.append([freq, magnitude, phase])

        df = pd.DataFrame(rows, columns=["Frequency", "Magnitude", "Phase"])
        
        return df
    
    def initialize(self):
        self.setup_connection()
