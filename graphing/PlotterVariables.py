import pandas as pd

class PlotterVariables():
    
    def __init__(self):
        self.axis_columns = ['X', 'Y', 'Z', 'Polar', 'Azimuth','Elevation']
        self.available_axes = None
        self.data = pd.DataFrame()
        self.frequency_limited_data = None
        self.available_frequencies = None
        self.current_frequency = None
        self.response_values = None
        
        self.response_type = "raw"
        self.color_map = 'viridis'
        
        self.interpolation = 0
        self.fig = None
        self.ax = None
        
        self.ax2 = None
    
    def zero_shift_axes(self, axis: str):
        min_value = self.frequency_limited_data[axis].min()
        self.frequency_limited_data.loc[:, axis] = self.frequency_limited_data[axis] - min_value