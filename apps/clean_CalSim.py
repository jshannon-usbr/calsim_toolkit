r"""

Summary
-------
The purpose of `clean_cs` is to remove unnecessary files in a CalSim study
prior to committing for version control in Git and packaging as a deliverable.

"""
# %% Import libraries.
# Import standard libraries.
import os
import glob
import shutil


# %% Define functions.
def clean_CalSim(cs_dir):
    r"""

    Summary
    -------
    No documentation as of 2019-02-25.

    Parameters
    ----------
    cs_dir : str
        Directory of the CalSim study.

    """
    # Get absolute path of provided directory.
    cs_abs_dir = os.path.abspath(cs_dir)
    # Identify files associated with WRIMS batch run.
    batch_files = glob.glob(os.path.join(cs_abs_dir, '*.bat'))
    batch_files += glob.glob(os.path.join(cs_abs_dir, '*.config'))
    batch_files += glob.glob(os.path.join(cs_abs_dir, '*.prgss'))
    # Identify files associated with DSS inputs and outputs.
    dss_files = glob.glob(os.path.join(cs_abs_dir, '**/*.dsc'), recursive=True)
    dss_files += glob.glob(os.path.join(cs_abs_dir, '**/*.dsd'),
                           recursive=True)
    dss_files += glob.glob(os.path.join(cs_abs_dir, '**/*.dsk'),
                           recursive=True)
    # Identify *.txt, *.par, and *.log files in CONV/Run.
    txt_files = glob.glob(os.path.join(cs_abs_dir, 'CONV/Run/*.txt'))
    txt_files += glob.glob(os.path.join(cs_abs_dir, 'CONV/Run/*.par'))
    txt_files += glob.glob(os.path.join(cs_abs_dir, 'CONV/Run/*.log'))
    # Remove identified files.
    id_files = batch_files + dss_files + txt_files
    for fp in id_files:
        try:
            os.remove(fp)
        except:
            msg = 'Unable to remove {}.'.format(fp)
            print(msg)
    # Remove subdirectory CONV/Run/=ILP=.
    ILP_dir = os.path.join(cs_abs_dir, 'CONV/Run/=ILP=')
    if os.path.exists(ILP_dir):
        try:
            shutil.rmtree(ILP_dir)
        except:
            msg = 'Unable to remove {}.'.format(ILP_dir)
            print(msg)
    # Remove __pycache__ directory.
    pycache_dir = os.path.join(cs_abs_dir, '__pycache__')
    if os.path.exists(pycache_dir):
        try:
            shutil.rmtree(pycache_dir)
        except:
            msg = 'Unable to remove {}.'.format(pycache_dir)
            print(msg)
    # Print message to console.
    msg = 'Successfully scrubbed unnecessary files from {}.'
    print(msg.format(cs_abs_dir))
    # Return success indicator.
    return 0


# %% Execute script.
if __name__ == '__main__':
    msg = ('This module is intended to be imported for use into another '
           'module. It is not intended to be run as a __main__ file.')
    print(msg)
