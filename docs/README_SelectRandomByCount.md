# Select Random By Count

Select a random subset of records in a feature.

**Category:** General<br>
**Source File:** [SelectRandomByCount.py](../tools/project/SelectRandomByCount.py)

# Usage

This tool is meant for use both in ArcGIS Pro and Python. It returns a selection with a random subset of records in the input features.

## Dialog

Parameters when running the tool through the ArcGIS Pro geoprocessing dialog.

>| Label | Description | Type |
>| :--- | :--- | :--- |
>| Input Features | Feature that contains records to select. | Feature Layer |
>| Subset Count | Number of records to select. | Long |

### Derived Output

>| Label | Description | Type |
>| :--- | :--- | :--- |
>| Feature With Selection | Input features with selection. | Feature Layer |
>| Count | Number of selected records. | Long |

## Python

```python
FlickTools.<Tool Name>(<Required Input>, {<Optional Input>})
```

>| Label | Description | Type |
>| :--- | :--- | :--- |
>| *Attribute* | *Description* | *Type* |

### Derived Output

>| Label | Description | Type |
>| :--- | :--- | :--- |
>| *Attribute* | *Description* | *Type* |

### Code Sample
```python
# Code sample
```
