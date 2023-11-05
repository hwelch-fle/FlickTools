# Zoom To HUC [¶](../README.md)

Zooms the camera to the extent of a watershed.

**Category:** General<br>
**Source File:** [ZoomToHUC.py](../tools/project/ZoomToHUC.py)

# Usage

This tool is meant for use in ArcGIS Pro. Before running the tool, select an active map view. If a map view is not selected, the tool will fail and display an error message.

## Dialog

Parameters when running the tool through the ArcGIS Pro geoprocessing dialog.

>| Label | Description | Type |
>| :--- | :--- | :--- |
>| State | US State the watershed intersects with. The default is Oregon. | Text |
>| Level | USGS watershed level, or field. The default is HUC8. | Text |
>| Watershed | USGS watershed name and code. | Text |