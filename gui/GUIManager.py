from gui.GRBLConfigViewController import GRBLConfigViewController
from gui.PNAConfigViewController import PNAConfigViewController
from gui.TerminalViewController import TerminalViewController

from procedures.Commands import Commands

import tkinter as tk

class GUIManager:
    
    def __init__(self, commands: Commands, calsets=None):
        #Create a root window
        self.root = tk.Tk()
        self.root.title('ATR Control Window')
        self.root.protocol("WM_DELETE_WINDOW", self.root.quit)
        
        #Instantiate each controller and their subsequent frames (widgets)
        self.GRBLConfigViewController = GRBLConfigViewController(self.root)
        self.PNAConfigViewController = PNAConfigViewController(self.root, calsets)
        self.TerminalViewController = TerminalViewController(self.root, commands)

        # Wire GUI commit events to update axis config (focus-out / Enter)
        try:
            self.GRBLConfigViewController.set_change_callback(commands.update_axis_config)
        except Exception:
            pass
        
        #Grid layout to position frames on the root
        self.GRBLConfigViewController.gui.grid(row=0, column=0, sticky="nsew")
        self.PNAConfigViewController.gui.grid(row=0, column=1, sticky='nsew')
        self.TerminalViewController.gui.grid(row=1, column=0, columnspan=2, sticky='nsew')
        
        #Configure the grid row column weights
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_rowconfigure(1, weight=1)
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_columnconfigure(1, weight=1)
        
        
        # Set root window size
        self.root.geometry('480x600')
    def update_configs(self):
        self.GRBLConfigViewController.update_config_values()
        self.PNAConfigViewController.update_config_values()