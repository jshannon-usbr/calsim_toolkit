"""
Summary
-------
The purpose of this module is to review and correct data unit issues in a
CalSim DSS file.

"""
# %% Import libraries.
# Import standard libraries.
import os
import argparse
# Import third party libraries.
import pandas as pd
# Import custom modules.
try:
    import custom_modules
    from tools.io import read_dss, write_dss
    from tools.transform import split_pathname, join_pathname
except(ModuleNotFoundError):
    from ..tools.io import read_dss, write_dss
    from ..tools.transform import split_pathname, join_pathname


# %% Define functions.
def main(fp, auto_correct_file=False, fp_init=False, verbose=True):
    """
    Summary
    -------
    This main function detects incorrect units in a CalSim DSS file and applies
    a correction. Note, this procedure is current optimized for CalSim3 DSS
    files.

    Parameters
    ----------
    fp : path
        Absolute or relative file path a CalSim DSS file.
    auto_correct_file : bool, default False, optional
        Option to bypass user prompt to correct CalSim unit labeling and
        automatically apply corrections.
    fp_init : bool, default False, optional
        Option to flag if `fp` is an initialization file (INIT).

    Returns
    -------
    part_Bs : list
        List of Part B variables flag for data unit correction. An empty list
        indicates that all variables units are correct according to this
        procedure.

    Notes
    -----
    1. According the HEC-DSS, the available data types are 'PER-AVER',
       'PER-CUM', and 'INST-VAL'.
    2. Correcting units in Init and SV *.dss files does not have an effect or
       creates errors when running a CalSim study. Storage units of 'TAF
       INST-VAL' do not seem to propogate through to the DV file, remaining in
       units of 'TAF PER-AVER'. As a result, it is best to use this tool as a
       pre-processor prior to visualization with the `calsim_toolkit`.

    """
    # Ensure passed file path is a DSS file.
    _, extn = os.path.splitext(fp)
    if extn.lower() != '.dss':
        msg = 'This procedure can currently only handle a *.dss file.'
        raise RuntimeError(msg)
    # Query in data.
    if fp_init:
        df = read_dss(fp, start_date='1918-05-31', end_date='1921-11-30')
    else:
        df = read_dss(fp, end_date='2015-09-30')
    df = split_pathname(df)
    # Flag where 'Units' column has additional whitespace.
    filter_ws = df['Units'] != df['Units'].str.strip()
    # Flag where 'STORAGE' variables are not unit date-types 'TAF INST-VAL'.
    filter_sc = df['Part C'] == 'STORAGE'
    filter_su = df['Units'] != 'TAF'
    filter_sd = df['Data Type'] != 'INST-VAL'
    filter_stor = (filter_sc & (filter_su | filter_sd))
    # Flag where non-STORAGE variables with unit 'TAF' are not 'PER-CUM'.
    filter_nc = df['Part C'] != 'STORAGE'
    filter_nu = df['Units'] == 'TAF'
    filter_nd = df['Data Type'] != 'PER-CUM'
    filter_nonstor = ((filter_nc & filter_nu) & filter_nd)
    # Flag variables with unit 'CFS' without date-type 'PER-AVER'.
    filter_cu = df['Units'] == 'CFS'
    filter_cd = df['Data Type'] != 'PER-AVER'
    filter_cfs = (filter_cu & filter_cd)
    # Combine filters into a single filter.
    filter_combo = (filter_ws | filter_stor | filter_nonstor | filter_cfs)
    # Correct or report data unit issues.
    if filter_combo.any():
        part_Bs = df.loc[filter_combo, 'Part B'].unique().tolist()
        df = join_pathname(df)
        if verbose:
            print('Found values requiring unit correction.')
            first_pth = ~df.duplicated('Pathname')
            col = ['Pathname', 'Units', 'Data Type']
            for v in df.loc[filter_ws & first_pth, col].values.tolist():
                p, u, _ = v
                print('{}: "{}" -> "{}"'.format(p, u, u.strip()))
            for v in df.loc[filter_stor & first_pth, col].values.tolist():
                p, u, d = v
                print(f'{p}: "{u} {d}" -> "TAF INST-VAL"')
            for v in df.loc[filter_nonstor & first_pth, col].values.tolist():
                p, u, d = v
                print(f'{p}: "{u} {d}" -> "{u} PER-CUM"')
            for v in df.loc[filter_cfs & first_pth, col].values.tolist():
                p, u, d = v
                print(f'{p}: "{u} {d}" -> "{u} PER-AVER"')
        if auto_correct_file:
            df['Units'] = df['Units'].str.strip()
            df.loc[filter_stor, ['Units', 'Data Type']] = ['TAF', 'INST-VAL']
            df.loc[filter_nonstor, 'Data Type'] = 'PER-CUM'
            df.loc[filter_cfs, 'Data Type'] = 'PER-AVER'
            _ = write_dss(fp, df.loc[filter_combo, :])
    else:
        if verbose: print('Found no variables requiring unit correction.')
        part_Bs = list()
    # Return list of Part B required for correction.
    return part_Bs


# %% Execute script.
if __name__ == '__main__':
    # Initialize argument parser.
    intro = '''
            Detects incorrect units in a CalSim DSS file and applies
            a correction.
            '''
    parser = argparse.ArgumentParser(description=intro)
    # Add positional arguments to parser.
    parser.add_argument('fp', metavar='DSS file path', type=str, nargs='?',
                        help='Absolute or relative path to DSS file.')
    # Add optional arguments.
    parser.add_argument('-c', '--correct', action='store_true', default=False,
                        help='''
                             Option to automatically correct detected unit
                             issues in DSS file.
                             ''')
    parser.add_argument('-i', '--init', action='store_true', default=False,
                        help='''
                             Option to flag if `fp` is an initialization file
                             (INIT).
                             ''')
    # Parse arguments.
    args = parser.parse_args()
    fp = args.fp.strip('"')
    auto_correct_file = args.correct
    fp_init = args.init
    verbose = not auto_correct_file
    # Pass arguments to function.
    _ = main(fp, auto_correct_file=auto_correct_file, fp_init=fp_init,
             verbose=verbose)
