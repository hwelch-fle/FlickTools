# Unique Values In Field [¶](../README.md)

Output all of the unique values for a field as a message in the geoprocessing pane, or as a table. Table output is only available for a single field.

**Category:** General<br>
**Source File:** [UniqueValuesInField.py](../tools/project/UniqueValuesInField.py)

# Usage

This tool is meant for use in ArcGIS Pro. To view the output of the tool when *Output as Table* is unchecked, click *View Details* in the geoprocessing pane.

## Dialog

Parameters when running the tool through the ArcGIS Pro geoprocessing dialog.

>| Label | Description | Type |
>| :--- | :--- | :--- |
>| Input Features | Feature that contains one or more fields. | Feature Layer; Table |
>| Field(s) to Summarize | The fields to summarize. | Field |
>| Include Counts | Indicate if counts of unique values should be included.<ul><li>*Checked:* Counts are included.</li><li>*Unchecked:* Counts are not included. This is the default.</li></ul> | Boolean |
>| Output as Table (optional) | Indicate if output should be as a table. Only available for a single field.<ul><li>*Checked:* Generate output as a table.</li><li>*Unchecked:* Output as a dialog message. This the default.</li></ul> | Boolean |
>| Output Table (optional) | Table that will contain tool output. Only available for a single field. | Table |