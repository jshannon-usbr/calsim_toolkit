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
from .tools import selection, transform, validation, variables
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

    def wide(self, **kwargs):
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
            print(msg)
        else:
            msg = 'Unable to transform DataFrame to wide data format.'
            raise TypeError(msg)
        # Return the transformed DataFrame.
        return df

    def condense(self):
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
            print(msg)
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

    def plot(self):
        # plot this array's data on a map, e.g., using Cartopy
        pass

    def b(self, b, match=True):
        # Initialize DataFrame.
        df = self._obj.copy()
        # Pass variables to selection function.
        df_filtered = selection.PartB(df, b, match=match)
        # Return filtered DataFrame.
        return df_filtered

    def wateryear(self):
        pass


def DF_WYT(fp, index='sac'):
    r'''

    Summary
    -------
    The `DF_OTFA` function retrieves a specified CalSim water year type (wyt)
    index from a given CalSim study.

    Parameters
    ----------
    fp : str, path object, or file-like object
        File path of 'wytypes.table' in CalSim study. Select one of the
        following:
            - sac
            - sjr
            - shasta
            - amerD8
            - fthr
            - trinity
            - amer40
            - dry
    index : str, default 'sac', optional
        String of date in ISO 8601 format.

    Returns
    -------
    DF : pandas DataFrames
        A DataFrame of specified CalSim water year type index.

    '''
    index = index.lower()
    index_col = {'sac': [1, 'SACindex'],
                 'sjr': [2, 'SJRindex'],
                 'shasta': [3, 'SHASTAindex'],
                 'amerD8': [4, 'AmerD893'],
                 'fthr': [5, 'FEATHERindex'],
                 'trinity': [6, 'Trinityindex'],
                 'amer40': [7, 'Amer403030'],
                 'dry': [8, 'DriestYrs']}
    if 'CalSim3' in fp:
        DF = pd.read_csv(fp, sep='\t', header=1, skiprows=list(range(11)),
                         usecols=[0, index_col[index][0]])
        wateryear = 'WATERYEAR'
    elif 'CalSimII' in fp:
        DF = pd.read_csv(fp, sep=r'\s+', header=1, skiprows=list(range(11)),
                         usecols=[0, index_col[index][0]])
        wateryear = 'wateryear'
    else:
        msg = 'Cannot parse "wytypes.table."'
        raise RuntimeError(msg)
    DF['DateTime'] = DF[wateryear].apply(lambda x: dt.date(x, 3, 31))
    DF.set_index('DateTime', inplace=True)
    DF.index = pd.to_datetime(DF.index)
    max_year = DF.index.year.max()
    date_index = pd.date_range(start='1921-10-31',
                               end='{}-09-30'.format(max_year), freq='M')
    DF = DF.reindex(date_index, method='ffill')
    DF.drop([wateryear], inplace=True, axis=1)
    return DF


# TODO: Let's do something here.
###############################################################################
###############################################################################
##########                        Tools                              ##########
###############################################################################
###############################################################################

