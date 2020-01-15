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
import json


# %% Define functions.
def prompt_reference(app):
    # Display prompt.
    prompt = ('A valid reference path was not found for the external'
              ' application "{}". Please, provide an existing path for the'
              ' application (it will be saved for future use):')
    print(prompt.format(app))
    input_path = input().strip(' ').strip('"')
    # Process reference path.
    pth = os.path.realpath(os.path.abspath(input_path))
    pth = '/'.join(pth.split('\\'))
    # Check if prompt input is valid.
    if not input_path:
        msg = 'Reference set to current directory {}. Is this correct? [y/n]:'
        print(msg.format(pth))
        response = input().lower()
        if response != 'y':
            pth = prompt_reference(app)
    if not os.path.exists(pth):
        pth = prompt_reference(app)
    # Return path.
    return pth


def update_app_reference(app_ref, app):
    # Prompt user for valid path reference for `app`.
    pth = prompt_reference(app)
    # Add updated path to dictionary.
    app_ref[app] = pth
    # Return updated dictionary.
    return app_ref


def external_apps_config(app=''):
    """
    Summary
    -------
    Function to provide dictionary of external application references or, if an
    `app` is specified, the saved path to the application.

    Parameters
    ----------
    app : string, default '', optional
        Key for providing external application path reference.

    Returns
    -------
    external_apps : dictionary
        If `app` = '', a dictionary is returned of saved application keys and
        absolute path references as associated values.
    app_path : string
        If a valid key is passed through `app`, the saved absolute path
        reference of the application is returned.

    """
    # Ensure ../data/external_apps.json exists.
    this_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.join(os.path.dirname(this_dir), 'data')
    app_fp = os.path.join(data_dir, 'external_apps.json')
    if not os.path.exists(data_dir):
        os.mkdir(data_dir)
    if not os.path.exists(app_fp):
        with open(app_fp, 'w') as f:
            f.write('{}')
    # Read external application references into a dictionary.
    with open(app_fp, 'r') as f:
        app_ref = json.load(f)
    # Return dictionary if no application key provided.
    if not app:
        return app_ref
    # Check if application is in dictionary keys.
    if app.lower() in app_ref.keys():
        app_path = app_ref[app.lower()]
    else:
        app_ref = update_app_reference(app_ref, app.lower())
        with open(app_fp, 'w') as f:
            json.dump(app_ref, f, separators=(',\n ', ': '))
        app_path = app_ref[app.lower()]
    # Return application reference.
    return app_path


# %% Execute script.
# Set variables.
t_steps = {'1MON': 'M', '1DAY': 'D', '1HOUR': 'H', '6HOUR': '6H'}
t_steps_inv = {v: k for k, v in t_steps.items()}
water_months = ['Oct', 'Nov', 'Dec', 'Jan', 'Feb', 'Mar',
                'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep']
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
