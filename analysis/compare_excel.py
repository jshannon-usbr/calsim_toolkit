"""
Summary
-------
The module compares and reports the differences between two excel files.

Notes
-----
1. Currently, these functions can only compare *.xls & *.xlsx files. Future
   development to include comparison with *.xlsm & *.xlsb files.
2. With openpyxl, you can get the column level from an index value, `idx`, with
   `openpyxl.utils.cell.get_column_letter(idx)`
3. For splitting a column of tuples: https://stackoverflow.com/a/29550458

"""
# %% Import libraries
# Import standard libraries.
import os
import warnings
import argparse
# Import third party libraries.
import openpyxl as oxl
import pandas as pd


# %% Define functions.
def read_excel(fp):
    """
    Summary
    -------
    Read the values and formulas of an excel workbook into a `pandas`
    DataFrame.

    Parameters
    ----------
    fp : path
        Absolute or relative file path to *.xlsx or *.xls workbook.

    Returns
    -------
    wb_content : `pandas` DataFrame
        A DataFrame containing the sheet name, row & column coordinates, and
        cell value for each recorded entry.

    """
    # Initialize variables.
    keys = ['Sheet', 'Row', 'Column', 'Value']
    # Open workbook.
    if os.path.exists(fp):
        wb = oxl.load_workbook(filename=fp)
    else:
        msg = '{} not found.'.format(fp)
        raise OSError(msg)
    # For each sheet, get cell range and each cell value.
    records = list()
    for sheet in wb:
        sheet_name = sheet.title
        for row in sheet.rows:
            for cell in row:
                if cell.value:
                    values = [sheet_name, cell.row, cell.column, cell.value]
                    record = dict(zip(keys, values))
                    records.append(record)
    # Construct DataFrame.
    wb_content = pd.DataFrame(records, columns=keys)
    # Return dictionary of information.
    return wb_content


def main(fp_original, fp_modified):
    print(fp_original, fp_modified, sep='\n')
    print('The function `compare_excel` is currently unavailable')
    pass


# %% Execute script.
# Suppress warnings from `openpyxl`.
warnings.simplefilter('ignore')
# Parse command line arguments.
if __name__ == '__main__':
    # Initialize argument parser.
    intro = '''
            The module summarizes contents of an Excel file (*.xlsx or *.xls)
            and compares the differences with an alternative excel file. If no
            path is provided in `fp1`, then a summary of content is produced
            with the `read_excel` function; otherwise, comparative differences
            with `fp0` are summarized with `main`.
            '''
    parser = argparse.ArgumentParser(description=intro)
    # Add positional arguments to parser.
    parser.add_argument('fp0', metavar='fp0', type=str, nargs='?',
                        help='File path to *.xlsx or *.xls for review.')
    # Add optional arguments.
    parser.add_argument('-f', '--fp1', metavar='fp1', type=str,
                        nargs='?',
                        help='''
                             File path to *.xlsx or *.xls for comparison to
                             `fp0`.
                             ''')
    # Parse arguments.
    args = parser.parse_args()
    fp0 = args.fp0.strip('"')
    fp1 = args.fp1.strip('"') if args.fp1 else None
    # Pass arguments to function.
    if args.fp1:
        main(fp0, fp1)
    else:
        df = read_excel(fp0)
        print(df)
