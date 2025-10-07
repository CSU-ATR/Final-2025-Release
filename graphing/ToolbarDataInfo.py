import tkinter as tk
from tkinter import ttk
import os

from data.DataManager import DataManager
from graphing.PlotController import PlotController

class ToolbarDataInfo:
    def __init__(self, parent, plot_controller: PlotController, update_frequency_slider, datamanager: DataManager):
        self.parent = parent
        self.plot_controller = plot_controller
        self.update_frequency_slider_method = update_frequency_slider
        self.info_win = None
        self.local_DataManager = datamanager
        
        self.timestamp = tk.StringVar(value="No Information")
        self.pna_settings = tk.StringVar(value="No Information")
        self.description_var = tk.StringVar(value="No Information")
        self.save_csv = tk.BooleanVar(value=True)
        self.save_hdf5 = tk.BooleanVar(value=True)
        
        self.filename_var = tk.StringVar(value="No valid files")
        self.selected_file = None
        self.file_combo = None
        self.file_list = []
        self.get_files()
        self.get_filename_information()
            
        btn = ttk.Button(parent, text="Data", command=self.create_data_info_menu)
        btn.pack(side=tk.LEFT, padx=2, pady=2)

    def create_data_info_menu(self):
        self.get_files()
        if not self.file_list:
            tk.messagebox.showinfo("No Files", "No valid data files found.")
            return

        if self.info_win:
            self.info_win.destroy()

        self.info_win = tk.Toplevel(self.parent)
        self.info_win.title("Data Information")
        self.info_win.geometry("500x500")
        self.info_win.resizable(True, True)

        # Setup grid and widgets
        for i in range(10):
            self.info_win.rowconfigure(i, weight=1)
        self.info_win.columnconfigure(0, weight=1)

        row = 0
        row = self.create_file_menu(row)
        row = self.create_filename_box(row)
        row = self.create_timestamp_box(row)
        row = self.create_pna_settings_box(row)
        row = self.create_description_box(row)
        row = self.create_save_format_checkboxes(row)
        self.create_save_button(row)


    def create_file_menu(self, row):
        ttk.Label(self.info_win, text="Select File:").grid(row=row, column=0, sticky='w', padx=10, pady=(10, 2))
        self.file_combo = ttk.Combobox(self.info_win, values=self.file_list)
        self.file_combo.set(self.selected_file or "No valid files")
        self.file_combo.grid(row=row+1, column=0, sticky='ew', padx=10)
        self.file_combo.bind("<<ComboboxSelected>>", lambda e: self.on_file_selected(self.file_combo.get()))
        return row + 2

    def create_filename_box(self, row):
        ttk.Label(self.info_win, text="Filename:").grid(row=row, column=0, sticky='w', padx=10, pady=(10, 2))
        filename_entry = ttk.Entry(self.info_win, textvariable=self.filename_var)
        filename_entry.grid(row=row+1, column=0, sticky='ew', padx=10)
        return row + 2

    def create_timestamp_box(self, row):
        ttk.Label(self.info_win, text="Time recorded:").grid(row=row, column=0, sticky='w', padx=10, pady=(10, 2))
        ttk.Label(self.info_win, textvariable=self.timestamp, relief="sunken").grid(row=row+1, column=0, sticky='ew', padx=10)
        return row + 2

    def create_pna_settings_box(self, row):
        ttk.Label(self.info_win, text="PNA Settings:").grid(row=row, column=0, sticky='w', padx=10, pady=(10, 2))
        ttk.Label(self.info_win, textvariable=self.pna_settings, relief="sunken").grid(row=row+1, column=0, sticky='ew', padx=10)
        return row + 2

    def create_description_box(self, row):
        ttk.Label(self.info_win, text="Description:").grid(row=row, column=0, sticky='w', padx=10, pady=(10, 2))
        description_entry = ttk.Entry(self.info_win, textvariable=self.description_var)
        description_entry.grid(row=row+1, column=0, sticky='ew', padx=10)
        return row + 2

    def create_save_format_checkboxes(self, row):
        ttk.Checkbutton(self.info_win, text="Save as CSV", variable=self.save_csv).grid(row=row, column=0, sticky='w', padx=10, pady=(10, 2))
        ttk.Checkbutton(self.info_win, text="Save as HDF5", variable=self.save_hdf5).grid(row=row+1, column=0, sticky='w', padx=10)
        return row + 2

    def create_save_button(self, row):
        save_btn = ttk.Button(self.info_win, text="Save", command=self.save_button_pressed)
        save_btn.grid(row=row, column=0, pady=15, padx=10, sticky='e')

    def on_file_selected(self, filename):
        self.selected_file = filename
        self.filename_var.set(self.strip_extension(filename))
        self.local_DataManager.update_filename(self.filename_var.get())
        self.update_data_from_file()
    
    def update_data_from_file(self, update_frequency_slider=True):
        if not self.selected_file:
            print("No file selected for update.")
            return
        
        extension = self.get_extension(self.selected_file)
        if extension == '.hdf5':
            self.local_DataManager.load_scan_data_hdf5()
        elif extension == '.csv':
            self.local_DataManager.load_scan_data_csv()
        else:
            return

        self.plot_controller.initialize_data(self.local_DataManager.ScanInformation.data)
        self.plot_controller.run_plotter()

        if update_frequency_slider:
            self.update_frequency_slider_method()

        self.timestamp.set(self.local_DataManager.ScanInformation.timestamp or "No timestamp")
        self.description_var.set(self.local_DataManager.ScanInformation.description or "No description")
        self.pna_settings.set(self.local_DataManager.ScanInformation.pna_config or "No PNA config")

    
    
    def save_button_pressed(self):
        new_desc = self.description_var.get()
        self.local_DataManager.ScanInformation.update_description(new_desc)

        # Get the new and old (full) filenames
        new_name = self.filename_var.get()
        old_name = self.strip_extension(self.selected_file)

        # If the name has changed, delete the old file
        if new_name != old_name:
            old_path = os.path.join(self.local_DataManager.DataStorage.directory, self.selected_file)
            try:
                if os.path.exists(old_path):
                    os.remove(old_path)
            except Exception as e:
                print(f"Error deleting old file: {e}")

        # Update DataManager filename and save with new name
        self.handle_filename_change(new_name)

        if self.save_csv.get():
            self.local_DataManager.save_scan_data_csv()
        if self.save_hdf5.get():
            self.local_DataManager.save_scan_data_hdf5()

        # Refresh file list and update combo box
        self.info_win.after(1000, self.get_files)

    def handle_filename_change(self, new_name):
        self.local_DataManager.update_filename(new_name)
    
    def get_files(self):
        self.local_DataManager.load_available_files()
        self.file_list = self.local_DataManager.DataStorage.files

        if not self.file_list:
            self.selected_file = None
            self.filename_var.set("No valid files")
        else:
            self.get_filename_information()
            
    def strip_extension(self, filename):
        return os.path.splitext(filename)[0]  # Strip extension

    def get_extension(self, filename):
        return os.path.splitext(self.selected_file)[1]

    def get_filename_information(self):
        if not self.file_list:
            self.selected_file = None
            self.filename_var.set("No valid files")
            return


        stripped_file_names = [self.strip_extension(file) for file in self.file_list]

        if "New_Scan" in stripped_file_names:
            index = stripped_file_names.index("New_Scan")
            self.selected_file = self.file_list[index]
        else:
            self.selected_file = self.file_list[0]

        self.filename_var = tk.StringVar(value=self.strip_extension(self.selected_file))
        self.handle_filename_change(self.filename_var.get())
        self.update_data_from_file(update_frequency_slider=False)