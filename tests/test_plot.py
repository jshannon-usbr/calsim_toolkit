"""
Summary
-------
The goal of `test_plot.py` is to test the a typical CalSim3 plotting work flow.

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
    fp0 = r'../data/CS3dv_copy.dss'
    # fp0 = r'../data/CS3dv.dss'
    fp1 = r'../data/2019-09-12_USBR_DV.dss'
    DVs = [fp0, fp0] * 4
    # part_b = 'S_SHSTA S_FOLSM C_KSWCK C_NTOMA D_SAC196_MTC000'.split()
    part_b = 'S_SHSTA S_FOLSM'.split()
    studies = 'Base Alt1'.split()
    df = cs.read_dss(DVs, b=part_b, end_date='2015-09-30')
    # df = cs.read_dss(DVs, b=part_b, studies=studies, end_date='2015-09-30')
    # df = cs.read_dss(fp0, b=part_b, end_date='2015-09-30')
    df = df.cs.plot('ma')
    return 0


# %% Execute script.
if __name__ == '__main__':
    main()
