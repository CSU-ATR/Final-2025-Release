from gui.GUIManager import GUIManager

from interfaces.InterfaceManager import InterfaceManager
from procedures.Commands import Commands
from data.DataManager import DataManager
USE_THREADING = False  # Set to False to disable threading

if USE_THREADING:
    import threading
import atexit

#I am so sorry for anyone that has to fix this garbage. there is a lot of cool things and interesting structure developed, 
# however its current implementation needs one final refactor and pass to actually accomplish the vision of this program

#Suggestions would be to further decouple components
# change architecture to be a pyramid of dependancies rather than current tree approach

#I hope to someday secretly deploy the fixed version post graduation but who knows.
#If you want help you can try to contact me at tuclaure@gmail.com, but uncertain how long ill remember shit about this
#Dont judge too harshly :(

def on_exit():
    """Define Exit behavior even if Unexpected"""
    try:
        if USE_THREADING:
            stop_event.set()

        interfaces.close_connections()
        print("connections closed")
    except Exception as e:
        pass

def background_initialization():
    """Tasks that need to be run in the background as GUI Initializes"""
    try:
        interfaces.initialize_connections()
        if interfaces.pna.connection:
            cal_sets = interfaces.get_pna_calsets()
            if cal_sets:
                datamanager.PNAConfig.cal_set = cal_sets
    except Exception as e:
        pass
datamanager = DataManager()
interfaces = InterfaceManager()
commands = Commands(interfaces, datamanager)
guis = GUIManager(commands, datamanager.PNAConfig.cal_set)
commands.set_root(guis.root)


commands.set_axes_config_get_function(guis.GRBLConfigViewController.get_config_values)
commands.set_pna_config_get_function(guis.PNAConfigViewController.get_config_values)

atexit.register(on_exit) #Register the function to close with
if USE_THREADING:
    stop_event = threading.Event()  # Create a threading event for closing

if USE_THREADING:
    initialization_thread = threading.Thread(target=background_initialization, daemon=True)
    initialization_thread.start()
else:
    background_initialization()  # Run directly if threading is off

# Main GUI loop
guis.root.mainloop()
