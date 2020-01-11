"""
Summary
-------
The module compares and reports the differences between two DSS files.

"""
# %% Import libraries
# Import third party libraries.
import pandas as pd
# Import custom modules.
import custom_modules
from tools.io import read_dss_catalog, read_dss
from tools.transform import split_pathname, tidy_to_wide


# %% Define functions.
def compare_dss(fp_alt0, fp_alt1):
    """
    Summary
    -------
    Compare data in two DSS studies.

    Notes
    -----
    1. This procedure is optimized for CalSim3 studies.

    """
    # Construct catalog of data records.
    cat_alt0 = read_dss_catalog(fp_alt0)
    cat_alt1 = read_dss_catalog(fp_alt1)
    cat_alt0['Study'] = 'Alt0'
    cat_alt1['Study'] = 'Alt1'
    catalog = pd.concat([cat_alt0, cat_alt1], ignore_index=True)
    # Relative to Alt1, identify variables removed from Alt0.
    duplicates = catalog.duplicated('Pathname', keep=False)
    catalog = split_pathname(catalog)
    filter_alt0 = (~duplicates) & (catalog.Study == 'Alt0')
    removed_variables = list(catalog.loc[filter_alt0, 'Part B'].unique())
    # Relative to Alt1, identify new variables.
    filter_alt1 = (~duplicates) & (catalog.Study == 'Alt1')
    added_variables = list(catalog.loc[filter_alt1, 'Part B'].unique())
    # Identify common variables with a change in time series.
    common_variables = list(catalog.loc[duplicates, 'Part B'].unique())
    df = read_dss([fp_alt0, fp_alt1], b=common_variables,
                  end_date='2015-09-30')
    df = tidy_to_wide(df)
    diff = df['Alt1'] - df['Alt0']
    min_data_change = diff.abs().min()
    min_data_change.name = 'Value'
    min_data_change = min_data_change.reset_index()
    filter_common = (min_data_change.Value > 0)
    data_change = list(min_data_change.loc[filter_common, 'Part B'].unique())
    # Output report, if applicable.
    # <JAS> TODO: Generate a report format.
    if False:
        pass
    # Return data differences.
    return removed_variables, added_variables, data_change


# %% Execute script.
if __name__ == '__main__':
    # TODO: Provide command line inputs via `argparse` library,
    #       https://docs.python.org/3/library/argparse.html
    fp_alt0 = '../../CalSim3/common/DSS/CS3L2015SVClean_wHD-New.dss'
    fp_alt1 = '../../Incoming/2020-01-08_FromDWR_DCR/DCRBL_CS3_20191228/common/DSS/CS3L2015SVClean.dss'
    compare_dss(fp_alt0, fp_alt1)
