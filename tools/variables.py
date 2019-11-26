"""
Summary
-------
The purpose of this module is to provide variables needed for the
`calsim_toolkit` library.

"""
# %% Import libraries.
# Import standard libraries.
import os
import sys


# %% Set variables.
t_steps = {'1MON': 'M', '1DAY': 'D', '1HOUR': 'H', '6HOUR': '6H'}
t_steps_inv = {v: k for k, v in t_steps.items()}
water_months = ['Oct', 'Nov', 'Dec', 'Jan', 'Feb', 'Mar',
                'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep']


# %% Execute script.
# Modify path reference.
cwd = os.getcwd()
this_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(this_dir)
CustDir = os.path.abspath(r'..\..\usbr_py3dss')
os.chdir(cwd)
if CustDir not in sys.path: sys.path.insert(1, CustDir)
# Notify user if __name__ == '__main__'.
if __name__ == '__main__':
    msg = ('This module is intended to be imported for use into another'
           ' module. It is not intended to be run as a __main__ file.')
    raise RuntimeError(msg)
