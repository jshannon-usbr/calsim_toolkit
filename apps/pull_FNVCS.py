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


# %% Define functions.
def main(model_a, model_b, verbose=True):
    # Initialize list of files of interest.
    file_types = ['wresl', 'table', 'launch']
    # Obtain list of all files from `model_a`.
    text_files_a = glob.glob(os.path.join(model_a, '.project'))
    for file_type in file_types:
        f = '**/*.{}'.format(file_type)
        text_files_a += glob.glob(os.path.join(model_a, f), recursive=True)
    # Copy file into `model_b` directory.
    text_files_b = list()
    for text_file in text_files_a:
        rel_path = os.path.relpath(text_file, start=model_a)
        abs_path = os.path.join(model_b, rel_path)
        if not os.path.exists(os.path.dirname(abs_path)):
            os.makedirs(os.path.dirname(abs_path))
        shutil.copyfile(text_file, abs_path)
    # Print message to console.
    if verbose:
        msg = 'Successfully transferred text files from {} to {}.'
        print(msg.format('A', 'B'))
    # Return success indicator.
    return 0


# %% Execute script.
if __name__ == '__main__':
    model_a = sys.argv[1][1:-1]
    model_b = sys.argv[2][1:-1]
    main(model_a, model_b)
