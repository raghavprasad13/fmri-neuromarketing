#!/usr/bin/env python3
# Identifies and saves 3D frames from 4D fMRI scan according
# to the timestamps associated with events in the experiment
#
# Author: Raghav Prasad
# Last modified: 30 June 2020

import pandas as pd
import nibabel as nib

from os.path import join
from os import mkdir
from glob import glob

VID_SCANS_DIR_NAME = 'video_scans'


def get_event_frames(func_path):
    csv_path = glob(join(func_path, '*.tsv'))[0]
    scan_path = glob(join(func_path, '*.nii.gz'))[0]

    events_df = pd.read_csv(csv_path, sep='\t', usecols=[0, 1, 2])
    events_df.drop(events_df[events_df['trial_type'] != 'video'].index,
                   axis=0,
                   inplace=True)
    events_df.reset_index(inplace=True)

    scan = nib.load(scan_path)

    frames = nib.funcs.four_to_three(scan)
    time_bw_frames = scan.header['pixdim'][4]

    mkdir(join(func_path, VID_SCANS_DIR_NAME))
    frames_dir = join(func_path, VID_SCANS_DIR_NAME)

    for ind in events_df.index:
        start = events_df['onset'][ind]
        duration = events_df['duration'][ind]

        start_frame_index = round(start/time_bw_frames)
        end_frame_index = start_frame_index + round(duration/time_bw_frames)

        required_frames = frames[start_frame_index:end_frame_index]

        four_d_img = nib.funcs.concat_images(required_frames)

        video_num = '0' + str(ind) if ind < 10 else str(ind)
        nib.save(four_d_img, join(frames_dir, 'video_'+video_num+'.nii.gz'))
