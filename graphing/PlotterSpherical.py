import numpy as np
import matplotlib.pyplot as plt
from scipy.interpolate import griddata
from matplotlib.colors import Normalize

from graphing.PlotterVariables import PlotterVariables

class PlotterSpherical():
    
    def __init__(self, plotter_variables: PlotterVariables):
        self.plotter_variables = plotter_variables
        
        self.azimuth_values = None
        self.elevation_values = None
        self.theta = None
        self.phi = None
        self.rho = None
        self.x = None
        self.y = None
        self.z = None
        
        self.slider_position = [0.25, 0.05, 0.5, 0.03] # [Left, Bottom, Width, Height]
        
        self.azimuth_grid = None
        self.elevation_grid = None
        self.interpolate_method = 'cubic'
        self.magnitude_grid = None
        
    def update_grid_values(self):
        self.azimuth_grid, self.elevation_grid = np.meshgrid(
            np.linspace(0, 360, self.plotter_variables.interpolation),
            np.linspace(0, 180, self.plotter_variables.interpolation)
        )
        
    def update_raw_coordinates(self):
        self.plotter_variables.zero_shift_axes('Azimuth')
        self.azimuth_values =  self.plotter_variables.frequency_limited_data['Azimuth'].values
        self.plotter_variables.zero_shift_axes('Elevation')
        self.elevation_values = self.plotter_variables.frequency_limited_data['Elevation'].values
    
    def update_polar_scatter_coordinates(self):
        self.theta = np.radians(self.azimuth_values)
        self.phi = np.radians(self.elevation_values)
        self.rho = self.plotter_variables.response_values
    
    def update_polar_grid_coordinates(self):
        self.theta = np.radians(self.azimuth_grid)
        self.phi = np.radians(self.elevation_grid)
        self.rho = np.nan_to_num(self.magnitude_grid)
        
    def update_cartesian_coordinates(self):
        self.x = self.rho * np.sin(self.phi) * np.cos(self.theta)
        self.y = self.rho * np.sin(self.phi) * np.sin(self.theta)
        self.z = self.rho * np.cos(self.phi)
        
    def scatter_plot(self):
            self.update_polar_scatter_coordinates()
            self.update_cartesian_coordinates()
            self.plotter_variables.ax.scatter(self.x, self.y, self.z, c=self.rho, cmap=self.plotter_variables.color_map)
        
    def interpolated_plot(self):
        points = np.vstack((self.azimuth_values, self.elevation_values)).T
        
        self.magnitude_grid = griddata(points, self.plotter_variables.response_values, 
                                (self.azimuth_grid, self.elevation_grid),
                                method=self.interpolate_method, fill_value=np.nan)
        
        
        self.update_polar_grid_coordinates()
        self.update_cartesian_coordinates()
        
        norm = Normalize(vmin=np.nanmin(self.rho), vmax=np.nanmax(self.rho))
        
        self.plotter_variables.ax.plot_surface(self.x, self.y, self.z,
                                    facecolors=plt.cm.get_cmap(self.plotter_variables.color_map)(norm(self.rho)),
                                    rstride=1, cstride=1, linewidth=0, antialiased=False, alpha=0.9)
    
    def start_plot(self):
        self.update_grid_values()
        self.update_raw_coordinates()
        if self.plotter_variables.interpolation > 0:
            self.interpolated_plot()
        else:
            self.scatter_plot()
            
        self.plotter_variables.ax.set_title(f"Frequency: {self.plotter_variables.current_frequency/1e9:.2f} GHz")
        self.plotter_variables.fig.canvas.draw_idle()
