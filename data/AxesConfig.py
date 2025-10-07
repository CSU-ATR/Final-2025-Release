from dataclasses import dataclass

@dataclass
class Axis_Components:
    """Helper data class to hold the values for each axis
    Describes the start and stop position of the movement, as well as the resolution required
    Has secondary data for the axis name and its gcodename"""
    start: float = 0.0
    stop: float = 0.0
    resolution: float = 0.0
    gCodeName: str = None
    axisName: str = None
    
    # Custom print for the data in an axis
    def __repr__(self):
        return (
                f"----------------------------------\n"
                f"Axis: {self.axisName}\n"
                f"Start: {self.start}\n"
                f"Stop: {self.stop}\n"
                f"Resolution: {self.resolution}\n"
                f"GCodeName {self.gCodeName}")

@dataclass
class AxesConfig:
    """Data Structure to hold a users defined movements of the GRBL axes positioning system
    Each Axis is a specific set of Axis_components"""
    X: Axis_Components
    Y: Axis_Components
    Z: Axis_Components
    Polar: Axis_Components
    Azimuth: Axis_Components
    Elevation: Axis_Components

    def __init__(self):
        # Initialize the components if they aren't already initialized
        self.X = Axis_Components()
        self.Y = Axis_Components()
        self.Z = Axis_Components()
        self.Polar = Axis_Components()
        self.Elevation = Axis_Components()
        self.Azimuth = Axis_Components()
        
        # Define the G-code and axis names
        self.X.gCodeName = "X"
        self.X.axisName = "X"
        
        self.Y.gCodeName = "Y"
        self.Y.axisName = "Y"
        
        self.Z.gCodeName = "Z"
        self.Z.axisName = "Z"
        
        self.Polar.gCodeName = "A"
        self.Polar.axisName = "Polar"
        
        self.Azimuth.gCodeName = "B"
        self.Azimuth.axisName = "Azimuth"
        
        self.Elevation.gCodeName = "C"
        self.Elevation.axisName = "Elevation"
        
    # Make Axii iterable by returning components as a list of axes
    def __iter__(self):
        return iter([self.X, self.Y, self.Z, self.Polar, self.Azimuth, self.Elevation])

    # Custom printout of all the axes in the datastructure
    def __repr__(self):
        return (f"Movement Settings\n"
                f"{self.X}\n"
                f"{self.Y}\n"
                f"{self.Z}\n"
                f"{self.Polar}\n"
                f"{self.Azimuth}\n"
                f"{self.Elevation}\n")
        
    # Return the GCodeName for an axis
    def getGCodeName(self):
        return self.gCodeName