# Common conversation factors
def cfs_to_taf(DF):
    r"""
    Summary
    -------
    Factor for converting all "CFS PER-AVER" time series into new
    "TAF PER-CUM" time series.

    """
    # TODOC: Provide documentation.
    # <JAS 2018-11-02>
    # Define conversion from 'CFS PER-AVER' to 'TAF PER-CUM.'
    def convert_to_taf(row):
        # [CFS] -> [CF/day]
        Step_1 = row['CFS'] * 86400
        # [CF/day] -> [CF/MON]
        Step_2 = Step_1 * row['days']
        # [CF/MON] -> [AF/MON]
        Step_3 = Step_2 * (1 / 43560)
        # [AF/MON] -> [TAF/MON]
        Step_4 = Step_3 * (1 / 1000)
        return Step_4
    # Select "CFS PER-AVER" time series that do not have an associated
    # "TAF PER-CUM" time series.
    df_cfs = DF.xs('CFS PER-AVER', level='DataType', axis=1)
    cfs_set = set(df_cfs.columns.get_level_values('Part B'))
    try:
        df_taf = DF.xs('TAF PER-CUM', level='DataType', axis=1)
        taf_set = set(df_taf.columns.get_level_values('Part B'))
    except KeyError:
        taf_set = set()
    Part_Bs = list(cfs_set - taf_set)
    # Check if there is a list of Part Bs to convert.
    if Part_Bs:
        # Select DataFrame of Part Bs.
        df = FilterByPartB(DF, Part_Bs)
        # Create new column header for conversion.
        cfs_col = df.columns
        taf_col = list()
        for c in cfs_col:
            study = c[0]
            part_b = c[1]
            part_f = c[2]
            part_c = c[3]
            datatype = 'TAF PER-CUM'
            taf_col.append((study, part_b, part_f, part_c, datatype))
        taf_col = pd.MultiIndex.from_tuples(taf_col,
                                            names=['Study', 'Part B', 'Part F',
                                                   'Part C', 'DataType'])
        df_t = pd.DataFrame(columns=taf_col, index=df.index)
        # Convert variables from 'CFS PER-AVER' to 'TAF PER-CUM.'
        for i in range(len(taf_col)):
            df_c = pd.DataFrame()
            df_c['CFS'] = df[cfs_col[i]]
            df_c['days'] = df.index.day.values
            row = ['CFS', 'days']
            df_t.loc[:, taf_col[i]] = df_c[row].apply(convert_to_taf, axis=1)
        # Append input DataFrame.
        DF_out = pd.concat([DF, df_t[taf_col]], axis=1)
    else:
        # Return input DataFrame since there is no list of Part Bs.
        DF_out = DF
    # Return DataFrame.
    return DF_out


def taf_to_cfs(DF):
    r"""
    Summary
    -------
    Factor for converting time series of unit "TAF PER-CUM" to unit
    "CFS PER-AVER."

    """
    # Define conversion from 'TAF PER-CUM' to 'CFS PER-AVER.'
    def convert_to_cfs(row):
        # [TAF/MON] -> [AF/MON]
        Step_1 = row['TAF'] * 1000
        # [AF/MON] -> [CF/MON]
        Step_2 = Step_1 * 43560
        # [CF/MON] -> [CF/day]
        Step_3 = Step_2 * (1 / row['days'])
        # [CF/day] -> [CFS]
        Step_4 = Step_3 * (1 / 86400)
        return Step_4
    # Select "TAF PER-CUM" time series that do not have an associated
    # "CFS PER-AVER" time series.
    df_taf = DF.xs('TAF PER-CUM', level='DataType', axis=1)
    taf_set = set(df_taf.columns.get_level_values('Part B'))
    try:
        df_cfs = DF.xs('CFS PER-AVER', level='DataType', axis=1)
        cfs_set = set(df_cfs.columns.get_level_values('Part B'))
    except KeyError:
        cfs_set = set()
    Part_Bs = list(taf_set - cfs_set)
    # Check if there is a list of Part Bs to convert.
    if Part_Bs:
        # Select DataFrame of Part Bs.
        df = FilterByPartB(DF, Part_Bs)
        # Create new column header for conversion.
        taf_col = df.columns
        cfs_col = list()
        for c in taf_col:
            study = c[0]
            part_b = c[1]
            part_f = c[2]
            part_c = c[3]
            datatype = 'CFS PER-AVER'
            cfs_col.append((study, part_b, part_f, part_c, datatype))
        cfs_col = pd.MultiIndex.from_tuples(cfs_col,
                                            names=['Study', 'Part B', 'Part F',
                                                   'Part C', 'DataType'])
        df_c = pd.DataFrame(columns=cfs_col, index=df.index)
        # Convert variables from 'TAF PER-CUM' to 'CFS PER-AVER.'
        for i in range(len(taf_col)):
            df_t = pd.DataFrame()
            df_t['TAF'] = df.loc[:, taf_col[i]]
            df_t['days'] = df.index.day.values
            row = ['TAF', 'days']
            df_c.loc[:, cfs_col[i]] = df_t[row].apply(convert_to_cfs, axis=1)
        # Append input DataFrame.
        DF_out = pd.concat([DF, df_c[cfs_col]], axis=1)
    else:
        # Return input DataFrame since there is no list of Part Bs.
        DF_out = DF
    # Return DataFrame.
    return DF_out





