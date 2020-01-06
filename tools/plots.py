"""
Summary
-------
This `plot` Python module is for the `calsim_toolkit` library and relies on
data formats specified therein.

Future Development
------------------
Below are a list of tasks for future development:

    1. Change plot styling to reflect Data-To-Ink ratio best practices [1_].
    2. Directory reorganization.
    3. Inclusion of `plotly` in addition to `matplotlib`.
    4. Add file configuration for connection to `usbr_py3dss`.
    5. Add capability to read difference data sources.
    6. Add `__init__.py`, `requirements.txt`, & `setup.py` to directory.
    7. Refine "Header" meta-data for module.
    8. Add option to see differences from baseline.
    9. Updated PlotPD() to address depreciation warning.
    10. Add error catching for y-axis range (Nan and Inf cases).
    11. Add option to present table data with chart.
    12. Modify library to incorporate "pyviz" environment workflow.
    13. Modify pd.DataFrame specifications to allow for MultiIndex or single
        level column index.
    14. Incorporate terminology of "tidy data" and "wide data."
    15. Incorporate `drop_input` option for conversion between TAF and CFS.
    16. Review capabilities of other unit variables (i.e. Not TAF or CFS).

References
----------
The references listed below are formatted according to Chicago Manual of Style,
16th Edition.

.. [1] "Customizing Matplotlib with Style Sheets and RcParams¶." Matplotlib:
   Python Plotting - Matplotlib 2.2.3 Documentation. Accessed February 01,
   2019. https://matplotlib.org/tutorials/introductory/customizing.html.

.. [2] "Plotly." Modern Visualization for the Data Era - Plotly. Accessed
   February 01, 2019. https://plot.ly/matplotlib/.

.. [3] "Plotly." Modern Visualization for the Data Era - Plotly. Accessed
   February 01, 2019. https://plot.ly/matplotlib/bar-charts/.

"""
# %% Import libraries.
# Import standard libraries.
import os
import datetime as dt
# Import third party libraries.
import numpy as np
from pandas.plotting import register_matplotlib_converters
import matplotlib.pyplot as plt
from sklearn.metrics import r2_score
# Import custom modules.
from ..analysis import stats


# %% Define functions.
def PlotChartNotes():
    # Obtain notes from text file.
    this_dir = os.path.dirname(os.path.abspath(__file__))
    with open(os.path.join(this_dir, 'plot_notes.txt')) as f:
        notes = f.read()
    # Return string.
    return notes


