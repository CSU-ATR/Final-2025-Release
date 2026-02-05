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
        # Validate inputs early
        if new_scan_data is None:
            Logger.ui("update_dataframe() received None for new_scan_data", source=self.source, level="warning")
            return
        if position is None:
            Logger.ui("update_dataframe() received None for position", source=self.source, level="warning")
            return

        try:
            X, Y, Z, Polar, Azimuth, Elevation = position
            new_scan_data_length = len(new_scan_data)

            temp_data = pd.DataFrame({
                'X': [X] * new_scan_data_length,
                'Y': [Y] * new_scan_data_length,
                'Z': [Z] * new_scan_data_length,
                'Polar': [Polar] * new_scan_data_length,
                'Azimuth': [Azimuth] * new_scan_data_length,
                'Elevation': [Elevation] * new_scan_data_length
            })

            new_scan_data.reset_index(drop=True, inplace=True)
            combined_data = temp_data.join(new_scan_data)
            formatted_new_scan_dataframe = combined_data[self.columns]

            new_values = np.vstack([self.data.values, formatted_new_scan_dataframe.values])
            self.data = pd.DataFrame(new_values, columns=self.columns)

        except Exception as e:
            Logger.ui(f"Failed to update dataframe: {e}", source=self.source, level="error")

