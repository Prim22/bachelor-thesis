import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from mpl_toolkits.axes_grid1 import make_axes_locatable
from scipy.interpolate import interp1d
import matplotlib.patches as mpatches
import pywt

def linear_interpolate_gaps(wl_full, refl_full, mask, needs_interpolation):
    """
    Linearly interpolate ONLY spectral gaps that need it (atmospheric regions).
    
    Parameters
    ----------
    wl_full : array
        Full wavelength array
    refl_full : array
        Full reflectance array
    mask : bool array
        True for valid bands, False for masked bands
    needs_interpolation : bool array
        True for bands that need interpolation (excludes VNIR/SWIR overlap)
    
    Returns
    -------
    refl_interpolated : array
        Reflectance with gaps linearly filled only where needed
    """
    refl_interpolated = refl_full.copy()
    
    # Create interpolator from valid points only
    interp_func = interp1d(wl_full[mask], refl_full[mask], 
                           kind='linear', fill_value='extrapolate')
    
    # Fill ONLY regions that need interpolation
    regions_to_fill = needs_interpolation & ~mask
    if regions_to_fill.sum() > 0:
        refl_interpolated[regions_to_fill] = interp_func(wl_full[regions_to_fill])
    
    return refl_interpolated

def plot_spectral_resampling(wl_bst_usgs, refl_bst_usgs,
                              wl_enmap_full, bst_usgs_enmap,
                              refl_enmap_interp, mask):
    """
    Two-panel plot showing USGS → EnMAP spectral resampling and gap interpolation.

    Args:
        wl_bst_usgs:       ndarray, original USGS lab wavelengths (nm)
        refl_bst_usgs:     ndarray, original USGS lab reflectance
        wl_enmap_full:     ndarray, EnMAP band centers (nm), all 224 bands
        bst_usgs_enmap:    ndarray, USGS spectrum resampled to EnMAP grid
        refl_enmap_interp: ndarray, resampled spectrum after gap interpolation
        mask:              boolean ndarray, True = kept band, False = masked
    """
    fig, axes = plt.subplots(2, 1, figsize=(14, 8), sharex=True)

    # ── Top: full spectrum comparison ─────────────────────────────
    axes[0].plot(wl_bst_usgs, refl_bst_usgs,
                 'k-', linewidth=0.5, alpha=0.7, label='Original Lab (1 nm sampling)')
    axes[0].plot(wl_enmap_full, bst_usgs_enmap,
                 'b-', linewidth=1.5, label='EnMAP Resampled (Full)')
    if (~mask).sum() > 0:
        axes[0].plot(wl_enmap_full[~mask], bst_usgs_enmap[~mask],
                     'ro', markersize=4, label='Masked Bands')
    axes[0].set_ylabel('Reflectance', fontweight='bold')
    axes[0].set_title('Spectral Resampling: USGS Lab → EnMAP Resolution',
                      fontsize=12, fontweight='bold')
    axes[0].legend(loc='upper right')
    axes[0].grid(True, alpha=0.3)

    # ── Bottom: before/after interpolation ────────────────────────
    axes[1].plot(wl_enmap_full, bst_usgs_enmap,
                 'b-', linewidth=1, alpha=0.5, label='Before Interpolation')
    axes[1].plot(wl_enmap_full, refl_enmap_interp,
                 'g-', linewidth=1.5, label='After Gap Interpolation')

    for region in [(418, 420), (1342, 1450), (1800, 2050), (2430, 2450)]:
        axes[1].axvspan(region[0], region[1], alpha=0.2, color='orange')
    axes[1].axvspan(900, 1000, alpha=0.15, color='cyan',
                    label='VNIR/SWIR overlap (SWIR kept)')

    axes[1].set_xlabel('Wavelength (nm)', fontweight='bold')
    axes[1].set_ylabel('Reflectance', fontweight='bold')
    axes[1].set_title('Linear Interpolation of Atmospheric Gaps (Excludes VNIR/SWIR Overlap)',
                      fontsize=12, fontweight='bold')
    axes[1].legend(loc='upper right')
    axes[1].grid(True, alpha=0.3)

    plt.tight_layout()
    plt.show()
    
