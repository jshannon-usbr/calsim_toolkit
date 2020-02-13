"""
Summary
-------
The purpose of this module is to provide Input/Output (I/O) functions for the
`calsim_toolkit` library.

Notes
-----
Reading and writing seems to handle timestep discrepency well between pandas
(midnight = 00:00, start of day) and HEC-DSS (midnight = 2400, end of day)
because of the frequency attribute of `pd.date_range` and HEC-DSS Part E. If
any shift occurs in time series, it may be due to this issue.

"""
# %% Import libraries.
# Import standard libraries.
import os
import sys
import datetime as dt
# Import third party libraries.
import numpy as np
import pandas as pd
# Import module libraries.
from . import transform, validation, variables
# Import custom libraries.
import dss3_functions_reference as dss


# %% Define functions.
def parse_filepaths(fp, studies=None):
    """
    Summary
    -------
    Function to parse filepath and optional study names into a format readable
    for the calsim_toolkit read/write functions.

    """
    # Check that inputs provided are compatible and zip data into list.
    if isinstance(fp, str) and (isinstance(studies, str) or not studies):
        study_fps = [(studies, fp)]
    elif isinstance(fp, list) and (isinstance(studies, list) or not studies):
        if studies and (len(fp) != len(studies)):
            msg = ('List length of file paths `fp` must equal list length of'
                   ' study names.')
            raise TypeError(msg)
        if not studies:
            studies = ['Alt{}'.format(i) for i in range(len(fp))]
        study_fps = list(zip(studies, fp))
    else:
        msg = 'Inputs provided are incompatible.'
        raise TypeError(msg)
    # Return list of tuples.
    return study_fps


def read_dss_catalog(fp, a=None, b=None, c=None, e=None, f=None, studies=None,
                     match=True):
    """
    Summary
    -------
    Function to query a single DSS catalog, given optional filters.

    Notes
    -----
    1. Add capability to search by *. Consider using Series.str.contains(),
       documented here, accessed 2019-09-12: https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.Series.str.contains.html#pandas.Series.str.contains
    2. Add capability to filter by full pathnames, if provided.
    3. Add capability to read lists from files.
    4. Add capability to change provided filters to UPPERCASE.

    """
    # Iterate through file paths.
    study_fps = parse_filepaths(fp, studies=studies)
    list_DSS_Cat = list()
    for study, f_path in study_fps:
        # Check if DSS file exists.
        if not os.path.exists(f_path):
            msg = 'File {} does not exist.'
            raise RuntimeError(msg.format(f_path))
        # Get pathlist from DSS Catalog given absolute or relative file path.
        pl = dss.get_catalog(f_path)[0]
        # Transform list of pathnames into pandas DataFrame.
        DSS_Cat_f = pd.DataFrame(pl, columns=['Pathname'])
        transform.split_pathname(DSS_Cat_f, inplace=True)
        # Filter by input search criteria.
        filter = DSS_Cat_f.any(axis=1)
        filters = dict()
        if a: filters['Part A'] = a if isinstance(a, list) else [a]
        if b: filters['Part B'] = b if isinstance(b, list) else [b]
        if c: filters['Part C'] = c if isinstance(c, list) else [c]
        if e: filters['Part E'] = e if isinstance(e, list) else [e]
        if f: filters['Part F'] = f if isinstance(f, list) else [f]
        if filters:
            for k, v in filters.items():
                v_upper = [x.upper() for x in v]
                if match:
                    filter = filter & DSS_Cat_f[k].isin(v_upper)
                else:
                    v_search = '|'.join(v_upper)
                    filter = filter & DSS_Cat_f[k].str.contains(v_search,
                                                                regex=True)
        # Apply filter and ensure values are returned.
        DSS_Cat_f = DSS_Cat_f.loc[filter, :]
        if DSS_Cat_f.empty:
            msg = 'No pathnames returned from provided filter criteria.'
            raise TypeError(msg)
        # Add file path to DataFrame.
        # ????: Should I add absolute file path?
        # <JAS 2019-09-12>
        DSS_Cat_f['File Path'] = f_path
        if study: DSS_Cat_f['Study'] = study
        # Add to list.
        list_DSS_Cat.append(DSS_Cat_f.copy())
    # Concatenate list of DataFrames into a single DataFrame.
    DSS_Cat = pd.concat(list_DSS_Cat).reset_index(drop=True)
    # Remove duplicate pathnames.
    duplicates = DSS_Cat.duplicated()
    DSS_Cat = DSS_Cat.loc[~duplicates, :]
    DSS_Cat.reset_index(drop=True, inplace=True)
    # Reconstruct pathnames.
    transform.join_pathname(DSS_Cat, inplace=True, e='skip')
    # Return filtered catalog.
    return DSS_Cat