def PlotAA(df, eom=9, show_plot=True):
    """
    Summary
    -------
    Plot of annual average bar chart.

    No documentation as of 2018-10-31.

    Future Development
    ------------------
    1. Add comma separator to y-axis.
    2. Add option to view by Sacramento Index Water Year Types.

    """
    # Obtain annualized values.
    df_mean = stats.PeriodMean(df, eom=eom)
    df_mean.name = 'Mean'
    df_mean = df_mean.reset_index()
    # Ensure only one cycle is present in dataset.
    if len(df_mean['Part A'].unique()) > 1:
        msg = 'This plotting method cannot handle multiple cycle data.'
        raise RuntimeError(msg)
    # Obtain list of studies.
    if 'Study' not in df_mean.columns:
        df_mean['Study'] = ''
    studies = list(df_mean.Study.unique())
    # Split Series by 'Data Type'.
    df_list = list()
    data_types = df_mean['Data Type'].unique()
    for data_type in data_types:
        df_list.append(df_mean.loc[df_mean['Data Type'] == data_type, :])
    # Initialize plot canvas and associated variables.
    fig, ax = plt.subplots(ncols=len(df_list), figsize=(16, 9))
    bar_start = 0.05
    var_width = 0.9
    bar_width = var_width / len(studies)
    # Plot data.
    for i, d in enumerate(df_list):
        # Ensure there is only one unit in dataset.
        units = d['Units'].unique()
        if len(units) > 1:
            msg = 'This plotting method cannot handle multiple units.'
            raise RuntimeError(msg)
        # Initialize variables for plotting data.
        ax_current = ax if len(df_list) == 1 else ax[i]
        # Iterate through each study and plot variables.
        for j, study in enumerate(studies):
            d_temp = d.sort_values('Part B').loc[d.Study == study, :]
            d_temp.reset_index(drop=True, inplace=True)
            val = d_temp['Mean'].values
            idx = d_temp.index.values + 0.05 + j * bar_width
            ax_current.bar(idx, val, bar_width, label=study, align='edge')
        # Set plot title.
        context = '/'.join(d['Part C'].unique()).title()
        chart_title = 'Annual Average Plot of {}'.format(context)
        ax_current.set_title(chart_title)
        # Modify x-axis and y-axis.
        x_lbl = d.sort_values('Part B').loc[d.Study == studies[0], 'Part B']
        x_idx = np.arange(x_lbl.index.size)
        ax_current.set_xticks(x_idx + 0.5)
        tick_labels = list(x_lbl.values)
        ax_current.set_xticklabels(tick_labels)
        x_min = min(x_idx)
        x_max = max(x_idx) + 1
        ax_current.set_xlim(left=x_min, right=x_max)
        y_border = 0.05 * (d.Mean.max() - d.Mean.min())
        y_lbl = ''.join(d['Units'].unique())
        ax_current.set_ylabel('{} ({})'.format(context, y_lbl))
        ax_current.set_xlabel('Part B')
        ax_current.spines['right'].set_visible(False)
        ax_current.spines['top'].set_visible(False)
        # Set legend.
        ax_current.legend(title='Study')
    # Adjust figure layout.
    plt.tight_layout()
    # Add figure notes.
    notes = PlotChartNotes()
    plt.figtext(0.05, 0, notes, ha='left', va='bottom', wrap=True)
    plt.subplots_adjust(bottom=0.2)
    # Show plot, if requested.
    if show_plot:
        plt.show()
    # Return figure and axes.
    return fig, ax


