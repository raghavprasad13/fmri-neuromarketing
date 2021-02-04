#!/usr/bin/env python3
# coding: utf-8
#
# This script thresholds the networks formed in the
# previous stage of the pipeline using a Data-Driven
# thresholding scheme based on Orthogonal Minimal Spanning Trees
#
# Author: Raghav Prasad
# Last modified: 02 February 2021

from dyconnmap.graphs.threshold import threshold_omst_global_cost_efficiency as threshold

import networkx as nx

import numpy as np

from os.path import join
import argparse
from multiprocessing import Pool
from tqdm import tqdm
from glob import glob
import warnings

warnings.filterwarnings('ignore')


def get_thresholded(scan_path):
    adj_mat = np.load(scan_path)
    np.nan_to_num(adj_mat, copy=False, posinf=0)

    neg_edges = np.argwhere(adj_mat < 0)
    neg_edges = neg_edges.T
    adj_mat_abs = np.absolute(adj_mat)

    thresholded = threshold(adj_mat_abs)
    thresholded_net = thresholded[1]
    np.fill_diagonal(thresholded_net, 0)
    thresholded_net[neg_edges[0], neg_edges[1]] *= -1

    return (scan_path, thresholded_net)


ap = argparse.ArgumentParser()
ap.add_argument("-d", "--dataset", required=True,
                help="path to dataset directory")
args = vars(ap.parse_args())

if args['dataset'][-1] == '/':
    args['dataset'] = args['dataset'][:len(args['dataset'])-1]

dataset_path = args['dataset']
vid_scan_dirs = glob(join(dataset_path, 'sub*', 'func', 'video_scans'))


if __name__ == '__main__':
    with Pool() as p:
        with tqdm(total=len(vid_scan_dirs),
                  desc='Subject networks thresholded') as pbar:
            for vid_scan_dir in vid_scan_dirs:
                scan_paths = glob(join(vid_scan_dir, '*_adj_mat.npy'))
                for scan_path, thresholded_net in p.imap_unordered(get_thresholded,
                                                                   scan_paths):
                    video_num = scan_path.split('/')[-1].split('_')[1]
                    func_net_after = nx.from_numpy_matrix(thresholded_net)
                    if func_net_after.number_of_edges() > 0:
                        np.save(join(vid_scan_dir,
                                     'video_'+video_num+'_adj_mat_thresh.npy'),
                                thresholded_net)
                pbar.update()