def read_dss(fp, start_date='1921-10-31', end_date='2003-09-30',
             supp_info=False, **kwargs):
    r"""
    Summary
    -------
    No summary as of 2019-09-13.

    Parameters
    ----------
    fp : str
        File path (absolute or relative) of DSS file.
    a, b, c, e, f : str or list, default None, optional
        Pathname part filters.
    start_date : str, default '1921-10-31', optional
        String of date in ISO 8601 format.
    end_date : str, default '2003-09-30', optional
        String of date in ISO 8601 format.
    format : str, default 'tidy', optional
        Format of returned DataFrame. Options include 'tidy' and 'CalSim'.
    supp_info : bool, default False, optional
        Option to return supplemental information.

    Returns
    -------
    DF: pandas DataFrame
        DataFrame of CalSim regular time series at the specified format.

    Notes
    -----
    1. Add capability to search by *. Consider using Series.str.contains(),
       documented here, accessed 2019-09-12: https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.Series.str.contains.html#pandas.Series.str.contains
    2. Add capability to filter by full pathnames, if provided.
    3. Add capability to read lists from files.
    4. Add capability to read multiple DSS files given list, dictionary, or json.
    5. Add capability to change provided filters to UPPERCASE.
    6. Add capability to read multiple time steps; currently only handles 1MON.

    """
    # Acquire catalog of pathnames.
    dss_cat = read_dss_catalog(fp, **kwargs)
    # Initialize values for `dss.read_regtsd`.
    cdate = dt.datetime.fromisoformat(start_date).strftime('%d%b%Y')
    ctime = dt.datetime.fromisoformat(start_date).strftime('%H%M')
    # Get list of studies and file paths.
    study_fps = transform.cat_to_study_fps(dss_cat)
    list_df = list()
    # Read data into DataFrame.
    for study, f_path in study_fps:
        # Get pathnames for current file.
        # TODO: Issue here if adding multiple alternatives with the same file.
        # <JAS 2019-09-17>
        fp_filt = (dss_cat['File Path'] == f_path)
        st_filt = (dss_cat['Study'] == study) if study else dss_cat.any(axis=1)
        cat_filter = (fp_filt & st_filt)
        s_pathnames = dss_cat.loc[cat_filter, 'Pathname']
        # Query data from DSS file.
        ifltab = dss.open_dss(f_path)[0]
        for row in s_pathnames.index:
            cpath = s_pathnames[row]
            t_step = cpath.split('/')[5]
            fq = variables.t_steps[t_step]
            datetime = pd.date_range(start=start_date, end=end_date, freq=fq,
                                     name='DateTime')
            # TODO: Future will handle timezone information; code below.
            # <JAS 2019-09-16>
            # datetime = pd.date_range(start=start_date, end=end_date, freq=fq,
                                     # name='DateTime', tz='America/Los_Angeles')
            nvals = datetime.size
            df_temp = pd.DataFrame(datetime, columns=['DateTime'])
            if study: df_temp['Study'] = study
            dss_data = dss.read_regtsd(ifltab, cpath, cdate, ctime, nvals)
            df_temp['Pathname'] = cpath
            df_temp['Units'] = dss_data[2].upper()
            df_temp['Data Type'] = dss_data[3].upper()
            df_temp['Value'] = list(dss_data[1])
            list_df.append(df_temp.copy())
        dss.close_dss(ifltab)
        df = pd.concat(list_df)
    # NOTE: Legacy code below handles meta-data.
    # <JAS 2019-09-13>
    if False:
        coords_info = dss_ret[7]
        supp_info = [cpath, fp, dss_ret[6], coords_info['X_Long'],
                     coords_info['Y_Lat'], coords_info['CoordSys'][0],
                     coords_info['Datum'][0], coords_info['DatumUnit'][0],
                     dss_ret[8], dss_ret[11].value]
        df_meta_temp = pd.Series(supp_info, index=meta_col).to_frame().T
        df_meta = pd.concat([df_meta, df_meta_temp])
        df_meta.reset_index(drop=True, inplace=True)
        df_meta = df_meta.infer_objects()
    # Replace DSS missing value indicators with NaN and reset indices.
    df['Value'].replace([-901, -902], np.nan, inplace=True)
    df.reset_index(drop=True, inplace=True)
    # Return DataFrame.
    return df


