"""
Summary
-------
The purpose of this script is to find all key paths in an HDF5 file.

"""
# %% Import libraries.
# Import standard libraries.
import os
import datetime as dt
import itertools
# Import third party libraries.
import h5py


# %% Define functions.
def Groups_and_Datasets(hf):
    list_groups = list()
    list_datasets = list()
    for k in hf.keys():
        if isinstance(hf[k], h5py.Group):
            list_groups.append(k)
        if isinstance(hf[k], h5py.Dataset):
            list_datasets.append(k)
    return list_groups, list_datasets


def get_Datasets(hf):
    dataset_keys = list()
    groups, datasets = Groups_and_Datasets(hf)
    dataset_keys += datasets
    while groups:
        sub_groups = list()
        datasets = list()
        for group in groups:
            some_sub_groups, some_datasets = Groups_and_Datasets(hf[group])
            data_keys = list(itertools.product([group], some_datasets))
            dataset_keys += ['/'.join(key) for key in data_keys]
            group_keys = list(itertools.product([group], some_sub_groups))
            sub_groups += ['/'.join(key) for key in group_keys]
        groups = sub_groups
    return dataset_keys
    
    
def compress_hdf5(fp, fp_out=''):
    if not fp_out:
        path_componants = os.path.split(fp)
        dir_out = path_componants[0]
        file_componants = os.path.splitext(path_componants[1])
        fname_out = file_componants[0] + '_compressed2'
        ext_out = file_componants[1]
        fp_out = os.path.realpath(os.path.join(dir_out, fname_out + ext_out))
    f1 = h5py.File(fp, 'r')
    f2 = h5py.File(fp_out, 'w')
    data_keys = get_Datasets(f1)
    for k in data_keys:
        print('{}: Transfering {}...'.format(dt.datetime.now(), k))
        # f2.create_dataset(k, data=f1[k], chunks=True)
        f2.create_dataset(k, data=f1[k], compression="gzip")
        print('{}: Transfer of {} complete.'.format(dt.datetime.now(), k))
    f1.close()
    f2.close()
    return 0


def read_hdf5(fp):
    with h5py.File(fp, 'r') as f:
        print(*get_Datasets(f), sep='\n')
        print(f['CALSIM/L2015A/IO Data/Info/IO Variable Lookup'][:])
        print(f['CALSIM/L2015A/IO Data/Data/Monthly/Timestep List'][:])
        print(f['CALSIM/L2015A/IO Data/Data/Monthly/Timestep Table'][:])
    return 0


# %% Execute script.
if __name__ == '__main__':
    fp = '../../CalSim3/CONV/DSS/2019-10-31_USBR_DV.h5'
    data = read_hdf5(fp)
    # compress_hdf5(fp)