def ConstructPath(Part_A, Part_B, Part_C, Part_E, Part_F):
    r"""This documentation is incomplete and not reviewed as of 2018-08-13.

    Construct a CalSimII or CalSim3 DSS pathname. As of 2018-08-13, this
    function is only capable of working with CalSimII & CalSim3 monthly
    timestep DSS files.

    Parameters
    ----------
    Part_A : str
        Part A of DSS pathname.
    Part_B : str
        Part B of DSS pathname.
    Part_C : str
        Part C of DSS pathname.
    Part_E : str
        Part E of DSS pathname.
    Part_F : str
        Part F of DSS pathname.

    Returns
    -------
    cpath : str
        Appropriate pathname format for querying CalSimII & CalSim3 from a DSS
        file.

    Examples
    --------
    Construct a CalSimII or CalSim3 DSS pathname.

    >>> import cs_otfa as cs
    >>> Part_A = 'CALSIM'
    >>> Part_B = 'S_SHSTA'
    >>> Part_C = 'STORAGE'
    >>> Part_E = '1MON'
    >>> Part_F = 'CALSIM30_10'
    >>> Pathname = cs.ConstructPath(Part_A, Part_B, Part_C, Part_E, Part_F)
    >>> print(Pathname)
    /CALSIM/S_SHSTA/STORAGE//1MON/CALSIM30_10/

    """
    cpath = r'/{}/{}/{}//{}/{}/'.format(Part_A, Part_B, Part_C, Part_E, Part_F)
    return cpath


def DF_2_DSS(fp, DF):
    r"""This documentation is incomplete and not reviewed as of 2018-08-13.

    Store DataFrame of regular timeseries into a CalSimII or CalSim3 DSS file.
    As of 2018-08-13, this function is only capable of working with CalSimII &
    CalSim3 DSS files. Also, as of 2019-04-23, this function only stores
    timeseries and does not store meta data (i.e. coordinates, ctzone, etc).

    Parameters
    ----------
    fp : str
        File path of DSS file.
    DF : pandas DataFrame
        DataFrame of CalSimII or CalSim3 regular monthly time series. Index is
        in datetime format.

    Returns
    -------
    None : None

    Examples
    --------
    Save a subset of a DataFrame to a DSS file. As of 2018-08-14, need to test
    if the below code returns expected result.

    >>> import cs_otfa as cs
    >>> fp = 'CS3_DV.dss'
    >>> PartBs = ['S_SHSTA','S_TRNTY']
    >>> # Assume large DataFrame, `DF`, that includes `PartBs`
    >>> cs.DF_2_DSS(fp, DF[PartBs])

    """
    # TODOC: Update documentation and provide source code notes.
    # <JAS 2018-11-02>
    # TODO: Code requires updating to match function `DSS_2_DF` logic.
    # <JAS 2019-01-03>
    ctime = '2400'
    cdate = DF.index[0].strftime('%d%b%Y')
    nvals = len(DF.index)
    DSS_File = dss.open_dss(fp)[0]
    # ???: Is this line above able to handle a new DSS file or only an existing
    #      file?
    # TODO: Look at JMG's example code.
    # <JAS 2019-04-23>
    for col in DF.columns:
        (Part_B, Part_A, Part_F, Part_C, Part_E, cunits, ctype) = col
        cpath = ConstructPath(Part_A, Part_B, Part_C, Part_E, Part_F)
        vals = list(DF[Part_B].values.reshape(nvals,))
        dss.write_regtsd(DSS_File, cpath, cdate, ctime,
                         nvals, vals, cunits, ctype, 0)
    dss.close_dss(DSS_File)
    print('DataFrame stored in {}'.format(fp))
    return None


