"""
Summary
-------
This Python module initialization file imports functions from
"calsim_toolkit.py" for use in the `calsim_toolkit` library.

Example
-------
No example as of 2019-09-12.

>>> import calsim_toolkit as cs

Notes
-----
1. No notes as of 2019-09-12.

"""
# %% Import libraries.
# Import custom libraries.
from .calsim_toolkit import *


# %% Execute script.
if __name__ == '__main__':
    msg = ('This module is intended to be imported for use into another '
           'module. It is not intended to be run as a __main__ file.')
    print(msg)
