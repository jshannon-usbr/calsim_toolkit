"""
Summary
-------
The purpose of this module is to transform data structures produced by the
`calsim_toolkit` library.

"""
# %% Import libraries.
# Import third party libraries.
import numpy as np
import pandas as pd
# Import module libraries.
from . import validation, variables


# %% Define functions.
def split_pathname(df, inplace=False):
    """
    Summary
    -------
    Function to split "Pathname" column of CalSim tidy DataFrame into parts.

    """
    # Initialize DataFrame for operation.
    df_out = df if inplace else df.copy()
    # Split Pathname into Parts.
    path_split = ['Part 0', 'Part A', 'Part B', 'Part C', 'Part D', 'Part E',
                  'Part F', 'Part 7']
    df_out[path_split] = df_out['Pathname'].str.split('/', expand=True)
    # Drop extra columns.
    drop_col = ['Pathname', 'Part 0', 'Part D', 'Part 7']
    df_out.drop(drop_col, axis=1, inplace=True)
    # Return DataFrame.
    return df_out


def join_pathname(df, inplace=False, a=None, c=None, e=None, f=None):
    """
    Summary
    -------
    Function to join pathname parts of CalSim tidy DataFrame into a "Pathname"
    column.

    """
    # Initialize DataFrame for operation.
    df_out = df if inplace else df.copy()
    # Infer Part E, if not provided.
    if not e:
        inf_t_step = pd.infer_freq(df_out['DateTime'].unique())
        e = variables.t_steps_inv[inf_t_step] if inf_t_step else None
    # Set column requirements.
    req_col = {'Part A': a, 'Part C': c, 'Part E': e, 'Part F': f}
    # Fill missing required columns.
    miss_col = list()
    for k, v in req_col.items():
        if k not in df_out.columns:
            if v:
                df_out[k] = v
            else:
                miss_col.append(k)
    if miss_col:
        msg = 'Values required for the following columns: {}.'
        raise ValueError(msg.format(miss_col))
    # Create "Pathname" column.
    construct_pathname = lambda x: r'/{}/{}/{}//{}/{}/'.format(*x.values)
    col_part = ['Part A', 'Part B', 'Part C', 'Part E', 'Part F']
    df_out['Pathname'] = df_out[col_part].apply(construct_pathname, axis=1)
    # Drop pathname parts.
    df_out.drop(col_part, axis=1, inplace=True)
    # Return DataFrame.
    return df_out


def cat_to_study_fps(df):
    """
    Function to extract a `study_fps` list from a DSS catalog DataFrame.
    See `.io.parse_filepaths` function for specifications regarding
    `study_fps`.

    """
    # Ensure input DataFrame meets catalog specifications.
    if not validation.is_catalog(df, verbose=True):
        msg = 'Input DataFrame is not a DSS catalog.'
        raise TypeError(msg)
    # Construct `study_fps` based on existence of 'Study' column.
    if 'Study' in df.columns:
        duplicates = df.duplicated(['Study', 'File Path'])
        df_study_fps = df.loc[~duplicates, ['Study', 'File Path']].copy()
        study_fps = list()
        for row in df_study_fps.index:
            study = df_study_fps.loc[row, 'Study']
            f_path = df_study_fps.loc[row, 'File Path']
            study_fps.append((study, f_path))
    else:
        f_paths = df['File Path'].unique()
        study_fps = list(zip([None] * len(f_paths), f_paths))
    # Return list of tuples.
    return study_fps

def tidy_to_wide(df):
    """
    Summary
    -------
    Transforms a copy of the input DataFrame from tidy to wide data format.

    """
    # Ensure input DataFrame is in tidy format.
    if not validation.is_tidy(df):
        msg = 'Cannot transform DataFrame from tidy format to wide format.'
        raise TypeError(msg)
    # Initialize DataFrame for operation.
    df_out = df.copy()
    # Split Pathname into Parts.
    split_pathname(df_out, inplace=True)
    # Pivot DataFrame.
    col_header = ['Part A', 'Part B', 'Part C', 'Part E', 'Part F',
                  'Units', 'Data Type']
    if 'Study' in df_out.columns:
        col_header.insert(0, 'Study')
    df_out.set_index(col_header + ['DateTime'], append=True, inplace=True)
    df_out.reset_index(0, drop=True, inplace=True)
    df_out = df_out['Value']
    df_out = df_out.unstack(col_header)
    df_out.index.freq = pd.infer_freq(df_out.index, warn=False)
    # Return DataFrame.
    return df_out


