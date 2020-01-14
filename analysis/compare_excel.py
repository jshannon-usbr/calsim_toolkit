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
# Import third party libraries.
import openpyxl as oxl
import pandas as pd


# %% Define functions.
def read_excel(fp):
    """
    Summary
    -------
    Read the values and formulas of an excel worbook into a `pandas` DataFrame.

    Parameters
    ----------
    fp : path
        File path to *.xlsx or *.xls workbook.

    Returns
    -------
    wb_content : `pandas` DataFrame
        A DataFrame containing the sheet name, row & column coordinates, and
        cell value for each recorded entry.

    """
    # Initialize variables.
    col = ['Sheet', 'Row', 'Column', 'Value']
    wb_content = pd.DataFrame(columns=col)
    i = 0
    # Open workbook.
    if os.path.exists(fp):
        wb = oxl.load_workbook(filename=fp)
    else:
        msg = '{} not found.'.format(fp)
        raise OSError(msg)
    # For each sheet, get cell range and each cell value.
    for sheet in wb:
        sheet_name = sheet.title
        for row in sheet.rows:
            for cell in row:
                if cell.value:
                    record = [sheet_name, cell.row, cell.column, cell.value]
                    wb_content.loc[i] = record
                    i += 1
    # Return dictionary of information.
    return wb_content


def compare_excel(fp_original, fp_modified):
    pass


# %% Execute script.
if __name__ == '__main__':
    # TODO: Provide command line inputs via `argparse` library,
    #       https://docs.python.org/3/library/argparse.html
    pass
