# This tool should probably be rewritten to better organize the data that is read from the input feature
# Relying on the index of multiple lists isn't great

import arcpy
from os import path as os_path
from collections import defaultdict

import utils.archelp as archelp
from utils.tool import Tool

class UniqueValuesInField(Tool):
    """Tool Definition"""
    
    def __init__(self) -> None:
        """
        Finds the values and counts of each unique value in a field and prints the results.

        @self.project: arcpy project object
        @self.project_location: path to the project
        @self.project_name: name of the project
        @self.default_gdb: path to the default gdb
        @self.params: tool parameters (set with archelp.get_parameters())
        """
        # Initialize the parent class
        super().__init__()
                
        # Overrides
        self.label = "Unique Values In Field"
        self.description = "Finds the values and counts of each unique value in a field and prints the results."
        self.category = "General"
        
        # Parameters
        self.params = {}
        
        # Acceptable field types
        self.field_types = ["Short","Long","Single","Double","Text","Date","Integer","SmallInteger","String"]
        
        return
    
    def getParameterInfo(self) -> None:
        """Define parameter definitions."""

        input_features = arcpy.Parameter(
            displayName = "Input Features",
            name = "input_features",
            datatype = ["GPFeatureLayer", "DETable"],
            parameterType = "Required",
            direction = "Input")
        
        fields = arcpy.Parameter(
            displayName = "Field(s) to Summarize",
            name = "fields",
            datatype = "Field",
            parameterType = "Required",
            direction = "Input",
            multiValue = True)
        fields.parameterDependencies = [input_features.name]
        fields.filter.list = self.field_types

        include_counts = arcpy.Parameter(
            displayName = "Include counts",
            name = "include_counts",
            datatype = "Boolean",
            parameterType = "Required",
            direction = "Input")
        include_counts.value = False

        output_as_table = arcpy.Parameter(
            displayName = "Output as Table",
            name = "output_as_table",
            datatype = "Boolean",
            parameterType = "Optional",
            direction = "Input")
        output_as_table.value = False
        
        output_table = arcpy.Parameter(
            displayName = "Output Table",
            name = "output_table",
            datatype = "DETable",
            parameterType = "Optional",
            direction = "Output",
            enabled = False)

        return [input_features, fields, include_counts, output_as_table, output_table]
    
    def updateParameters(self, parameters: list[arcpy.Parameter]) -> None:
        """
        Modify the values and properties of parameters before internal
        validation is performed. This method is called whenever a parameter
        has been changed.
        """

        # Allows reference to parameters by name instead of index
        local_params = archelp.get_params(parameters)

        # If multiple fields have been entered, disable checkbox and output path. Else, enable checkbox
        if local_params["fields"].altered and len(local_params["fields"].valueAsText.split(";")) > 1:
            local_params["output_as_table"].enabled = False
            local_params["output_as_table"].value = False
            local_params["output_table"].enabled = False
        else:
            local_params["output_as_table"].enabled = True
        
        # If checkbox to output as table is enabled and has been checked, enable and autofill path
        if not parameters[3].value:
            parameters[4].enabled = False
        elif parameters[3].enabled and parameters[3].value:
            parameters[4].enabled = True
            
            default_path = os_path.join(arcpy.env.workspace, f"{arcpy.ValidateTableName(parameters[0].valueAsText)}_UniqueValues")
            current_path = parameters[4].valueAsText
            
            if current_path != default_path and current_path != None:
                parameters[4].value = os_path.join(arcpy.env.workspace, arcpy.ValidateTableName(os_path.basename(parameters[4].valueAsText)))
            else:
                parameters[4].value = default_path

        return
    
    def _outputAsTable(self, row_dicts, output_table, input_fields, len_longest_values, count_cb) -> None:
        """
        Generate a new table with the output of the tool.
        """

        # Create table with appropriate fields
        arcpy.SetProgressor("default", "Creating output table...")
        t_path, t_name = os_path.split(output_table)
        arcpy.management.CreateTable(t_path, t_name)
        arcpy.management.AddField(output_table, f"{input_fields[0]}_VALUES", "TEXT", field_length = len_longest_values[0])
        if count_cb: arcpy.management.AddField(output_table, f"{input_fields[0]}_COUNT", "LONG")

        # Set progressor for populating table step
        arcpy.SetProgressor("step", "Populating output table...")
        num_rows = len(row_dicts[0])
        row_pos = 0

        # Set list of fields for insert cursor, removing count field if necessary
        cursor_fields = [f"{input_fields[0]}_VALUES", f"{input_fields[0]}_COUNT"]
        if not count_cb: cursor_fields[:] = [f"{input_fields[0]}_VALUES"]

        # Iterate through rows dicts, adding a row to new table for each key in dictionary and updating progressor
        with arcpy.da.InsertCursor(output_table, cursor_fields) as cursor:
            for row in sorted(row_dicts[0].items()): 
                row_pos += 1
                arcpy.SetProgressorPosition(int((row_pos / num_rows) * 100))
                
                if not count_cb: row = (row[0],)
                cursor.insertRow(row)
        
        return
    
    def _outputAsMessage(self, row_dicts, num_fields, parameters, len_longest_values, count_cb, messages) -> None:
        """
        Print messages to the geoprocssing window with the output of the tool.
        """

        # Collect the list of fields from input and the attributes of those fields
        input_fields = parameters[1].valueAsText.split(";")
        field_attributes = dict([(f.name, f) for f in arcpy.ListFields(parameters[0].valueAsText) if f.name in input_fields])

        # Generate and then print an output for each dictionary in list
        # Might be good to add the field type to each output here
        arcpy.SetProgressor("default", "Generating output message(s)...")
        for i in range(num_fields):
            num_f = 0
            out_message = f"## FIELD: {input_fields[i]}\n     Type: {field_attributes[input_fields[i]].type}\n     Domain: {field_attributes[input_fields[i]].domain}\n\n     "
            
            # Create a new line of five values and append it to the message
            for values in sorted(row_dicts[i].items()):
                out_message = out_message + f"{values[0]}{' ' * (len_longest_values[i] - len(str(values[0])))}"
                if count_cb:
                    out_message = out_message + f": {values[1]: <10}"
                else:
                    out_message = out_message + "    "
                
                num_f += 1
                if num_f == 5:
                    num_f = 0
                    out_message = out_message + "\n     "
                
            if num_f < 5 and i < (num_fields - 1): out_message = out_message + "\n"
            out_message = out_message + "\n"
            messages.addMessage(out_message)

        return

    def execute(self, parameters: list[arcpy.Parameter], messages: list) -> None:
        """
        The source code of the tool.
        """

        # Get parameter values
        input_features = parameters[0].valueAsText
        input_fields = parameters[1].valueAsText.split(";")
        count_cb = parameters[2].value
        output_cb = parameters[3].value
        output_table = parameters[4].valueAsText

        # Define variables to hold number of fields, length of longest field value, and list of dictionaries with
        # each unique value in each of the fields
        num_fields = len(input_fields)
        len_longest_values = [0 for i in range(num_fields)]
        row_dicts = [defaultdict(int) for i in range(num_fields)]

        # Populate the list of dictionaries with unique values in each field and store length of longest field
        arcpy.SetProgressor("step", "Reading input rows...")
        num_rows = int(arcpy.management.GetCount(input_features)[0])
        row_pos = 0
        with arcpy.da.SearchCursor(input_features, input_fields) as cursor:
            for row in cursor:
                row_pos += 1
                arcpy.SetProgressorPosition(int((row_pos / num_rows) * 100))
                for i in range(num_fields):
                    if row[i] == None:
                        f_val = "<Null>"
                    elif str(row[i]) == "":
                        f_val = "<Empty String>"
                    elif str(row[i]) == " ":
                        f_val = "<Space>"
                    elif str(row[i]) == "  ":
                        f_val = "<Double Space>"
                    else:
                        f_val = str(row[i])

                    row_dicts[i][f_val] += 1
                    if len(f_val) > len_longest_values[i]: len_longest_values[i] = len(f_val)

        # Generate different outputs depending on which option user selected
        if output_cb:
            self._outputAsTable(row_dicts, output_table, input_fields, len_longest_values, count_cb)
        elif not output_cb:
            self._outputAsMessage(row_dicts, num_fields, parameters, len_longest_values, count_cb, messages)

        # Allows reference to parameters by name instead of index
        self.params = archelp.get_params(parameters)

        return