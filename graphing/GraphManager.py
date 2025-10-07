import pandas as pd
import tkinter as tk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# from graphing.GraphToolbar import GraphToolbar
from graphing.ToolbarCombined import ToolbarCombined
from graphing.PlotController import PlotController
from data.DataManager import DataManager

class GraphManager():
    def __init__(self, tk_root=None):
        if tk_root:
            self.root = tk.Toplevel(tk_root)
        else:
            self.root = tk.Tk()
            
        self.root.title('ATR Generated Graph')
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)
        self.canvas = None
        self.toolbar = None
        self.local_DataManager = DataManager()
        
        self.plotcontroller = PlotController()
        
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

        self.draw_view()
        self.generate_toolbar()
    
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