def plot_dwt_decomposition(wl_enmap_full, refl_enmap_interp, dwt_results,
                            wavelet='db4'):
    """
    7-panel DWT decomposition plot: original, approximation, and D1–D5 details.

    Args:
        wl_enmap_full:     ndarray, EnMAP wavelengths (nm)
        refl_enmap_interp: ndarray, interpolated reflectance spectrum
        dwt_results:       dict keyed by wavelet name, each containing
                           {'recons': {'A': ..., 'D1': ..., ..., 'D5': ...}}
        wavelet:           str, which wavelet to display (default 'db4')
    """
    recons = dwt_results[wavelet]['recons']

    fig, axes = plt.subplots(7, 1, figsize=(14, 12), sharex=True)

    # Original
    axes[0].plot(wl_enmap_full, refl_enmap_interp, 'k-', linewidth=1.5)
    axes[0].set_ylabel('Original', fontweight='bold')
    axes[0].set_title(f'DWT Decomposition: {wavelet.upper()} Wavelet',
                      fontsize=12, fontweight='bold')
    axes[0].grid(True, alpha=0.3)

    # Approximation
    axes[1].plot(wl_enmap_full, recons['A'], 'b-', linewidth=1.5)
    axes[1].set_ylabel('Approx (A)', fontweight='bold')
    axes[1].grid(True, alpha=0.3)

    # Details D1–D5
    nd_ranges = [(540, 580), (700, 730), (770, 788), (820, 840)]
    colors = ['red', 'orange', 'green', 'purple', 'brown']

    for i, level in enumerate(['D1', 'D2', 'D3', 'D4', 'D5'], 2):
        if level in recons:
            axes[i].plot(wl_enmap_full, recons[level],
                         color=colors[i - 2], linewidth=1)
            axes[i].set_ylabel(level, fontweight='bold')
            axes[i].grid(True, alpha=0.3)
            for nd_range in nd_ranges:
                axes[i].axvspan(nd_range[0], nd_range[1], alpha=0.1, color='cyan')

    axes[-1].set_xlabel('Wavelength (nm)', fontweight='bold')

    nd_patch = mpatches.Patch(color='cyan', alpha=0.2, label='Nd absorption regions')
    fig.legend(handles=[nd_patch], loc='upper right',
               bbox_to_anchor=(0.98, 0.98), frameon=True)

    plt.tight_layout()
    plt.show()

    print(f"✓ DWT decomposition visualized for {wavelet}")
    print("  Cyan regions mark known Nd absorption features")
    
def plot_scalogram_with_top_spectrum(
    power,
    scales,
    wavelengths,
    spectrum,
    title="Bastnaesite Scalogram"
):
    # Highlighted wavelength regions
    ND_BANDS = [(540, 580), (700, 730), (770, 788), (820, 840)]
    # Convert scales to approximate feature width (FWHM)
    fwhm_axis = 2.355 * scales * np.mean(np.diff(wavelengths))

    # ---------------- Figure ----------------
    fig = plt.figure(figsize=(14, 7))

    # Shared LEFT/WIDTH so spectrum ends before colorbar
    left = 0.08
    width = 0.78

    # Top spectrum axis
    ax_spec = fig.add_axes([left, 0.78, width, 0.18])

    # Scalogram axis
    ax = fig.add_axes([left, 0.10, width, 0.62])

    # ---------------- Spectrum ----------------
    ax_spec.plot(
        wavelengths,
        spectrum,
        color='green',
        linewidth=1.2
    )

    # Highlight ND bands on top spectrum
    for start, end in ND_BANDS:
        ax_spec.axvspan(
            start,
            end,
            color='cyan',
            alpha=0.25
        )

    ax_spec.set_xlim(wavelengths.min(), wavelengths.max())

    ax_spec.set_ylabel("Reflectance")
    ax_spec.set_xticks([])
    ax_spec.set_title("Bastnaesite Spectrum")

    # ---------------- Scalogram ----------------
    im = ax.contourf(
        wavelengths,
        fwhm_axis,
        power,
        levels=25,
        cmap='hot'
    )

    # Highlight ND bands on scalogram
    for start, end in ND_BANDS:
        ax.axvspan(
            start,
            end,
            color='cyan',
            alpha=0.15
        )

    # Dedicated colorbar axis
    cax = fig.add_axes([0.88, 0.10, 0.02, 0.62])

    cbar = fig.colorbar(im, cax=cax)
    cbar.set_label("Power")

    ax.set_xlabel("Wavelength (nm)")
    ax.set_ylabel("Feature Width (nm)")
    ax.set_title(title)

    ax.grid(alpha=0.2)

    plt.show()
    
