"""
A general purpose module for any backend related functions
put functions that have to do with managing the toolbox or error handling here
"""

def buildDevError(label: str, desc: str):
    class Development(object):
        def __init__(self):
            """Placeholder tool for development tools"""

            self.category = "In Development"
            self.label = label
            self.alias = self.label.replace(" ", "")
            self.description = desc
            return
    return Development