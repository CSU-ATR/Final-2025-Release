import tkinter as tk
from tkinter import Spinbox

class GRBLConfigView(tk.Frame):
    def __init__(self, parent, settings, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        
        self.settings = settings
        self.entries = {}
        self.configure_layout()
        self.grid(row=0, column=0, sticky="nsew") 
        
    def configure_layout(self):
        # Configure grid weights for dynamic resizing
        for col in range(self.settings["column_count"]):
            self.grid_columnconfigure(col, weight=self.settings["column_weight"])
        for row in range(self.settings["row_count"]):
            self.grid_rowconfigure(row, weight=self.settings["row_weight"])

        # Set Row Labels
        for row, label in enumerate(self.settings["row_labels"]):
            lbl = tk.Label(self, text=label, font=self.settings["font"])
            lbl.grid(row=row+1, column=0, padx=self.settings["padx"], pady=self.settings["pady"], sticky="w")

        # Set Column Labels
        for col, label in enumerate(self.settings["column_labels"]):
            lbl = tk.Label(self, text=label, font=self.settings["font"])
            lbl.grid(row=0, column=col+1, padx=self.settings["padx"], pady=self.settings["pady"], sticky="w")

        # Create Spinboxes for each combination of row and column
        for row_label in self.settings["row_labels"]:
            for col_label in self.settings["column_labels"]:
                spinbox_settings = self.settings["spinbox_settings"].get((row_label, col_label))
                if spinbox_settings:
                    spinbox = Spinbox(
                        self,
                        from_=spinbox_settings[1],
                        to=spinbox_settings[2],
                        increment=spinbox_settings[3],
                        width=self.settings["spinbox_width"],
                    )
                    spinbox.delete(0, "end")
                    spinbox.insert(0, spinbox_settings[0])
                    spinbox.grid(row=self.settings["row_labels"].index(row_label)+1, column=self.settings["column_labels"].index(col_label)+1, padx=self.settings["padx"], pady=self.settings["pady"], sticky="ew")
                    self.entries[f"{row_label} {col_label}"] = spinbox

    def get_parameters(self):
        parameters = {}
        for label, widget in self.entries.items():
            parameters[label] = float(widget.get())
        return parameters

    def set_values(self, values):
        for label, value in values.items():
            if label in self.entries:
                widget = self.entries[label]
                widget.delete(0, tk.END)
                widget.insert(0, value)
