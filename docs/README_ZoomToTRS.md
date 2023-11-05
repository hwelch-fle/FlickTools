# Zoom To TRS [¶](../README.md)

Zooms the camera to the extent of a township, range, and section. This tool only works for areas in the state of Oregon.

**Category:** General<br>
**Source File:** [ZoomToTRS.py](../tools/project/ZoomToTRS.py)

# Usage

This tool is meant for use in ArcGIS Pro. Before running the tool, select an active map view. If a map view is not selected, the tool will fail and display an error message.

## Dialog

Parameters when running the tool through the ArcGIS Pro geoprocessing dialog.

>| Label | Description | Type |
>| :--- | :--- | :--- |
>| Township | Township code in the format *T7N* or *T7S*. | Text |
>| Range | Range code in the format *R3W* or *R3E*. | Text |
>| Section (optional) | Section number in the format *25*. | Text |
>| Enter as complete PLSS address | Indicate if input is a complete address or three partials.<ul><li>*Checked:* Input is a complete PLSS address.</li><li>*Unchecked:* Inputs are partial addresses. This is the default.</li></ul> | Boolean |
>| Full Address | A complete PLSS address in the format *T7S R3W Section 25* or *T7S R3W Sec 25*. | Text |