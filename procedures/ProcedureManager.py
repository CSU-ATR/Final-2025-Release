from data.DataManager import DataManager
from interfaces.InterfaceManager import InterfaceManager
from procedures.GCodeGenerator import generate_snake_commands
from gui.PNAConfigViewController import PNAConfigViewController
# Avoid importing GUIManager here to prevent circular imports. GUI values should be pushed into DataManager before starting a scan.
USE_THREADING = True

if USE_THREADING:
    import threading


import time
class ProcedureManager:
    
    def __init__(self, interfaceManager: InterfaceManager, dataManager: DataManager, debug=False, ui_output=True):
        self.interfaceManager = interfaceManager
        self.dataManager = dataManager
        self.filename = "default"
        
    # def runScan(self, stop_event: threading.Event = None): #dethread
    def runScan(self, stop_event = None):
        # Expect caller to have synced GUI values into dataManager before starting scan
        self.interfaceManager.configure_pna(self.dataManager.PNAConfig)
        commands = generate_snake_commands(self.dataManager.AxesConfig)
        
        for instruction in commands:
            if stop_event and stop_event.is_set():
                self.interfaceManager.output_message("Interrupting Scan")
                break

            self.interfaceManager.grbl.send_instruction(instruction)

            try:
                status = self.interfaceManager.grbl.get_status()
            except Exception as e:
                self.interfaceManager.output_message(f"Error getting GRBL status: {e}", level="error")
                break

            while status == 'Run':
                try:
                    status = self.interfaceManager.grbl.get_status()
                except Exception as e:
                    self.interfaceManager.output_message(f"Error during status polling: {e}", level="error")
                    break

                if stop_event and stop_event.is_set():
                    self.interfaceManager.output_message("Interrupting Scan")
                    break

                time.sleep(0.05)

                
            
            #Add an alarm catch so it doesnt dump info
            data = self.interfaceManager.fetch_pna_data()
            position = self.interfaceManager.get_grbl_position()
            self.dataManager.update_data(data, position)