# fmri-neuromarketing

- [fmri-neuromarketing](#fmri-neuromarketing)
  - [Installation guide](#installation-guide)
  - [Atlas resampling](#atlas-resampling)
  - [fMRI scan preprocessing](#fmri-scan-preprocessing)
  - [Network construction](#network-construction)
  - [Thresholding](#thresholding)

## Installation guide

1. Clone this repository: `git clone https://github.com/raghavprasad13/fmri-neuromarketing.git`
2. In your terminal, navigate to the location you cloned this repository and type `pip3 install -r requirements.txt` to install the Python dependencies
3. Run the pipeline: `./full_pipeline.sh path/to/dataset`. In case this gives an error saying `Permission denied`, execute the following in the Terminal: `chmod a+x *.sh *.py`

## Atlas resampling

There is a mismatch in the dimensions of the dataset scans and the Juelich Atlas provided as a part of [FSL](https://fsl.fmrib.ox.ac.uk/fsl/fslwiki/Atlases). The Juelich Atlas has dimensions of 91x109x91 whereas the dataset scans have dimensions 53x63x44. Thus, to reconcile this mismatch, "resampling" was done on the Juelich Atlas to match the dimensions of the dataset scans and is given as `Resampled_Juelich_Atlas.nii.gz` in this repository.

## fMRI scan preprocessing

There are a total of 60 subjects in the dataset. Each subject has a corresponding fMRI scan. Each of these scans spans the duration of 35 commercials (visual stimuli). The preprocessor module [`preprocessor.py`] extracts the frames corresponding to each of these 35 commercials for each subject to form 4D fMRI images for each commercial for each subject. This yields 60 x 35 = 2100 scans in total.

## Network construction

Constructing networks from the preprocessed images required the generation of adjacency matrices. This was accomplished using a "combined functional connectivity" method which uses a combination of pairwise partial correlations and bivariate correlation to produce an adjacency matrix corresponding to each scan. This is achieved by `fmri_to_network.r` in conjunction with `parcellate.py`  
The calculation of partial correlations is a computationally intensive task, mainly due to the pre-calculation of residuals before computing cross-correlation. This calculation was made many times faster with the use of the [ppcor](https://cran.r-project.org/web/packages/ppcor/ppcor.pdf) package for R.

## Thresholding

Each of the networks (adjacency matrices) produced by the previous module are thresholded to reduce network complexity and preserve only significant edges. This is done using a data-driven method using orthogonal minimal spanning trees ([OMSTs](https://www.frontiersin.org/articles/10.3389/fninf.2017.00028/full)). This eliminates the use of arbitrary thresholding schemes such as absolute and proportional thresholding.
