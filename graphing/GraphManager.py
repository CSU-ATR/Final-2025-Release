import pandas as pd
import tkinter as tk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# from graphing.GraphToolbar import GraphToolbar
from graphing.ToolbarCombined import ToolbarCombined
from graphing.PlotController import PlotController
from data.DataManager import DataManager

class GraphManager():
    def __init__(self, tk_root=None, data_manager: DataManager = None):
        # if a shared data manager is provided we use it; otherwise fall back to
        # creating a local one (behaviour preserved for backward compatibility).
        if tk_root:
            self.root = tk.Toplevel(tk_root)
        else:
            self.root = tk.Tk()

        self.root.title('ATR Generated Graph')
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)
        self.canvas = None
        self.toolbar = None

        if data_manager is None:
            self.local_DataManager = DataManager()
        else:
            self.local_DataManager = data_manager

        # register for live update notifications if possible
        try:
            self.local_DataManager.register_update_callback(self._on_data_manager_update)
        except Exception:
            pass

        self.plotcontroller = PlotController()

        # seed the plot with an empty dataframe so matplotlib has something to
        # work with; real data will arrive via the callback.
        default_data = {
            'Azimuth': [0, 0],
            'Elevation': [0, 0],
            'Magnitude': [0,0],
            'X': [0,0],
            'Y': [0,0],
            'Z': [0,0],
            'Frequency': [0, 0],
            'Phase': [0,0]
        }

        data = pd.DataFrame(default_data)

        self.plotcontroller.initialize_data(data)
        self.plotcontroller.run_plotter()

        # if the provided data manager already contains scan results, replace
        # the dummy data immediately so the window opens with real data
        if data_manager is not None and hasattr(self.local_DataManager, 'ScanInformation'):
            existing = self.local_DataManager.ScanInformation.data
            if existing is not None and not existing.empty:
                # schedule an immediate refresh on the main thread
                self.root.after(0, self._refresh_plot)

        self.draw_view()
        self.generate_toolbar()

    def _on_data_manager_update(self, full_dataframe):
        """Callback invoked from DataManager when new scan data arrives.

        This may be executed from a background thread, so we schedule the
        actual plotting work on the Tk event loop.
        """
        # schedule GUI work on main thread
        try:
            self.root.after(0, self._refresh_plot)
        except Exception:
            pass

    def _refresh_plot(self):
        # bring the latest data into the plot controller and redraw
        df = self.local_DataManager.ScanInformation.data
        if df is None or df.empty:
            return
        self.plotcontroller.initialize_data(df)
        self.plotcontroller.run_plotter()
        if self.canvas:
            self.canvas.draw_idle()
    
    def draw_view(self):
        if self.canvas:  # If a plot is already present, clear it
            self.canvas.get_tk_widget().destroy()
        
        self.canvas = FigureCanvasTkAgg(self.plotcontroller.plotter_variables.fig, master=self.root)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)
        
    def generate_toolbar(self):
        if self.toolbar:
            self.toolbar.destroy()
        
        self.toolbar = ToolbarCombined(self.canvas, self.root, self.plotcontroller, self.local_DataManager)
        self.toolbar.update()  # Update the toolbar state
        self.toolbar.pack(side=tk.TOP, fill=tk.X)
    
    def run(self):
        self.root.mainloop()
    
    def on_close(self):
        # Do any cleanup here
        # remove our callback so the data manager doesn't hold a stale ref
        try:
            self.local_DataManager.unregister_update_callback(self._on_data_manager_update)
        except Exception:
            pass

        if self.canvas:
            self.canvas.get_tk_widget().destroy()
            self.canvas = None
        if self.toolbar:
            self.toolbar.destroy()
            self.toolbar = None
        self.root.quit()  # Exit the mainloop
        self.root.destroy()  # Destroy the main window

    
if __name__ == "__main__":
    app = GraphManager()
    app.run()