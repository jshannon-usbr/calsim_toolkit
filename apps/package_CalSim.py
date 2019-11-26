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
# Import custom modules.
# ????: Should I keep this?
# <JAS 2019-10-24>
try:
    from .clean_CalSim import clean_CalSim
except ModuleNotFoundError:
    from clean_CalSim import clean_CalSim


def change_permissions_recursive(path, mode):
    """
    Summary
    -------
    Function accessed from the following link on 2019-10-23:
    https://www.tutorialspoint.com/How-to-change-the-permission-of-a-directory-using-Python

    """
    for root, dirs, files in os.walk(path, topdown=False):
        for dir in [os.path.join(root,d) for d in dirs]:
            os.chmod(dir, mode)
        for file in [os.path.join(root, f) for f in files]:
            os.chmod(file, mode)
    return 0


# %% Define functions.
def binaries_for_removal(dir):
    # Create list of all CalSim binaries in the study.
    all_binaries = glob.glob(os.path.join(dir, '**/*.dss'), recursive=True)
    all_binaries += glob.glob(os.path.join(dir, '**/*.dll'), recursive=True)
    all_binaries += glob.glob(os.path.join(dir, 'CONV\\DSS\\*.out'))
    # Get list of *.launch file(s).
    launch_files = glob.glob(os.path.join(dir, '*.launch'))
    # Acquire *.dss files associated with *.launch file(s).
    binary_files = list()
    for launch_fp in launch_files:
        with open(launch_fp) as f:
            data = f.read()
        data = data.split('\n')
        for line in data:
            if '.DSS' in line.upper():
                fp_dss = line.split('value="')[1]
                fp_dss = fp_dss[:-3]
                if os.path.relpath(fp_dss):
                    fp_dss = os.path.join(dir, fp_dss)
                if os.path.isfile(fp_dss):
                    CONV = 'CONV'
                    fp_dss = re.sub(CONV, CONV, fp_dss, flags=re.IGNORECASE)
                    binary_files.append(fp_dss)
    # Search CalSim3 *.wresl files for all *.dll external references.
    wresl_files = glob.glob(os.path.join(dir, '**/*.wresl'), recursive=True)
    WRESL = ''
    external_dir = 'CONV\\Run\\External'
    for wresl_fp in wresl_files:
        with open(wresl_fp) as f:
            data = f.read()
        WRESL += data
    DLLs = re.findall(r'(?<=\s)[\w]+(?=\.dll)', WRESL)
    DLLs = list(set(DLLs))
    # Add CVGroundwater_x64.dll, accessed through interfacetogw_x64.dll.
    DLLs += ['CVGroundwater_x64']
    # Acquire relative paths for all *.dll binaries.
    for DLL in DLLs:
        DLL += '.dll'
        DLL = os.path.join(dir, external_dir, DLL)
        if os.path.isfile(DLL):
            binary_files.append(DLL)
    # Return list of binaries for removal.
    removal_list = list(set(all_binaries) - set(binary_files))
    return removal_list


def package_study(study_dir):
    # Normalize input study path.
    study_dir_abs = os.path.abspath(study_dir)
    common_dir = os.path.dirname(study_dir_abs)
    # Copy, rename, and clean the package study directory.
    study_name = '{}_USBR_CalSim3'.format(dt.date.today().isoformat())
    package_dir = os.path.join(common_dir, study_name)
    shutil.copytree(study_dir_abs, package_dir)
    clean_CalSim(package_dir)
    # Identify used binaries and delete unused binaries.
    removal_list = binaries_for_removal(package_dir)
    for file in removal_list:
        os.remove(file)
    msg = 'Successfully removed unnecessary binaries from {}'
    print(msg.format(package_dir))
    # Extract hash and branch from latest clean repository.
    # TODO: Make dynamic for sharing with other people.
    # <JAS 2019-10-23>
    git_path = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                            'git.json')
    with open(git_path, 'r') as f:
        data = json.load(f)
    git = data['GIT']
    git_reset = git + ' checkout -- .'
    stream = sb.run(git_reset.split(), cwd=package_dir, encoding='utf-8',
                    stdout=sb.PIPE)
    git_branch = git + ' branch'
    stream = sb.run(git_branch.split(), cwd=package_dir, encoding='utf-8',
                    stdout=sb.PIPE)
    branches = stream.stdout.split('\n')
    src_branch = ''
    for branch in branches:
        if '*' in branch:
            src_branch += branch.strip().split()[1]
    git_commits = git + ' rev-list HEAD'
    stream = sb.run(git_commits.split(), cwd=package_dir, encoding='utf-8',
                    stdout=sb.PIPE)
    commit = stream.stdout.split('\n')[0]
    # Add hash and branch information to .launch file.
    launch_files = glob.glob(os.path.join(package_dir, '*.launch'))
    for launch_file in launch_files:
        with open(launch_file) as f:
            data = f.read()
        data = data.split('\n')
        for i in range(len(data)):
            if 'DESCRIPTION' in data[i]:
                line = data[i].split('"')
                line[-2] += ' version: {} ({})'.format(src_branch, commit)
                line[-2] = line[-2].strip()
                data[i] = '"'.join(line)
        data = '\n'.join(data)
        with open(launch_file, 'w') as f:
            f.write(data)
    msg = 'Successfully added version control note to {}'
    print(msg.format(package_dir))
    # Remove files and directories unrelated to CalSim.
    git_repo = os.path.join(package_dir, '.git')
    change_permissions_recursive(git_repo, stat.S_IWRITE)
    shutil.rmtree(git_repo)
    os.remove(os.path.join(package_dir, '.gitignore'))
    unrelated_files = list()
    file_types = ['link', 'py', 'md', 'xml', 'pdf', 'xlsx']
    for file_type in file_types:
        glob_path = os.path.join(package_dir, '**\\*.{}'.format(file_type))
        unrelated_files += glob.glob(glob_path, recursive=True)
    for file in unrelated_files:
        os.remove(file)
    msg = 'Successfully removed non-CalSim files from {}'
    print(msg.format(package_dir))
    # Zip package.
    zip_fp = '{}.zip'.format(package_dir)
    shutil.make_archive(package_dir, 'zip', common_dir,
                        os.path.basename(package_dir))
    shutil.rmtree(package_dir)
    msg = 'Successfully packaged CalSim study into {}'
    print(msg.format(zip_fp))
    # Return success indicator.
    return 0


# %% Execute script.
# ????: Should I keep this?
# <JAS 2019-10-24>
if __name__ == '__main__':
    package_study('CalSim3')
