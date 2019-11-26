"""
Summary
-------
The purpose of this module is to validate data structures produced by the
`calsim_toolkit` library.

"""
# %% Import libraries.
# Import third party libraries.
import pandas as pd


# %% Define functions.
def is_catalog(df, verbose=False):
    # Ensure input is a DataFrame.
    if not isinstance(df, pd.DataFrame):
        msg = 'Input must be a pandas DataFrame.'
    # Make sure columns are appropriate.
    val_col = ['File Path', 'Pathname']
    if 'Study' in df.columns:
        val_col += ['Study']
    if (set(val_col) != set(df.columns)):
        if verbose:
            msg = ('DataFrame columns do not match catalog format'
                   ' specifications.')
            print(msg)
        return False
    # Return success.
    return True


def is_tidy(df, verbose=False):
    # Ensure input is a DataFrame.
    if not isinstance(df, pd.DataFrame):
        msg = 'Input must be a pandas DataFrame.'
    # Make sure columns are appropriate.
    val_col = ['DateTime', 'Pathname', 'Units', 'Data Type', 'Value']
    if 'Study' in df.columns:
        val_col += ['Study']
    if (set(val_col) != set(df.columns)):
        if verbose:
            msg = 'DataFrame columns do not match tidy format specifications.'
            print(msg)
        return False
    # Check that there are no duplicates.
    check_col = list(set(val_col) - set(['Value']))
    duplicates = df.duplicated(check_col, keep=False)
    if duplicates.any():
        if verbose:
            print(df.loc[duplicates, :])
            msg = ('DataFrame contains duplicate records (shown above).'
                   ' Please, remove duplicate data.')
            print(msg)
        return False
    # Return success.
    return True


def is_wide(df, verbose=False):
    # Ensure input is a DataFrame.
    if not isinstance(df, pd.DataFrame):
        msg = 'Input must be a pandas DataFrame.'
    # Make sure level names are appropriate.
    val_lvl = ['Part A', 'Part B', 'Part C', 'Part E',
               'Part F', 'Units', 'Data Type']
    if 'Study' in df.columns.names:
        val_lvl += ['Study']
    if (set(val_lvl) != set(df.columns.names)):
        if verbose:
            msg = ('DataFrame column level names do not match wide format'
                   ' specifications.')
            print(msg)
        return False
    # Check that there are no duplicate column headers.
    duplicates = df.columns.duplicated(keep=False)
    if duplicates.any():
        if verbose:
            print(df.loc[:, duplicates])
            msg = ('DataFrame contains duplicate columns (shown above).'
                   ' Please, remove duplicate data.')
            print(msg)
        return False
    # Return success.
    return True


def is_condense(df, verbose=False):
    # Ensure input is a DataFrame.
    if not isinstance(df, pd.DataFrame):
        msg = 'Input must be a pandas DataFrame.'
    # Make sure level names are appropriate.
    val_lvl = ['Part A', 'Part B', 'Part C', 'Part E',
               'Part F', 'Units & Type']
    if 'Study' in df.columns.names:
        val_lvl += ['Study']
    if not (set(df.columns.names) <= set(val_lvl)):
        if verbose:
            msg = ('DataFrame column level names do not match condense format'
                   ' specifications.')
            print(msg)
        return False
    # Check that there are no duplicate column headers.
    duplicates = df.columns.duplicated(keep=False)
    if duplicates.any():
        if verbose:
            print(df.loc[:, duplicates])
            msg = ('DataFrame contains duplicate columns (shown above).'
                   ' Please, remove duplicate data.')
            print(msg)
        return False
    # Return success.
    return True


# %% Execute script.
if __name__ == '__main__':
    msg = ('This module is intended to be imported for use into another'
           ' module. It is not intended to be run as a __main__ file.')
    raise RuntimeError(msg)
