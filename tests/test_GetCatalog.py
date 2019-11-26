"""
Summary
-------
The purpose of this script is to test the functionality of the
`read_dss_catalog` in the `calsim_toolkit` module.

"""
# %% Import libraries.
# Import standard libraries.
import os
import sys
# Import custom libraries.
cwd = os.getcwd()
this_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(this_dir)
CustDir = os.path.abspath('../..')
os.chdir(cwd)
if CustDir not in sys.path: sys.path.insert(1, CustDir)
import calsim_toolkit as cs


# %% Define functions.
def main():
    fp = r'../data/CS3dv.dss'
    part_b = 's_shsta S_FOLSM C_KSWCK'.split()
    df = cs.read_dss_catalog(fp, b=part_b, match=False)
    print(df)


# %% Execute script.
if __name__ == '__main__':
    main()
