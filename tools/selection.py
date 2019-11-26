"""
Summary
-------
The purpose of this module is to select from data structures produced by the
`calsim_toolkit` library.

"""
# %% Import libraries.
# Import module libraries.
from . import transform, validation


# %% Define functions.
def PartB(df, b, match=True):
    # Initialize DataFrame.
    df_copy = df.copy()
    # Ensure `b` is a list.
    b_uppr = [x.upper() for x in b] if isinstance(b, list) else [b.upper()]
    # Filter DataFrame, based on DataFrame type.
    if validation.is_tidy(df_copy):
        if match:
            df_split = transform.split_pathname(df_copy)
            filter = df_split['Part B'].isin(b_uppr)
        else:
            b_search = '|'.join(b_uppr)
            df_split = transform.split_pathname(df_copy)
            filter = df_split['Part B'].str.contains(b_search, regex=True)
        df_filtered = df_copy.loc[filter, :].copy()
    elif validation.is_wide(df_copy) or validation.is_condense(df_copy):
        col_list = list()
        Part_Bs = df_copy.columns.get_level_values('Part B')
        for i in range(len(Part_Bs)):
            for j in range(len(b_uppr)):
                if match:
                    if Part_Bs[i] == b_uppr[j]:
                        col_list.append(df_copy.columns[i])
                else:
                    if b_uppr[j] in Part_Bs[i]:
                        col_list.append(df_copy.columns[i])
        df_filtered = df_copy.loc[:, col_list].copy()
    # If no filtered succeed, return the original DataFrame.
    if df_filtered.empty:
        msg = 'No data filtered based on given criteria.'
        print(msg)
        return df_copy
    # Otherwise, return filtered DataFrame.
    return df_filtered


# %% Execute script.
if __name__ == '__main__':
    msg = ('This module is intended to be imported for use into another'
           ' module. It is not intended to be run as a __main__ file.')
    raise RuntimeError(msg)
