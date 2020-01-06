# CalSim Toolkit Python Module

Summary
-------
This library is intended for interaction with CalSim studies and related data.
A modeler is able to run CalSim with Python commands, query data from DSS
files, and call standard pre-/post-processing functions.

Acronyms
--------
| Abbreviation | Name
|--------------|-------------------------------------------------------------|
|DSS           | Data Storage System                                         |
|DWR           | State of California Department of Water Resources           |
|HEC           | U.S. Army Corps of Engineers' Hydrologic Engineering Center |
|USBR          | U.S. Department of the Interior, Bureau of Reclamation      |

Tutorial
--------
Follow the Jupyter Notebook in [exploration/tutorial_00.ipynb](exploration/tutorial_00.ipynb)
for information regarding typical usage.

Dependencies
------------
This module relies on the [usbr_py3dss](https://github.com/jshannon-usbr/usbr_py3dss)\
for reading from and writing data to DSS files. This module also utilizes
Python objects in many popular third party libraries that ship with
[Anaconda for Python](https://www.anaconda.com/), such as [pandas](https://pandas.pydata.org/),
[numpy](https://numpy.org/), and [matplotlib](https://matplotlib.org/).

Contact Information
-------------------
This tool is maintained by USBR in Sacramento, CA. Contact Jim Shannon at
jshannon@usbr.gov.

Future Development
------------------
Future development tasks will focus on the following priorities:
    1. Add read/write capabilities with HDF5 files formatted for CalSim studies;
    2. Add [pyhecdss](https://github.com/CADWRDeltaModeling/pyhecdss) as an alternative underlying dependency.
    3. Write data to excel spreadsheets for use in many existing
    post-processing tools;
    4. Apply data filtering by DWR Water Year Type;
    5. Develop plot types saved for future use;
    5. Include post-processing techniques representing USBR interests;
    6. Update `variable_dependencies` application to output `pandas` DataFrame; 
    7. Expand documentation;
    8. Draw plots with `plotly`.
