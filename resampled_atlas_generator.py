from nilearn.image import resample_to_img
import nibabel as nib

from os import environ
from os.path import join


try:
    FSLDIR = environ['FSLDIR']
except KeyError:
    print('Error! FSL not installed')
    exit()

ATLAS_PATH = join(FSLDIR, 'data', 'atlases', 'Juelich',
                  'Juelich-maxprob-thr25-2mm.nii.gz')
SAMPLE_SUB_SCAN = join('..', 'Data', 'rsm-tvc35_copy', 'sub-PP01', 'func',
                       'sub-PP01_task-TVC_space-MNI152NLin6Sym_bold.nii.gz')

src_img = nib.load(ATLAS_PATH)
target_img = nib.load(SAMPLE_SUB_SCAN)

resampled_atlas = resample_to_img(src_img, target_img, copy=True)

nib.save(resampled_atlas, join('..', 'Data', 'Resampled_Juelich_Atlas.nii.gz'))
