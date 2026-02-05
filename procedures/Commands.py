from misc.Logger import Logger
from interfaces.InterfaceManager import InterfaceManager
from data.DataManager import DataManager
from procedures.ProcedureManager import ProcedureManager
from gui.GRBLConfigViewController import GRBLConfigViewController
from gui.PNAConfigViewController import PNAConfigViewController
import os
USE_THREADING = True

if USE_THREADING:
    import threading

from graphing.GraphManager import GraphManager

class Commands:
    
    source = "Commands"
    
    dict = {
        "help": {"function": "display_help", "description": "Show this message"},
        "clear": {"function": "clear_terminal", "description": "Clear the terminal screen"},
        "g": {"function": "grbl_commands", "description": "List common GRBL commands or execute GRBL command"},
        "scan": {"function": "scan", "description": "Run a scan"},
        "stop": {"function": "stopscan", "description": "interupt a scan"},
        "graph": {"function": "graph", "description": "Generate a graph (placeholder)"},
        "congrbl": {"function": "connect_grbl", "description": "Try to connect to and initialize GRBL"},
        "conpna": {"function": "connect_pna", "description": "Try to connect to the PNA"},
        # "homeconfig": {"function": "home_configuration", "description": "Home all configured axes (placeholder)"},
        "resetgrbl": {"function": "reset_grbl", "description": "Send 0x18 to grbl to reset eeprom"},
        # "resetfirmware": {"function": "reset_grbl_firmware", "description": "Reset GRBL firmware to defaults from source"},
        "setpna": {"function": "set_pna_config_get_function", "description": "Sets Config file Using GUI Values"},
        "savepna": {"function": "save_pna_configuration", "description": "Save PNA config [usage: savepna <filename>]"},
        "loadpna": {"function": "load_pna_configuration", "description": "Load PNA config [usage: loadpna <filename>]"},
        "saveaxes": {"function": "save_axes_configuration", "description": "Save axes config [usage: saveaxes <filename>]"},
        "loadaxes": {"function": "load_axes_configuration", "description": "Load axes config [usage: loadaxes <filename>]"},
        "savegrbl": {"function": "save_grbl_settings", "description": "Save current GRBL settings to a file in configurations/ [usage: savegrbl <filename>]"},
        "loadgrbl": {"function": "load_grbl_settings", "description": "Load GRBL settings from a file in configurations/ [usage: loadgrbl <filename>]"},
        "tuck": {"function": "dev_function", "description": "This is a dev function used for testing"},
    }
    
    grbl_commands_list = [
        "execute a GRBL cmd with g 'cmd'",
        "G0 [Axis][Position] - Immediate move an Axis to a Position",
        "$$ - View GRBL settings",
        "$# - View gCode parameters",
        "$G - View active gCode modes",
        "$H - Run homing cycle",
        "$X - Disable alarm lock",
        "? - Current status report",
    ]
    
    def __init__(self, interfaceManager: InterfaceManager, datamanager: DataManager):
        self.interfaces = interfaceManager
        self.datamanager = datamanager
        self.proceduremanager = ProcedureManager(interfaceManager=interfaceManager, dataManager=datamanager)
        if USE_THREADING:
            self.scan_stop_event = threading.Event()
        else:
            self.scan_stop_event = None

        self.get_axes_config = None
        self.get_pna_config = None
        self.tk_root = None
    
    def set_root(self, tk_root):
        self.tk_root = tk_root
        
    def set_pna_config_get_function(self, function: PNAConfigViewController.get_config_values):
        self.get_pna_config = function
    
    def set_axes_config_get_function(self, function: GRBLConfigViewController.get_config_values):
        self.get_axes_config = function

    def clear_terminal(self):
        pass #placeholder as actual logic is done in the ui
    
    def output_message(self, message, level="info"):
        Logger.ui(message, source=self.source, level=level)

    def unknown_command(self, command):
        self.output_message(f"> {command} - Unknown command. Type 'help' for a list of commands.")
        
    def display_help(self):
        help_text = "\n".join(
            f"- {command} : {entry['description']}"
            for command, entry in self.dict.items()
            if command != "tuck"
        )
        self.output_message(help_text)

    def grbl_commands(self, args=None):
        if args is None:
            command_list = "Common GRBL Commands:\n" + "\n".join(self.grbl_commands_list)
            self.output_message(command_list)
        else:
            if self.interfaces.grbl.connection:
                self.interfaces.grbl.send_instruction(args + '\n', print_instruction=True)
            else:
                self.output_message("Not Connected to GRBL", level='error')

    def connect_grbl(self):
        self.interfaces.grbl.initialize()

    def connect_pna(self):
        self.interfaces.pna.initialize()

    def _get_argument(self, args, required=False):
        if args is None or args.strip() == "":
            if required:
                self.output_message("Missing required filename argument.", level="error")
            return None
        return args.strip().split()[0]

    def load_grbl_settings(self, args=None):
        filename = self._get_argument(args)
        if filename:
            filepath = os.path.join("configurations", filename)
            self.interfaces.load_grbl_settings(filepath)
        else:
            self.interfaces.load_grbl_settings()
        

    def save_grbl_settings(self, args=None):
        print("Not Implemented")
        # filename = self._get_argument(args, required=True)
        # if filename:
        #     filepath = os.path.join("configurations", filename)
        #     self.interfaces.save_grbl_settings(filepath)
    
    def reset_grbl(self):
        self.interfaces.grbl.reset()
        
    def reset_grbl_firmware(self):
        self.output_message('Not currently Implemented')

    def save_pna_configuration(self, args=None):
        filename = self._get_argument(args, required=True)
        print(filename)
        if filename:
            self.datamanager.ConfigStorage.save_pna_config(self.datamanager.PNAConfig, filename)
            
    def load_pna_configuration(self, args=None):
        filename = self._get_argument(args, required=True)
        if filename:
            new_config = self.datamanager.ConfigStorage.load_pna_config(filename)
            self.datamanager.PNAConfig = new_config

    def save_axes_configuration(self, args=None):
        filename = self._get_argument(args, required=True)
        if filename:
            self.datamanager.ConfigStorage.save_axes_config(self.datamanager.AxesConfig, filename)

    def load_axes_configuration(self, args=None):
        filename = self._get_argument(args, required=True)
        if filename:
            new_config = self.datamanager.ConfigStorage.load_axes_config(filename)
            self.datamanager.AxesConfig = new_config

    def scan(self, args=None):
        # Sync GUI axis and PNA settings into DataManager before running the scan
        try:
            self.update_axis_config()
        except Exception as e:
            self.output_message(f"Failed to update axis configuration: {e}", level="error")
            return
        try:
            self.update_pna_config()
        except Exception as e:
            self.output_message(f"Failed to update PNA configuration: {e}", level="error")
            return

        if USE_THREADING:
            def scanthread():
                self.proceduremanager.runScan(self.scan_stop_event)
            initialization_thread = threading.Thread(target=scanthread, daemon=True)
            initialization_thread.start()
        else:
            self.proceduremanager.runScan(self.scan_stop_event)

    def stopscan(self, args=None):
        if self.scan_stop_event:
            self.scan_stop_event.set()
            
    def graph(self, args=None):
        self.output_message("Launching Graphing Window")
        app = GraphManager(self.tk_root)
        app.run()

    def home_configuration(self, args=None):
        self.output_message("Sending home command to all configured axes (placeholder: Not fully implemented)")
        # self.interfaces.home_all_axes()

    def dev_function(self, args=None):
        self.output_message("Dev function currently does nothing ")
    
    def update_axis_config(self):  # Sync GUI values into DataManager
        # If getter isn't configured yet (startup ordering) silently return to avoid spamming UI
        if not self.get_axes_config:
            #self.output_message("No axes config getter configured", level="error")
            return
        try:
            new_axes = self.get_axes_config()
            if new_axes is None:
                self.output_message("GUI returned no axis configuration", level="error")
                return
            self.datamanager.AxesConfig = new_axes
            #self.output_message("Axes configuration updated from UI")
        except Exception as e:
            self.output_message(f"Error updating axes config: {e}", level="error")

    def update_pna_config(self):
        # If getter isn't configured yet (startup ordering) silently return
        if not self.get_pna_config:
            #self.output_message("No PNA config getter configured", level="error")
            return
        try:
            new_pna = self.get_pna_config()
            if new_pna is None:
                self.output_message("GUI returned no PNA configuration", level="error")
                return
            self.datamanager.PNAConfig = new_pna
            #self.output_message("PNA configuration updated from UI")
        except Exception as e:
            self.output_message(f"Error updating PNA config: {e}", level="error")

