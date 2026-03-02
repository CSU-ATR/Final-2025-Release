from matplotlib.backends.backend_tkagg import NavigationToolbar2Tk
from graphing.ToolbarSettings import ToolbarSettings
from graphing.ToolbarDataInfo import ToolbarDataInfo
from graphing.ToolbarExportSTL import ToolbarExportSTL
from graphing.PlotController import PlotController
from data.DataManager import DataManager

class ToolbarCombined(NavigationToolbar2Tk):
    def __init__(self, canvas, window, plot_controller: PlotController, datamanager: DataManager):
        super().__init__(canvas, window)
        self.settings_icon = ToolbarSettings(self, plot_controller)
        self.data_info_icon = ToolbarDataInfo(self, plot_controller, self.settings_icon.update_frequency_slider, datamanager)
        self.export_stl_icon = ToolbarExportSTL(self, plot_controller)
