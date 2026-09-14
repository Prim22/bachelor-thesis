import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import pearsonr



def plot_pca_lab_correlation_heatmap(corr_matrix, spectrum_names, component_names):
    """
    Plot the PCA-loadings-vs-USGS-lab-spectra Pearson correlation heatmap,
    grouped by mineral class.

    Parameters
    ----------
    corr_matrix : ndarray (n_components, n_spectra)
        Pearson correlation coefficients, columns ordered as in spectrum_names.
    spectrum_names : list of str
        Names of the lab spectra, in the same column order as corr_matrix.
    component_names : list of str
        Names of the PCA components (e.g. 'PC1', 'PC2', ...).
    """
    # Group spectra by mineral class
    ordered_spectra = [

        # REE minerals
        'Bastnaesite_crystal.txt',

        # Iron oxides
        'Hematite.txt',

        # Carbonates / carbonatites
        'Calcite.txt',
        'Dolomite.txt',

        # Silica / silicates
        'Chalcedony.txt',
        'Augite.txt',

        # Vegetation
        'Blackbrush.txt',
        'Juniper.txt'
    ]

    # Reorder correlation matrix columns
    ordered_indices = [spectrum_names.index(name) for name in ordered_spectra]

    corr_matrix_plot = corr_matrix[:, ordered_indices]
    spectrum_names_plot = ordered_spectra

    # Create figure
    fig, ax = plt.subplots(figsize=(12, 6))

    # Heatmap
    im = ax.imshow(
        corr_matrix_plot,
        cmap='RdBu_r',
        vmin=-1,
        vmax=1,
        aspect='auto',
        interpolation='none'
    )

    ax.grid(False)

    ax.set_xticks(np.arange(len(spectrum_names_plot)))
    ax.set_yticks(np.arange(len(component_names)))

    ax.set_xticklabels(spectrum_names_plot, rotation=45, ha='right', fontsize=9)
    ax.set_yticklabels(component_names, fontsize=10)

    # Add correlation values
    for i in range(len(component_names)):
        for j in range(len(spectrum_names_plot)):
            r_val = corr_matrix_plot[i, j]
            if np.isfinite(r_val):
                ax.text(
                    j, i, f'{r_val:.2f}',
                    ha="center", va="center",
                    color="black" if abs(r_val) < 0.5 else "white",
                    fontsize=8, fontweight='bold'
                )

    # Add group separator lines
    group_boundaries = [1, 2, 4, 6]
    for boundary in group_boundaries:
        ax.axvline(boundary - 0.5, color='black', linewidth=2)

    # Add group labels
    group_labels = [
        ('REE', 0.005),
        ('Iron Oxide', 1),
        ('Carbonates', 2.5),
        ('Silica/Silicates', 4.5),
        ('Vegetation', 6.5)
    ]

    for label, xpos in group_labels:
        ax.text(xpos, -0.9, label, ha='center', va='bottom', fontsize=10, fontweight='bold')

    # Colorbar
    cbar = plt.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
    cbar.set_label('Pearson Correlation (r)', rotation=270, labelpad=20, fontsize=11)

    # Titles and labels
    ax.set_title('PCA Loadings vs USGS Lab Spectra\nGrouped Mineral Correlation Map',
                 fontsize=14, fontweight='bold', pad=50)
    ax.set_xlabel('USGS Reference Spectra', fontsize=11, fontweight='bold')
    ax.set_ylabel('PCA Components', fontsize=11, fontweight='bold')

    plt.tight_layout()
    plt.show()


