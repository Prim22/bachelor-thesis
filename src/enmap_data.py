# enmap_data.py
import numpy as np
import pandas as pd
import os

# -----------------------------
# Load EnMAP Band Centers & FWHM
# -----------------------------
def load_enmap_bands(xlsx_path_or_url):
    """
    Reads EnMAP VNIR + SWIR bands from Excel.
    Returns:
        centers: numpy array of all band centers (nm), SORTED
        fwhm: numpy array of all FWHM (nm), sorted by wavelength
    """
    sheets = pd.read_excel(xlsx_path_or_url, sheet_name=None)
    vnir_df = sheets['VNIR']
    swir_df = sheets['SWIR']
    
    vnir_centers = vnir_df['CW (nm)'].to_numpy()
    vnir_fwhm    = vnir_df['FWHM (nm)'].to_numpy()
    
    swir_centers = swir_df['CW (nm)'].to_numpy()
    swir_fwhm    = swir_df['FWHM (nm)'].to_numpy()
    
    centers = np.concatenate([vnir_centers, swir_centers])
    fwhm    = np.concatenate([vnir_fwhm, swir_fwhm])
    
    sort_idx = np.argsort(centers)
    centers = centers[sort_idx]
    fwhm = fwhm[sort_idx]
    
    return centers, fwhm

def create_band_mask(wavelengths, fwhm, overlap_fwhm_threshold=10):

    mask = np.ones(len(wavelengths), dtype=bool)

    overlap_region = (wavelengths >= 900) & (wavelengths <= 1000)
    vnir_in_overlap = overlap_region & (fwhm < overlap_fwhm_threshold)

    interp_regions = (
        ((wavelengths >= 418)  & (wavelengths <= 420))  |
        ((wavelengths >= 1342) & (wavelengths <= 1450)) |
        ((wavelengths >= 1800) & (wavelengths <= 2050)) |
        ((wavelengths >= 2430) & (wavelengths <= 2450))
    )

    mask[vnir_in_overlap] = False
    mask[interp_regions] = False

    return mask, vnir_in_overlap, interp_regions

# -----------------------------
# Read USGS Spectra (splib07a AREF format)
# -----------------------------
def read_splib07a_aref(filepath):
    """
    Reads a splib07a AREF file:
    - Skips first 3 lines
    - Reads remaining reflectance values
    - Assigns wavelength from 400 to 2500 nm
    """
    with open(filepath, 'r') as f:
        lines = f.readlines()[3:]  # skip first 3 lines
    
    refl = []
    for l in lines:
        l = l.strip()
        if l == "":
            continue
        try:
            val = float(l)
            if val == -1.23e+034:  # skip invalid placeholders
                continue
            refl.append(val)
        except ValueError:
            continue
    
    refl = np.array(refl)
    wl = np.linspace(400, 2500, len(refl))
    return wl, refl


def load_usgs_spectra(folder_path):
    """
    Loads all USGS spectra from .txt or .asc files in a folder.
    
    Returns:
        spectra_dict: dict with filename keys and (wl, refl) tuples
    """
    files = [f for f in os.listdir(folder_path) if f.lower().endswith(('.txt','.asc'))]
    spectra_dict = {}
    for fname in files:
        path = os.path.join(folder_path, fname)
        try:
            wl, refl = read_splib07a_aref(path)
            spectra_dict[fname] = (wl, refl)
        except Exception as e:
            print(f"Failed to load {fname}: {e}")
    return spectra_dict


# -----------------------------
# Resample All USGS Spectra to a Common Grid
# -----------------------------
def resample_usgs_library(usgs_spectra, wl_lab):
    """
    Interpolates all USGS spectra onto a common wavelength grid.
    
    Returns:
        resampled_library: dict with filename keys and (wl_lab, refl_interp)
    """
    resampled_library = {}
    for name, (wl, refl) in usgs_spectra.items():
        refl_interp = np.interp(wl_lab, wl, refl, left=np.nan, right=np.nan)
        # Fill NaNs with nearest valid mean
        nan_mask = np.isnan(refl_interp)
        if nan_mask.any():
            valid_idx = np.where(~nan_mask)[0]
            if len(valid_idx) == 0:
                continue
            refl_interp[nan_mask] = refl_interp[valid_idx].mean()
        resampled_library[name] = (wl_lab, refl_interp)
    return resampled_library

# -----------------------------
# Load Hyperspectral Cube
# -----------------------------
def load_hyperspectral_cube(hdr_path, wl_all, roi_row1, roi_row2, roi_col1, roi_col2):
    """
    Loads an EnMAP hyperspectral cube from a ENVI .hdr file,
    converts DN to reflectance, crops to ROI, and aligns bands to wl_all.

    Args:
        hdr_path:  path to the .hdr file
        wl_all:    numpy array of EnMAP band centers (from load_enmap_bands)
        roi_row1, roi_row2: row bounds of the ROI (order doesn't matter)
        roi_col1, roi_col2: col bounds of the ROI (order doesn't matter)

    Returns:
        cube_data: numpy array (rows × cols × bands) in reflectance [0–1]
        wl_used:   numpy array of wavelengths matching the band axis
    """
    import spectral
    from pathlib import Path

    print(f'Loading: {Path(hdr_path).name}\n')

    if not Path(hdr_path).exists():
        raise FileNotFoundError(f"HDR file not found: {hdr_path}")

    cube = spectral.open_image(hdr_path)
    cube_data = cube.load()
    print(f' Raw cube shape: {cube_data.shape}  (rows × cols × bands)')

    if cube_data.max() > 10:
        cube_data = cube_data.astype(float) / 10000.0
        print(' Scaled DN → reflectance (÷10000)')
    else:
        print(' Data already in reflectance units')

    r_min, r_max = sorted([roi_row1, roi_row2])
    c_min, c_max = sorted([roi_col1, roi_col2])
    cube_data = cube_data[r_min:r_max, c_min:c_max, :]
    print(f' Cropped to ROI: {cube_data.shape}')

    n_bands = cube_data.shape[2]
    n_use = min(n_bands, len(wl_all))
    cube_data = cube_data[:, :, :n_use]
    wl_used = wl_all[:n_use]
    print(f' Working with {n_use} bands ({wl_used[0]:.1f}–{wl_used[-1]:.1f} nm)')

    return cube_data, wl_used
