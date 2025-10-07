import numpy as np
import matplotlib.pyplot as plt
from scipy.interpolate import griddata
from matplotlib.colors import Normalize

from graphing.PlotterVariables import PlotterVariables

class PlotterPlanar():
    
    def __init__(self, plotter_variables: PlotterVariables):
        self.plotter_variables = plotter_variables
        
        self.x_values = None
        self.y_values = None
        self.z_values = None
        self.x_grid = None
        self.y_grid = None
        self.z_grid = None
        
        self.slider_position = [0.25, 0.05, 0.5, 0.03]  # [Left, Bottom, Width, Height]
        self.interpolate_method = 'cubic'
        
    def update_raw_coordinates(self):
        self.plotter_variables.zero_shift_axes('X')
        self.x_values = self.plotter_variables.frequency_limited_data['X'].values
        self.plotter_variables.zero_shift_axes('Y')
        self.y_values = self.plotter_variables.frequency_limited_data['Y'].values
        self.z_values = self.plotter_variables.response_values
    
    def update_grid_coordinates(self):
        self.x_grid, self.y_grid = np.meshgrid(
            np.linspace(self.x_values.min(), self.x_values.max(), self.plotter_variables.interpolation),
            np.linspace(self.y_values.min(), self.y_values.max(), self.plotter_variables.interpolation)
        )
        points = np.vstack((self.x_values, self.y_values)).T
        self.z_grid = griddata(points, self.z_values,
                               (self.x_grid, self.y_grid),
                               method=self.interpolate_method, fill_value=np.nan)
    
    def scatter_plot(self):
        self.plotter_variables.ax.scatter(self.x_values, self.y_values, self.z_values,
                                          c=self.z_values, cmap=self.plotter_variables.color_map)
    
    def interpolated_plot(self):
        self.update_grid_coordinates()
        
        norm = Normalize(vmin=np.nanmin(self.z_grid), vmax=np.nanmax(self.z_grid))
        
        self.plotter_variables.ax.plot_surface(self.x_grid, self.y_grid, self.z_grid,
                                               facecolors=plt.cm.get_cmap(self.plotter_variables.color_map)(norm(self.z_grid)),
                                               rstride=1, cstride=1, linewidth=0, antialiased=True, alpha=0.9)
    
    def start_plot(self):
        self.update_raw_coordinates()
        
        if self.plotter_variables.interpolation > 0:
            self.interpolated_plot()
        else:
            self.scatter_plot()
        
        self.plotter_variables.ax.set_title(f"Frequency: {self.plotter_variables.current_frequency / 1e9:.2f} GHz")
        self.plotter_variables.ax.set_xlabel("X")
        self.plotter_variables.ax.set_ylabel("Y")
        self.plotter_variables.ax.set_zlabel("Response")
        self.plotter_variables.fig.canvas.draw_idle()