from dataclasses import dataclass, asdict

@dataclass
class PNAConfig:
    """A data class to hold user defined configurations to be sent to the PNA for a scan"""
    cal_set: str = None
    s_parameter: str = None            # S Parameter in S11, S12, S21, S22
    source_power: float = None         # Source Power in dBm
    start_frequency: float = None      # Start Frequency in Hz
    stop_frequency: float = None       # Stop Frequency in Hz
    if_bandwidth: float = None         # IF Bandwidth in Hz
    sweep_points: int = None           # Number of Sweep Points
    averaging_points: int = None       # Number of Averaging Points
    
    def __repr__(self):
        return (f"Scan Data\n"
                f"Calibration {self.cal_set}\n"
                f"S Parameter {self.s_parameter}\n"
                f"Source Power {self.source_power}\n"
                f"Start Frequency {self.start_frequency}\n"
                f"Stop Frequency {self.stop_frequency}\n"
                f"IF Bandwidth {self.if_bandwidth}\n"
                f"Sweep Points {self.sweep_points}\n"
                f"Averaging Points {self.averaging_points}\n") 
    
    def to_dict(self):
        return asdict(self)
