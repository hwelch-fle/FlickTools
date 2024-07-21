import arcpy
import os
import builtins

from typing import Any, Generator, Literal
from enum import Enum
import utils.constants.ftconstants as ftconstants

# Use this module for any helper functions or classes that you want to use 
# between tools. If you find yourself re-impelementing the same function in 
# multiple tools, consider moving it here.

class controlCLSID(Enum):
    """ See [Parameter Controls](https://pro.arcgis.com/en/pro-app/latest/arcpy/geoprocessing_and_python/parameter-controls.htm)
        documentation for more information on parameter controls.
    """
    EXCLUDE_INTERSECT_AND_UNION = '{15F0D1C1-F783-49BC-8D16-619B8E92F668}'
    SLIDER_RANGE = '{C8C46E43-3D27-4485-9B38-A49F3AC588D9}'
    LARGE_NUMBER = '{7A47E79C-9734-4167-9698-BFB00F43AE41}'
    COMPOSITE_SWITCH = '{BEDF969C-20D2-4C41-96DA-32408CA72BF6}'
    MULTILINE = '{E5456E51-0C41-4797-9EE4-5269820C6F0E}'
    MULTIVALUE_CHECKBOX = '{172840BF-D385-4F83-80E8-2AC3B79EB0E0}'
    MULTIVALUE_CHECK_ALL = '{38C34610-C7F7-11D5-A693-0008C711C8C1}'
    FEATURE_LAYER_CREATE = '{60061247-BCA8-473E-A7AF-A2026DDE1C2D}'
    HORIZONTAL_VALUE_TABLE = '{1AA9A769-D3F3-4EB0-85CB-CC07C79313C8}'
    SINGLE_VALUE_TABLE = '{1A1CA7EC-A47A-4187-A15C-6EDBA4FE0CF7}'

def row_to_dict(cursor: arcpy.da.SearchCursor) -> Generator[dict[str, Any], None, None]:
    """
    Converts a arcpy.da Cursor row to a dictionary

    @cursor: The cursor to convert

    Usage:
    >>> cursor = arcpy.da.SearchCursor(<features>, <headers>, <sql_clause>)
    >>> for row in row_to_dict(cursor):
    >>>     print(row['fieldName'])
    >>> del cursor
    """

    for row in cursor:
        yield dict(zip(cursor.fields, row))

def get_databases(location: str, database_name: str="None") -> list:
    """
    Gets all the databases in the location

    @location: The location to search for databases
    @database_name: The name of the database to search for (default is None)
    @return: A list of databases
    """

    databases = []
    for root, dirs, files in os.walk(location):
        for dir in dirs:
            if dir.endswith(".gdb"):
                databases.append(os.path.join(root, dir))
    if database_name != "None":
        databases = [x for x in databases if x.lower().endswith(database_name)]
    return databases

def walk_database(database: str, datatype: str=None, dataset: str=None) -> dict[str]:
    """
    Walks the database and returns a list of all the feature classes

    @database: The database to walk (path to the database)
    @datatype: The datatype to search for (all, table, featureclass)
    @dataset: The dataset to search for
    @return: A dictionary of feature classes 
             (In the format {<feature class name>:<feature class path>})
    """

    feature_classes = []
    arcpy.env.workspace = database
    feature_classes = [os.path.join(database, dataset, fc) 
                       for fc in arcpy.ListFeatureClasses(feature_dataset=dataset, feature_type=datatype)]
    
    return {os.path.basename(path):path for path in feature_classes}

def get_tables(database: str) -> dict[str]:
    """
    Gets all the tables in the database

    @database: The database to search
    @return: A dictionary of tables 
             (In the format {<table name>: table path>})
    """

    tables = []
    arcpy.env.workspace = database
    tables = [os.path.join(database, table) for table in arcpy.ListTables()]
    return {os.path.basename(path):path for path in tables}

def get_project(project_location: str) -> str:
    """
    Gets the project from the project path

    @project: The project path
    @raises Exception: If the project is not an ArcGIS Pro project file
    @return: The project
    """

    if not project_location.endswith(".aprx"):
        raise Exception("Project must be an ArcGIS Pro project")
    return arcpy.mp.ArcGISProject(project_location)
    
def msg(message: str="", level: str="message") -> None:
    """
    Prints a message to the console and adds a message to ArcGIS Pro

    @message: The message to print
    @level: The level of the message (message, warning, error)
    """
    
    message = str(message)
    level = str(level).lower()
    level = ("message" if level not in ["message", "warning", "error"] else level)
    # Message
    if level == "message":
        print(message)
        arcpy.AddMessage(message)
    # Warning
    elif level == "warning":
        print(f"WARNING: {message}")
        arcpy.AddWarning(message)
    # Error
    elif level == "error":
        print(f"ERROR: {message}")
        arcpy.AddError(message)
    return

