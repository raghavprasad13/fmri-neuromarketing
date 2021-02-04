#!/usr/bin/env python3
# Parcellates 4D fMRI image into ROIs using an atlas
#
# Author: Raghav Prasad
# Last modified: 28 December 2020

import numpy as np
import nibabel as nib
import warnings

warnings.filterwarnings('ignore')


def time_series_to_matrix(subject_time_series_path, atlas_path):
    '''
    Makes correlation matrix from atlas
    '''
    subject_time_series = nib.load(subject_time_series_path).get_fdata()
    atlas = nib.load(atlas_path).get_fdata().astype(int)

    g = np.zeros((np.max(atlas), subject_time_series.shape[-1]))
    for i in range(np.max(atlas)):
        g[i, :] = np.nanmean(subject_time_series[atlas == i+1], axis=0)

    np.nan_to_num(g, copy=False)

    h = np.mean(g, axis=1)
    return {'pre_adj': g, 'avg_node_vals': h}