def wide_to_tidy(df):
    """
    Summary
    -------
    Transforms a copy of the input DataFrame from wide to tidy data format.

    """
    # ISSUE: Need to address sort order to maintain original ordering.
    # <JAS 2019-10-08>
    # Ensure input DataFrame is in wide format.
    if not validation.is_wide(df):
        msg = 'Cannot transform DataFrame from wide format to tidy format.'
        raise TypeError(msg)
    # Initialize DataFrame for operation.
    df_out = df.copy()
    # Fill NaNs to prevent data loss.
    df_out.fillna(-901, inplace=True)
    # Pivot DataFrame.
    df_out = df_out.stack(df_out.columns.names)
    df_out.name = 'Value'
    df_out = df_out.reset_index()
    # Join pathname parts into "Pathname" column.
    join_pathname(df_out, inplace=True)
    # Replace -901 with NaNs.
    df_out.replace(-901, np.nan, inplace=True)
    # Return DataFrame.
    return df_out


def tidy_to_condense(df):
    """
    Summary
    -------
    Transforms a copy of the input DataFrame from tidy to condense data format.

    """
    # Ensure input DataFrame is in tidy format.
    if not validation.is_tidy(df):
        msg = 'Cannot transform DataFrame from tidy format to condense format.'
        raise TypeError(msg)
    # Initialize DataFrame for operation.
    df_out = df.copy()
    # Split Pathname into Parts.
    split_pathname(df_out, inplace=True)
    # Combine 'Units' and 'Data Type' columns in 'Units & Type' column.
    col_unit = ['Units', 'Data Type']
    new_unit = lambda x: '{} {}'.format(*x.values)
    df_out['Units & Type'] = df_out[col_unit].apply(new_unit, axis=1)
    df_out.drop(col_unit, axis=1, inplace=True)
    # Drop columns with unique values.
    col_uni = ['Part A', 'Part C', 'Part E', 'Part F']
    if 'Study' in df_out.columns:
        col_uni += ['Study']
    for c in col_uni:
        if len(df_out[c].unique()) == 1:
            df_out.drop(c, axis=1, inplace=True)
    # Pivot DataFrame.
    col_idx = list(set(df_out.columns) - set(['Value']))
    df_out.set_index(col_idx, append=True, inplace=True)
    df_out.reset_index(0, drop=True, inplace=True)
    df_out = df_out['Value']
    idx_piv = sorted(list(set(col_idx) - set(['DateTime'])))
    if 'Study' in idx_piv:
        idx_piv.remove('Study')
        idx_piv.insert(0, 'Study')
    df_out = df_out.unstack(idx_piv)
    df_out.index.freq = pd.infer_freq(df_out.index, warn=False)
    # Return DataFrame.
    return df_out


def condense_to_tidy(df, a=None, c=None, f=None):
    """
    Summary
    -------
    Transforms a copy of the input DataFrame from condense to tidy data format.

    """
    # ISSUE: Need to address sort order to maintain original ordering.
    # <JAS 2019-10-08>
    # Ensure input DataFrame is in wide format.
    if not validation.is_condense(df):
        msg = 'Cannot transform DataFrame from condense format to tidy format.'
        raise TypeError(msg)
    # Initialize DataFrame for operation.
    df_out = df.copy()
    # Fill NaNs to prevent data loss.
    df_out.fillna(-901, inplace=True)
    # Pivot DataFrame.
    df_out = df_out.stack(df_out.columns.names)
    df_out.name = 'Value'
    df_out = df_out.reset_index()
    # Split 'Units & Type' column into 'Units' and 'Data Type' columns.
    org_unit = ['Units', 'Data Type']
    df_out[org_unit] = df_out['Units & Type'].str.split(expand=True)
    df_out.drop('Units & Type', axis=1, inplace=True)
    # Join pathname parts into "Pathname" column.
    join_pathname(df_out, inplace=True, a=a, c=c, f=f)
    # Replace -901 with NaNs.
    df_out.replace(-901, np.nan, inplace=True)
    # Return DataFrame.
    return df_out


# %% Execute script.
if __name__ == '__main__':
    msg = ('This module is intended to be imported for use into another'
           ' module. It is not intended to be run as a __main__ file.')
    raise RuntimeError(msg)
