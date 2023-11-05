from importlib import reload
from traceback import format_exc

import utils.dev
reload(utils.dev)
from utils.dev import buildDevError

import utils.arcpy_tools
reload(utils.arcpy_tools)

# This should be a function or loop of some kind.
try:
    import tools.project.UniqueValuesInField
    reload(tools.project.UniqueValuesInField)
    from tools.project.UniqueValuesInField import UniqueValuesInField
except ImportError:
    UniqueValuesInField = buildDevError("Unique Values In Field", format_exc())

try:
    import tools.project.SelectRandomByCount
    reload(tools.project.SelectRandomByCount)
    from tools.project.SelectRandomByCount import SelectRandomByCount
except ImportError:
    SelectRandomByCount = buildDevError("Select Random By Count", format_exc())

try:
    import tools.project.ZoomToTRS
    reload(tools.project.ZoomToTRS)
    from tools.project.ZoomToTRS import ZoomToTRS
except ImportError:
    ZoomToTRS = buildDevError("Select Random By Count", format_exc())

try:
    import tools.project.FieldDomains
    reload(tools.project.FieldDomains)
    from tools.project.FieldDomains import FieldDomains
except ImportError:
    FieldDomains = buildDevError("Field Domains", format_exc())

try:
    import tools.project.ZoomToHUC
    reload(tools.project.ZoomToHUC)
    from tools.project.ZoomToHUC import ZoomToHUC
except ImportError:
    ZoomToHUC = buildDevError("Calculate Fish Presence Fields", format_exc())

class Toolbox(object):
    def __init__(self):
        """Define the toolbox (the name of the toolbox is the name of the .pyt file)."""
        
        self.label = "FlickTools"
        self.alias = "FlickTools"
        
        # List of tool classes associated with this toolbox
        self.tools = [UniqueValuesInField, 
                      SelectRandomByCount, 
                      ZoomToTRS,
                      FieldDomains,
                      ZoomToHUC]
