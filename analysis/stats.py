"""
Summary
-------
The purpose of this module is to calculate statistics on data structures
produced by the `calsim_toolkit` library and associated CalSim studies.

"""
# %% Import libraries.
# Import standard libraries.
import datetime as dt
# Import third party libraries.
import numpy as np
import pandas as pd
# Import module libraries.
from ..tools import transform, validation, variables


# %% Define functions.
def AggregateAnnual(df, eom=9):
    # Initialize DataFrame and other variables.
    df_copy = df.copy()
    cols = df_copy.columns
    return_tidy = False
    return_wide = False
    return_condense = False
    water_year = lambda x: x.year if x.month < 10 else x.year + 1
    # Transform DataFrame to tidy format.
    if validation.is_tidy(df_copy):
        return_tidy = True
        transform.split_pathname(df_copy, inplace=True)
    elif validation.is_wide(df_copy):
        return_wide = True
        df_copy = transform.wide_to_tidy(df_copy)
        transform.split_pathname(df_copy, inplace=True)
    elif validation.is_condense(df_copy):
        return_condense = True
        df_copy = transform.condense_to_tidy(df_copy, a='CALSIM', c='TEMP',
                                             f='TEMP')
        transform.split_pathname(df_copy, inplace=True)
    else:
        msg = 'DataFrame format unrecognizable!'
        raise RuntimeError(msg)
    # Split DataFrame by "Data Type".
    df_aver = df_copy.loc[df_copy['Data Type'] == 'PER-AVER', :].copy()
    df_cum = df_copy.loc[df_copy['Data Type'] == 'PER-CUM', :].copy()
    df_val = df_copy.loc[df_copy['Data Type'] == 'INST-VAL', :].copy()
    # Define grouping for aggregation.
    grouping = list(set(df_copy.columns) - set(['Value']))
    # Calculate annual means for 'PER-AVER'.
    df_aver['DateTime'] = df_aver['DateTime'].apply(water_year)
    df_aver = df_aver.groupby(grouping).mean()
    df_aver.reset_index(inplace=True)
    # Calculate annual sums for 'PER-CUM'.
    df_cum['DateTime'] = df_cum['DateTime'].apply(water_year)
    df_cum = df_cum.groupby(grouping).sum()
    df_cum.reset_index(inplace=True)
    # Re-index 'INST-VAL' DataFrame based on End of Month (eom) value.
    df_val = df_val.loc[df_val['DateTime'].dt.month == eom, :]
    df_val['DateTime'] = df_val['DateTime'].apply(water_year)
    # Concatenate DataFrames.
    df_annual = pd.concat([df_aver, df_cum, df_val],
                          ignore_index=True, sort=True)
    # Transform DataFrame to its original format.
    df_annual = transform.join_pathname(df_annual, e='temp')
    df_annual['DateTime'] = pd.to_datetime(df_annual['DateTime'], format='%Y')
    if return_tidy:
        df_annual['DateTime'] = df_annual['DateTime'].dt.year
        df_annual = df_annual[cols].copy()
        df_annual.rename({'DateTime': 'Water Year'}, axis=1, inplace=True)
    elif return_wide:
        df_annual = transform.tidy_to_wide(df_annual)
        df_annual.index = df_annual.index.year
        df_annual.index.name = 'Water Year'
        df_annual = df_annual[cols].copy()
    elif return_condense:
        df_annual = transform.tidy_to_condense(df_annual)
        df_annual.index = df_annual.index.year
        df_annual.index.name = 'Water Year'
        df_annual = df_annual[cols].copy()
    # Return DataFrame of annual aggregation.
    return df_annual


def PeriodMean(df, eom=9, stdev=False):
    # Override `stdev`.
    # NOTE: `stdev` will be available for future use.
    # <JAS 2020-01-03>
    stdev = False
    # Initialize DataFrame.
    df_copy = df.copy()
    # Transform DataFrame, if it is in tidy format.
    return_tidy = False
    if validation.is_tidy(df_copy):
        df_copy = transform.tidy_to_wide(df_copy)
        return_tidy = True
    # Pass DataFrame to `AggregateAnnual`.
    df_mean = AggregateAnnual(df_copy, eom=eom)
    # Calculate means.
    df_mean = df_mean.mean()
    # Transform back to tidy format, if applicable.
    if return_tidy:
        df_mean.name = 'Value'
        df_mean = df_mean.reset_index()
    # Return Series or DataFrame.
    return df_mean


