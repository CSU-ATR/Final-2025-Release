from misc.Logger import Logger
from data.PNAConfig import PNAConfig

import pandas as pd
import numpy as np
from datetime import datetime

class ScanInformation:
    columns = ['X', 'Y', 'Z', 'Polar', 'Azimuth', 'Elevation', 'Frequency', 'Magnitude', 'Phase']
    data = pd.DataFrame(columns=columns)
    description = "Undefined Scan"
    timestamp = "No information"
    pna_config = PNAConfig()
    
    source = "Scan Information"
    
    def update_timestamp(self):
        """Update the timestamp to the current time."""
        self.timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    def update_description(self, new_desc):
        self.description = new_desc

    def update_dataframe(self, new_scan_data, position):
        # Extract X, Y, Z, Polar, Azimuth, Elevation from grbl_response
        if position is None:
            return
        
        X, Y, Z, Polar, Azimuth, Elevation = position
        
        new_scan_data_length = len(new_scan_data)
        
        # Create a temporary DataFrame for the position values
        temp_data = pd.DataFrame({
            'X': [X] * new_scan_data_length,
            'Y': [Y] * new_scan_data_length,
            'Z': [Z] * new_scan_data_length,
            'Polar': [Polar] * new_scan_data_length,
            'Azimuth': [Azimuth] * new_scan_data_length,
            'Elevation': [Elevation] * new_scan_data_length
        })
        
        # Ensure new_scan_data has a matching index and columns
        new_scan_data.reset_index(drop=True, inplace=True)
        
        # Combine temp_data (position data) and new_scan_data
        combined_data = temp_data.join(new_scan_data)
        
        # Ensure the columns match the order defined in 'columns'
        formatted_new_scan_dataframe = combined_data[self.columns]
        
        # Use np.vstack to vertically stack the current scan_data with the new data
        new_values = np.vstack([self.data.values, formatted_new_scan_dataframe.values])
        
        # Create a new DataFrame from the stacked values
        self.data = pd.DataFrame(new_values, columns=self.columns)