def write_dss(fp, df):
    """
    Summary
    -------
    No documentation as of 2019-09-13. Write to existing DSS file. If one does
    not exist, a DSS file will be created.

    `fp` must be string or dictionary.

    """
    # Make a copy of the input DataFrame.
    df_copy = df.copy()
    # Ensure DataFrame is tidy prior to writing.
    if not validation.is_tidy(df_copy):
        # TODO: In the future, write code to transform DataFrame.
        # <JAS 2019-09-13>
        msg = 'DataFrame is not in CalSim tidy format.'
        raise RuntimeError(msg)
    # Prepare for iteration over multiple DSS files.
    # TODO: Improve code below because, while stable, it is not end-user
    #       friendly or very readable code.
    # <JAS 2019-09-18>
    if 'Study' in df_copy.columns:
        if not isinstance(fp, dict):
            msg = ('Must provide dictionary of {study: file path} for DataFrame'
                   ' with "Study" column.')
            raise TypeError(msg)
        gv_st = list(fp.keys())
        ex_st = list(df_copy['Study'].unique())
        if (set(gv_st) != set(ex_st)) or (len(gv_st) != len(ex_st)):
            ms_st = set(ex_st) - set(gv_st)
            et_st = set(gv_st) - set(ex_st)
            msg = list()
            if ms_st:
                msg += [('The following studies are missing from `fp`'
                         ' dictionary: {}'.format(list(ms_st)))]
            if et_st:
                msg += [('The following studies do not exist in the'
                         ' DataFrame: {}'.format(list(et_st)))]
            raise RuntimeError('\n'.join(msg))
        study_fps = fp
    else:
        if not isinstance(fp, str):
            msg = ('Must provide file path as string (relative or absolute)'
                   ' for DataFrame.')
            raise TypeError(msg)
        study_fps = {None: fp}
    # Replace NaNs with -901.
    # ????: What is the difference between -901 and -902?
    # <JAS 2019-09-16>
    df_copy['Value'].fillna(-901, inplace=True)
    # Write to DSS file(s).
    for study, f_path in study_fps.items():
        dss_fp = dss.open_dss(f_path)[0]
        st_filt = (df_copy['Study'] == study) if study else df_copy.any(axis=1)
        df_study = df_copy.loc[st_filt, :]
        list_pathname = df_study['Pathname'].unique()
        for pathname in list_pathname:
            pathname_filter = (df_study['Pathname'] == pathname)
            df_pathname = df_study.loc[pathname_filter, :].copy()
            df_pathname.sort_values('DateTime', inplace=True)
            df_pathname.reset_index(drop=True, inplace=True)
            cpath = pathname
            cdate = df_pathname['DateTime'].dt.strftime('%d%b%Y').values[0]
            ctime = df_pathname['DateTime'].dt.strftime('%H%M').values[0]
            vals = df_pathname['Value'].to_list()
            cunits = df_pathname['Units'].values[0]
            ctype = df_pathname['Data Type'].values[0]
            # TODO: Future to include writing meta-data and write options.
            # <JAS 2019-09-16>
            dss.write_regtsd(dss_fp, cpath, cdate, ctime, vals, cunits, ctype)
        dss.close_dss(dss_fp)
        if study:
            write_msg = 'Study {} successfully written to {} at {}.'
            print(write_msg.format(study, f_path, dt.datetime.now()))
        else:
            write_msg = 'DataFrame successfully written to {} at {}.'
            print(write_msg.format(f_path, dt.datetime.now()))
    # Return success indicator.
    return 0


