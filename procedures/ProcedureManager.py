from data.DataManager import DataManager
from interfaces.InterfaceManager import InterfaceManager
from procedures.GCodeGenerator import generate_snake_commands

import threading

import time
class ProcedureManager:
    
    def __init__(self, interfaceManager: InterfaceManager, dataManager: DataManager, debug=False, ui_output=True):
        self.interfaceManager = interfaceManager
        self.dataManager = dataManager
        self.filename = "default"
        
    def runScan(self, stop_event: threading.Event = None):
        #self.guiManager.update_configs #Needs to take the gui config values and put them into the datamanager objects
        self.interfaceManager.configure_pna(self.dataManager.PNAConfig)
        commands = generate_snake_commands(self.dataManager.AxesConfig)
        
        for instruction in commands:
            if stop_event.is_set():
                self.interfaceManager.output_message("Interupting Scan")
                break
            
            self.interfaceManager.grbl.send_instruction(instruction)
            status = self.interfaceManager.grbl.get_status()
            
            while status == 'Run':
                status = self.interfaceManager.grbl.get_status()
                if stop_event.is_set():
                    self.interfaceManager.output_message("Interupting Scan")
                    break
                time.sleep(0.05)
                
            
            #Add an alarm catch so it doesnt dump info
            data = self.interfaceManager.fetch_pna_data()
            position = self.interfaceManager.get_grbl_position()
            self.dataManager.update_data(data, position)