def PlotEX(df, eom=None, show_plot=True):
    """
    Summary
    -------
    Plot of monthly exceedence probability.

    Future Development
    ------------------
    1. Provide option for Annual Exceedence.
    2. Provide option for end of specified month for storage variables.
    3. Add option to view by Sacramento Index Water Year Types.

    """
    # Ensure 'Study' is in header.
    # TODO: Add code.
    # Obtain exceedence probabilities.
    if eom:
        df_excd = stats.AnnualExceedence(df, eom=eom)
    else:
        df_excd = stats.MonthlyExceedence(df)
    # Get list of variables.
    var_list = set(df_excd.columns.get_level_values('Part B'))
    # Determine number of axes in the figure.
    n_var = len(var_list)
    n_row = np.int(np.around(np.sqrt(n_var)))
    if n_row**2 >= n_var:
        n_col = n_row
    else:
        n_col = n_row + 1
    fig, ax = plt.subplots(nrows=n_row, ncols=n_col, figsize=(16, 9))
    # Remove extra axes, if necessary.
    if n_row * n_col != n_var:
        n_empty = n_row * n_col - n_var
        for k in range(n_empty):
            ax[-1, -(1+k)].remove()
    # Initialize variables for updating axes.
    cur_row = 0
    cur_col = 0
    # Plot each variable.
    for var in var_list:
        df_exc = df_excd.xs(var, level='Part B', axis=1)
        # Initialize parameters for current axis.
        y_min = np.min(df_exc.values)
        y_max = np.max(df_exc.values)
        col_var = df_exc.columns
        # Select current axis.
        if n_row == 1 and n_col == 1:
            ax_cur = ax
        elif n_row == 1:
            ax_cur = ax[cur_col]
        else:
            ax_cur = ax[cur_row, cur_col]
        # Plot study results for each variable.
        for c in col_var:
            sr_plot = df_exc[c]
            label_c = '{} {}'.format(*c[:2])
            ax_cur.plot(sr_plot, label=label_c, alpha=0.7)
        # Set plot title.
        if eom:
            month_name = dt.date(1900, eom, 1).strftime('%B')
            temp_title = 'Exceedence Plot of {} (End of {})'
            ax_cur.set_title(temp_title.format(var, month_name))
        else:
            ax_cur.set_title('Exceedence Plot of {} (All Months)'.format(var))
        # Modify x-axis and y-axis.
        label_c = set(df_exc.columns.get_level_values('Part C'))
        label_u = set(df_exc.columns.get_level_values('Data Type'))
        ax_cur.set_ylabel('{} ({})'.format(r'/'.join(label_c),
                                           r'/'.join(label_u)))
        ax_cur.set_ylim(bottom=y_min, top=y_max)
        ax_cur.set_xlabel('Exceedance Probability')
        ax_cur.spines['right'].set_visible(False)
        ax_cur.spines['top'].set_visible(False)
        # Set legend.
        ax_cur.legend(title='Study, Part F')
        # Update current axis.
        cur_col += 1
        if cur_col >= n_col:
            cur_col = 0
            cur_row += 1
    # Adjust layout.
    plt.tight_layout()
    # Add figure notes.
    t = PlotChartNotes()
    if n_row * n_col != n_var:
        x_pos = (1 - n_empty / n_col) + 0.025
        y_pos = (1 / n_row) - 0.025
        plt.figtext(x_pos, y_pos, t, ha='left', va='top', wrap=True)
    else:
        plt.figtext(0.05, 0, t, ha='left', va='bottom', wrap=True)
        plt.subplots_adjust(bottom=0.2)
    # Show plot, if requested.
    if show_plot:
        plt.show()
    # Return figure and axes.
    return fig, ax


def PlotMA(df, show_plot=True):
    """
    Summary
    -------
    Plot of monthly averages.

    No documentation as of 2018-11-01.

    Future Development
    ------------------
    1. Add option to view by Sacramento Index Water Year Types.

    """
    # Ensure 'Study' is in header.
    # TODO: Add code.
    # Obtain monthly means.
    df_ave = stats.MonthlyMean(df)
    # Get list of variables.
    var_list = set(df_ave.columns.get_level_values('Part B'))
    # Determine number of axes in the figure.
    n_var = len(var_list)
    n_row = np.int(np.around(np.sqrt(n_var)))
    if n_row**2 >= n_var:
        n_col = n_row
    else:
        n_col = n_row + 1
    fig, ax = plt.subplots(nrows=n_row, ncols=n_col, figsize=(16, 9))
    # Remove extra axes, if necessary.
    if n_row * n_col != n_var:
        n_empty = n_row * n_col - n_var
        for k in range(n_empty):
            ax[-1, -(1+k)].remove()
    # Initialize variables for updating axes.
    cur_row = 0
    cur_col = 0
    var_width = 0.9
    idx = np.arange(12)
    x_min = 0
    x_max = 12
    # Plot each variable.
    for var in var_list:
        df_var = df_ave.xs(var, level='Part B', axis=1)
        # Initialize parameters for current axis.
        y_min = np.min(df_var.values) * 0.95
        y_max = np.max(df_var.values) * 1.05
        col_var = df_var.columns
        bar_width = var_width / len(col_var)
        # Select current axis.
        if n_row == 1 and n_col == 1:
            ax_cur = ax
        elif n_row == 1:
            ax_cur = ax[cur_col]
        else:
            ax_cur = ax[cur_row, cur_col]
        # Plot study results for each variable.
        for c in col_var:
            idx_c = idx + 0.05 + col_var.get_loc(c) * bar_width
            val_c = df_var[c].values
            lab_c = '{} {}'.format(*c[:2])
            ax_cur.bar(idx_c, val_c, bar_width, label=lab_c, align='edge')
        # Set plot title.
        ax_cur.set_title('Monthly Averages of {}'.format(var))
        # Modify x-axis and y-axis.
        ax_cur.set_xticks(idx + 0.5)
        tick_labels = list(df_ave.index)
        ax_cur.set_xticklabels(tick_labels)
        label_c = set(df_var.columns.get_level_values('Part C'))
        label_u = set(df_var.columns.get_level_values('Data Type'))
        ax_cur.set_ylabel('{} ({})'.format(r'/'.join(label_c),
                                           r'/'.join(label_u)))
        ax_cur.set_ylim(bottom=y_min, top=y_max)
        ax_cur.set_xlim(left=x_min, right=x_max)
        ax_cur.set_xlabel('Month')
        ax_cur.spines['right'].set_visible(False)
        ax_cur.spines['top'].set_visible(False)
        # Set legend.
        ax_cur.legend(title='Study, Part A')
        # Update current axis.
        cur_col += 1
        if cur_col >= n_col:
            cur_col = 0
            cur_row += 1
    # Adjust layout.
    plt.tight_layout()
    # Add figure notes.
    t = PlotChartNotes()
    if n_row * n_col != n_var:
        x_pos = (1 - n_empty / n_col) * 1.05
        y_pos = (1 / n_row) * 0.95
        plt.figtext(x_pos, y_pos, t, ha='left', va='top', wrap=True)
    else:
        plt.figtext(0.05, 0, t, ha='left', va='bottom', wrap=True)
        plt.subplots_adjust(bottom=0.2)
    # Show plot, if requested.
    if show_plot:
        plt.show()
    # Return figure and axes.
    return fig, ax


