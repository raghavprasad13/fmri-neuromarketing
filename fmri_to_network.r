#!/usr/local/bin/Rscript --vanilla
# Usage pet_to_network.r -d path/to/dataset
# 
# Requirements:
# * optparse
# * ppcor
# * reticulate
# * RcppCNPy
# * progress
# 
# Last updated: 04 February 2021
# Author: Raghav Prasad


to_install <- c("optparse", "ppcor", "reticulate", "RcppCNPy", "progress")

install.packages(setdiff(to_install, rownames(installed.packages())), repos = "https://mirrors.ustc.edu.cn/CRAN/")

library("optparse")
library("ppcor")
library('reticulate')
library('RcppCNPy')
library('progress')

sink(file = "/dev/null", append = FALSE, type = c("output", "message"), split = FALSE)	# prevents verbose output
 
option_list = list(
  make_option(c("-d", "--dataset"), default=NULL, type="character",
              help="path to dataset directory", metavar="character")
);

opt_parser = OptionParser(option_list=option_list);
opt = parse_args(opt_parser);

if (is.null(opt$dataset)){
  print_help(opt_parser);
  stop("At least one argument must be supplied (input file).n", call.=FALSE);
}

FSLDIR <- Sys.getenv('FSLDIR');
if(FSLDIR == '')
	stop("Seems like you don't have FSL installed", call.=FALSE);

dataset_path <- opt$dataset

parcel_path <- 'Resampled_Juelich_Atlas.nii.gz'
vid_scan_dirs <- Sys.glob(file.path(dataset_path, 'sub*', 'func', 'video_scans'))

total <- length(vid_scan_dirs)

source_python("parcellate.py")

pb <- progress_bar$new(
	format = "Subject networks constructed (:current/:total) [:bar] (:percent) in :elapsed, eta: :eta",
	total=total, clear=FALSE)

pb$tick(0)
for (vid_scan_dir in vid_scan_dirs) {
    scan_paths <- Sys.glob(file.path(vid_scan_dir, '*.nii.gz'))
    for (scan_path in scan_paths) { 
        matrices <- time_series_to_matrix(scan_path, parcel_path)

        # matrices$pre_adj has dimensions num_nodes * time_series_len
        # ppcor.pcor constructs an adjacency matrix of size equal to the number of columns in matrices$pre_adj
        # Thus, in order to get an adjacency matrix of size num_nodes, matrices$pre_adj is transposed

        tryCatch({
            pre_adj_transpose <- t(matrices$pre_adj)
            adj_mat_part <- pcor(pre_adj_transpose, "pearson")		# partial correlation matrix
            adj_mat_corr <- cor(pre_adj_transpose)					# bivariate correlation matrix

            corr_zero_indices <- which(adj_mat_corr == 0)			# Get the indices of the zero elements in the bivariate correlation matrix
            adj_mat_part$estimate[corr_zero_indices] = 0			# Set the elements of the partial correlation matrix indexed by corr_zero_indices to zero

            vid_scan_path_list <- strsplit(scan_path, '/')[[1]]
            vid_scan_name_w_ext <- vid_scan_path_list[length(vid_scan_path_list)]
            vid_scan_name <- substr(vid_scan_name_w_ext, 1, 8)

            adj_mat_path <- file.path(vid_scan_dir, paste(vid_scan_name, "adj_mat.npy", sep='_'))
            percolation_path <- file.path(vid_scan_dir, paste(vid_scan_name, "avg_node_vals.npy", sep='_'))
            npySave(adj_mat_path, adj_mat_part$estimate, checkPath=FALSE)
            npySave(percolation_path, matrices$avg_node_vals, checkPath=FALSE)
        }, error=function(e){cat("ERROR:", scan_path, "\n")})
        # pre_adj_transpose <- t(matrices$pre_adj)
        # adj_mat_part <- pcor(pre_adj_transpose, "pearson")		# partial correlation matrix
        # adj_mat_corr <- cor(pre_adj_transpose)					# bivariate correlation matrix

        # corr_zero_indices <- which(adj_mat_corr == 0)			# Get the indices of the zero elements in the bivariate correlation matrix
        # adj_mat_part$estimate[corr_zero_indices] = 0			# Set the elements of the partial correlation matrix indexed by corr_zero_indices to zero

        # vid_scan_name <- strsplit(scan_path, '/')[[1]]
        # vid_scan_name <- vid_scan_name[length(vid_scan_name)]

        # adj_mat_path <- file.path(vid_scan_dir, paste(vid_scan_name, "adj_mat.npy", sep='_'))
        # percolation_path <- file.path(vid_scan_dir, paste(vid_scan_name, "avg_node_vals.npy", sep='_'))
        # npySave(adj_mat_path, adj_mat_part$estimate, checkPath=FALSE)
        # npySave(percolation_path, matrices$avg_node_vals, checkPath=FALSE)
    }
	pb$tick()
}
