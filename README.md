# Bachelor Thesis — REE Detection in EnMAP Hyperspectral Data


This repository contains the code and analysis notebooks developed for my Bachelor's thesis on the detection and analysis of rare earth element (REE) signatures in EnMAP hyperspectral imagery.


The project investigates hyperspectral data processing and spectral analysis using methods including principal component analysis (PCA) and wavelet-based analysis.


> **Note:** The EnMAP hyperspectral scene used in this research is not included in this repository because the data cannot be redistributed. The analysis can be reproduced by providing the required EnMAP scene locally and configuring its path as described below.


---


## Project Structure


```text
bachelor-thesis/
│
├── config/
│   └── data_config.example.yaml
│
├── data/
│   ├── EnMAP_Spectral_Bands.xlsx
│   └── usgs_folder/
│
├── notebooks/
│   ├── REE_PCA_Implementation.ipynb
│   └── REE_WaveletDecomposition.ipynb
│
├── src/
│   ├── enmap_data.py
│   ├── enmap_utils.py
│   ├── ree_pca_viz.py
│   └── ree_wavelet_viz.py
│
├── environment.yml
├── .gitignore
└── README.md
Directories and files
notebooks/ — Jupyter notebooks containing the main analysis workflows.
src/ — Reusable Python functions used by the notebooks.
data/ — Supporting data used by the analysis, including EnMAP spectral band information and USGS reference spectra.
config/ — Local configuration for paths to datasets that cannot be included in the repository.
environment.yml — Conda environment specification for reproducing the Python environment.
.gitignore — Specifies local, temporary, and restricted files that should not be committed.
Requirements

The project uses Python through the Conda package manager.

The required environment is specified in:

environment.yml

Create the environment with:

conda env create -f environment.yml

Then activate it:

conda activate bachelor-thesis

If the environment already exists and needs to be updated:

conda env update -f environment.yml
EnMAP Data

The EnMAP hyperspectral scene used in the thesis is not included in this repository due to data redistribution restrictions.

To run the notebooks, obtain access to the required EnMAP scene and store it locally.

Create a local configuration file by copying:

config/data_config.example.yaml

to:

config/data_config.yaml

Then edit data_config.yaml and provide the path to the local EnMAP .HDR file.

For example:

enmap_hdr: "C:/path/to/your/ENMAP_SPECTRAL_IMAGE.HDR"

The local data_config.yaml file is ignored by Git and should not be committed.

Running the Analysis

After activating the Conda environment, launch Jupyter:

jupyter notebook

Open the notebooks located in:

notebooks/

The notebooks currently included in the repository are:

REE PCA Implementation

REE_PCA_Implementation.ipynb

Implementation and analysis of PCA-based processing for the EnMAP hyperspectral data.

REE Wavelet Decomposition

REE_WaveletDecomposition.ipynb

Wavelet-based decomposition and analysis of spectral information for REE detection.

Reproducibility

The repository is structured so that the analysis environment and code can be reproduced without distributing the restricted EnMAP scene.

Reproducibility requires:

The repository contents.
The Conda environment specified in environment.yml.
Access to the required EnMAP hyperspectral scene.
A local config/data_config.yaml pointing to the scene.

The raw EnMAP hyperspectral data itself is not part of the repository.

Data Sources

The project uses:

EnMAP hyperspectral imagery for the primary analysis.
EnMAP spectral band information provided in data/EnMAP_Spectral_Bands.xlsx.
USGS spectral reference data contained in data/usgs_folder/.
Thesis

Author: [Your Name]
Degree: Bachelor's Thesis
Institution: [University / Institution]
Year: 2026

Thesis title: [Your official thesis title]