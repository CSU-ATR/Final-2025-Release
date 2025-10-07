import tkinter as tk
from tkinter import ttk

from graphing.PlotController import PlotController

class ToolbarSettings:
    def __init__(self, parent, plot_controller: PlotController):
        self.parent = parent
        self.plot_controller = plot_controller
        self.freq_slider = None
        self.interpolation_slider = None
        self.menu_window = None
        
        btn = ttk.Button(parent, text="Settings", command=self.create_toolbar_menu)
        btn.pack(side=tk.LEFT, padx=2, pady=2)

    def create_toolbar_menu(self):
        if self.menu_window:
            self.menu_window.destroy()
        self.menu_window = tk.Toplevel(self.parent)
        self.menu_window.title("ATR Settings")
        self.menu_window.geometry("300x350")

        self.create_plot_type_menu()
        self.create_cmap_menu()
        self.create_response_type_menu()
        self.create_interpolation_slider()
        self.create_frequency_slider(label=True)

    def create_frequency_slider(self, label=False):
        if label:
            ttk.Label(self.menu_window, text="Frequency:").pack(pady=(15, 0))
        freq_max, freq_min, freq_curr = self.get_frequency_values()
        self.freq_slider = tk.Scale(self.menu_window, from_=freq_min, to=freq_max, orient=tk.HORIZONTAL,
                                    length=200)
        self.freq_slider.set(freq_curr)
        self.freq_slider.pack(pady=5)
        self.set_freq_slider_to_valid_values(self.plot_controller.plotter_variables.available_frequencies)
        
    def update_frequency_slider(self):
        if self.freq_slider:
            self.freq_slider.destroy()
            self.create_frequency_slider()
        
    def get_frequency_values(self):
        freqs = self.plot_controller.plotter_variables.available_frequencies
        return freqs.max(), freqs.min(), self.plot_controller.plotter_variables.current_frequency

    def set_freq_slider_to_valid_values(self, freqs):
        def on_slider_change(val):
            val = float(val)
            closest = min(freqs, key=lambda x: abs(x - val))
            self.freq_slider.set(closest)
            self.plot_controller.set_current_frequency(closest)
            self.plot_controller.run_plotter()

        self.freq_slider.config(command=on_slider_change)

    def create_interpolation_slider(self):
        ttk.Label(self.menu_window, text="Interpolation:").pack(pady=(15, 0))
        self.interpolation_slider = tk.Scale(self.menu_window, from_=0, to=100, orient=tk.HORIZONTAL,
                                             command=self.on_interpolation_change, length=200)
        self.interpolation_slider.set(0)
        self.interpolation_slider.pack(pady=5)

    def on_interpolation_change(self, val):
        self.plot_controller.set_interpolation(int(float(val)))
        self.plot_controller.run_plotter()

    def create_plot_type_menu(self):
        ttk.Label(self.menu_window, text="Plot Type").pack(pady=(10, 0))
        self.plot_type_combobox = ttk.Combobox(self.menu_window, values=self.plot_controller.plot_types, state="readonly")
        self.plot_type_combobox.set(self.plot_controller.plotter_type)
        self.plot_type_combobox.pack(pady=5)
        self.plot_type_combobox.bind("<<ComboboxSelected>>", self.on_plot_type_selected)

    def on_plot_type_selected(self, event=None):
        self.plot_controller.update_plotter_type(self.plot_type_combobox.get())
        self.plot_controller.run_plotter()

    def create_response_type_menu(self):
        ttk.Label(self.menu_window, text="Response Type").pack(pady=(10, 0))
        self.response_type_combobox = ttk.Combobox(self.menu_window,
                                                   values=self.plot_controller.response_type_options,
                                                   state="readonly")
        self.response_type_combobox.set(self.plot_controller.plotter_variables.response_type)
        self.response_type_combobox.pack(pady=5)
        self.response_type_combobox.bind("<<ComboboxSelected>>", self.on_response_type_selected)

    def on_response_type_selected(self, event=None):
        self.plot_controller.update_response_type(self.response_type_combobox.get())
        self.plot_controller.run_plotter()

    def create_cmap_menu(self):
        ttk.Label(self.menu_window, text="Color Mapping").pack(pady=(10, 0))
        self.cmap_combobox = ttk.Combobox(self.menu_window,
                                          values=self.plot_controller.color_map_options,
                                          state="readonly")
        self.cmap_combobox.set(self.plot_controller.plotter_variables.color_map)
        self.cmap_combobox.pack(pady=5)
        self.cmap_combobox.bind("<<ComboboxSelected>>", self.on_cmap_selected)

    def on_cmap_selected(self, event=None):
        self.plot_controller.update_color_map(self.cmap_combobox.get())
        self.plot_controller.run_plotter()