def DSS_2_DF(fp, pths, start_date='1921-10-31', end_date='2003-09-30'):
    r"""This documentation is incomplete and not reviewed as of 2018-08-13.

    Query regular timeseries from a CalSimII or CalSim3 DSS file. As of
    2018-08-13, this function is only capable of working with CalSimII &
    CalSim3 DSS files.

    Parameters
    ----------
    fp : str
        File path of DSS file.
    vl : str or list
        String of single path name or a list of strings of multiple pathnames.
    start_date : str, default '1921-10-31', optional
        String of date in ISO 8601 format.
    end_date : str, default '2003-09-30', optional
        String of date in ISO 8601 format.

    Returns
    -------
    DF : list of pandas DataFrames
        Two DataFrames are returned. The first entry is a DataFrame of CalSimII
        or CalSim3 regular monthly time series. The second entry is a DataFrame
        of Supplemental Information associated with DSS pathname.

    Examples
    --------
    Query a single regular monthly timeseries from a DSS file.

    >>> import cs_otfa as cs
    >>> fp = 'CS3_DV.dss'
    >>> Pths = '/CALSIM/S_SHSTA/STORAGE//1MON/CALSIM30_10/'
    >>> Start_Date = '1921-10-31'
    >>> End_Date = '2015-09-30'
    >>> DV_DF = cs.DSS_2_DF(fp, Pths, Start_Date, End_Date)

    Query multiple regular monthly timeseries from a DSS file.

    >>> import cs_otfa as cs
    >>> fp = 'CS3_DV.dss'
    >>> Pths = ['/CALSIM/S_SHSTA/STORAGE//1MON/CALSIM30_10/',
    ...         '/CALSIM/S_TRNTY/STORAGE//1MON/CALSIM30_10/']
    >>> Start_Date = '1921-10-31'
    >>> End_Date = '2015-09-30'
    >>> DV_DF = cs.DSS_2_DF(fp, Pths, Start_Date, End_Date)

    """
    # TODOC: Update documentation.
    # <JAS 2018-11-02>
    # Initialize variables for DataFrame construction.
    s_date = dt.datetime.fromisoformat(start_date)
    e_date = dt.datetime.fromisoformat(end_date)
    t_delta = rd.relativedelta(e_date, s_date)
    datetime = pd.Series(pd.date_range(start=s_date,
                                       end=e_date,
                                       freq='M',
                                       name='DateTime',
                                       normalize=False))
    meta_col = ['Pathname', 'DSS File Path', 'Supplemental Info',
                'X-Coordinate', 'Y-Coordinate', 'Coordinate System',
                'Horizontal Datum', 'Datum Units', 'Time Zone ID',
                'Time Zone Offset']
    df_rts = pd.DataFrame()
    df_meta = pd.DataFrame()
    # Initialize variables for DSS query.
    ifltab = dss.open_dss(fp)[0]
    cdate = s_date.strftime('%d%b%Y')
    ctime = '2400'
    nvals = 12*t_delta.years+t_delta.months+1
    # Construct panthname list, if only one pathname is given.
    if not isinstance(pths, list):
        pths = [pths]
    # Retrieve data for each pathname.
    for cpath in pths:
        dss_ret = dss.read_regtsd(ifltab, cpath, cdate, ctime, nvals)
        # Add data to df_rts.
        pathname = pd.Series([cpath] * nvals, name='Pathname')
        filepath = pd.Series([fp] * nvals, name='DSS File Path')
        values = pd.Series(list(dss_ret[1]), name='Values', dtype=np.float64)
        unit = pd.Series([dss_ret[2].upper()] * nvals, name='Unit')
        dtype = pd.Series([dss_ret[3].upper()] * nvals, name='Type')
        df_rts_temp = pd.concat([pathname, filepath, datetime,
                                 values, unit, dtype],
                                axis=1)
        df_rts = pd.concat([df_rts, df_rts_temp])
        # Add data to df_meta.
        coords_info = dss_ret[7]
        supp_info = [cpath, fp, dss_ret[6], coords_info['X_Long'],
                     coords_info['Y_Lat'], coords_info['CoordSys'][0],
                     coords_info['Datum'][0], coords_info['DatumUnit'][0],
                     dss_ret[8], dss_ret[11].value]
        df_meta_temp = pd.Series(supp_info, index=meta_col).to_frame().T
        df_meta = pd.concat([df_meta, df_meta_temp])
    # Disconnect from database.
    dss.close_dss(ifltab)
    # Replace DSS missing value indicators with NaN and reset indices.
    df_rts.replace([-901, -902], np.nan, inplace=True)
    df_rts.reset_index(drop=True, inplace=True)
    df_meta.reset_index(drop=True, inplace=True)
    df_meta = df_meta.infer_objects()
    # Compile list of DataFrames.
    DF = [df_rts, df_meta]
    return DF


