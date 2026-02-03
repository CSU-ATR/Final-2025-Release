from data.AxesConfig import AxesConfig, Axis_Components
from data.PNAConfig import PNAConfig

import os
import json
from dataclasses import asdict

class ConfigStorage():
    CONFIG_DIR = 'configurations'


    def __init__(self):
        
        # Ensure the configurations directory exists
        if not os.path.exists(self.CONFIG_DIR):
            os.makedirs(self.CONFIG_DIR)
            print("JSON")
    def save_pna_config(self, config: PNAConfig, filename: str):
        """Saves a PNAConfig object to a JSON file in the configurations folder."""
        filepath = os.path.join(self.CONFIG_DIR, filename)
        with open(filepath, 'w') as file:
            print("dumping JSON")
            json.dump(asdict(config), file, indent=4)

    def load_pna_config(self, filename: str) -> PNAConfig:
        """Loads a PNAConfig object from a JSON file in the configurations folder."""
        filepath = os.path.join(self.CONFIG_DIR, filename)
        with open(filepath, 'r') as file:
            print("Returning JSON")
            data = json.load(file)
        return PNAConfig(**data)
    
    def save_axes_config(self, config: AxesConfig, filename: str):
        """Saves an AxesConfig object to a JSON file in the configurations folder."""
        filepath = os.path.join(self.CONFIG_DIR, filename)
        with open(filepath, 'w') as file:
            json.dump(asdict(config), file, indent=4)

    def load_axes_config(self, filename: str) -> AxesConfig:
        """Loads an AxesConfig object from a JSON file in the configurations folder."""
        filepath = os.path.join(self.CONFIG_DIR, filename)
        with open(filepath, 'r') as file:
            data = json.load(file)
        config = AxesConfig()
        for axis in ['X', 'Y', 'Z', 'Polar', 'Azimuth', 'Elevation']:
            setattr(config, axis, Axis_Components(**data[axis]))
        return config