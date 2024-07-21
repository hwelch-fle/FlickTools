import arcpy
import os
import utils.archelp as archelp

class Tool(object):
    """
    Base class for all tools that use python objects to build parameters,
    any unused functions can be left blank in a tool that implements this class
    If you need to overwrite a function, just redefine it in the tool.
    any parameters that you think will be useful in multiple tools should be
    defined here so they're available to all tools that inherit this class
    """
    def __init__(self) -> None:
        """
        Tool Description

        @self.project: arcpy project object
        @self.project_location: path to the project
        @self.project_name: name of the project
        @self.default_gdb: path to the default gdb
        @self.params: tool parameters (set with archelp.get_parameters())
        """
        
        # Tool parameters
        self.label = "Tool"
        self.description = "Base class for all tools that use python objects to build parameters"
        self.canRunInBackground = False
        self.category = "Unassigned"
        
        # Project variables
        self.project = arcpy.mp.ArcGISProject("CURRENT")
        self.project_location = self.project.homeFolder
        self.project_name = os.path.basename(self.project_location)
        
        # Database variables
        self.default_gdb = self.project.defaultGeodatabase
        
        # Parameters
        self.params = {}
        
        return

    def getParameterInfo(self) -> list:
        """Define parameter definitions"""
        return []
    
    def isLicensed(self) -> bool:
        """Set whether tool is licensed to execute."""
        return True
    
    def updateParameters(self, parameters: list[arcpy.Parameter]) -> None:
        """
        Modify the values and properties of parameters before internal
        validation is performed. This method is called whenever a parameter
        has been changed.
        """
        return
    
    def updateMessages(self, parameters: list[arcpy.Parameter]) -> None:
        """
        Modify the messages created by internal validation for each tool
        parameter. This method is called after internal validation.
        """
        return
    
    def execute(self, parameters: list[arcpy.Parameter], messages: list) -> None:
        """The source code of the tool."""
        return
    
    def postExecute(self, parameters: list[arcpy.Parameter]) -> None:
        """
        This method takes place after outputs are processed and
        added to the display.
        """
        return