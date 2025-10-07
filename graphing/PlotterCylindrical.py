import numpy as np
import matplotlib.pyplot as plt
from scipy.interpolate import griddata
from matplotlib.colors import Normalize

from graphing.PlotterVariables import PlotterVariables

class PlotterCylindrical():
    
    def __init__(self, plotter_variables: PlotterVariables):
        self.plotter_variables = plotter_variables
        
        self.azimuth_values = None
        self.height_values = None
        self.r = None
        self.theta = None
        self.x = None
        self.y = None
        self.z = None
        
        self.slider_position = [0.25, 0.05, 0.5, 0.03]  # [Left, Bottom, Width, Height]
        
        self.azimuth_grid = None
        self.height_grid = None
        self.interpolate_method = 'cubic'
        self.magnitude_grid = None
        
    def update_grid_values(self):
        # Creating the grid for azimuthal angle and height
        self.azimuth_grid, self.height_grid = np.meshgrid(
            np.linspace(0, 360, self.plotter_variables.interpolation),
            np.linspace(np.min(self.plotter_variables.frequency_limited_data['X']), 
                        np.max(self.plotter_variables.frequency_limited_data['X']),
                        self.plotter_variables.interpolation)
        )
        
    def update_raw_coordinates(self):
        self.plotter_variables.zero_shift_axes('Azimuth')
        self.azimuth_values = self.plotter_variables.frequency_limited_data['Azimuth'].values
        self.plotter_variables.zero_shift_axes('X')
        self.height_values = self.plotter_variables.frequency_limited_data['X'].values
    
    def update_cylindrical_coordinates(self):
        self.theta = np.radians(self.azimuth_values)
        self.r = self.plotter_variables.response_values
        self.z = self.height_values
        
    def update_cylindrical_grid_coordinates(self):
        self.theta = np.radians(self.azimuth_grid)
        self.r = np.nan_to_num(self.magnitude_grid)
        self.z = self.height_grid
        
    def update_cartesian_coordinates(self):
        # Convert cylindrical to cartesian coordinates
        self.x = self.r * np.cos(self.theta)
        self.y = self.r * np.sin(self.theta)
        self.z = self.z
        
    def scatter_plot(self):
        # Scatter plot for cylindrical coordinates
        self.update_cylindrical_coordinates()
        self.update_cartesian_coordinates()
        self.plotter_variables.ax.scatter(self.x, self.y, self.z, c=self.r, cmap=self.plotter_variables.color_map)
        
    def interpolated_plot(self):
        # Interpolated plot for cylindrical coordinates
        points = np.vstack((self.azimuth_values, self.height_values)).T
        
        # Interpolate the magnitude grid over the cylindrical coordinate grid
        self.magnitude_grid = griddata(points, self.plotter_variables.response_values, 
                                       (self.azimuth_grid, self.height_grid),
                                       method=self.interpolate_method, fill_value=np.nan)
        
        self.update_cylindrical_grid_coordinates()
        self.update_cartesian_coordinates()
        
        norm = Normalize(vmin=np.nanmin(self.r), vmax=np.nanmax(self.r))
        
        # Plot surface for interpolated cylindrical data
        self.plotter_variables.ax.plot_surface(self.x, self.y, self.z,
                                               facecolors=plt.cm.get_cmap(self.plotter_variables.color_map)(norm(self.r)),
                                               rstride=1, cstride=1, linewidth=0, antialiased=False, alpha=0.9)
    
    def start_plot(self):
        # Start the plot for cylindrical data
        self.update_grid_values()
        self.update_raw_coordinates()
        if self.plotter_variables.interpolation > 0:
            self.interpolated_plot()
        else:
            self.scatter_plot()
            
        self.plotter_variables.ax.set_title(f"Frequency: {self.plotter_variables.current_frequency/1e9:.2f} GHz")
        self.plotter_variables.fig.canvas.draw_idle()