def FilterByPartB(DF, PartBs, maintain_order=False):
    r"""
    Summary
    -------
    Filter DataFrame by CalSim Part B.

    No documentation as of 2018-09-11.

    """
    # TODOC: Provide documentation and source code notes.
    # <JAS 2018-11-02>
    # Check if `DF` is a `pandas` DataFrame.
    if not isinstance(DF, pd.DataFrame):
        err_msg = ('DF must be a DataFrame.')
        raise TypeError(err_msg)
    # Maintain Part B ordering, if it is important.
    if maintain_order:
        df_studies = list(DF.columns.get_level_values('Study'))
        # Construct 'Study' list.
        df_study_list = list()
        for df_study in df_studies:
            if df_study not in df_study_list:
                df_study_list.append(df_study)
        # Swap levels to reorder.
        DF_temp = DF.copy().swaplevel('Study', 'Part B', axis=1)
        DF_temp = DF_temp[PartBs].swaplevel('Study', 'Part B', axis=1)
        # Set result to output DataFrame.
        DF_out = DF_temp[df_study_list]
    # Quickly select Part Bs, if ordering is not important.
    else:
        All = slice(None)
        col = (All, PartBs, All, All, All)
        DF_out = DF.loc[:, col].copy()
    # Return Output DataFrame.
    return DF_out





def GetRTS(DF_Pathnames, s_date='1921-10-31', e_date='2003-09-30'):
    r"""Wrapper for DSS_2_DF. Allows for iterating over multiple DSS files.

    This function requires output from GetDSS_Catalog().

    No additional documentation as of 2018-09-10.
    """
    # TODOC: Provide documentation.
    # <JAS 2018-11-02>
    # Ensure output of GetDSS_Catalog() is passed through DF_Pathnames.
    if 'DSS File Path' not in DF_Pathnames.columns:
        raise SyntaxError('Column "DSS File Path" not in DF_Pathnames.')
    # Limit number of retrievals to prevent over-utilizing computer resources.
    function_limit = 300
    nDF_Var = DF_Pathnames.index.shape[0]
    if nDF_Var > function_limit:
        err_msg = ('DF_Pathnames shape greater than ' +
                   'function_limit of {}.'.format(function_limit))
        raise ValueError(err_msg)
    # Separate available and unavailable data.
    dfna = DF_Pathnames[pd.isna(DF_Pathnames).any(axis=1)].copy()
    dfp = DF_Pathnames[pd.notna(DF_Pathnames).all(axis=1)].copy()
    # Set index for dfp from 'Part B' to 'DSS File Path.'
    dfp.set_index('DSS File Path', inplace=True)
    # Rewrite Pathnames for dfna.
    FakePathname = lambda x: ConstructPath('CALSIM', x, 'NA', '1MON', 'NA')
    dfna['Pathname'] = dfna.index.map(FakePathname)
    # Acquire list of DSS File Paths.
    DSS_fps = dfp.index.unique().values
    # Initialize return DataFrames.
    df_rts = pd.DataFrame()
    df_meta = pd.DataFrame()
    # Get data from each DSS File Path.
    for DSS in DSS_fps:
        # Get list of pathnames for given DSS File Path.
        if dfp.loc[DSS, :].shape[0] == 1:
            paths = dfp.loc[DSS, 'Pathname']
        else:
            paths = list(dfp.loc[DSS, 'Pathname'].values)
        # Retrieve data.
        df_rts_temp, df_meta_temp = DSS_2_DF(DSS, paths, s_date, e_date)
        # Store data into return DataFrames.
        df_rts = pd.concat([df_rts, df_rts_temp])
        df_meta = pd.concat([df_meta, df_meta_temp])
    # Get Pathnames from dfna.
    var_na = list(dfna['Pathname'].values)
    # Retrieve unavailable data.
    df_rts_temp, df_meta_temp = DSS_2_DF(DSS_fps[0], var_na, s_date, e_date)
    df_rts_temp.replace(DSS_fps[0], np.nan, inplace=True)
    df_meta_temp.replace(DSS_fps[0], np.nan, inplace=True)
    # Store unavailable data.
    df_rts = pd.concat([df_rts, df_rts_temp])
    df_meta = pd.concat([df_meta, df_meta_temp])
    # Replace blank units with NaN.
    df_rts['Unit'].replace([' '], np.nan, inplace=True)
    # Reset index for df_rts and df_meta.
    df_rts.reset_index(drop=True, inplace=True)
    df_meta.reset_index(drop=True, inplace=True)
    # Compile list of DataFrames.
    DF = [df_rts, df_meta]
    return DF


