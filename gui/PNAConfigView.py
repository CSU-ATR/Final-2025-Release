import tkinter as tk
from tkinter import Spinbox, ttk

class PNAConfigView(tk.Frame):
    def __init__(self, parent, settings, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        
        self.settings = settings
        self.entries = {}
        self.configure_layout()
        self.grid(row=0, column=0, sticky="nsew")  # Add this line to ensure the frame is placed in the window
        
    def configure_layout(self):
        
        # Configure grid weights for dynamic resizing
        self.grid_columnconfigure(0, weight=self.settings["column_0_weight"])
        self.grid_columnconfigure(1, weight=self.settings["column_1_weight"])
        
        for row in range(self.settings["box_count"]):
            self.grid_rowconfigure(row, weight=self.settings["row_weight"])

        #Set Labels
        for row, label in enumerate(self.settings["box_settings"].keys()):
            lbl = tk.Label(self, text=label, font=self.settings["font"])
            lbl.grid(row=row, column=0, padx=self.settings["padx"], pady=self.settings["pady"], sticky="w")

        #Create ComboBox
            if label == "S Parameter" or label == "Calibration":
                combobox_settings = self.settings["box_settings"][label]
                s_param_combobox = ttk.Combobox(
                    self,
                    values=combobox_settings[0],
                    font=self.settings["font"],
                    state="readonly",
                    width=self.settings["combobox_width"],
                )
                s_param_combobox.set(combobox_settings[1])
                s_param_combobox.grid(row=row, column=1, padx=self.settings['padx'], pady=self.settings['pady'], sticky="ew")
                self.entries[label] = s_param_combobox
            
        #Create Spinbox
            else:
                spinbox_settings = self.settings["box_settings"][label]
                spinbox = Spinbox(
                    self,
                    from_=spinbox_settings[1],
                    to=spinbox_settings[2],
                    increment=spinbox_settings[3],
                    width=self.settings["spinbox_width"],
                )
                spinbox.delete(0, "end")
                spinbox.insert(0, spinbox_settings[0])
                spinbox.grid(row=row, column=1, padx=self.settings['padx'], pady=self.settings['pady'], sticky="ew")
                self.entries[label] = spinbox

    def enforce_column_width(self, event):
        # Enforce a maximum width for column 1
        for widget in self.entries.values():
            widget.update_idletasks()  # Update geometry info
            if widget.winfo_width() > self.settings["max_column_width"]:
                widget.config(width=self.settings["max_column_width"] // 10)  # Adjust width proportionally

    def get_parameters(self):
        parameters = {}
        for label, widget in self.entries.items():
            parameters[label] = widget.get()
        return parameters

    def set_values(self, values):
        for label, value in values.items():
            if label in self.entries:
                widget = self.entries[label]
                if isinstance(widget, ttk.Combobox):
                    widget.set(value)
                else:
                    widget.delete(0, tk.END)
                    widget.insert(0, value)
    
    def update_calibration_options(self, new_options):
        calibration_box = self.entries.get("Calibration")
        calibration_box['values'] = new_options