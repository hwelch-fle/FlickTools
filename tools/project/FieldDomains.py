import arcpy

import utils.archelp as archelp
from utils.constants.ftconstants import TAB
from utils.tool import Tool

class FieldDomains(Tool):
    """Tool Definition"""
    
    def __init__(self) -> None:
        """
        Displays the domains for one or more fields in a feature.

        @self.project: arcpy project object
        @self.project_location: path to the project
        @self.project_name: name of the project
        @self.default_gdb: path to the default gdb
        @self.params: tool parameters (set with archelp.get_parameters())
        """
        
        # Initialize the parent class
        super().__init__()
                
        # Overrides
        self.label = "Field Domains"
        self.description = "Displays the domains for one or more fields in a feature."
        self.canRunInBackground = False
        self.category = "General"
        
        # Parameters
        self.params = {}
        
        return
    
    def getParameterInfo(self) -> list:
        """Define parameter definitions."""

        input_features = arcpy.Parameter(
            displayName = "Input Features",
            name = "input_features",
            datatype = ["GPFeatureLayer", "DEFeatureClass"],
            parameterType = "Required",
            direction = "Input")
        
        fields = arcpy.Parameter(
            displayName = "Field(s)",
            name = "fields",
            datatype = "Field",
            parameterType = "Required",
            direction = "Input",
            multiValue = True)
        fields.parameterDependencies = [input_features.name]

        return [input_features, fields]

    def execute(self, parameters:list[arcpy.Parameter], messages:list) -> None:
        """The source code of the tool."""
        
        # Allows reference to parameters by name instead of index
        self.params = archelp.get_params(parameters)
      
        # Get all domains objects and filtered field objects in input features
        feature_properties = arcpy.Describe(self.params["input_features"].valueAsText)
        domains = {d.name: d for d in arcpy.da.ListDomains(feature_properties.path)}
        fields = [f for f in feature_properties.fields if f.name in self.params["fields"].valueAsText.split(";")]

        # Build output for each input field
        out_message = []
        num_fields = len(fields)

        for counter, field in enumerate(fields):
            out_message.append(f"## FIELD: {field.aliasName} [{field.name}]\n")
            
            # Build info about domain if there is one
            if field.domain in domains:
                domain = domains[field.domain]

                out_message.append((f"{TAB}Domain: {domain.name}\n"
                                    f"{TAB}Type: {domain.domainType}\n"
                                    f"{TAB}Nullable: {field.isNullable}\n\n"))
                
                if domain.domainType == "CodedValue":
                    out_message.append(archelp.print_dict(domain.codedValues, tab_num=1))
                elif domain.domainType == "Range":
                    out_message.append((f"{TAB}Min: {domain.range[0]}\n"
                                        f"{TAB}Max: {domain.range[1]}\n"))
            else:
                out_message.append(f"{TAB}Domain: <None>\n")

            # Print an extra return if we have more fields to print
            if counter < num_fields - 1: out_message.append("\n")

        # Print output message
        archelp.msg("".join(out_message))
        
        return