def StoreRTS(DF_Pathnames, DF_data, s_date='1921-10-31', e_date='2003-09-30'):
    r"""Wrapper for DF_2_DSS. Allows for iterating over multiple DSS files.

    This function requires a dataframe structured like output from
    GetDSS_Catalog().

    Parameters
    ----------
    DF_Pathnames : pandas DataFrame
        Catalog of variables and associated file paths in which to be stored.
    DF_data : list of pandas DataFrame
        Data to be stored into DSS files. DF_data[0] is the regular time series
        data (df_rts) and DF_data[1] is the associated meta data (df_meta).
    start_date : str, default '1921-10-31', optional
        String of date in ISO 8601 format.
    end_date : str, default '2003-09-30', optional
        String of date in ISO 8601 format.

    No additional documentation as of 2019-01-09.

    """
    # TODO: Write code for this function.
    # <JAS 2018-11-02>
    # Return error while code is in development.
    dev_msg = 'Function is currently in development and not ready for use.'
    raise RuntimeError(dev_msg)
    # Ensure output of GetDSS_Catalog() is passed through DF_Pathnames.
    if 'DSS File Path' not in DF_Pathnames.columns:
        raise SyntaxError('Column "DSS File Path" not in DF_Pathnames.')
    # Limit number of retrievals to prevent over-utilizing computer resources.
    function_limit = 100
    nDF_Var = DF_Pathnames.index.shape[0]
    if nDF_Var > function_limit:
        err_msg = ('DF_Pathnames shape greater than ' +
                   'function_limit of {}.'.format(function_limit))
        raise ValueError(err_msg)
    # Separate available and unavailable data.
    dfna = DF_Pathnames[pd.isna(DF_Pathnames).any(axis=1)].copy()
    dfp = DF_Pathnames[pd.notna(DF_Pathnames).all(axis=1)].copy()
    pass

# TODO: Let's do something here.
###############################################################################
###############################################################################
##########                        Plots                              ##########
###############################################################################
###############################################################################


# TODO: Let's do something here.
###############################################################################
###############################################################################
##########                        Main                               ##########
###############################################################################
###############################################################################

# %% Execute code.
# Define attributes.
plot_lib = 'matplotlib'
# Prevent execution as __main__.
if __name__ == '__main__':
    msg = ('This module is intended to be imported for use into another'
           ' module. It is not intended to be run as a __main__ file.')
    raise RuntimeError(msg)
