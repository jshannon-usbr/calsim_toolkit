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
    from clean_CalSim import clean_CalSim
    from variable_dependencies import remove_comments
    from tools.variables import external_apps_config
except(ModuleNotFoundError):
    from .clean_CalSim import clean_CalSim
    from .variable_dependencies import remove_comments
    from ..tools.variables import external_apps_config


# %% Define functions.
def win_zip(dist_name, files):
    wzzip = external_apps_config('wzzip')
    if 'WZZIP.EXE' not in wzzip:
        msg = 'Unable to find external application "WZZIP.exe".'
        raise RuntimeError(msg)
    fp_list = '{}.lst'.format(dist_name)
    content = '\n'.join(files)
    with open(fp_list, 'w') as f:
        f.write(content)
    wz_zip = [wzzip] + '-a -P -r -Jhrs -whs {}.zip @{}'.format(dist_name, fp_list).split()
    stream = sb.run(wz_zip, cwd=os.getcwd(), encoding='utf-8', stdout=sb.PIPE)
    os.remove(fp_list)
    return 0


def python_zip(dist_name, files):
    zip_fp = '{}.zip'.format(dist_name)
    with zipfile.ZipFile(zip_fp, 'w') as f:
        for file in files:
            f.write(file)
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
        _, b_file = os.path.split(binary)
        b_pth = os.path.join(study, '**', b_file)
        binary_paths += glob.glob(b_pth, recursive=True)
    # Return list of DLLs.
    return binary_paths


def main(study_dir, dist_name='', verbose=True):
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
        dist_name = '{}_USBR_{}'.format(today, study)
    # Initialize variables, stash changes, and add version control note.
    git = external_apps_config('git')
    stash = True
    no_stash = 'No local changes to save'
    git_stash = (git + ' stash').split()
    stream = sb.run(git_stash, cwd=study, encoding='utf-8', stdout=sb.PIPE)
    if no_stash in stream.stdout:
        stash = False
    git_branch = (git + ' rev-parse --abbrev-ref HEAD').split()
    stream = sb.run(git_branch, cwd=study, encoding='utf-8', stdout=sb.PIPE)
    branch = stream.stdout.split('\n')[0]
    git_commits = (git + ' rev-list HEAD').split()
    stream = sb.run(git_commits, cwd=study, encoding='utf-8', stdout=sb.PIPE)
    commit = stream.stdout.split('\n')[0]
    fp_vcs = os.path.join(study, 'vcs.dyddm')
    with open(fp_vcs, 'w') as f:
        f.write('{} ({})'.format(branch, commit))
    files = [fp_vcs]
    # List all meta-data files.
    files += glob.glob(os.path.join(study, '.project'))
    files += glob.glob(os.path.join(study, '*.launch'))
    files += glob.glob(os.path.join(study, '.gitignore'))
    files += glob.glob(os.path.join(study, '.git', '**', '*'), recursive=True)
    # List all CalSim text files.
    files += glob.glob(os.path.join(study, '**', '*.wresl'), recursive=True)
    files += glob.glob(os.path.join(study, '**', '*.table'), recursive=True)
    files += glob.glob(os.path.join(study, '**', '*.dat'), recursive=True)
    files += glob.glob(os.path.join(study, '**', '*.in'), recursive=True)
    # List all required DLL files.
    files += obtain_DLLs(study)
    # List any *.class files that may be required.
    files += glob.glob(os.path.join(study, '**', '*.class'), recursive=True)
    # List all I/O files.
    files += obtain_IO(study)
    # Zip package.
    try:
        _ = win_zip(dist_name, files)
    except RuntimeError:
        _ = python_zip(dist_name, files)
    print(f'Successfully compressed {study} to {dist_name}.zip')
    # Remove `fp_vcs`, pop stash, and return to original working directory.
    os.remove(fp_vcs)
    if stash:
        git_stash_pop = (git + ' stash pop').split()
        _ = sb.run(git_stash_pop, cwd=study, encoding='utf-8', stdout=sb.PIPE)
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
    # Parse arguments.
    args = parser.parse_args()
    study_dir = args.study_dir.strip('"')
    dist_name = args.dist_name.strip('"')
    verbose = args.verbose
    # Pass arguments to function.
    _ = main(study_dir, dist_name=dist_name, verbose=verbose)
