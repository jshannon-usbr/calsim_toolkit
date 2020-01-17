"""
Summary
-------
To methodically pull study files to a version controlled study From a
Non-Version Controlled Study (FNVCS), this Python file moves the following file
types from directory to another:
    - *.wresl
    - *.table
    - *.project
    - *.launch

"""
# %% Import libraries.
# Import standard libraries.
import os
import sys
import glob
import shutil
import subprocess as sb
import argparse
# Import custom modules.
try:
    import custom_modules
    from tools.variables import external_apps_config
except(ModuleNotFoundError):
    from ..tools.variables import external_apps_config


# %% Define functions.
def main(NVCS, vcs, verbose=True):
    """
    Summary
    -------
    Main function to pull contents of a non-version controlled study into a
    version controlled study directory.

    Parameters
    ----------
    NVCS : path
        Absolute or relative path to non-version controlled study directory.
    vcs : path
        Absolute or relative path to version controlled study directory.
    verbose : boolean, default True, optional
        Print message to report successful transfer of files.

    Returns
    -------
    _ : int
        The value of 0 is returned to indicate success.

    Notes
    -----
    1. The current function only moves the following files types:
        - *.wresl
        - *.table
        - .project
        - *.launch
        - *.dat
    2. Future development to include moving the following files types:
        - *.dss
        - *.dll
        - *.h5
    3. Future development will consider procedure to prevent accidental
       overwrite of binary and non-version controlled files.

    """
    # Ensure directories passed are valid.
    if not os.path.exists(NVCS) or not os.path.isdir(NVCS):
        msg = '{} is not a valid directory.'
        raise TypeError(msg.format(NVCS))
    git_idx = os.path.join(vcs, '.git')
    if not os.path.exists(git_idx) or not os.path.isdir(vcs):
        msg = '{} is not a valid version controlled directory.'
        raise TypeError(msg.format(vcs))
    # Initialize list of files of interest.
    file_types = ['wresl', 'table', 'launch', 'dat']
    # Obtain list of all files from `NVCS`.
    text_files_NVCS = glob.glob(os.path.join(NVCS, '.project'))
    for file_type in file_types:
        f = '**/*.{}'.format(file_type)
        text_files_NVCS += glob.glob(os.path.join(NVCS, f), recursive=True)
    # Remove all version controlled files from `vcs`.
    git = external_apps_config(app='git')
    git_ls = git + ' ls-tree -r --name-only HEAD'
    stream = sb.run(git_ls.split(), cwd=vcs, encoding='utf-8', stdout=sb.PIPE)
    text_files_vcs = stream.stdout.strip().split('\n')
    text_files_vcs = list(set(text_files_vcs) - set(['.gitignore']))
    for f in text_files_vcs:
        os.remove(os.path.join(vcs, f))
    # Copy file into `vcs` directory.
    for text_file in text_files_NVCS:
        rel_path = os.path.relpath(text_file, start=NVCS)
        abs_path = os.path.join(vcs, rel_path)
        if not os.path.exists(os.path.dirname(abs_path)):
            os.makedirs(os.path.dirname(abs_path))
        shutil.copyfile(text_file, abs_path)
    # Remove empty folders from `vcs`.
    failed_del = list()
    for root, dirs, files in os.walk(vcs, topdown=False):
        for dir in dirs:
            dir_pth = os.path.join(root, dir)
            n_files = len(os.listdir(dir_pth))
            if n_files == 0:
                try:
                    os.rmdir(dir_pth)
                except:
                    failed_del.append(dir_pth)
    # Print message to console.
    if verbose:
        if failed_del:
            print('Failed to delete the following empty directories:')
            for f in failed_del:
                print(f)
        msg = ('Successfully transferred text files from {} to {}.'
               ' Ready for review prior to commit.')
        print(msg.format('NVCS', 'vcs'))
    # Return success indicator.
    return 0


# %% Execute script.
if __name__ == '__main__':
    # Initialize argument parser.
    intro = '''
            Main function to pull contents of a non-version controlled study
            into a version controlled study directory.
            '''
    parser = argparse.ArgumentParser(description=intro)
    # Add positional arguments to parser.
    parser.add_argument('NVCS', metavar='non-version controlled study',
                        type=str, nargs='?',
                        help='''
                             Absolute or relative path to non-version
                             controlled study directory.
                             ''')
    parser.add_argument('vcs', metavar='version controlled study', type=str,
                        nargs='?',
                        help='''
                             Absolute or relative path to version controlled
                             study directory.
                             ''')
    # Add optional arguments.
    parser.add_argument('-s', '--silent', dest='verbose', action='store_false',
                        default=True,
                        help='Suppress report successful transfer of files.')
    # Parse arguments.
    args = parser.parse_args()
    NVCS = args.NVCS.strip('"')
    vcs = args.vcs.strip('"')
    verbose = args.verbose
    # Pass arguments to function.
    _ = main(NVCS, vcs, verbose=verbose)