# Override alternative print function that works as a full print and arcpy.AddMessage
def print(*values: object,
          sep: str = " ",
          end: str = "\n",
          file = None,
          flush: bool = False,
          severity: Literal['INFO', 'WARNING', 'ERROR'] = None):
    """ Print a message to the ArcGIS Pro message queue and stdout
    set severity to 'WARNING' or 'ERROR' to print to the ArcGIS Pro message queue with the appropriate severity
    """
        
    # Print the message to stdout
    builtins.print(*values, sep=sep, end=end, file=file, flush=flush)
    
    end = "" if end is '\n' else end
    message = f"{sep.join(map(str, values))}{end}"
    # Print the message to the ArcGIS Pro message queue with the appropriate severity
    match severity:
        case "WARNING":
            arcpy.AddWarning(f"{message}")
        case "ERROR":
            arcpy.AddError(f"{message}")
        case _:
            arcpy.AddMessage(f"{message}")
    return

    
def get_params(parameters: list, filter_list: list[str]=None) -> dict:
    """
    Converts the parameters to a dictionary

    @parameters: The parameters to convert
    @filter_list: List of parameter names to filter by
    @return: The parameters as a dictionary
    """

    if filter_list:
        params = {p.name:p for p in parameters if p.name in filter_list}
    else:
        params = {p.name:p for p in parameters}

    return params

def get_rows(features: str, fields: list[str], query: str=None)-> Generator[dict[str, Any], None, None]:
    """
    Gets the rows from the feature class

    @features: The feature class to get the rows from
    @fields: The fields to get from the feature class
    @query: The query to filter the rows by (optional)
    @yield: A Search cursor and a dictionary of rows 
            (In the format {<field>: <value>})
    
    Usage:
    >>> for cursor, row in get_rows(<features>, <fields>, <query>):
    >>>     print(row['fieldName'])
    """
    
    with arcpy.da.SearchCursor(features, fields, query) as cursor:
        for row in row_to_dict(cursor):
            yield cursor, row
                
def update_rows(features: str, fields: list[str], query: str=None) -> Generator[dict[str, Any], None, None]:
    """
    Updates the rows in the feature class

    @features: The feature class to update the rows in
    @fields: The fields to update
    @query: The query to filter the rows by (optional)
    @yield: An update cursor and a dictionary of rows 
            (In the format {<field>: <value>})
    
    Usage:
    >>> for cursor, row in update_rows(<features>, <fields>, <query>):
    >>>     row['fieldName'] = <value>
    >>>     cursor.updateRow(list(row.values()))
    """

    with arcpy.da.UpdateCursor(features, fields, query) as cursor:
        for row in row_to_dict(cursor):
            yield cursor, row
            
def insert_rows(features:str, fields: list[str], rows: list[list], query: str=None) -> int:
    """
    Inserts the rows into the feature class
    
    @features: The feature class to insert the rows into
    @fields: The fields to insert
    @query: The query to filter the rows by (optional)
    @rows: The rows to insert
    @return: count of rows inserted
    
    Usage:
    >>> rows = [[<value>, <value>], [<value>, <value>]]
    >>> insert_rows(<features>, <fields>, rows, <query>)
    """
    
    row_count = 0
    
    with arcpy.da.InsertCursor(features, fields, query) as cursor:
        for row in rows:
            cursor.insertRow(row)
            row_count += 1
    
    return row_count #len(rows)

# Probably be good to add some error checking to this. Maybe check to see if workplace exists
def create_scratch_name(data_type: str, prefix: str="scratch", suffix: str="", workspace: str=None, name_list: list[str]=None) -> str:
    """
    Creates a scratch name that is unique to the given geodatabase and 
    appends it to a list of scratch names.

    @data_type: Data type to generate unique name
    @prefix: Prefix added to unique name
    @suffix: Suffix added to unique name
    @workspace: Workspace to create name in. If None, current workspace is used
    @name_list: Existing list to append name to
    @return: Unique scratch name
    """

    # Create unique name
    if suffix != "": suffix = f"_{suffix}"
    valid_name = arcpy.ValidateTableName(f"{prefix}_{data_type}{suffix}", workspace)
    unique_name = arcpy.CreateUniqueName(valid_name, workspace)

    # Append name to list if there is one
    if name_list: list.append(unique_name)

    return unique_name

def delete_scratch_names(scratch_names: list[str]) -> list[str]:
    """
    Deletes objects in 'scratchNames' list. These should only be arcpy objects
    that were created by 'createScratchNames'.

    @scratch_names: List of names to delete
    @return: List of any names that could not be deleted
    """

    # Create a place to store any names that couldn't be deleted
    cant_delete = []

    # Try to delete scratch names in list
    for name in scratch_names:
        if arcpy.Exists(name):
            if not arcpy.Delete_management(name):
                msg("warning", f"Unable to delete feature '{name}'.")
                cant_delete.append(name)
        else:
            msg("warning", f"Feature '{name}' does not exist.")
            cant_delete.append(name)

    return cant_delete

def print_dict(dict_to_print: dict, tab_num: int = 0, tab: str = ftconstants.TAB) -> str:
    """
    Pretty print a dictionary.

    @dict_to_print: Dictionary to print
    @return: "<key>: <value>" formatted string
    """

    key_padding = len(max([str(k) for k in dict_to_print.keys()], key = len)) + 1
    tab_padding = tab * tab_num

    # Could make this recursive to print nested dictionaries
    dict_string = [f"{tab_padding}{k:<{key_padding}}: {v}\n" for k, v in dict_to_print.items()]
    
    return "".join(dict_string)