def MonthlyMean(df, stdev=False):
    # Override `stdev`.
    # NOTE: `stdev` will be available for future use.
    # <JAS 2019-10-09>
    stdev = False
    # Initialize DataFrame.
    df_copy = df.copy()
    # Transform DataFrame, if it is in tidy format.
    return_tidy = False
    if validation.is_tidy(df_copy):
        df_copy = transform.tidy_to_wide(df_copy)
        return_tidy = True
    # Calculate monthly means.
    df_month = df_copy.groupby(df_copy.index.month).mean()
    # Re-index by month names.
    month_name = lambda x: dt.datetime(2000, x.name, 1).strftime('%b')
    df_month.index = df_month.apply(month_name, axis=1)
    df_month = df_month.reindex(variables.water_months)
    df_month.index.name = 'Month'
    # Repeat process if standard deviation is requested.
    if stdev:
        df_stdev = df_copy.groupby(df_copy.index.month).std()
        df_stdev.index = df_stdev.apply(month_name, axis=1)
        df_stdev = df_stdev.reindex(variables.water_months)
        # ????: When transforming back into a tidy format; do I want to combine
        #       means and standard deviations? What does `pyviz` require?
        # <JAS 2019-10-08>
        return df_month, df_stdev
    # Transform back to tidy format, if applicable.
    if return_tidy:
        df_month = df_month.stack(list(range(df_month.columns.nlevels)))
        df_month.name = 'Value'
        df_month = df_month.reset_index()
    # Return DataFrame of annual aggregation.
    return df_month


def MonthlyExceedence(df):
    # Initialize DataFrame.
    df_copy = df.copy()
    # Transform DataFrame, if it is in tidy format.
    return_tidy = False
    if validation.is_tidy(df_copy):
        df_copy = transform.tidy_to_wide(df_copy)
        return_tidy = True
    # Create DataFrame of Exceedence ratios, ignoring missing values.
    df_excd = df_copy.rank(method='first', ascending=False)
    df_excd = df_excd / (df_excd.max() + 1)
    # Concatenate Exceedence ratios and original values into single DataFrame.
    df_list = list()
    for col in df_copy.columns:
        s_temp = pd.Series(df_copy[col].values, index=df_excd[col].values,
                           copy=True, name=col)
        df_list.append(s_temp)
    df_exceedence = pd.concat(df_list, axis=1)
    df_exceedence.columns.set_names(df_copy.columns.names, inplace=True)
    df_exceedence.index.name = 'Exceedence Probability'
    # Fill in missing values.
    df_exceedence.fillna(method='bfill', inplace=True)
    df_exceedence.fillna(method='ffill', inplace=True)
    # Transform back to tidy format, if applicable.
    if return_tidy:
        num_lvls = list(range(df_exceedence.columns.nlevels))
        df_exceedence = df_exceedence.stack(num_lvls)
        df_exceedence.name = 'Value'
        df_exceedence = df_exceedence.reset_index()
    # Return DataFrame of annual aggregation.
    return df_exceedence


def AnnualExceedence(df, eom=9):
    # Initialize DataFrame.
    df_copy = df.copy()
    # Transform DataFrame, if it is in tidy format.
    return_tidy = False
    if validation.is_tidy(df_copy):
        df_copy = transform.tidy_to_wide(df_copy)
        return_tidy = True
    # Pass DataFrame to `AggregateAnnual`.
    df_excda = AggregateAnnual(df_copy, eom=eom)
    # Create DataFrame of Exceedence ratios, ignoring missing values.
    df_excd = df_excda.rank(method='first', ascending=False)
    df_excd = df_excd / (df_excd.max() + 1)
    # Concatenate Exceedence ratios and original values into single DataFrame.
    df_list = list()
    for col in df_excda.columns:
        s_temp = pd.Series(df_excda[col].values, index=df_excd[col].values,
                           copy=True, name=col)
        df_list.append(s_temp)
    df_exceedence = pd.concat(df_list, axis=1)
    df_exceedence.columns.set_names(df_excda.columns.names, inplace=True)
    df_exceedence.index.name = 'Exceedence Probability'
    # Fill in missing values.
    df_exceedence.fillna(method='bfill', inplace=True)
    df_exceedence.fillna(method='ffill', inplace=True)
    # Transform back to tidy format, if applicable.
    if return_tidy:
        num_lvls = list(range(df_exceedence.columns.nlevels))
        df_exceedence = df_exceedence.stack(num_lvls)
        df_exceedence.name = 'Value'
        df_exceedence = df_exceedence.reset_index()
    # Return DataFrame of annual aggregation.
    return df_exceedence


# %% Execute script.
if __name__ == '__main__':
    msg = ('This module is intended to be imported for use into another'
           ' module. It is not intended to be run as a __main__ file.')
    raise RuntimeError(msg)
