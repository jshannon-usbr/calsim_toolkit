"""
Summary
-------
The purpose of this script is to test the reading and writing functionality of
the `calsim_toolkit` module on HEC5Q data.

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
    fp = r'../../HEC5Q/NAA/AR_HEC5Q_Q5/Model/AR_WQ_Report.dss'
    # fp = r'../../HEC5Q/NAA/AR_HEC5Q_Q5/Model/CALSIMII_HEC5Q.dss'
    fp_out = r'../data/HEC5Q_test_out.dss'
    part_b = 'AMERICAN'.split()
    # part_b = 'GERBER_1920'.split()
    # df = cs.read_dss(fp, b=part_b, end_date='2015-09-30')
    # df = cs.read_dss(fp, b=part_b, c='SWRAD', end_date='2015-09-30')
    df = cs.read_dss(fp, e='1DAY', end_date='2015-09-30')
    df = df.cs.wide()
    df.cs.to_dss(fp_out, a='CalSim3', f='JAS_dev')
    return 0


# %% Execute script.
if __name__ == '__main__':
    main()
