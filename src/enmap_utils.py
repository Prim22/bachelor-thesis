# enmap_utils.py
import numpy as np
import pandas as pd
from scipy.spatial.distance import cdist
from scipy.linalg import inv
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler
from math import log, sqrt, pi, exp
from scipy.spatial import ConvexHull
from scipy.optimize import nnls

# -----------------------------
# Gaussian Spectral Response Function (SRF)
# -----------------------------
def gaussian_srf(wl_grid, center, fwhm):
    sigma = fwhm / (2*np.sqrt(2*np.log(2)))
    g = np.exp(-0.5 * ((wl_grid - center)/sigma)**2)
    g[np.abs(wl_grid - center) > 3*sigma] = 0.0
    area = np.trapezoid(g, wl_grid)
    if area == 0:
        return g
    return g / area

def resample_spectrum(wl_lab, refl_lab, centers, fwhm):
    out = []
    for c, f in zip(centers, fwhm):
        srf = gaussian_srf(wl_lab, c, f)
        val = np.trapezoid(srf * refl_lab, wl_lab)
        out.append(val)
    return np.array(out)
