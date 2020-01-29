"""
Summary
-------
The purpose of this module is to create a zip package for a CalSim study.

Notes
-----
1. How to make a file hidden:
   https://stackoverflow.com/questions/43441883/how-can-i-make-a-file-hidden-on-windows

"""
# %% Import libraries.
# Import standard libraries.
import os
import shutil
import glob
import re
import json
import stat
import subprocess as sb
import datetime as dt
import zipfile
import argparse
# Import custom modules.
try:
    import custom_modules
    from variable_dependencies import remove_comments
    from tools.variables import external_apps_config
except(ModuleNotFoundError):
    from .variable_dependencies import remove_comments
    from ..tools.variables import external_apps_config


# %% Define functions.
def win_zip(dist_name):
    wzzip = external_apps_config('wzzip')
    if 'WZZIP.EXE' not in wzzip:
        msg = 'Unable to find external application "WZZIP.exe".'
        raise RuntimeError(msg)
    wz_app = [wzzip]
    wz_flg = '-a -P -r -Jhrs -whs'.split()
    wz_arg = r'{}.zip {}\*.*'.format(dist_name, dist_name).split()
    wz_zip = wz_app + wz_flg + wz_arg
    stream = sb.run(wz_zip, cwd=os.getcwd(), encoding='utf-8', stdout=sb.PIPE)
    shutil.rmtree(dist_name)
    return 0


def python_zip(dist_name):
    zip_fp = '{}.zip'.format(dist_name)
    files = glob.glob(os.path.join(dist_name, '*'))
    files = glob.glob(os.path.join(dist_name, '.*'))
    files += glob.glob(os.path.join(dist_name, '**', '*'), recursive=True)
    files += glob.glob(os.path.join(dist_name, '.git', '**', '*'), recursive=True)
    files = list(set(files))
    with zipfile.ZipFile(zip_fp, 'w') as f:
        for file in files:
            f.write(file)
    shutil.rmtree(dist_name)
    return 0


def obtain_DLLs(study):
    # Search CalSim3 *.wresl files for all *.dll external references.
    paths = os.path.join(study, '**', '*.wresl')
    wresl_files = glob.glob(paths, recursive=True)
    WRESL = ''
    for wresl_file in wresl_files:
        with open(wresl_file) as f:
            content = f.read()
        code = remove_comments(content)
        WRESL += code + '\n'
    DLLs = list(re.findall(r'\b\w+\.dll\b', WRESL))
    DLLs = list(set(DLLs))
    # Add supporting DLL not directly found in WRESL code.
    if 'interfacetogw_x64.dll' in DLLs:
        DLLs += ['CVGroundwater_x64.dll']
    if 'interfacetocamdll_x64.dll' in DLLs:
        DLLs += ['CAMDLL_x64.dll']
    # Acquire relative paths for all *.dll binaries.
    dll_paths = list()
    for DLL in DLLs:
        dll_paths += glob.glob(os.path.join(study, '**', DLL), recursive=True)
    # Return list of DLLs.
    return dll_paths


def obtain_IO(study):
    """
    Notes
    -----
    1. Future development to also add groundwater output files to list.

    """
    # Initialize regex code.
    re_base = r'(?<=_{}\" value=\").+(?=\"/>)'
    re_init = re_base.format('INIT')
    re_svar = re_base.format('SVAR')
    re_dvar = re_base.format('DVAR')
    # Search CalSim3 *.launch files for all I/O binary file references.
    paths = os.path.join(study, '*.launch')
    launch_files = glob.glob(paths)
    launch = ''
    for launch_file in launch_files:
        with open(launch_file) as f:
            content = f.read()
        launch += content + '\n'
    binaries = list(re.findall(re_init, launch))
    binaries += list(re.findall(re_svar, launch))
    binaries += list(re.findall(re_dvar, launch))
    binaries = list(set(binaries))
    # Acquire relative paths for all I/O binary files.
    binary_paths = list()
    for binary in binaries:
        b_file = os.path.basename(binary)
        b_pth = os.path.join(study, '**', b_file)
        binary_paths += glob.glob(b_pth, recursive=True)
    # Return list of DLLs.
    return binary_paths


