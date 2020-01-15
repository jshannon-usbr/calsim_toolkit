"""
Summary
-------
The module allows for references to custom modules in `calsim_toolkit`.

"""
# %% Import libraries
# Import standard libraries.
import os
import sys


# %% Execute script.
this_dir = os.path.dirname(os.path.abspath(__file__))
dir_cs = os.path.realpath(os.path.dirname(this_dir))
sys.path.insert(1, dir_cs)
