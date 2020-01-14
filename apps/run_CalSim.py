"""
Summary
-------
This application allows a user to run a CalSim study in Python.

Example
-------
Execute the following code to run a CalSim3 study.

>>> from calsim_toolkit.apps import run_CalSim
>>> lf = 'CalSim3/Existing.launch'
>>> run_CalSim.run_CalSim(lf)

"""
# %% Import libraries.
# Import standard libraries.
import os
import glob
import json
import subprocess as sb


# %% Define functions.
def clean_WRIMS_dir(WRIMS):
    """
    Summary
    -------
    Function to clean the pathname for WRIMS in a readable manner for Python.

    """
    cleaned_WRIMS = WRIMS
    if WRIMS.startswith("'") or WRIMS.startswith('"'):
        cleaned_WRIMS = cleaned_WRIMS[1:]
    if WRIMS.endswith("'") or WRIMS.endswith('"'):
        cleaned_WRIMS = cleaned_WRIMS[:-1]
    cleaned_WRIMS = os.path.realpath(cleaned_WRIMS)
    return cleaned_WRIMS


def WRIMS_config():
    """
    Summary
    -------
    Function to configure Python's connection to WRIMS.

    Returns
    -------
    WRIMS : path
        Configured directory path of WRIMS application.
    launch_group_file : path
        File path of grouped launch files as input into WRIMS *.bat
        applications.
    settings_file : path
        File path to settings for WRIMS application.

    """
    # Obtain WRIMS application directory.
    this_dir = os.path.dirname(os.path.abspath(__file__))
    config = os.path.join(this_dir, 'wrims.json')
    if os.path.exists(config):
        with open(config, 'r') as f:
            data = json.load(f)
        WRIMS = data['WRIMS']
        if not os.path.exists(WRIMS):
            err_msg = ('"wrims.json" must contain a valid existing directory.'
                       ' Please, provide a valid directory containing the'
                       ' WRIMS application. The directory will be saved for'
                       ' future use:')
            print(err_msg)
            raw_WRIMS = input()
            if not raw_WRIMS: raise (RuntimeError)
            WRIMS = clean_WRIMS_dir(raw_WRIMS)
            data['WRIMS'] = WRIMS
            with open(config, 'w') as f:
                json.dump(data, f)
    else:
        msg = ('Please, provide a valid directory containing the WRIMS'
               ' application. The directory will be saved for future use:')
        print(msg)
        raw_WRIMS = input()
        if not raw_WRIMS: raise (RuntimeError)
        WRIMS = clean_WRIMS_dir(raw_WRIMS)
        data = {'WRIMS': WRIMS}
        with open(config, 'w') as f:
            json.dump(data, f)
    # Obtain launch group file.
    launch_group_file = os.path.join(WRIMS, r'batchrun/LaunchFileGroup.lfg')
    launch_group_file = os.path.realpath(launch_group_file)
    # Obtain settings file.
    settings_file = os.path.join(WRIMS, r'data/setting.prf')
    settings_file = os.path.realpath(settings_file)
    # Return paths.
    return WRIMS, launch_group_file, settings_file


def WRIMS_settings(settings_file, solver='CBC', memory=4096, cycles=False,
                   cycle_list=[]):
    """
    Summary
    -------
    A function to write settings for WRIMS.

    Parameters
    ----------
    settings_file : path
        File path to settings for WRIMS application; an return of
        `WRIMS_config`.
    solver : string, default 'CBC', optional
        CalSim Solver; choose either 'xa' or 'cbc'. This variable is not case
        sensitive.
    memory : integer, default 4096, optional
        Memory allocated for WRIMS to utilize, in Megabytes (MB); provide a
        multiple of 64 for efficient use of 64-bit computer resources.
    cycles : boolean, default False, optional
        Option to write CalSim cycle solutions to output *.dss file.
    cycle_list : list of integers, default [], optional,
        List of specific CalSim cycle solutions to write to output *.dss file.
        If list is empty and `cycles` = True, then all cycle solutions are
        written to output *.dss file.

    Returns
    -------
    _ : int
        The value of 0 is returned to indicate success.

    """
    # Initialize variables.
    solver_options = ['XA', 'CBC']
    options_list = list()
    # Add solver to options.
    if solver.upper() not in solver_options:
        msg = 'Invalid solver specified.'
        raise RuntimeError(msg)
    options_list.append(solver.upper())
    # Add memory allocation to options.
    if not isinstance(memory, int):
        msg = 'Allocated memory must be an integer value in MB.'
        raise RuntimeError(msg)
    if memory > 8192:
        msg = 'Allocated memory exceeds built-in cap of 8 GB.'
        raise RuntimeError(msg)
    options_list.append(str(memory))
    # Set cycle solution options.
    if cycles:
        options_list.append('true')
        if cycle_list:
            options_list.append('false')
            if not all(isinstance(n, int) for n in cycle_list):
                msg = '`cycle_list` provided must be list of integers.'
                raise RuntimeError(msg)
            cycle_num = ', '.join([str(x) for x in cycle_list])
            options_list.append("'{}'".format(cycle_num))
        else:
            options_list.append('true')
            options_list.append("''")
    else:
        options_list.append('false')
        options_list.append('true')
        options_list.append("''")
    # Write settings to file.
    options = '\n'.join(options_list)
    with open(settings_file, 'w') as f:
        f.write(options)
    # Return success indicator.
    return 0


