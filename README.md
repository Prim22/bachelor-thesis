# Bachelor Thesis — REE Detection in EnMAP Hyperspectral Data
 
**Machine Learning Decomposition Framework for Identifying Rare Earth Elements in Hyperspectral Remote Sensing Images**
 
This repository contains the code and analysis notebooks developed for my Bachelor's thesis on the detection and analysis of rare earth element (REE) signatures in EnMAP hyperspectral imagery. The project investigates a data-driven framework combining **Principal Component Analysis (PCA)** and **wavelet-based spectral decomposition** (Continuous Wavelet Transform / Mexican Hat and Discrete Wavelet Transform / Daubechies db4) to explore REE-related spectral structure without relying on ad hoc preprocessing or extensive ground-truth data.
 
The case study site is the Mountain Pass REE mine, California, using EnMAP satellite hyperspectral imagery and USGS Spectral Library laboratory reference spectra (bastnäsite).
 
> **Note:** The EnMAP hyperspectral scene used in this research is **not included** in this repository, as the data cannot be redistributed. The analysis can be reproduced by providing the required EnMAP scene locally and configuring its path as described below.
 
---
 
## Project Structure
 
```
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
```
 
### Directories and files
 
| Path | Description |
|---|---|
| `notebooks/` | Jupyter notebooks containing the main analysis workflows. |
| `src/` | Reusable Python functions used by the notebooks. |
| `data/` | Supporting data used by the analysis, including EnMAP spectral band information and USGS reference spectra. |
| `config/` | Local configuration for paths to datasets that cannot be included in the repository. |
| `environment.yml` | Conda environment specification for reproducing the Python environment. |
| `.gitignore` | Specifies local, temporary, and restricted files that should not be committed. |
 
---
 
## Requirements
 
The project uses Python through the Conda package manager. The required environment is specified in `environment.yml`.
 
Create the environment with:
 
```bash
conda env create -f environment.yml
```
 
Then activate it:
 
```bash
conda activate bachelor-thesis
```
 
If the environment already exists and needs to be updated:
 
```bash
conda env update -f environment.yml
```
 
---
 
## EnMAP Data
 
The EnMAP hyperspectral scene used in the thesis is not included in this repository due to data redistribution restrictions.
 
To run the notebooks:
 
1. Obtain access to the required EnMAP Level-2A scene and store it locally. Data can be requested via the [EnMAP data access portal](https://www.enmap.org/data_access/).
2. Create a local configuration file by copying:
```
   config/data_config.example.yaml
```
   to:
```
   config/data_config.yaml
```
3. Edit `data_config.yaml` and provide the path to the local EnMAP `.HDR` file, for example:
```yaml
   enmap_hdr: "C:/path/to/your/ENMAP_SPECTRAL_IMAGE.HDR"
```
 
The local `data_config.yaml` file is ignored by Git and should not be committed.
 
---
 
## Running the Analysis
 
After activating the Conda environment, launch Jupyter:
 
```bash
jupyter notebook
```
 
Open the notebooks located in `notebooks/`:
 
- **`REE_PCA_Implementation.ipynb`**
  Implementation and analysis of PCA-based decomposition of the EnMAP hyperspectral cube, including scree plots, spatial score maps, and spectral loadings.
- **`REE_WaveletDecomposition.ipynb`**
  Wavelet-based decomposition (CWT Mexican Hat and DWT Daubechies db4) of laboratory reference spectra, and the proposed framework correlating decomposed PCA loadings with decomposed laboratory spectra to evaluate scale-dependent spectral similarity.
---
 
## Methodology Overview
 
1. **PCA-based decomposition** of the EnMAP hyperspectral scene to identify dominant, data-driven modes of spectral variability.
2. **Wavelet decomposition** of USGS laboratory reference spectra (bastnäsite) to isolate scale-specific absorption features associated with neodymium (Nd) absorption dips.
3. **Cross-correlation** (Pearson) between PCA loadings and laboratory spectra, both in raw form and after Daubechies (db4) decomposition, to evaluate whether low-variance PCA components capture diagnostically relevant REE spectral structure at consistent scales.
For full methodological details, results, and discussion, see the thesis document.
 
---
 
## Reproducibility
 
The repository is structured so that the analysis environment and code can be reproduced without distributing the restricted EnMAP scene.
 
Reproducibility requires:
 
- The repository contents.
- The Conda environment specified in `environment.yml`.
- Access to the required EnMAP hyperspectral scene.
- A local `config/data_config.yaml` pointing to the scene.
The raw EnMAP hyperspectral data itself is not part of the repository.
 
---
 
## Data Sources
 
- **EnMAP** hyperspectral imagery (DLR) — primary hyperspectral scene, licensed product, not redistributed. [Data access portal](https://www.enmap.org/data_access/)
- **EnMAP spectral band information** — `data/EnMAP_Spectral_Bands.xlsx`
- **USGS Spectral Library Version 7** (`splib07a`) — laboratory reference spectra, public domain (CC0 1.0) — `data/usgs_folder/`. [USGS data release](https://www.usgs.gov/data/usgs-spectral-library-version-7-data)
---
 
## Thesis
 
| | |
|---|---|
| **Author** | Cristofer Pablo Muckenthaler Gallardo |
| **Degree** | Bachelor Thesis, Computer Science |
| **Institution** | School of Computer Science and Engineering, Constructor University |
| **Supervisor** | Prof. Dr. Joachim Vogt |
| **Submission date** | May 19, 2026 |
| **Title** | Machine Learning Decomposition Framework for Identifying Rare Earth Elements in Hyperspectral Remote Sensing Images |
 
---
 
## License
 
See the LICENSE file for the full terms.
 