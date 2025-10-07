import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

from graphing.PlotterVariables import PlotterVariables
from graphing.PlotterSpherical import PlotterSpherical
from graphing.PlotterPlanar import PlotterPlanar
from graphing.PlotterCylindrical import PlotterCylindrical

class PlotController:
    def __init__(self):
        self.plotter_variables = PlotterVariables()
        self.plotter_type = 'Spherical'
        self.plot_types = ['Spherical', 'Planar', 'Cylindrical', '2D']
        self.figure_size = (10,6)
        self.plotter = None
        
        self.color_map_options = [
                                    # Perceptually Uniform Sequential
                                    'viridis', 'viridis_r',
                                    'plasma', 'plasma_r',

                                    # Sequential
                                    'Blues', 'Blues_r',
                                    'YlGnBu', 'YlGnBu_r',

                                    # Diverging
                                    'RdBu', 'RdBu_r',
                                    'coolwarm', 'coolwarm_r',

                                    # Qualitative
                                    'tab10', 'tab10_r',
                                    'Set2', 'Set2_r'
                                ]
        
        self.response_type_options = ['raw', 'db', 'phase']


    def run_plotter(self):
        self.limit_data_by_current_frequency()
        self.update_response_values()
        
        if self.plotter == None:
            pass #INITIALIZE PLOTTER
        
        if self.plotter_type == 'Spherical':
            self.plot_spherical()
            
        elif self.plotter_type == 'Planar':
            self.plot_planar()
        
        elif self.plotter_type == 'Cylindrical':
            self.plot_cylindrical()
        
        elif self.plotter_type == '2D':
            self.plot_two_dimension()
        
        self.plotter.start_plot()
    
    def update_plotter_type(self, type):
        self.plotter_type = type
    
    def plot_spherical(self):
        ax = self.plotter_variables.ax
        if ax is None or self.plotter_variables.fig is None:
            self.plotter_variables.fig = plt.figure(figsize=self.figure_size)
            self.plotter_variables.ax = self.plotter_variables.fig.add_subplot(111, projection='3d')
        else:
            ax.clear()

        if not isinstance(self.plotter, PlotterSpherical):
            self.plotter = PlotterSpherical(self.plotter_variables)
    
    def plot_planar(self):
        ax = self.plotter_variables.ax
        if ax is None or self.plotter_variables.fig is None:
            self.plotter_variables.fig = plt.figure(figsize=self.figure_size)
            self.plotter_variables.ax = self.plotter_variables.fig.add_subplot(111, projection='3d')
        else:
            ax.clear()

        if not isinstance(self.plotter, PlotterPlanar):
            self.plotter = PlotterPlanar(self.plotter_variables)
    
    def plot_cylindrical(self):
        ax = self.plotter_variables.ax
        if ax is None or self.plotter_variables.fig is None:
            self.plotter_variables.fig = plt.figure(figsize=self.figure_size)
            self.plotter_variables.ax = self.plotter_variables.fig.add_subplot(111, projection='3d')
        else:
            ax.clear()

        if not isinstance(self.plotter, PlotterCylindrical):
            self.plotter = PlotterCylindrical(self.plotter_variables)
    
    def plot_two_dimension(self):
        pass
    
    def set_data(self, new_data: pd.DataFrame):
        self.plotter_variables.data = new_data
    
    def set_interpolation(self, interpolation):
        self.plotter_variables.interpolation = interpolation
    
    def set_current_frequency(self, frequency):
        self.plotter_variables.current_frequency = frequency
        
    def update_available_frequencies(self):
        frequencies = np.sort(self.plotter_variables.data['Frequency'].unique())
        self.plotter_variables.available_frequencies = frequencies
    
    def limit_data_by_current_frequency(self):
        data = self.plotter_variables.data
        current_frequency = self.plotter_variables.current_frequency
        frequency_limited_data = data[data['Frequency'] == current_frequency]
        self.plotter_variables.frequency_limited_data = frequency_limited_data

    def set_response_values_to_raw_magnitude(self): #pna default 
        response = self.plotter_variables.frequency_limited_data['Magnitude'].values
        self.plotter_variables.response_values = response
    
    def set_response_values_to_db_magnitude(self): # 20log10(raw)
        magnitude = self.plotter_variables.frequency_limited_data['Magnitude'].values 
        self.plotter_variables.response_values = 20 * np.log10(magnitude)
    
    def set_response_values_to_phase(self): # phase
        self.plotter_variables.response_values = self.plotter_variables.frequency_limited_data['Phase'].values
    
    def update_response_type(self, response_type):
        self.plotter_variables.response_type = response_type
        self.update_response_values()
        
    def update_response_values(self):
        response_type = self.plotter_variables.response_type
        
        if response_type == 'raw':
            self.set_response_values_to_raw_magnitude()
            
        # elif response_type == 'linear':
        #     self.set_response_values_to_linear_magnitude()
        
        elif response_type == 'db':
            self.set_response_values_to_db_magnitude()
        
        elif response_type == 'phase':
            self.set_response_values_to_phase()
        
        else:
            self.set_response_values_to_raw_magnitude()
    
    def update_viable_axes(self):
        axes_data = self.plotter_variables.data[self.plotter_variables.axis_columns] #get just the axes
        non_constant_columns = axes_data.columns[axes_data.nunique() > 1] #get the columns with 1+ unique values
        self.plotter_variables.available_axes = axes_data.loc[:, non_constant_columns].columns.tolist()
    
    def update_color_map(self, map):
        self.plotter_variables.color_map = map

    def initialize_data(self, data: pd.DataFrame):
        self.set_data(data)
        self.update_available_frequencies()
        if self.plotter_variables.current_frequency not in self.plotter_variables.available_frequencies: #if our initial isnt part of those
            self.plotter_variables.current_frequency = self.plotter_variables.available_frequencies[0] #update it to the first
        self.limit_data_by_current_frequency()
        self.set_response_values_to_raw_magnitude()
