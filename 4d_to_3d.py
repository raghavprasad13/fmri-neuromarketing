#!/usr/bin/env python3
# coding: utf-8
#
# This script splits up each 4D fMRI scan into its
# constituent frames and timestamps it
#
# Author: Raghav Prasad
# Last modified: 26 December 2020

import nibabel as nib
import argparse
from glob import glob
from os.path import join

ap = argparse.ArgumentParser()
ap.add_argument("-d", "--dataset", required=True,
                help="path to dataset directory")
args = vars(ap.parse_args())

if args['dataset'][-1] == '/':
    args['dataset'] = args['dataset'][:len(args['dataset'])-1]

dataset_path = args['dataset']

scan_paths = glob(join(dataset_path, '*', 'func', '*.nii.gz'))


def save_3d_frame(img_frameno_tuple):
    img = img_frameno_tuple[0]
    frame_num = img_frameno_tuple[1]

    nib.save(img, 'frame_' + frame_num + '.nii.gz')


for scan_path in scan_paths[:10]:
    scan = nib.load(scan_path)
    frames = nib.funcs.four_to_three(scan)
    frames = [(frames[frame_num], str(frame_num))
              for frame_num in range(len(frames))]
    map(frames, save_3d_frame)

    print(type(frames[0]))