def run_CalSim(lf, run_parallel=False, run_bat=True, **kwargs):
    # TODO: Add options to modify launch file.
    """
    Summary
    -------
    A function to run CalSim studies through WRIMS .bat files.

    Parameters
    ----------
    lf : path or list of paths
        Absolute or relative file path(s) to CalSim *.launch file(s). If a
        study directory is provided, this function will search for all *.launch
        files in the directory, but not in any subdirectories.
    run_parallel : bool, default False, optional
        Option to run multiple CalSim studies in parallel. Default option is to
        run CalSim studies in sequential order.
    run_bat : bool, default True, optional
        Option to not run CalSim studies. This option is intended for debugging
        the function.
    **kwargs : optional
        Keyword arguments to pass to the `WRIMS_settings` function.

    Returns
    -------
    _ : int
        The value of 0 is returned to indicate success. Intermediate messages
        are printed to console to indicate when processes are complete.

    """
    # TODO: Start here to re-write code!
    # <JAS 2019-10-09>
    # Initialize variables.
    solver_opts = ['XA', 'CBC']
    # Get WRIMSv2 configuration paths.
    WRIMS, launch_group_file, settings_file = WRIMS_config()
    # Modify settings.
    WRIMS_settings(settings_file, **kwargs)
    # Prepare list of launch files.
    if isinstance(lf, list):
        launch_files = lf
    elif os.path.isdir(lf):
        launch_files = glob.glob(os.path.join(lf, '*.launch'))
    else:
        launch_files = [lf]
    launch_files = [x for x in launch_files if 'wsi' not in x.lower()]
    for i in range(len(launch_files)):
        launch_files[i] = os.path.realpath(launch_files[i])
        if not os.path.exists(launch_files[i]):
            msg = 'Path {} does not exist'.format(launch_files[i])
            raise RuntimeError(msg)
    # Run CalSim studies in parallel or sequence.
    if run_parallel:
        # Connect to parallel engine.
        CalSim = os.path.join(WRIMS, r'batchrun/ParallelBatchRun.bat')
        CalSim = os.path.realpath(CalSim)
        if os.path.exists(CalSim):
            work_dir = os.path.dirname(CalSim)
        else:
            err_msg = 'File not found: ' + CalSim
            raise ValueError(err_msg)
        # Break list of *.launch files into packets.
        chunk = 5
        data_packet = [launch_files[i:i + chunk]
                       for i in range (0, len(launch_files), chunk)]
        for packet in data_packet:
            # Write *.launch files to *.lfg file.
            with open(launch_group_file, 'w') as file:
                file.write('\n'.join(packet))
            # Run subprocess.
            if run_bat:
                process = sb.run(CalSim, cwd=work_dir)
                if process.returncode != 0:
                    print('CalSim Subprocess Failed.')
                else:
                    print('CalSim Subprocess Complete!')
    else:
        # Connect to sequential engine.
        CalSim = os.path.join(WRIMS, r'batchrun/SequentialBatchRun.bat')
        CalSim = os.path.realpath(CalSim)
        if os.path.exists(CalSim):
            work_dir = os.path.dirname(CalSim)
        else:
            err_msg = 'File not found: ' + CalSim
            raise ValueError(err_msg)
        # Write *.launch files to *.lfg file.
        with open(launch_group_file, 'w') as file:
            file.write('\n'.join(launch_files))
        # Run subprocess.
        if run_bat:
            process = sb.run(CalSim, cwd=work_dir)
            if process.returncode != 0:
                print('CalSim Subprocess Failed.')
            else:
                print('CalSim Subprocess Complete!')
    # Return completion indicator.
    return 0


# %% Execute script.
if __name__ == '__main__':
    msg = ('This module is intended to be imported for use into another'
           ' module. It is not intended to be run as a __main__ file.')
    raise RuntimeError(msg)
