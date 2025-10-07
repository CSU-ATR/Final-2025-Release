import numpy as np
import matplotlib.pyplot as plt

#from graphing.PlotterVariables 
import PlotterVariables

import matplotlib.pyplot as plt
import numpy as np

class Plotter2D:
    def __init__(self, plotter_variables: PlotterVariables):
        self.plotter_variables = plotter_variables

    def start_plot(self):
        axes = self.plotter_variables.available_axes
        fig = self.plotter_variables.fig
        if fig is None:
            fig = plt.figure(figsize=(10, 5))
            self.plotter_variables.fig = fig

        # Clear the figure and set up subplots based on number of axes
        fig.clf()
        if len(axes) == 1:
            ax = fig.add_subplot(111, projection=self._get_projection(axes[0]))
            self.plotter_variables.ax = ax
            self._plot_single(ax, axes[0])
        elif len(axes) == 2:
            ax1 = fig.add_subplot(121, projection=self._get_projection(axes[0]))
            ax2 = fig.add_subplot(122, projection=self._get_projection(axes[1]))
            self.plotter_variables.ax = (ax1, ax2)
            self._plot_dual(ax1, ax2, axes[0], axes[1])

    def _plot_single(self, ax, axis_name):
        values = self.plotter_variables.frequency_limited_data[axis_name].values
        response = self.plotter_variables.response_values

        if self._is_polar_axis(axis_name):
            theta = np.radians(values)
            ax.plot(theta, response)
        else:
            ax.plot(values, response)
        ax.set_title(axis_name)

    def _plot_dual(self, ax1, ax2, axis_a, axis_b):
        df = self.plotter_variables.frequency_limited_data

        # Get unique values for filtering
        unique_a = df[axis_a].unique()
        unique_b = df[axis_b].unique()

        # Pick a static value for axis_b to plot axis_a
        static_b = unique_b[len(unique_b) // 2]
        static_a = unique_a[len(unique_a) // 2]

        # Plot axis_a graph while holding axis_b steady
        subset_a = df[df[axis_b] == static_b]
        self._plot_on_axis(ax1, subset_a[axis_a].values, subset_a, axis_a, f"{axis_a} (at {axis_b}={static_b})")

        # Plot axis_b graph while holding axis_a steady
        subset_b = df[df[axis_a] == static_a]
        self._plot_on_axis(ax2, subset_b[axis_b].values, subset_b, axis_b, f"{axis_b} (at {axis_a}={static_a})")

    def _plot_on_axis(self, ax, x_values, subset, label, title):
        response = subset['Magnitude'].values if self.plotter_variables.response_type == 'raw' else self.plotter_variables.response_values
        if self._is_polar_axis(label):
            theta = np.radians(x_values)
            ax.plot(theta, response)
        else:
            ax.plot(x_values, response)
        ax.set_title(title)

    def _is_polar_axis(self, axis):
        return axis in ['Azimuth', 'Elevation', 'Polar']

    def _get_projection(self, axis):
        return 'polar' if self._is_polar_axis(axis) else None

        
        
#create a 2d plotter using this style as a basis

# how it should work is as follows

# if there are two values stored in plotter_variables.available_axes then plot two graphs side by side

# if there is only 1 value stored plot only 1 graph

# plotter_variables.available_axes holds the list of axes

# you can get the plotter information in the same way as values = self.plotter_variables.frequency_limited_data[axe_name].values

# if there are two graphs you will need to limit the data frame by a variable that holds a static value of the OTHER axe

# What this means is that you will have a static variable of axe A's values that limits axes B's values, and vice versa.

# This is because both pieces of information were gathered at the same time and to compare you need to have steady values

# If the axe_name is Azimuth, Elevation, Polar. You will need to plot in polar coordinates, else you can do cartesian

# You should not plot anything in Plotter2d, but rather merely place the graph on the ax, actual plotting is handled by PlotController