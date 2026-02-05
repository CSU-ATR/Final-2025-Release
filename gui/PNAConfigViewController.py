from gui.PNAConfigView import PNAConfigView
from data.PNAConfig import PNAConfig

class PNAConfigViewController:
    UI_FONT = ("Arial", 8, "bold")
    SPINBOX_WIDTH = 10
    COMBOBOX_WIDTH = 10
    PADX = 5
    PADY = 5
    MAX_COLUMN_WIDTH = 150  # Max width for column
    COLUMN0_WEIGHT = 1
    COLUMN1_WEIGHT = 1
    ROW_WEIGHT = 1
    
    GHz_to_Hz = 1e9
    
    ###THIS IS A SHITFIX. IDEALLY LABELS SHOULD BE THEir OWN VALUE IN TARGET SETTINGS, but that would require a large redesign so this shitfix essentially provides a map of variable names to widget labels
    key_map = {
            's_parameter': 'S Parameter',
            'cal_set': 'Calibration',
            'source_power': 'Source Power (dB)',
            'start_frequency': 'Start Frequency (GHz)',
            'stop_frequency': 'Stop Frequency (GHz)',
            'if_bandwidth': 'IF Bandwidth',
            'sweep_points': 'Sweep Points',
            'averaging_points': 'Averaging Points'
        }
    
    default_calset = 'CH1_CALREG'
    
    def __init__(self, parent, calset):
        # Determine calibration defaults/options
        if calset:
            default_calset = calset
        #(start, _from, to, increment)
        self.box_settings = {
            "S Parameter": (["S11", "S12", "S21", "S22"], "S21"), #
            "Calibration": (self.default_calset, self.default_calset),
            "Source Power (dB)": (-10, -100, 100, 1),
            "Start Frequency (GHz)": (8, 10e-3, 50.0, 0.001),  # Scaled to GHz
            "Stop Frequency (GHz)": (12, 10e-3, 50.0, 0.001),  # Scaled to GHz
            "IF Bandwidth": (100, 1, 10_000, 1),
            "Sweep Points": (21, 2, 1001, 1),
            "Averaging Points": (10, 1, 100, 1),
        }
    
        self.box_count = len(self.box_settings)
    
        settings = {
            "font": self.UI_FONT,
            "spinbox_width": self.SPINBOX_WIDTH,
            "combobox_width": self.COMBOBOX_WIDTH,
            "padx": self.PADX,
            "pady": self.PADY,
            "max_column_width": self.MAX_COLUMN_WIDTH,
            "box_settings": self.box_settings,
            "box_count": self.box_count,
            "column_0_weight": self.COLUMN0_WEIGHT,
            "column_1_weight": self.COLUMN1_WEIGHT,
            "row_weight": self.ROW_WEIGHT,
        }
        
        self.gui = PNAConfigView(parent, settings)  # Create an instance of PNAConfigView
        
    def get_config_values(self):
        # Create an array of the keys in box_settings called parameter_names
        parameter_names = list(self.box_settings.keys())
        
        # Get the parameters from the GUI
        params = self.gui.get_parameters()
        
        # Create config_values with converted frequencies in the same line
        config_values = {
            "s_parameter": params.get(parameter_names[0]),  # S Parameter
            "cal_set": params.get(parameter_names[1]),
            "source_power": float(params.get(parameter_names[2])) if params.get(parameter_names[2]) else None,  # Source Power
            "start_frequency": float(params.get(parameter_names[3])) * self.GHz_to_Hz if params.get(parameter_names[3]) else None,  # Start Frequency in Hz
            "stop_frequency": float(params.get(parameter_names[4])) * self.GHz_to_Hz if params.get(parameter_names[4]) else None,  # Stop Frequency in Hz
            "if_bandwidth": float(params.get(parameter_names[5])) if params.get(parameter_names[5]) else None,  # IF Bandwidth
            "sweep_points": int(params.get(parameter_names[6])) if params.get(parameter_names[6]) else None,  # Sweep Points
            "averaging_points": int(params.get(parameter_names[7])) if params.get(parameter_names[7]) else None,  # Averaging Points
        }
        
        # Return the PNAConfig with the dynamically retrieved values
        return PNAConfig(
            s_parameter=config_values.get("s_parameter"),
            cal_set=config_values.get("cal_set"),
            source_power=float(config_values.get("source_power")),
            start_frequency=float(config_values.get("start_frequency")),
            stop_frequency=float(config_values.get("stop_frequency")),
            if_bandwidth=float(config_values.get("if_bandwidth")),
            sweep_points=int(config_values.get("sweep_points")),
            averaging_points=int(config_values.get("averaging_points")),
        )
    
    def set_config_values(self, PNAConfig: PNAConfig): 
        config_dict = PNAConfig.to_dict()
        config_dict['start_frequency'] = config_dict['start_frequency']/self.GHz_to_Hz
        config_dict['stop_frequency'] = config_dict['stop_frequency']/self.GHz_to_Hz 

        # Create new dictionary with renamed keys
        renamed = {self.key_map.get(k, k): v for k, v in config_dict.items()}
        self.gui.set_values(renamed)
    
    def set_calsets(self, calsets: list):
        self.gui.update_calibration_options(calsets)