def main(study_dir, dist_name='', verbose=True, compress=True):
    """
    Summary
    -------
    Function to package a CalSim study for distribution.

    Parameters
    ----------
    study_dir : path
        Absolute or relative path to study directory.
    dist_name : string, default '', optional
        Name of the study *.zip file for distribution. If not provided, a name
        is automatically generated.
    verbose : boolean, default True, optional
        Option to allow messages to print to console.
    compress: boolean, default True, optional
        Option to compress study package.

    Returns
    -------
    _ : int
        The value of 0 is returned to indicate success.

    """
    # Switch working directory.
    CWD = os.getcwd()
    wd, study = os.path.split(os.path.abspath(study_dir))
    os.chdir(wd)
    if not dist_name:
        today = dt.date.today().isoformat()
        dist_name = 'USBR_{}_{}'.format(study, today)
    # Initialize variables, stash changes, and add version control note.
    git = external_apps_config('git')
    # Clone current branch.
    git_clone = (git + f' clone {study} {dist_name}').split()
    if os.path.exists(dist_name):
        msg = f'{dist_name} already exists; overwrite denied.'
        raise RuntimeError(msg)
    stream = sb.run(git_clone, cwd=wd, encoding='utf-8', stdout=sb.PIPE)
    # Hide .gitignore.
    fp = os.path.join(dist_name, '.gitignore')
    if os.path.exists(fp):
        p = os.popen('attrib +h ' + fp)
        p.close()
    else:
        print('No .gitignore file found.')
    # Remove remote.
    git_rm = (git + ' remote rm origin').split()
    stream = sb.run(git_rm, cwd=dist_name, encoding='utf-8', stdout=sb.PIPE)
    # Acquire list of binaries.
    files = obtain_DLLs(study)
    files += glob.glob(os.path.join(study, '**', '*.class'), recursive=True)
    files += obtain_IO(study)
    # Copy binaries to package.
    for file in files:
        d_path = os.path.join(dist_name, os.path.relpath(file, start=study))
        if not os.path.exists(os.path.dirname(d_path)):
            os.makedirs(os.path.dirname(d_path))
        shutil.copyfile(file, d_path)
    # Zip package.
    if compress:
        try:
            _ = win_zip(dist_name)
            msg = 'Successfully compressed {} to {}.zip with WinZip.'
            print(msg.format(study, dist_name))
        except RuntimeError:
            _ = python_zip(dist_name)
            msg = 'Successfully compressed {} to {}.zip with Python.'
            print(msg.format(study, dist_name))
    # Return to original working directory.
    os.chdir(CWD)
    # Return success indicator.
    return 0


# %% Execute script.
if __name__ == '__main__':
    # Initialize argument parser.
    intro = 'Main function to package a CalSim study for distribution.'
    parser = argparse.ArgumentParser(description=intro)
    # Add positional arguments to parser.
    parser.add_argument('study_dir', metavar='study directory', type=str,
                        nargs='?',
                        help='Absolute or relative path to study directory.')
    # Add optional arguments.
    parser.add_argument('-d', '--dist_name', metavar='distribution name',
                        type=str, nargs='?', default='',
                        help='''
                             Name of the study *.zip file for distribution. If
                             not provided, a name is automatically generated.
                             ''')
    parser.add_argument('-s', '--silent', dest='verbose', action='store_false',
                        default=True,
                        help='Option to suppress messages to console.')
    parser.add_argument('-u', '--uncompressed', dest='compress',
                        action='store_false', default=True,
                        help='Option to suppress messages to console.')
    # Parse arguments.
    args = parser.parse_args()
    study_dir = args.study_dir.strip('"')
    dist_name = args.dist_name.strip('"')
    verbose = args.verbose
    compress = args.compress
    # Pass arguments to function.
    _ = main(study_dir, dist_name=dist_name, verbose=verbose,
             compress=compress)
