from gui.GRBLConfigView import GRBLConfigView
from data import AxesConfig

class GRBLConfigViewController:
    UI_FONT = ("Arial", 8, "bold")
    SPINBOX_WIDTH = 8
    PADX = 5
    PADY = 5
    MAX_COLUMN_WIDTH = 150  # Max width for column
    COLUMN_WEIGHT = 1
    ROW_WEIGHT = 1
    
    row_labels = ["X", "Y", "Z", "Polar", "Azimuth", "Elevation"]
    col_labels = ["Start", "Stop", "Resolution"]
    
    row_count = len(row_labels) +1 
    col_count = len(col_labels) +1
    
    # Format: (start, lower bound, upper bound, increment)
    spinbox_settings = {
        ("X", "Start"): (0, -100, 100, 1),
        ("X", "Stop"): (0, -100, 100, 1),
        ("X", "Resolution"): (1, 0, 100, 1),
        ("Y", "Start"): (0, 0, 100, 1),
        ("Y", "Stop"): (0, 0, 100, 1),
        ("Y", "Resolution"): (1, 0, 100, 1),
        ("Z", "Start"): (0, 0, 100, 1),
        ("Z", "Stop"): (0, 0, 100, 1),
        ("Z", "Resolution"): (1, 0, 100, 1),
        ("Polar", "Start"): (0, 0, 100, 1),
        ("Polar", "Stop"): (0, 0, 100, 1),
        ("Polar", "Resolution"): (1, 0, 100, 1),
        ("Azimuth", "Start"): (0, -90, 270, 1),
        ("Azimuth", "Stop"): (0, -90, 360, 1),
        ("Azimuth", "Resolution"): (1, 0, 100, 1),
        ("Elevation", "Start"): (0, 0, 100, 1),
        ("Elevation", "Stop"): (0, 0, 100, 1),
        ("Elevation", "Resolution"): (1, 0, 100, 1),
    }
    
    def __init__(self, parent):
        settings = {
            "font": self.UI_FONT,
            "spinbox_width": self.SPINBOX_WIDTH,
            "padx": self.PADX,
            "pady": self.PADY,
            "max_column_width": self.MAX_COLUMN_WIDTH,
            "row_labels": self.row_labels,
            "column_labels": self.col_labels,
            "row_count": self.row_count,
            "column_count": self.col_count,
            "spinbox_settings": self.spinbox_settings,
            "column_weight": self.COLUMN_WEIGHT,
            "row_weight": self.ROW_WEIGHT,
        }
        
        self.gui = GRBLConfigView(parent, settings)  # Create an instance of MovementSettingsUI
        
        
    def get_config_values(self):
        
        # Get the parameters from the GUI
        params = self.gui.get_parameters()
        
        # Create a new Axes object to hold the axis components
        axes = AxesConfig.AxesConfig()
        
        # Populate the axis components with the values from the GUI
        axes.X.start = params.get("X Start")
        axes.X.stop = params.get("X Stop")
        axes.X.resolution = params.get("X Resolution")
        
        axes.Y.start = params.get("Y Start")
        axes.Y.stop = params.get("Y Stop")
        axes.Y.resolution = params.get("Y Resolution")
        
        axes.Z.start = params.get("Z Start")
        axes.Z.stop = params.get("Z Stop")
        axes.Z.resolution = params.get("Z Resolution")
        
        axes.Polar.start = params.get("Polar Start")
        axes.Polar.stop = params.get("Polar Stop")
        axes.Polar.resolution = params.get("Polar Resolution")
        
        axes.Azimuth.start = params.get("Azimuth Start")
        axes.Azimuth.stop = params.get("Azimuth Stop")
        axes.Azimuth.resolution = params.get("Azimuth Resolution")
        
        axes.Elevation.start = params.get("Elevation Start")
        axes.Elevation.stop = params.get("Elevation Stop")
        axes.Elevation.resolution = params.get("Elevation Resolution")
        
        # Create a new GRBLConfig object with the populated axis data
        return axes