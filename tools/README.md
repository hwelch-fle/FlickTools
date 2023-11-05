## Tool Template
Use the following code as a template when creating new tools.

```python
import arcpy

import utils.arcpy_tools as archelp
from utils.tool import Tool

class MyTool(Tool):
    """Tool Definition"""
    
    def __init__(self) -> None:
        """
        Tool Description.

        @self.project: arcpy project object
        @self.project_location: Path to the project
        @self.project_name: Name of the project
        @self.default_gdb: Path to the default gdb
        @self.params: Tool parameters (set with archelp.get_parameters())
        """
        
        # Initialize the parent class
        super().__init__()
                
        # Overrides
        self.label = "Default Tool"
        self.description = "Default tool description"
        self.category = "Default"
        
        # Parameters
        self.params = {}
        self.example_int = 3
        
        return
    
    def getParameterInfo(self) -> list:
        """Define parameter definitions."""
        return []

    def execute(self, parameters: list[arcpy.Parameter], messages: list) -> None:
        """The source code of the tool."""

        # Allows reference to parameters by name instead of index
        self.params = archelp.get_params(parameters)

        return
```

<br>

## Doc Template
Use the following template when creating a new docs document.

#### File name: 
```
README_<Tool Name>.md
```

#### Markdown template (remove code block escape characters):
```markdown
# Tool Name [¶](../README.md)

*Quick description of tool.*

**Category:** <br>
**Source File:** [<filename>.py](../tools/project/<filename>.py)

# Usage

This tool is meant for use both in ArcGIS Pro and Python.

## Dialog

Parameters when running the tool through the ArcGIS Pro geoprocessing dialog.

>| Label | Description | Type |
>| :--- | :--- | :--- |
>| *Attribute* | *Description* | *Type* |

### Derived Output

>| Label | Description | Type |
>| :--- | :--- | :--- |
>| *Attribute* | *Description* | *Type* |

## Python

\```python
FlickTools.<Tool Name>(<Required Input>, {<Optional Input>})
\```

>| Label | Description | Type |
>| :--- | :--- | :--- |
>| *Attribute* | *Description* | *Type* |

### Derived Output

>| Label | Description | Type |
>| :--- | :--- | :--- |
>| *Attribute* | *Description* | *Type* |

### Code Sample

\```python
# Code sample
\```
```