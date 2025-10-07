import re

from interfaces.GRBLController import GRBL
from interfaces.PNAController import PNA
from data.PNAConfig import PNAConfig
from misc.Logger import Logger

class InterfaceManager:
    
    def __init__(self, debug=False, ui_output=True):
        self.grbl = GRBL()
        self.pna = PNA()
        self.calset_querry = ":SENS:CORR:CSET:CAT? NAME"
        self.pna_sweep_time = 0
        
        self.source = "Interface"
        self.debug = debug
        self.ui_output = ui_output
        
    def output_message(self, message, level='info'):
        if self.debug :
            Logger.console(message, self.source, level)
        
        if self.ui_output:
            Logger.ui(message, self.source, level)
    
    def load_grbl_settings(self, filename='configurations/default_grbl_settings.txt'):
        with open(filename, 'r') as file:
            settings = file.readlines()
        file.close()
        if self.grbl.connection:
            for setting in settings:
                self.grbl.send_instruction(setting)
            self.output_message("Loaded GRBL Settings")
        
        else:
            self.output_message("GRBL Not Connected")
            
    def get_grbl_position(self):
        grbl_response = self.grbl.send_instruction('?')
        match = re.search(r'MPos:([0-9.-]+),([0-9.-]+),([0-9.-]+),([0-9.-]+),([0-9.-]+),([0-9.-]+)', grbl_response)
        if match:
            X = float(match.group(1))
            Y = float(match.group(2))
            Z = float(match.group(3))
            Polar = float(match.group(4))
            Azimuth = float(match.group(5))
            Elevation = float(match.group(6))
            return X, Y, Z, Polar, Azimuth, Elevation
        else:
            Logger.console("No Position Data Found", source=self.source, level="error")
            return None  # Return None if no match found
        
    def get_grbl_axis_information(self):
        # Parse the data into a dictionary
        grbl_settings_list = self.grbl.send_instruction("$$")
        data = {}
        for line in grbl_settings_list.strip().split("\n"):
            key, value = line.split("=")
            data[key] = float(value)

        # Define axis labels
        axes = ["X", "Y", "Z", "Polar", "Azimuth", "Elevation"]

        # Create structured dictionary
        result = {}
        for i, axis in enumerate(axes):
            max_rate_key = f"$11{i}"
            accel_key = f"$12{i}"
            if max_rate_key in data and accel_key in data:
                result[axis] = {"Max Rate": data[max_rate_key], "Acceleration": data[accel_key]}
            else:
                result[axis] = {}
                
    def configure_pna(self, PNAConfig: PNAConfig):
        self.pna.configure_analyzer(PNAConfig)
        self.pna_sweep_time = self.pna.sweep_time
        
    def get_pna_calsets(self):
        calsets = self.pna.send_command(self.calset_querry, expect_response=True)
        calsets = calsets[1:-1]
        calsets = calsets.split(',')
        return calsets
    
    def fetch_pna_data(self):
        df = self.pna.fetch_data()
        return df

    def initialize_connections(self):
        self.output_message("Initializing Connections")
        self.grbl.initialize()
        self.pna.setup_connection()
        if self.grbl.connection and self.pna.connection:
            self.output_message("ATR is Ready")
        else:
            self.output_message("Connections Failed", level="error")
    
    def close_connections(self):
        self.pna.close_connection()
        self.grbl.close_connection()
    
    
            