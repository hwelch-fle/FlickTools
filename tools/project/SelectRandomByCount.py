import arcpy
import random

import utils.archelp as archelp
from utils.tool import Tool

class SelectRandomByCount(Tool):
    """Tool Definition"""
    
    def __init__(self) -> None:
        """
        Selects a random subset of rows in a given feature. 
        
        Credit for portions of this tool can be found at: https://gis.stackexchange.com/questions/78251/how-to-randomly-subset-x-of-selected-points

        @self.project: arcpy project object
        @self.project_location: path to the project
        @self.project_name: name of the project
        @self.default_gdb: path to the default gdb
        @self.params: tool parameters (set with archelp.get_parameters())
        """
        # Initialize the parent class
        super().__init__()
                
        # Overrides
        self.label = "Select Random By Count"
        self.description = "Selects a random subset of rows in a given feature."
        self.category = "General"
        
        # Parameters
        self.params = {}
        
        return
    
    def getParameterInfo(self) -> list:
        """
        Define parameter definitions
        """

        p_input_feautres = arcpy.Parameter(
            displayName = "Input Features",
            name = "input_features",
            datatype = "GPFeatureLayer",
            parameterType = "Required",
            direction = "Input")
        
        p_subset_count = arcpy.Parameter(
            displayName = "Subset Count",
            name = "subset_count",
            datatype = "GPLong",
            parameterType = "Required",
            direction = "Input")
        
        p_selected_feautres = arcpy.Parameter(
            displayName = "Feature With Selection",
            name = "selected_features",
            datatype = "GPFeatureLayer",
            parameterType = "Derived",
            direction = "Output")
        p_selected_feautres.parameterDependencies = [p_input_feautres.name]
        p_selected_feautres.schema.clone = True

        p_selected_count = arcpy.Parameter(
            displayName = "Count",
            name = "selected_count",
            datatype = "GPLong",
            parameterType = "Derived",
            direction = "Output")

        return [p_input_feautres, p_subset_count, p_selected_feautres, p_selected_count]

    def updateMessages(self, parameters: list[arcpy.Parameter]) -> None:
        """
        Modify the messages created by internal validation for each tool
        parameter.  This method is called after internal validation.
        """

        if (parameters[0].value != None) and (parameters[1].value != None) and (int(parameters[1].value) > int(arcpy.management.GetCount(parameters[0].value)[0])):
            parameters[1].setWarningMessage("Subset Count is greater than the number of rows in Input Features.")

        return

    def execute(self, parameters: list[arcpy.Parameter], messages: list) -> None:
        """The source code of the tool."""

        # Get parameter and row count values
        input_features = parameters[0].valueAsText
        subset_count = int(parameters[1].valueAsText)
        layer_count = int(arcpy.management.GetCount(input_features)[0])
    
        # Correct subset count if entered value is greater than the number of rows in the input features
        if layer_count < subset_count:
            subset_count = layer_count
        
        # Select subset from the input features
        #
        # Credit for this portion of the tool can be found at:
        #   https://gis.stackexchange.com/questions/78251/how-to-randomly-subset-x-of-selected-points
        if subset_count != 0:
            oids = [oid for oid, in arcpy.da.SearchCursor (input_features, "OID@")]
            oidFldName = arcpy.Describe(input_features).OIDFieldName
            path = arcpy.Describe(input_features).path
            delimOidFld = arcpy.AddFieldDelimiters(path, oidFldName)
            randOids = random.sample(oids, subset_count)
            oidsStr = ", ".join(map(str, randOids))
            sql = "{0} IN ({1})".format(delimOidFld, oidsStr)
            selected_features = arcpy.SelectLayerByAttribute_management (input_features, "", sql)

        # Update derived parameters and print message to geoprocessing window
        parameters[2].value = selected_features
        parameters[3].value = int(arcpy.management.GetCount(parameters[2].value)[0])
        arcpy.AddMessage(f"Number of selected features = {parameters[3].valueAsText}")

        return