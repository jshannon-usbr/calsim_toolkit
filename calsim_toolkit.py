r"""

Summary
-------
The CalSim Toolkit Python module is developed for in house querying,
processing, and visualization of CalSim data from DSS files. Use of this module
requires the `usbr_py3dss.zip` python module.

Main tasks
----------
1. Query
2. Process
3. Run
4. Write
5. Visualize

Examples
--------
Importing the module.

>>> import calsim_toolkit as cs

Notes
-----
Below are module project notes:

    1. This project is NOT version controlled with Git.

Future Development
------------------
Below are a list of tasks for future development:

    1. Change plot styling to reflect Data-To-Ink ratio best practices [1_].
    2. Directory reorganization.
    3. Inclusion of `plotly` and `pyviz` in addition to`matplotlib`.
    4. Add file configuration for connection to `usbr_py3dss`.
    5. Add capability to read different data sources (e.g. DSS, SQLite).
    6. Add `__init__.py`, `requirements.txt`, & `setup.py` to directory.
    7. Refine "Header" meta-data for module.
    8. Add option to see differences from baseline, where appropriate.
    9. Updated PlotPD() to address depreciation warning.
    10. Add error catching for y-axis range (Nan and Inf cases).
    11. Add option to present table data with chart.
    12. Modify library to incorporate "pyviz" environment workflow.
    13. Modify pd.DataFrame specifications to allow for MultiIndex or single
        level column index.
    14. Incorporate terminology of "tidy data" and "wide data."
    15. Incorporate `drop_input` option for conversion between TAF and CFS.
    16. Review capabilities of other unit variables (i.e. Not TAF or CFS).
    17. Produce a table of exceedence plots where the values are replaced by
        their respective time steps.
    18. Separate module into query, process, and visualization tools.
    19. Modify query tools to read from file as well as a list.
    20. Create tool to convert DSS to SQLite (or any DB file via SQALalchemy?).
    21. Should I rethink the name of this module?
    22. Include data query from DSS into excel.

References
----------
The references listed below are formatted according to Chicago Manual of Style,
16th Edition.

.. [1] "Customizing Matplotlib with Style Sheets and RcParams¶." Matplotlib:
   Python Plotting - Matplotlib 2.2.3 Documentation. Accessed February 01,
   2019. https://matplotlib.org/tutorials/introductory/customizing.html.

.. [2] "Plotly." Modern Visualization for the Data Era - Plotly. Accessed
   February 01, 2019. https://plot.ly/matplotlib/.

.. [3] "Plotly." Modern Visualization for the Data Era - Plotly. Accessed
   February 01, 2019. https://plot.ly/matplotlib/bar-charts/.

"""
# %% Import libraries.
# Import standard libraries.
import os
import sys
import datetime as dt
# Import third party libraries.
import dateutil.relativedelta as rd
import matplotlib.pyplot as plt
# TODO: Created separate libraries for `matplotlib', `pyviz`, and `plotly`.
# <JAS 2019-03-20>
import numpy as np
import pandas as pd
from sklearn.metrics import r2_score
# Import module libraries.
from .tools.io import *
from .tools import plots, selection, transform, validation, variables
# Import custom libraries.
import dss3_functions_reference as dss


# %% Define functions.
def _run_CalSim_():
    pass


# %% Establish classes.
# NOTE: For extending pandas DataFrames, see
# https://pandas.pydata.org/pandas-docs/stable/development/extending.html
# <JAS 2019-06-18>
@pd.api.extensions.register_dataframe_accessor("cs")
class CalSimAccessor(object):
    def __init__(self, pandas_obj):
        self._validate(pandas_obj)
        self._obj = pandas_obj

    @staticmethod
    def _validate(obj):
        if not (validation.is_tidy(obj) or validation.is_wide(obj)
                or validation.is_condense(obj)):
            validation.is_tidy(obj, verbose=True)
            validation.is_wide(obj, verbose=True)
            validation.is_condense(obj, verbose=True)
            msg = 'DataFrame does not meet calsim_toolkit specifications.'
            raise TypeError(msg)

    @property
    def no_property(self):
        msg = 'This would return a property.'
        return msg

    def tidy(self, verbose=True, **kwargs):
        # Initialize DataFrame.
        df = self._obj.copy()
        # Transform DataFrame, based on DataFrame type.
        if validation.is_wide(df):
            df = transform.wide_to_tidy(df)
        elif validation.is_condense(df):
            df = transform.condense_to_tidy(df, **kwargs)
        elif validation.is_tidy(df):
            msg = 'DataFrame is already in tidy format.'
            if verbose: print(msg)
        else:
            msg = 'Unable to transform DataFrame to tidy data format.'
            raise TypeError(msg)
        # Return the transformed DataFrame.
        return df

    def wide(self, verbose=True, **kwargs):
        # Initialize DataFrame.
        df = self._obj.copy()
        # Transform DataFrame, based on DataFrame type.
        if validation.is_tidy(df):
            df = transform.tidy_to_wide(df)
        elif validation.is_condense(df):
            df = transform.condense_to_tidy(df, **kwargs)
            df = transform.tidy_to_wide(df)
        elif validation.is_wide(df):
            msg = 'DataFrame is already in wide format.'
            if verbose: print(msg)
        else:
            msg = 'Unable to transform DataFrame to wide data format.'
            raise TypeError(msg)
        # Return the transformed DataFrame.
        return df

    def condense(self, verbose=True):
        # Initialize DataFrame.
        df = self._obj.copy()
        # Transform DataFrame, based on DataFrame type.
        if validation.is_tidy(df):
            df = transform.tidy_to_condense(df)
        elif validation.is_wide(df):
            df = transform.wide_to_tidy(df)
            df = transform.tidy_to_condense(df)
        elif validation.is_condense(df):
            msg = 'DataFrame is already in condense format.'
            if verbose: print(msg)
        else:
            msg = 'Unable to transform DataFrame to wide data format.'
            raise TypeError(msg)
        # Return the transformed DataFrame.
        return df

    def to_dss(self, file_path, **kwargs):
        # Initialize DataFrame.
        df = self._obj.copy()
        # Transform DataFrame to tidy format, if necessary.
        df = df.cs.tidy(verbose=False, **kwargs)
        # Write the DataFrame to a DSS file
        write_dss(file_path, df)
        # Return success indicator.
        return 0

    def to_excel():
        pass

    def plot(self, plot_type='', **kwargs):
        # Initialize DataFrame.
        df = self._obj.copy()
        # Transform to wide format.
        df = df.cs.wide(verbose=False)
        # Initialize methods.
        if plot_type:
            plot_type = plot_type.upper()
        else:
            plot_type = 'TS'
        plot_types = {'AA': plots.PlotAA,
                      'EX': plots.PlotEX,
                      'MA': plots.PlotMA,
                      'SP': plots.PlotSP, 
                      'TS': plots.PlotTS}
        # Obtain plot.
        fig, ax = plot_types[plot_type](df, **kwargs)
        # Return plot.
        return fig, ax

    def b(self, b, match=True):
        # Initialize DataFrame.
        df = self._obj.copy()
        # Pass variables to selection function.
        df_filtered = selection.PartB(df, b, match=match)
        # Return filtered DataFrame.
        return df_filtered

    def wateryear(self):
        pass


# %% Execute code.
# Define attributes.
plot_lib = 'matplotlib'
# Prevent execution as __main__.
if __name__ == '__main__':
    msg = ('This module is intended to be imported for use into another'
           ' module. It is not intended to be run as a __main__ file.')
    raise RuntimeError(msg)
