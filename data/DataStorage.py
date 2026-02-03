from data.PNAConfig import PNAConfig
from data.ScanInformation import ScanInformation

import h5py
import pandas as pd
import os

class DataStorage:
    def __init__(self):
        self.directory = "datasets"
        os.makedirs(self.directory, exist_ok=True)
        self.accepted_extensions = ['.csv','.hdf5']
        self.files = None
        self.get_files_by_extension()
    
    def get_files_by_extension(self):
        # Get a list of all files in the directory
        all_files = os.listdir(self.directory)
        
        # Filter out files that do not have the specified extensions
        matching_files = [file for file in all_files if any(file.endswith(ext) for ext in self.accepted_extensions)]
        
        self.files = matching_files
        
    def save_to_hdf5(self, filename: str, scan_data: ScanInformation, pna_config: PNAConfig):
        # Ensure the file is saved in the datasets folder
        file_path = os.path.join(self.directory, filename + '.hdf5')
        
        with h5py.File(file_path, 'w') as f:
            # Save scan data
            # f.create_dataset('scan_data', data=scan_data.data.to_numpy(), dtype='f8')
            f.create_dataset('scan_data', data=scan_data.data.to_numpy())
            
            # Save column names
            f.create_dataset('columns', data=[col.encode('utf8') for col in scan_data.data.columns])
            
            # Save metadata
            f.attrs['timestamp'] = scan_data.timestamp
            f.attrs['scan description'] = scan_data.description
            f.attrs['pna configuration'] = str(pna_config)
    
    def load_from_hdf5(self, filename: str):
        new_ScanInformation = ScanInformation()
        
        # Load from the datasets folder
        file_path = os.path.join(self.directory, filename + '.hdf5')
        
        with h5py.File(file_path, 'r') as f:
            # Load scan data
            scan_data_array = f['scan_data'][:]
            
            # Load column names
            column_names = [name.decode('utf8') for name in f['columns']]
            
            # Restore scan data into DataFrame
            new_ScanInformation.data = pd.DataFrame(scan_data_array, columns=column_names)
            
            # Load metadata
            temp_timestamp = f.attrs.get('timestamp')
            if temp_timestamp != None:
                new_ScanInformation.timestamp  = temp_timestamp
            temp_description = f.attrs.get('scan description')
            if temp_description != None:
                new_ScanInformation.description  = temp_description
            temp_pna_config = f.attrs.get('pna configuration')
            if temp_pna_config != None:
                new_ScanInformation.pna_config  = temp_pna_config
        
            return new_ScanInformation
    
    def save_to_csv(self, filename: str, scan_data: ScanInformation):
        # Ensure the file is saved in the datasets folder
        file_path = os.path.join(self.directory, filename + ".csv")
        scan_data.data.to_csv(file_path, index=False)
        
    def load_from_csv(self, filename: str):
        # Load from the datasets folder
        file_path = os.path.join(self.directory, filename + ".csv")
        new_ScanInformation = ScanInformation()
        new_ScanInformation.data = pd.read_csv(file_path)
        return new_ScanInformation
