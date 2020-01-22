"""
Summary
-------
The module compares and reports the differences between two DSS files.

"""
# %% Import libraries
# Import standard libraries.
import argparse
# Import third party libraries.
import pandas as pd
# Import custom modules.
try:
    import custom_modules
    from tools.io import read_dss_catalog, read_dss
    from tools.transform import split_pathname, tidy_to_wide
except(ModuleNotFoundError):
    from ..tools.io import read_dss_catalog, read_dss
    from ..tools.transform import split_pathname, tidy_to_wide


# %% Define functions.
def main(fp_alt0, fp_alt1, output_file='', verbose=False):
    """
    Summary
    -------
    Compare data in two DSS studies.

    Notes
    -----
    1. This procedure is optimized for CalSim3 studies.

    Parameters
    ----------
    fp_alt0 : path
        Absolute or relative file path to baseline *.dss file.
    fp_alt1 : path
        Absolute or relative file path to alternative *.dss file.
    output_file : path, default '', optional
        Absolute or relative file path for writing comparison report to disk.
        If no path is provided, the report is not written to disk.
    verbose : boolean, default True, optional
        Option to display contents of comparison report to console.

    Returns
    -------
    removed_variables : list
        List of Part B variables removed from `fp_alt1` with respect to
        `fp_alt0`.
    added_variables : list
        List of Part B variables added to `fp_alt1` with respect to
        `fp_alt0`.
    data_change : list
        List of common Part B variables time series with differences between
        `fp_alt0`and `fp_alt1`.

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
    if output_file or verbose:
        report = f'Variables removed from {fp_alt1} relative to {fp_alt0}.'
        for removed_variable in removed_variables:
            report += '\n' + removed_variable
        report += ('\n\n'
                   + f'Variables added to {fp_alt1} relative to {fp_alt0}.')
        for added_variable in added_variables:
            report += '\n' + added_variable
        report += ('\n\n'
                   + f'Common variables with changes in {fp_alt1}'
                   + f' relative to {fp_alt0}.')
        for d in data_change:
            report += '\n' + d
    if output_file:
        with open(output_file, 'w') as fp:
            fp.write(report)
        msg = 'Successfully written report to {}'
        print(msg.format(output_file))
    if verbose:
        print(report)
    # Return data differences.
    return removed_variables, added_variables, data_change


# %% Execute script.
# Parse command line arguments.
if __name__ == '__main__':
    # Initialize argument parser.
    intro = '''
            The module compares and reports the differences between two DSS
            files.
            '''
    parser = argparse.ArgumentParser(description=intro)
    # Add positional arguments to parser.
    parser.add_argument('fp_alt0', metavar='fp_alt0', type=str, nargs='?',
                        help='''
                             Absolute or relative file path to baseline *.dss
                             file.
                             ''')
    parser.add_argument('fp_alt1', metavar='fp_alt1', type=str, nargs='?',
                        help='''
                             Absolute or relative file path to alternative
                             *.dss file.
                             ''')
    # Add optional arguments.
    parser.add_argument('-o', '--outfile', metavar='output file', type=str,
                        nargs='?', default='',
                        help='''
                             Absolute or relative file path for writing
                             comparison report to disk. If no path is provided,
                             the report is not written to disk.
                             ''')
    parser.add_argument('-s', '--silent', dest='verbose', action='store_false',
                        default=True,
                        help='''
                             Option to suppress contents of comparison report
                             to console.
                             ''')
    # Parse arguments.
    args = parser.parse_args()
    fp0 = args.fp_alt0.strip('"')
    fp1 = args.fp_alt1.strip('"')
    output_file = args.outfile.strip('"')
    verbose = args.verbose
    # Pass arguments to function.
    _ = main(fp0, fp1, output_file=output_file, verbose=verbose)
