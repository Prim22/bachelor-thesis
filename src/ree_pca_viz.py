import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from mpl_toolkits.axes_grid1 import make_axes_locatable

# -----------------------------
# RGB + 3D Cube Visualization
# -----------------------------
def plot_rgb_and_cube(cube, wavelengths, title='Hyperspectral Data Cube\nMountain Pass Mine'):
    """
    Side-by-side RGB preview and 3D spectral cube visualization.

    Args:
        cube:        ndarray (n_rows, n_cols, n_bands) in reflectance
        wavelengths: ndarray (n_bands,) of band centers in nm
        title:       title for the 3D cube subplot
    """
    n_rows, n_cols, n_bands = cube.shape
    cmap = plt.get_cmap('turbo')

    # RGB composite
    r_idx = np.argmin(np.abs(wavelengths - 650))
    g_idx = np.argmin(np.abs(wavelengths - 550))
    b_idx = np.argmin(np.abs(wavelengths - 470))
    rgb = np.dstack([cube[:, :, r_idx], cube[:, :, g_idx], cube[:, :, b_idx]])
    rgb_stretched = np.clip((rgb - rgb.min()) / (np.percentile(rgb, 99) - rgb.min()), 0, 1)

    # Face color arrays
    def _make_face_colors(intensity):
        n_b, n_spatial = intensity.shape
        colors = np.zeros((n_b, n_spatial, 3))
        for i in range(n_b):
            s = intensity[i]
            lo, hi = np.percentile(s, [5, 95])
            norm = np.clip((s - lo) / (hi - lo), 0, 1) if hi > lo else np.zeros_like(s)
            colors[i] = cmap(norm)[:, :3]
        return colors

    front_colors = _make_face_colors(np.mean(cube, axis=0).T)
    side_colors  = _make_face_colors(np.mean(cube, axis=1).T)

    x_grid = np.arange(n_cols)
    y_grid = np.arange(n_rows)
    z_grid = np.arange(n_bands)

    fig = plt.figure(figsize=(20, 8))

    # Left: RGB
    ax1 = fig.add_subplot(1, 2, 1)
    ax1.imshow(rgb_stretched)
    ax1.set_title(
        f'RGB Preview\nR:{wavelengths[r_idx]:.0f} nm  '
        f'G:{wavelengths[g_idx]:.0f} nm  B:{wavelengths[b_idx]:.0f} nm',
        fontsize=12
    )
    ax1.axis('off')

    # Right: 3D cube
    ax2 = fig.add_subplot(1, 2, 2, projection='3d')

    X_top, Y_top = np.meshgrid(x_grid, y_grid)
    ax2.plot_surface(X_top, Y_top, np.ones_like(X_top) * (n_bands - 1),
                     facecolors=rgb_stretched, shade=False, rstride=1, cstride=1)

    X_front, Z_front = np.meshgrid(x_grid, z_grid)
    ax2.plot_surface(X_front, np.zeros_like(X_front), Z_front,
                     facecolors=front_colors, shade=False, rstride=1, cstride=1)
    for z in range(0, n_bands, max(1, n_bands // 40)):
        ax2.plot(x_grid, np.zeros_like(x_grid), z, color='white', alpha=0.4, linewidth=0.6)

    Z_side, Y_side = np.meshgrid(z_grid, y_grid)
    ax2.plot_surface(np.ones_like(Y_side) * (n_cols - 1), Y_side, Z_side,
                     facecolors=np.swapaxes(side_colors, 0, 1), shade=False, rstride=1, cstride=1)
    for z in range(0, n_bands, max(1, n_bands // 40)):
        ax2.plot(np.ones_like(y_grid) * (n_cols - 1), y_grid, z, color='white', alpha=0.4, linewidth=0.6)

    ax2.set_xlim(0, n_cols);  ax2.set_ylim(0, n_rows);  ax2.set_zlim(0, n_bands)
    ax2.xaxis.pane.fill = False;  ax2.yaxis.pane.fill = False;  ax2.zaxis.pane.fill = False
    ax2.grid(False)
    ax2.set_xlabel('Spatial dimension r', labelpad=10, fontsize=10)
    ax2.set_ylabel('Spatial dimension c', labelpad=10, fontsize=10)
    ax2.set_zlabel('Spectral\nwavelength b', labelpad=15, fontsize=10)
    ax2.set_title(title, fontsize=12)
    ax2.view_init(elev=30, azim=-55)

    plt.tight_layout()
    plt.show()


# -----------------------------
# Scree Plot
# -----------------------------
def plot_scree(var_ratio, method_name='PCA'):
    components = np.arange(1, len(var_ratio) + 1)
    fig, axes = plt.subplots(1, 2, figsize=(12, 5))

    for ax, log in zip(axes, [False, True]):
        ax.plot(components, var_ratio, 'o-', linewidth=2, markersize=5)
        if log:
            ax.set_yscale('log')
            ax.set_title(f'{method_name}: Variance Explained (Log)', fontweight='bold')
            ax.set_ylabel('Variance Ratio (log)')
            ax.grid(True, alpha=0.3, which='both')
        else:
            ax.set_title(f'{method_name}: Variance Explained', fontweight='bold')
            ax.set_ylabel('Variance Ratio')
            ax.grid(True, alpha=0.3)
        ax.set_xlabel('Component')

    plt.suptitle(f'{method_name} Scree Plot', fontsize=14, fontweight='bold')
    plt.tight_layout()
    plt.show()


# -----------------------------
# Spatial Component Maps
# -----------------------------
def plot_spatial_components(img, method_name, n_show=16, cmap='RdBu_r'):
    n_cols_grid = 4
    n_rows_grid = (n_show + 3) // 4

    fig, axes = plt.subplots(n_rows_grid, n_cols_grid, figsize=(10, n_rows_grid * 2.5))
    axes = axes.flatten()

    for i in range(n_show):
        component = img[:, :, i]
        vmin, vmax = np.nanpercentile(component, [2, 98])
        im = axes[i].imshow(component, cmap=cmap, vmin=vmin, vmax=vmax)
        axes[i].set_title(f'{method_name} {i+1}', fontsize=10)
        axes[i].axis('off')
        divider = make_axes_locatable(axes[i])
        cax = divider.append_axes("bottom", size="5%", pad=0.3)
        plt.colorbar(im, cax=cax, orientation='horizontal').ax.tick_params(labelsize=7)

    for j in range(n_show, len(axes)):
        axes[j].set_visible(False)

    plt.tight_layout()
    plt.show()


# -----------------------------
# Spectral Loadings
# -----------------------------
def plot_loadings(loadings, wavelengths, method_name, n_show=9):
    n_cols_grid = 3
    n_rows_grid = (n_show + 2) // 3

    fig, axes = plt.subplots(n_rows_grid, n_cols_grid, figsize=(18, n_rows_grid * 4))
    axes = axes.flatten()

    for i in range(min(n_show, loadings.shape[1])):
        ax = axes[i]
        ax.plot(wavelengths, loadings[:, i], linewidth=1.5, color='steelblue')
        ax.axhline(0, color='black', linestyle='--', linewidth=0.8, alpha=0.5)

        ax.set_title(f'{method_name} Component {i+1}', fontsize=11, fontweight='bold')
        ax.set_xlabel('Wavelength (nm)', fontsize=9)
        ax.set_ylabel('Loading', fontsize=9)
        ax.grid(True, alpha=0.3)

    for j in range(n_show, len(axes)):
        axes[j].set_visible(False)

    plt.tight_layout()
    plt.show()