def PlotSP(df, show_plot=True):
    """
    Summary
    -------
    Scatter plot.

    X-Data : single time series, baseline.
    Y-Data : multiple time series, alternatives.

    Only compares overlapping time frame.

    No documentation as of 2018-11-01.

    Future Development
    ------------------
    1. Add option to view by Sacramento Index Water Year Types.

    """
    # Ensure 'Study' is in header.
    # TODO: Add code.
    # Get list of variables.
    var_list = set(df.columns.get_level_values('Part B'))
    # Determine number of axes in the figure.
    n_var = len(var_list)
    n_row = np.int(np.around(np.sqrt(n_var)))
    if n_row**2 >= n_var:
        n_col = n_row
    else:
        n_col = n_row + 1
    fig, ax = plt.subplots(nrows=n_row, ncols=n_col, figsize=(16, 9))
    # Remove extra axes, if necessary.
    if n_row * n_col != n_var:
        n_empty = n_row * n_col - n_var
        for k in range(n_empty):
            ax[-1, -(1+k)].remove()
    # Initialize variables for updating axes.
    cur_row = 0
    cur_col = 0
    # Plot each variable.
    for var in var_list:
        df_var = df.xs(var, level='Part B', axis=1)
        # Initialize parameters for current axis.
        col_var = df_var.columns
        base = df_var[col_var[0]].values
        # Select current axis.
        if n_row == 1 and n_col == 1:
            ax_cur = ax
        elif n_row == 1:
            ax_cur = ax[cur_col]
        else:
            ax_cur = ax[cur_row, cur_col]
        # Plot study results against each study.
        for c in col_var[1:]:
            label_c = '{} {}'.format(*c[:2])
            vals = df_var[c].values
            score = r2_score(base, vals)
            ax_cur.scatter(base, vals,
                           label='{} (R^2: {:.2f})'.format(label_c, score),
                           alpha=0.7)
        # Set plot title.
        ax_cur.set_title('Scatter Plot of {}'.format(var))
        # Modify x-axis and y-axis.
        label_c = set(df_var.columns.get_level_values('Part C'))
        label_u = set(df_var.columns.get_level_values('Data Type'))
        ax_cur.set_ylabel('{} ({})'.format(r'/'.join(label_c),
                                           r'/'.join(label_u)))
        ax_cur.set_xlabel(var)
        ax_cur.spines['right'].set_visible(False)
        ax_cur.spines['top'].set_visible(False)
        # Set legend.
        ax_cur.legend(title='Study, Part A')
        # Update current axis.
        cur_col += 1
        if cur_col >= n_col:
            cur_col = 0
            cur_row += 1
    # Adjust layout.
    plt.tight_layout()
    # Add figure notes.
    t = PlotChartNotes()
    if n_row * n_col != n_var:
        x_pos = (1 - n_empty / n_col) + 0.025
        y_pos = (1 / n_row) - 0.025
        plt.figtext(x_pos, y_pos, t, ha='left', va='top', wrap=True)
    else:
        plt.figtext(0.05, 0, t, ha='left', va='bottom', wrap=True)
        plt.subplots_adjust(bottom=0.2)
    # Show plot, if requested.
    if show_plot:
        plt.show()
    # Return figure and axes.
    return fig, ax


