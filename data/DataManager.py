from data.AxesConfig import AxesConfig
from data.PNAConfig import PNAConfig
from data.ScanInformation import ScanInformation
from data.ConfigStorage import ConfigStorage
from data.DataStorage import DataStorage


class DataManager:

    def __init__(self):
        self.AxesConfig = AxesConfig()
        self.PNAConfig = PNAConfig()
        self.ScanInformation = ScanInformation()
        self.ConfigStorage = ConfigStorage()
        self.DataStorage = DataStorage()
        self.data_filename = "New_Scan"

        # observers that want to be notified when new scan data arrives
        # callbacks receive one argument: the full DataFrame (ScanInformation.data)
        self._update_callbacks = []
    
    def update_filename(self, new_filename):
        self.data_filename = new_filename
    
    def register_update_callback(self, callback):
        """Register a function to be called after each data update.

        Callbacks should accept a single argument containing the full
        pandas.DataFrame of current scan data.  This allows UI components to
        refresh plots without polling.  The callback will be invoked from the
        thread that updates the data, so GUI callbacks should schedule the
        actual work on the main thread (e.g. via ``tk_root.after``).
        """
        if callback not in self._update_callbacks:
            self._update_callbacks.append(callback)

    def unregister_update_callback(self, callback):
        """Remove a previously registered update callback."""
        if callback in self._update_callbacks:
            self._update_callbacks.remove(callback)

    def _notify_update_callbacks(self):
        for cb in list(self._update_callbacks):
            try:
                cb(self.ScanInformation.data)
            except Exception:
                # make sure one faulty observer doesn't break the scan
                pass

    def update_data(self, new_data, positions):
        self.ScanInformation.update_timestamp()
        self.ScanInformation.update_dataframe(new_data, positions)
        self.save_scan_data_csv()
        # self.save_scan_data_hdf5()

        # notify observers after the data frame has been modified
        self._notify_update_callbacks()
    
    def save_axes_config(self):
        self.ConfigStorage.save_axes_config(self.AxesConfig, self.data_filename)
        
    def load_axes_config(self):
        self.AxesConfig = self.ConfigStorage.load_axes_config(self.data_filename)
    
    def save_pna_config(self):
        self.ConfigStorage.save_pna_config(self.PNAConfig, self.data_filename)
    
    def load_pna_config(self):
        self.PNAConfig = self.ConfigStorage.load_pna_config(self.data_filename)
    
    def save_scan_data_hdf5(self):
        self.DataStorage.save_to_hdf5(self.data_filename, self.ScanInformation, self.PNAConfig)
    
    def save_scan_data_csv(self):
        self.DataStorage.save_to_csv(self.data_filename, self.ScanInformation)
    
    def load_scan_data_hdf5(self):
        self.ScanInformation = self.DataStorage.load_from_hdf5(self.data_filename)
    
    def load_scan_data_csv(self):
        self.ScanInformation = self.DataStorage.load_from_csv(self.data_filename)
    
    def load_available_files(self):
        self.DataStorage.get_files_by_extension()