def write_spreadsheet(format=''):
    """
    Notes
    -----
    Acceptable formats will be 'DSS Add-In' and 'Jacobs'.

    """
    pass


def write_sqlite():
    """
    Notes
    -----
    Code must first validate if the existing database is valid. It will create
    a new DB file if one does not exist.

    """
    pass


def read_CSH_LandUse(fp, **kwargs):
    """
    Summary
    -------
    Specialize query tool for reading CalSimHydro monthly repeating time
    series, starting at 4000-01-31.

    Parameters
    ----------
    fp : str
        File path (absolute or relative) of DSS file.
    **kwargs
        Keyword arguments to pass to `read_dss_catalog`.

    Returns
    -------
    df : pandas.DataFrame
        DataFrame of regular repeating time series with year as 2000 rather
        than 4000.

    """
    # Acquire catalog of pathnames.
    dss_cat = read_dss_catalog(fp, **kwargs)
    # Initialize values for `dss.read_regtsd`.
    cdate = '31Jan4000'
    ctime = '2400'
    # Get list of studies and file paths.
    study_fps = transform.cat_to_study_fps(dss_cat)
    list_df = list()
    # Read data into DataFrame.
    for study, f_path in study_fps:
        # Get pathnames for current file.
        # TODO: Issue here if adding multiple alternatives with the same file.
        # <JAS 2019-09-17>
        fp_filt = (dss_cat['File Path'] == f_path)
        st_filt = (dss_cat['Study'] == study) if study else dss_cat.any(axis=1)
        cat_filter = (fp_filt & st_filt)
        s_pathnames = dss_cat.loc[cat_filter, 'Pathname']
        # Query data from DSS file.
        ifltab = dss.open_dss(f_path)[0]
        for row in s_pathnames.index:
            cpath = s_pathnames[row]
            t_step = cpath.split('/')[5]
            fq = variables.t_steps[t_step]
            datetime = pd.date_range(start='2000-01-31', end='2000-12-31',
                                     freq=fq, name='DateTime')
            # TODO: Future will handle timezone information; code below.
            # <JAS 2019-09-16>
            # datetime = pd.date_range(start=start_date, end=end_date, freq=fq,
                                     # name='DateTime', tz='America/Los_Angeles')
            nvals = datetime.size
            df_temp = pd.DataFrame(datetime, columns=['DateTime'])
            if study: df_temp['Study'] = study
            dss_data = dss.read_regtsd(ifltab, cpath, cdate, ctime, nvals)
            df_temp['Pathname'] = cpath
            df_temp['Units'] = dss_data[2].upper()
            df_temp['Data Type'] = dss_data[3].upper()
            df_temp['Value'] = list(dss_data[1])
            list_df.append(df_temp.copy())
        dss.close_dss(ifltab)
        df = pd.concat(list_df)
    # NOTE: Legacy code below handles meta-data.
    # <JAS 2019-09-13>
    if False:
        coords_info = dss_ret[7]
        supp_info = [cpath, fp, dss_ret[6], coords_info['X_Long'],
                     coords_info['Y_Lat'], coords_info['CoordSys'][0],
                     coords_info['Datum'][0], coords_info['DatumUnit'][0],
                     dss_ret[8], dss_ret[11].value]
        df_meta_temp = pd.Series(supp_info, index=meta_col).to_frame().T
        df_meta = pd.concat([df_meta, df_meta_temp])
        df_meta.reset_index(drop=True, inplace=True)
        df_meta = df_meta.infer_objects()
    # Replace DSS missing value indicators with NaN and reset indices.
    df['Value'].replace([-901, -902], np.nan, inplace=True)
    df.reset_index(drop=True, inplace=True)
    # Return DataFrame.
    return df


# %% Execute script.
if __name__ == '__main__':
    msg = ('This module is intended to be imported for use into another'
           ' module. It is not intended to be run as a __main__ file.')
    raise RuntimeError(msg)
