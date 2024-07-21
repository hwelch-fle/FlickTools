import sys
from pathlib import Path
from importlib import reload

# Manually add the path to the root of the project
ROOT = str(Path(__file__).parents[2].absolute())

# Insert the module roots to the system path
sys.path.insert(0, ROOT) # ../pytframe2
sys.path.insert(1, rf"{ROOT}\tools") # ../pytframe2/tools
sys.path.insert(2, rf"{ROOT}\utils") # ../pytframe2/utils
# NOTE: Add more module paths here if needed

# Import dynamic modules with pyt_reload prefix
import utils.reloader as pyt_reload_reloader 
import utils.arcpy_tools as pyt_reload_arcpy_tools
import utils.tool as pyt_reload_tool

# Inline reloader of dynamic modules
[
    print(f"Reloaded {reload(module).__name__}") 
    for module_name, module in globals().items() 
    if module_name.startswith("pyt_reload")
]

# Import the Tool Importer function
from utils.reloader import import_tools
from utils.tool import Tool

TOOLS =\
    {
        "project": 
            [
                "UniqueValuesInField",
                "SelectRandomByCount",
                "ZoomToTRS",
                "FieldDomains",
                "ZoomToHUC",
            ],
    }

# Import all tools from the TOOLS dictionary
IMPORTS: list[type[Tool]] = import_tools(TOOLS)

class Toolbox(object):
    def __init__(self):
        """Define the toolbox (the name of the toolbox is the name of the .pyt file)."""
        
        self.label = "FlickTools"
        self.alias = "FlickTools"
        
        # List of tool classes associated with this toolbox
        self.tools = TOOLS