def plot_wavelet_correlation_heatmaps(correlation_results, N_PCA_COMPONENTS, DECOMP_LEVEL):
    """
    Plot a grid of wavelet-scale correlation heatmaps, one per lab spectrum:
    PC loadings (wavelet-decomposed) vs lab spectrum (wavelet-decomposed).

    Parameters
    ----------
    correlation_results : dict
        {lab_name: {'correlations': ndarray (N_PCA_COMPONENTS, DECOMP_LEVEL), 'p_values': ndarray}}
    N_PCA_COMPONENTS : int
        Number of PCA components (rows in each correlation matrix).
    DECOMP_LEVEL : int
        Number of wavelet decomposition levels (columns in each correlation matrix).
    """
    n_spectra = len(correlation_results)
    n_cols = 2
    n_rows = int(np.ceil(n_spectra / n_cols))

    fig, axes = plt.subplots(n_rows, n_cols, figsize=(14, 18))
    axes = axes.ravel() if n_spectra > 1 else [axes]

    for idx, (lab_name, results) in enumerate(correlation_results.items()):
        ax = axes[idx]
        ax.grid(False)
        corr_matrix_w = results['correlations']

        im = ax.imshow(
            corr_matrix_w,
            aspect='auto',
            cmap='RdBu_r',
            vmin=-1,
            vmax=1,
            interpolation='nearest'
        )

        for i in range(corr_matrix_w.shape[0]):
            for j in range(corr_matrix_w.shape[1]):
                value = corr_matrix_w[i, j]
                if abs(value) > 0.5:
                    ax.text(j, i, f'{value:.2f}', ha='center', va='center',
                            color='black', fontsize=8, fontweight='bold')

        ax.set_xlabel('Wavelet Detail Level (1=fine, 5=coarse)', fontsize=11)
        ax.set_ylabel('Principal Component', fontsize=11)
        ax.set_title(f'{lab_name}', fontsize=12, fontweight='bold')

        ax.set_xticks(range(DECOMP_LEVEL))
        ax.set_xticklabels([f'D{j+1}' for j in range(DECOMP_LEVEL)])

        ax.set_yticks(range(0, N_PCA_COMPONENTS, 2))
        ax.set_yticklabels([f'PC{i+1}' for i in range(0, N_PCA_COMPONENTS, 2)])

        cbar = plt.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
        cbar.set_label('Pearson r', fontsize=10)

    for idx in range(n_spectra, len(axes)):
        axes[idx].axis('off')

    plt.tight_layout(rect=[0, 0, 1, 0.96])
    plt.suptitle('Wavelet Correlation: PC Loadings vs Laboratory Spectra',
                 fontsize=14, fontweight='bold', y=1.00)
    plt.show()

def compute_correlation_map(loadings, lab_spectra_dict, wavelengths):
    '''Compute Pearson correlation between PCA loadings and lab spectra.'''
    n_comp = loadings.shape[1]
    n_spectra = len(lab_spectra_dict)

    corr_matrix = np.zeros((n_comp, n_spectra))
    pval_matrix = np.zeros((n_comp, n_spectra))

    for i in range(n_comp):
        loading = loadings[:, i]
        for j, (name, spectrum) in enumerate(lab_spectra_dict.items()):
            valid = np.isfinite(loading) & np.isfinite(spectrum)
            if np.sum(valid) > 3:
                r, p = pearsonr(loading[valid], spectrum[valid])
                corr_matrix[i, j] = r
                pval_matrix[i, j] = p
            else:
                corr_matrix[i, j] = np.nan
                pval_matrix[i, j] = np.nan

    return corr_matrix, pval_matrix

    
def compute_wavelet_correlation(details_pc, details_lab):
    '''Compute Pearson correlation between wavelet detail coefficients per level.'''
    n_levels = min(len(details_pc), len(details_lab))
    correlations = np.zeros(n_levels)
    p_values = np.zeros(n_levels)

    for j in range(n_levels):
        d_pc = details_pc[j]
        d_lab = details_lab[j]

        min_len = min(len(d_pc), len(d_lab))
        d_pc_trim = d_pc[:min_len]
        d_lab_trim = d_lab[:min_len]

        valid = np.isfinite(d_pc_trim) & np.isfinite(d_lab_trim)
        if valid.sum() > 2:
            r, p = pearsonr(d_pc_trim[valid], d_lab_trim[valid])
            correlations[j] = r
            p_values[j] = p
        else:
            correlations[j] = np.nan
            p_values[j] = np.nan

    return correlations, p_values