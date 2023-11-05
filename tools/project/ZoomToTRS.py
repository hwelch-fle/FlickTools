import arcpy
import requests

import utils.arcpy_tools as archelp
from utils.tool import Tool

class ZoomToTRS(Tool):
    """Tool Definition"""
    
    def __init__(self) -> None:
        """
        Zoom to a specific Township, Section, and Range.

        @self.project: arcpy project object
        @self.project_location: path to the project
        @self.project_name: name of the project
        @self.default_gdb: path to the default gdb
        @self.params: tool parameters (set with archelp.get_parameters())
        """
        # Initialize the parent class
        super().__init__()
                
        # Overrides
        self.label = "Zoom To TRS"
        self.description = "Zoom to a specific Township, Section, and Range."
        self.category = "General"
        
        # Parameters
        self.params = {}
        
        return
    
    def getParameterInfo(self) -> list:
        """Define parameter definitions."""

        use_full_address = arcpy.Parameter(
            displayName = "Enter as complete PLSS address",
            name = "use_full_address",
            datatype = "Boolean",
            parameterType = "Required",
            direction = "Input")
        use_full_address.value = False

        full_address = arcpy.Parameter(
            displayName = "Full Address",
            name = "full_address",
            datatype = "GPString",
            parameterType = "Required",
            direction = "Input")
        # full_address.value = "@"
        # full_address.enabled = False
        
        address_township = arcpy.Parameter(
            displayName = "Township",
            name = "address_township",
            datatype = "GPString",
            parameterType = "Required",
            direction = "Input")

        address_range = arcpy.Parameter(
            displayName = "Range",
            name = "address_range",
            datatype = "GPString",
            parameterType = "Required",
            direction = "Input")
        
        address_section = arcpy.Parameter(
            displayName = "Section",
            name = "address_section",
            datatype = "GPString",
            parameterType = "Optional",
            direction = "Input")

        return [full_address, address_township, address_range, address_section, use_full_address]

    def updateParameters(self, parameters: list[arcpy.Parameter]) -> None:
        """
        Modify the values and properties of parameters before internal
        validation is performed.  This method is called whenever a parameter
        has been changed.
        """
        
        # Allows reference to parameters by name instead of index
        local_params = archelp.get_params(parameters)

        # Set visibility for appropriate parameters depending on whether or not the "Enter as complete 
        # PLSS address" checkbox is checked and set values to get around error checking
        #
        # This function uses the "@" character to fill values in required parameters if they are not
        # already filled by the user.
        if local_params["use_full_address"].value:
            local_params["full_address"].enabled = True
            if local_params["full_address"].valueAsText == "@": 
                local_params["full_address"].value = None

            for f in ["address_township", "address_range", "address_section"]: 
                local_params[f].enabled = False
                if not local_params[f].altered: 
                    local_params[f].value = "@"
        elif not local_params["use_full_address"].value:
            local_params["full_address"].enabled = False
            if not local_params["full_address"].altered: 
                local_params["full_address"].value = "@"

            for f in ["address_township", "address_range", "address_section"]: 
                local_params[f].enabled = True
                if local_params[f].valueAsText == "@": 
                    local_params[f].value = None
        
        # Standardize formatting for partial address fields
        for f in ["address_township", "address_range", "address_section"]:
            if local_params[f].valueAsText not in [None, "@"]: 
                local_params[f].value = local_params[f].valueAsText.upper()
                if local_params[f].valueAsText.startswith("0"):
                    local_params[f].value = local_params[f].valueAsText[1:]

        # Standardize formatting for complete address field
        if local_params["full_address"].valueAsText not in [None, "@"]:
            local_params["full_address"].value = local_params["full_address"].valueAsText.upper()

        return
    
    def _validateInput(self, input_type: str, value: str) -> bool:
        """
        Ensure that inputs are in a valid format.

        @input_type: Indicates township, section, or range input.
        @value: Value of parameter.
        @return: Bool indicating if input is valid or not.
        """

        # Default error message
        valid = True

        # Split value as needed
        if input_type != "address_section":
            value_char = value[-1:]
            value = value[:-1]

        # Check if input is valid
        if input_type == "address_township" and value_char not in ["N", "S"]:
            valid = False
        elif input_type == "address_range" and value_char not in ["E", "W"]:
            valid = False

        if not value.isnumeric():
            valid = False
        
        return valid
    
    def updateMessages(self, parameters: list[arcpy.Parameter]) -> None:
        """
        Modify the messages created by internal validation for each tool
        parameter. This method is called after internal validation.
        """

        # Allows reference to parameters by name instead of index
        local_params = archelp.get_params(parameters)

        # List of input types to check
        input_types = ["address_township", "address_range", "address_section"]

        # Do some rudimentary error checking to make sure that inputs are at least somewhat correct.
        #
        # Depending on the value of the checkbox, error checking on a field may or may not occur. This
        # happens because some fields are set as required and must be filled with a value. The value
        # of empty fields are set as "@" which does not meet the requirements below.
        if not local_params["use_full_address"].value:
            # Check if each individual address parameter is valid.
            for t in input_types:
                if local_params[t].valueAsText not in [None, "@"] and not self._validateInput(local_params[t].name, local_params[t].valueAsText):
                    local_params[t].setErrorMessage("Input is not valid.")
        elif local_params["use_full_address"].value and local_params["full_address"].valueAsText not in [None, "@"]:
            # Split full address parameter into component parts, removing unnecessary substrings or characters.
            param_string = local_params["full_address"].valueAsText
            for substring in ["R","T","SEC","SECTION"]:
                if substring in param_string: 
                    param_string = param_string.replace(substring, "")
            param_list = [s for s in param_string.split(" ") if s != ""]

            # Check if each component part is valid
            for i in range(len(param_list)):
                if not self._validateInput(input_types[i], param_list[i]):
                    local_params["full_address"].setErrorMessage("Input is not valid.")
                    break
                
        return
    
    def _parseUserInput(self, parameters: dict[str, arcpy.Parameter]) -> dict:
        """
        Parse user input into a dictionary of values.

        @return: Parameters components as a dictionary.
        """
        
        if parameters["use_full_address"].value:
            # Split full address parameter into component parts, removing unnecessary substrings or characters.
            param_string = parameters["full_address"].valueAsText
            for substring in ["R","T","SEC","SECTION"]:
                if substring in param_string: 
                    param_string = param_string.replace(substring, "")
            param_list = [s for s in param_string.split(" ") if s != ""]

            # Add a value for section if one was not provided by the user.
            if len(param_list) < 3: param_list += [None]
        elif not parameters["use_full_address"].value:
            # Collect the township, range, and section parameters into a single list.
            param_list = [parameters[n].valueAsText for n in ["address_township", "address_range", "address_section"]]

        # Build a dictionary of parsed parameters.
        parsed_parameters = {
            "twn": param_list[0][:-1],
            "twn_char": param_list[0][-1:],
            "rng": param_list[1][:-1],
            "rng_char": param_list[1][-1:],
            "sec": param_list[2]}
        
        return parsed_parameters

    def execute(self, parameters: list[arcpy.Parameter], messages: list) -> None:
        """The source code of the tool."""

        # Get a dictionary of parsed parameters and create reference to the current map view.
        parsed_params = self._parseUserInput(archelp.get_params(parameters))
        current_view = self.project.activeView

        if current_view is not None:
            # Set REST parameters depending on whether or not a section has been specified.
            if parsed_params['sec'] == None or parsed_params['sec'] == "":
                url_base = r"https://gis.odf.oregon.gov/ags1/rest/services/Public/PLSS/MapServer/0/query?"
                section_param = ""
            else:
                url_base = r"https://gis.odf.oregon.gov/ags1/rest/services/Public/PLSS/MapServer/1/query?"
                section_param = f" and Section = '{parsed_params['sec']}'"

            # Build a dictionary of REST parameters based on the parsed parameters and map spatial reference.
            query_params = {"where": f"Twn = '{parsed_params['twn']}' and TwnChar = '{parsed_params['twn_char']}' and Rng = '{parsed_params['rng']}' and RngChar = '{parsed_params['rng_char']}'{section_param}",
                            "returnExtentOnly": "true",
                            "outSR": f"{current_view.map.spatialReference.factoryCode}",
                            "f": "pjson"}
            
            # Perform the REST request to get extent of township and range or section.
            # Probably should put a try block in here
            resp = requests.get(url = url_base, params = query_params).json()
            ext_list = [resp['extent'][i] for i in ['xmin','ymin','xmax','ymax']]

            # Print some value messages to the geoprocessing window.
            messages.addMessage(f"WHERE: {query_params['where']}\nWKID: {query_params['outSR']}\nEXTENT: {ext_list}")
            
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