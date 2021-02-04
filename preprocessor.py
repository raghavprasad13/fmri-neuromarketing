#!/usr/bin/env python3
#
# Usage: ./preprocessor.py -d path/to/dataset
#
# Author: Raghav Prasad
# Last modified: 28 December 2020

import argparse
from os import environ
from os.path import join
from glob import glob
from multiprocessing import Pool

from isolate_frames import get_event_frames, VID_SCANS_DIR_NAME

from tqdm import tqdm

try:
    FSLDIR = environ['FSLDIR']
except KeyError:
    print('Error! FSL not installed')
    exit()

ATLAS_PATH = join(FSLDIR, 'data', 'atlases', 'Juelich',
                  'Juelich-maxprob-thr25-2mm.nii.gz')

ap = argparse.ArgumentParser()
ap.add_argument("-d", "--dataset", required=True,
                help="path to dataset directory")
args = vars(ap.parse_args())

if args['dataset'][-1] == '/':
    args['dataset'] = args['dataset'][:len(args['dataset'])-1]

dataset_path = args['dataset']
func_paths = glob(join(dataset_path, 'sub*', 'func'))

if __name__ == '__main__':
    with Pool() as p:
        with tqdm(total=len(func_paths), desc='Scan frames obtained') as pbar:
            for _ in p.imap_unordered(get_event_frames, func_paths):
                pbar.update()

        vid_scans_paths = glob(join(dataset_path, 'sub*', 'func',
                                    VID_SCANS_DIR_NAME, '*'))