def PlotTS(df, show_plot=True):
    """
    Summary
    -------
    Plot of CalSim time series.

    No documentation as of 2018-11-01.

    Future Development
    ------------------
    1. Add option to view by Sacramento Index Water Year Types.

    """
    # Register matplotlib converters, per documentation.
    register_matplotlib_converters()
    # Ensure 'Study' is in header.
    # TODO: Add code.
    # Get list of variables.
    var_list = set(df.columns.get_level_values('Part B'))
    # Determine number of axes in the figure.
    n_var = len(var_list)
    n_row = np.int(np.around(np.sqrt(n_var)))
    if n_row**2 >= n_var:
        n_col = n_row
    else:
        n_col = n_row + 1
    fig, ax = plt.subplots(nrows=n_row, ncols=n_col, figsize=(16, 9))
    # Remove extra axes, if necessary.
    if n_row * n_col != n_var:
        n_empty = n_row * n_col - n_var
        for k in range(n_empty):
            ax[-1, -(1+k)].remove()
    # Initialize variables for updating axes.
    cur_row = 0
    cur_col = 0
    # Plot each variable.
    for var in var_list:
        df_var = df.xs(var, level='Part B', axis=1)
        # Initialize parameters for current axis.
        y_min = np.min(df_var.values)
        y_max = np.max(df_var.values)
        col_var = df_var.columns
        # Select current axis.
        if n_row == 1 and n_col == 1:
            ax_cur = ax
        elif n_row == 1:
            ax_cur = ax[cur_col]
        else:
            ax_cur = ax[cur_row, cur_col]
        # Plot study results for each variable.
        for c in col_var:
            label_c = '{} {}'.format(*c[:2])
            ax_cur.plot(df_var[c], label=label_c, alpha=0.7)
        # Set plot title.
        ax_cur.set_title('Time Series Plot of {}'.format(var))
        # Modify x-axis and y-axis.
        label_c = set(df_var.columns.get_level_values('Part C'))
        label_u = set(df_var.columns.get_level_values('Data Type'))
        ax_cur.set_ylabel('{} ({})'.format(r'/'.join(label_c),
                                           r'/'.join(label_u)))
        ax_cur.set_ylim(bottom=y_min, top=y_max)
        ax_cur.set_xlabel('CalSim Period of Record (Monthly)')
        ax_cur.spines['right'].set_visible(False)
        ax_cur.spines['top'].set_visible(False)
        # Set legend.
        ax_cur.legend(title='Study, Part A')
        # Update current axis.
        cur_col += 1
        if cur_col >= n_col:
            cur_col = 0
            cur_row += 1
    # Adjust layout.
    plt.tight_layout()
    # Add figure notes.
    t = PlotChartNotes()
    if n_row * n_col != n_var:
        x_pos = (1 - n_empty / n_col) + 0.025
        y_pos = (1 / n_row) - 0.025
        plt.figtext(x_pos, y_pos, t, ha='left', va='top', wrap=True)
    else:
        plt.figtext(0.05, 0, t, ha='left', va='bottom', wrap=True)
        plt.subplots_adjust(bottom=0.2)
    # Show plot, if requested.
    if show_plot:
        plt.show()
    # Return figure and axes.
    return fig, ax


