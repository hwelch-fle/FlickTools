import arcpy
import requests

import utils.arcpy_tools as archelp
from utils.constants.ftconstants import STATES
from utils.tool import Tool

class ZoomToHUC(Tool):
    """Tool Definition"""
    
    def __init__(self) -> None:
        """
        Zoom to a HUC.

        @self.project: arcpy project object
        @self.project_location: Path to the project
        @self.project_name: Name of the project
        @self.default_gdb: Path to the default gdb
        @self.params: Tool parameters (set with archelp.get_parameters())
        """
        
        # Initialize the parent class
        super().__init__()
                
        # Overrides
        self.label = "Zoom To HUC"
        self.description = "Zoom to a HUC."
        self.category = "General"
        
        # Parameters
        self.params = {}

        # USGS feature layer numbers for each HUC layer
        self.huc_layers = {"HUC2": 1, "HUC4": 2, "HUC6": 3, "HUC8": 4,
                           "HUC10": 5, "HUC12": 6, "HUC14": 7, "HUC16": 8}
        
        return
    
    def getParameterInfo(self) -> list:
        """Define parameter definitions."""

        state = arcpy.Parameter(
            displayName = "State",
            name = "state",
            datatype = "GPString",
            parameterType = "Required",
            direction = "Input")
        state.filter.type = "ValueList"
        state.filter.list = list(STATES.keys())
        state.value = "Oregon"
        
        huc_level = arcpy.Parameter(
            displayName = "Level",
            name = "huc_level",
            datatype = "GPString",
            parameterType = "Required",
            direction = "Input")
        huc_level.filter.type = "ValueList"
        huc_level.filter.list = list(self.huc_layers.keys())
        huc_level.value = "HUC8"
        
        huc = arcpy.Parameter(
            displayName = "Watershed",
            name = "huc",
            datatype = "GPString",
            parameterType = "Required",
            direction = "Input")
        huc.filter.type = "ValueList"

        return [state, huc_level, huc]
    
    def updateParameters(self, parameters: list[arcpy.Parameter]) -> None:
        """
        Modify the values and properties of parameters before internal
        validation is performed. This method is called whenever a parameter
        has been changed.
        """

        # Allows reference to parameters by name instead of index
        self.params = archelp.get_params(parameters)

        if not self.params["state"].hasBeenValidated or not self.params["huc_level"].hasBeenValidated:
            # Get all HUCs in current state from USGS REST 
            # Probably need a try except around this
            layer = self.huc_layers[self.params["huc_level"].valueAsText]
            state = STATES[self.params["state"].valueAsText]
            huc_level = self.params["huc_level"].valueAsText.lower()
            base_url = f"https://hydrowfs.nationalmap.gov/arcgis/rest/services/wbd/MapServer/{layer}/query"
            query = {
                "where": f"states LIKE '%{state}%'",
                "returnGeometry": "false",
                "outFields": f"{huc_level},name",
                "f": "pjson"}
            resp = requests.get(base_url, query).json()

            # Parse response and set list for huc field
            layer_list = [f"{i['attributes']['name']} [{i['attributes'][huc_level]}]" for i in resp['features']]
            self.params["huc"].filter.list = sorted(layer_list)
            self.params["huc"].value = None

        return

    def execute(self, parameters: list[arcpy.Parameter], messages: list) -> None:
        """The source code of the tool."""

        # Get a dictionary of parsed parameters and create reference to the current map view.
        self.params = archelp.get_params(parameters)
        current_view = self.project.activeView

        if current_view is not None:
            # Get extent of specified HUC from USGS REST
            # Probably should put a try block in here
            layer = self.huc_layers[self.params["huc_level"].valueAsText]
            huc_level = self.params["huc_level"].valueAsText.lower()
            huc = self.params["huc"].valueAsText.split(" ")[-1][1:-1]
            base_url = f"https://hydrowfs.nationalmap.gov/arcgis/rest/services/wbd/MapServer/{layer}/query"
            query_params = {"where": f"{huc_level} = '{huc}'",
                            "returnExtentOnly": "true",
                            "outSR": f"{current_view.map.spatialReference.factoryCode}",
                            "f": "pjson"}
            resp = requests.get(base_url, query_params).json()
            ext_list = [resp['extent'][i] for i in ['xmin','ymin','xmax','ymax']]

            # Print some value messages to the geoprocessing window.
            archelp.msg(f"WHERE: {query_params['where']}\nWKID: {query_params['outSR']}\nEXTENT: {ext_list}")
            
            # Set the map extent using the extent recieved from the REST request if it is valid.
            if "NaN" not in ext_list:
                ext = arcpy.Extent(XMin = resp['extent']['xmin'], YMin = resp['extent']['ymin'], 
                                   XMax = resp['extent']['xmax'], YMax = resp['extent']['ymax'], 
                                   spatial_reference = arcpy.SpatialReference(resp['extent']['spatialReference']['latestWkid']))
                current_view.camera.setExtent(ext)
            else:
                archelp.msg("Error: Invalid extent. Check tool parameters.", "error")
        else:
            archelp.msg("Error: No map view selected. Select a map view before running tool.", "error")

        return