def summarize_wavelets(
    wl_enmap_full,
    test_wavelets=('haar', 'db4', 'sym6'),
    max_level_wavelet='db4',
    max_display_level=6,
):
    """
    Print wavelet family properties and estimate characteristic
    scales (in nm) for a set of DWT decomposition levels, given a clean
    (masked) wavelength array.
 
    Parameters
    ----------
    wl_enmap_full : array-like
        1D array of wavelengths (nm) for the clean/masked bands.
    test_wavelets : iterable of str, optional
        Wavelet names to summarize (default: ('haar', 'db4', 'sym6')).
    max_level_wavelet : str, optional
        Wavelet used to compute the max DWT decomposition level
        (default: 'db4').
    max_display_level : int, optional
        Upper bound on how many decomposition levels to print
        characteristic widths for (default: 6).
 
    Returns
    -------
    dict
        {
            'mean_sampling': float,
            'n_clean': int,
            'max_level': int,
            'char_widths': {j: width_nm, ...}
        }
    """
    wl_enmap_full = np.asarray(wl_enmap_full)
 
    # ------------------------------------------------------------------
    # Wavelet family properties
    # ------------------------------------------------------------------
    print("Wavelet Families for DWT:")
    print("=" * 60)
    for wav in test_wavelets:
        w = pywt.Wavelet(wav)
        print(f"\n{wav.upper()}:")
        print(f"  Family: {w.family_name}")
        print(f"  Vanishing moments: {w.vanishing_moments_psi}")
        print(f"  Filter length: {w.dec_len}")
        print(f"  Symmetry: {w.symmetry}")
        print(f"  Orthogonal: {w.orthogonal}")
        print(f"  Biorthogonal: {w.biorthogonal}")
 
    # ------------------------------------------------------------------
    # Characteristic scales for clean bands
    # ------------------------------------------------------------------
    mean_sampling = np.mean(np.diff(wl_enmap_full))
    n_clean = len(wl_enmap_full)
    max_level = pywt.dwt_max_level(n_clean, max_level_wavelet)
 
    print(f"\n{'=' * 60}")
    print("Signal properties:")
    print(f"  Number of clean bands: {n_clean}")
    print(f"  Mean sampling interval: {mean_sampling:.2f} nm")
    print(f"  Maximum DWT level: {max_level}")
 
    print(f"\nCharacteristic widths (nm):")
    print(f"  scale_j \u2248 2^j \u00d7 \u0394\u03bb_sampling")
    print(f"  {'-' * 50}")
 
    char_widths = {}
    for j in range(1, min(max_display_level, max_level + 1)):
        char_width = (2 ** j) * mean_sampling
        char_widths[j] = char_width
        print(f"  D{j}: 2^{j} \u00d7 {mean_sampling:.2f} = {char_width:.1f} nm")
 
    print(f"\n  \u2192 D1-D2 target REE features (10-50 nm FWHM)")
    print(f"  \u2192 D3-D4 capture broader features (Fe oxides, continuum)")
 
    return {
        'mean_sampling': mean_sampling,
        'n_clean': n_clean,
        'max_level': max_level,
        'char_widths': char_widths,
    }

def perform_dwt_multilevel(signal, wavelet='db4', level=5):
    """
    Perform multi-level DWT and return coefficients + reconstructions.
    
    Parameters
    ----------
    signal : array
        Input spectrum
    wavelet : str
        Wavelet name (e.g., 'haar', 'db4', 'sym4')
    level : int
        Decomposition levels
    
    Returns
    -------
    coeffs : list
        [cA_n, cD_n, ..., cD_1]
    reconstructions : dict
        {'A': approx, 'D1': detail1, 'D2': detail2, ...}
    """
    # Decompose
    coeffs = pywt.wavedec(signal, wavelet, level=level)
    
    # Reconstruct each component
    reconstructions = {} #Each reconstruction is the part of the original signal that lives at that scale
    
    # Approximation (lowest frequency)
    coeffs_approx = [coeffs[0]] + [np.zeros_like(c) for c in coeffs[1:]]
    reconstructions['A'] = pywt.waverec(coeffs_approx, wavelet)
    
    # Details (high frequency to low frequency)
    for i in range(1, len(coeffs)):
        coeffs_detail = [np.zeros_like(coeffs[0])] + \
                        [np.zeros_like(c) if j != i else c 
                         for j, c in enumerate(coeffs[1:], 1)]
        reconstructions[f'D{len(coeffs)-i}'] = pywt.waverec(coeffs_detail, wavelet)
    
    # Trim to original length (pywt may pad)
    for key in reconstructions:
        reconstructions[key] = reconstructions[key][:len(signal)]
    
    return coeffs, reconstructions