if False:
    def __future_PlotMC__(DF):
        r"""
        Summary
        -------
        Plot of monthly counts. Intended for use on binary time series.

        Warning: Only use this function for binary Derived Time Series.

        Future Development
        ------------------
        1. Add option to view by Sacramento Index Water Year Types.

        """
        # TODOC: Provide docstring.
        # <JAS 2018-11-02>
        # Get list of Part B to verify DataFrame meets procedure specifications.
        df_bi = DF.xs('NONE BINARY', level='DataType', axis=1, drop_level=False)
        var_list = set(df_bi.columns.get_level_values('Part B'))
        # Compute monthly averages over DataFrame.
        df_ave = df_bi.groupby(DF.index.month).sum()
        # Determine number of axes in the figure.
        n_var = len(var_list)
        n_row = np.int(np.around(np.sqrt(n_var)))
        if n_row**2 >= n_var:
            n_col = n_row
        else:
            n_col = n_row + 1
        fig, ax = plt.subplots(nrows=n_row, ncols=n_col, figsize=(16, 9))
        # Remove extra axes, if necessary.
        if n_row * n_col != n_var:
            n_empty = n_row * n_col - n_var
            for k in range(n_empty):
                ax[-1, -(1+k)].remove()
        # Initialize variables for updating axes.
        cur_row = 0
        cur_col = 0
        var_width = 0.9
        idx = np.arange(12)
        x_min = 0
        x_max = 12
        # Plot each variable.
        for var in var_list:
            df_var = df_ave.xs(var, level='Part B', axis=1)
            # Initialize parameters for current axis.
            y_min = np.min(df_var.values) * 0.95
            y_max = np.max(df_var.values) * 1.05
            col_var = df_var.columns
            bar_width = var_width / len(col_var)
            # Select current axis.
            if n_row == 1 and n_col == 1:
                ax_cur = ax
            elif n_row == 1:
                ax_cur = ax[cur_col]
            else:
                ax_cur = ax[cur_row, cur_col]
            # Plot study results for each variable.
            for c in col_var:
                idx_c = idx + 0.05 + col_var.get_loc(c) * bar_width
                val_c = df_var[c].values
                lab_c = '{} {}'.format(*c[:2])
                ax_cur.bar(idx_c, val_c, bar_width, label=lab_c, align='edge')
            # Set plot title.
            ax_cur.set_title('Monthly Count of {}'.format(var))
            # Modify x-axis and y-axis.
            ax_cur.set_xticks(idx + 0.5)
            tick_labels = ('JAN', 'FEB', 'MAR', 'APR', 'MAY', 'JUN',
                           'JUL', 'AUG', 'SEP', 'OCT', 'NOV', 'DEC')
            ax_cur.set_xticklabels(tick_labels)
            ax_cur.set_ylabel('Number of Occurrences')
            ax_cur.set_ylim(bottom=y_min, top=y_max)
            ax_cur.set_xlim(left=x_min, right=x_max)
            ax_cur.set_xlabel('Month')
            ax_cur.spines['right'].set_visible(False)
            ax_cur.spines['top'].set_visible(False)
            # Set legend.
            ax_cur.legend(title='Study, Part F')
            # Update current axis.
            cur_col += 1
            if cur_col >= n_col:
                cur_col = 0
                cur_row += 1
        # Adjust layout.
        plt.tight_layout()
        # Add figure notes.
        t = PlotChartNotes()
        if n_row * n_col != n_var:
            x_pos = (1 - n_empty / n_col) * 1.05
            y_pos = (1 / n_row) * 0.95
            plt.figtext(x_pos, y_pos, t, ha='left', va='top', wrap=True)
        else:
            plt.figtext(0.05, 0, t, ha='left', va='bottom', wrap=True)
            plt.subplots_adjust(bottom=0.2)
        # Return figure and axes.
        return fig, ax


    def __future__PlotPD(DF):
        r"""
        Summary
        -------
        Plot probability density distribution.

        No documentation as of 2018-11-01.

        Future Development
        ------------------
        1. Add option to view by Sacramento Index Water Year Types.

        """
        # TODOC: Provide docstring.
        # <JAS 2018-11-01>
        # Get list of Part B to verify DataFrame meets procedure specifications.
        var_list = set(DF.columns.get_level_values('Part B'))
        # Determine number of axes in the figure.
        n_var = len(var_list)
        n_row = np.int(np.around(np.sqrt(n_var)))
        if n_row**2 >= n_var:
            n_col = n_row
        else:
            n_col = n_row + 1
        fig, ax = plt.subplots(nrows=n_row, ncols=n_col, figsize=(16, 9))
        # Remove extra axes, if necessary.
        if n_row * n_col != n_var:
            n_empty = n_row * n_col - n_var
            for k in range(n_empty):
                ax[-1, -(1+k)].remove()
        # Initialize variables for updating axes.
        cur_row = 0
        cur_col = 0
        # Plot each variable.
        for var in var_list:
            df_var = DF.xs(var, level='Part B', axis=1)
            # Initialize parameters for current axis.
            x_min = np.min(df_var.values)
            x_max = np.max(df_var.values)
            y_min = 0
            y_max = 0
            col_var = df_var.columns
            # Select current axis.
            if n_row == 1 and n_col == 1:
                ax_cur = ax
            elif n_row == 1:
                ax_cur = ax[cur_col]
            else:
                ax_cur = ax[cur_row, cur_col]
            # Plot study results for each variable.
            for c in col_var:
                vals_c = df_var[c].dropna().values
                label_c = '{} {}'.format(*c[:2])
                n, _, _ = ax_cur.hist(vals_c, range=(x_min, x_max), bins=25,
                                      normed=False, label=label_c, alpha=0.7)
                n_max = np.max(n)
                y_max = np.max([y_max, n_max])
            # Set plot title.
            ax_cur.set_title('Histogram of {}'.format(var))
            # Modify x-axis and y-axis.
            label_c = set(df_var.columns.get_level_values('Part C'))
            label_u = set(df_var.columns.get_level_values('DataType'))
            ax_cur.set_xlabel('{} ({})'.format(r'/'.join(label_c),
                                               r'/'.join(label_u)))
            ax_cur.set_xlim(left=x_min, right=x_max)
            ax_cur.set_ylim(bottom=y_min, top=y_max)
            ax_cur.set_ylabel('Bin Count')
            ax_cur.spines['right'].set_visible(False)
            ax_cur.spines['top'].set_visible(False)
            # Set legend.
            ax_cur.legend(title='Study, Part F')
            # Update current axis.
            cur_col += 1
            if cur_col >= n_col:
                cur_col = 0
                cur_row += 1
        # Adjust layout.
        plt.tight_layout()
        # Add figure notes.
        t = PlotChartNotes()
        if n_row * n_col != n_var:
            x_pos = (1 - n_empty / n_col) * 1.05
            y_pos = (1 / n_row) * 0.95
            plt.figtext(x_pos, y_pos, t, ha='left', va='top', wrap=True)
        else:
            plt.figtext(0.05, 0, t, ha='left', va='bottom', wrap=True)
            plt.subplots_adjust(bottom=0.2)
        # Return figure and axes.
        return fig, ax


# %% Execute code.
if __name__ == '__main__':
    msg = ('This module is intended to be imported for use into another'
           ' module. It is not intended to be run as a __main__ file.')
    print(msg)
