import pandas as pd
import numpy as np


class PlotterVariables:
    def __init__(self):
        self.axis_columns = ['X', 'Y', 'Z', 'Polar', 'Azimuth', 'Elevation']
        self.available_axes = None

        self.data = pd.DataFrame()
        self.frequency_limited_data = None

        self.available_frequencies = None
        self.current_frequency = None

        self.response_values = None
        self.response_type = "raw"
        self.color_map = 'viridis'

        # GUI sets this. Interpretation:
        # 0 => scatter
        # >0 => surface with upsampling target resolution (clamped in PlotterSpherical)
        self.interpolation = 0

        self.fig = None
        self.ax = None
        self.ax2 = None

    # KEEPING this for backwards compatibility (other plot types might use it)
    # should NOT use it for spherical geometry.
    def zero_shift_axes(self, axis: str):
        if self.frequency_limited_data is None or axis not in self.frequency_limited_data.columns:
            return
        min_value = self.frequency_limited_data[axis].min()
        self.frequency_limited_data.loc[:, axis] = self.frequency_limited_data[axis] - min_value

    
    def get_zero_shifted_axis(self, axis: str) -> np.ndarray:
        vals = self.frequency_limited_data[axis].to_numpy()
        return vals - np.nanmin(vals)
