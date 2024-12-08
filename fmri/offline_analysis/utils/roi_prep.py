import numpy as np
from scipy.ndimage import binary_dilation, binary_erosion, label
import nibabel as nb
import matplotlib.pyplot as plt
import matplotlib


def remove_small_clusters(mask, coords_to_delete, min_cluster_size):
    '''
    Revome clusters of size lower than min_size from the initial mask if not
    fully connected or already contains small clusters

    Parameters
    ----------

    mask : 3D numpy array
        mask volume

    coords_to_delete : 2D numpy array [n voxels] x 3
        coordinates of the voxels to be removed from mask according to the
        tvals thresholding

    min_size : int
        minimum allowed cluster size

    Returns
    ----------

    new_mask : 3D numpy array
        boolean final mask volume

    new_mask (flatten) : 1D array
        boolean final mask flatten

    '''

    def filter_connected_components(volume, min_thr):
        """
        Return a 3D array where only connected components greater than a size
        threshold (min_thr) are retained.

        Parameters
        ----------
        volume : numpy.ndarray
            3D boolean array indicating a volume.
        min_thr : int
            Minimum size (in voxels) for a connected component to be retained.

        Returns
        -------
        filtered_volume : numpy.ndarray
            3D boolean array with only the connected components greater than min_thr.
        """
        # Ensure the input is a numpy array
        volume = np.asarray(volume)

        # Label connected components
        labels, label_nb = label(volume, structure=np.ones((3,3,3))) #for 26 connectivity
        if not label_nb:
            raise ValueError("No non-zero values: no connected components")

        # Count the size of each component
        label_count = np.bincount(labels.ravel().astype(int))

        # Discard the 0 label (background)
        label_count[0] = 0

        # Filter labels by size threshold
        valid_labels = np.where(label_count >= min_thr)[0]

        # Create a boolean mask for components meeting the size criteria
        filtered_volume = np.isin(labels, valid_labels)

        return filtered_volume

    new_mask = mask.copy()
    for coord in coords_to_delete:
        new_mask[coord[0], coord[1], coord[2]] = 0

    # further remove small clusters
    new_mask = filter_connected_components(new_mask, min_cluster_size)

    return new_mask.astype(bool), new_mask[mask.astype(bool)].astype(bool)

def heuristic_epi_mask(mean_epi, lower_cutoff=0.2,upper_cutoff=0.85, exclude_zeros=True, opening=3, connected=True, threshold_factor=0.5, outdir=None):

    """ Heuristic masking procedure taken from nilearn.masking.compute_epi_mask"""

    def largest_connected_component(volume):
        """Return the largest connected component of a 3D array.

        Parameters
        ----------
        volume : numpy.ndarray
            3D boolean array indicating a volume.

        Returns
        -------
        volume : numpy.ndarray
            3D boolean array with only one connected component.
        """

        # We use asarray to be able to work with masked arrays.
        volume = np.asarray(volume)
        labels, label_nb = label(volume)
        if not label_nb:
            raise ValueError("No non-zero values: no connected components")
        if label_nb == 1:
            return volume.astype(bool)
        label_count = np.bincount(labels.ravel().astype(int))
        # discard the 0 label
        label_count[0] = 0
        return labels == label_count.argmax()


    mean_epi[np.logical_not(np.isfinite(mean_epi))] = 0
    sorted_input = np.sort(np.ravel(mean_epi))
    if exclude_zeros:
        sorted_input = sorted_input[sorted_input != 0]
    lower_cutoff = int(np.floor(lower_cutoff * len(sorted_input)))
    upper_cutoff = min(
        int(np.floor(upper_cutoff * len(sorted_input))), len(sorted_input) - 1
    )

    delta = (
            sorted_input[lower_cutoff + 1: upper_cutoff + 1]
            - sorted_input[lower_cutoff:upper_cutoff]
    )
    ia = delta.argmax()
    threshold = threshold_factor * (
            sorted_input[ia + lower_cutoff] + sorted_input[ia + lower_cutoff + 1]
    )

    fig, ax = plt.subplots()

    ax.axvline(sorted_input[lower_cutoff],color='black', linestyle='--')
    ax.axvline(sorted_input[upper_cutoff], color='black', linestyle='--')
    ax.axvline(threshold, color='red', linestyle='--')
    ax.hist(sorted_input, bins=100)
    fig.savefig(f'{outdir}/epi_histogram.jpg')

    plt.show()

    mask = mean_epi >= threshold

    if opening:
        opening = int(opening)
        mask = binary_erosion(mask, iterations=opening)
    mask_any = mask.any()
    if not mask_any:
        raise ValueError("Computed an empty mask.")

    if connected and mask_any:
        mask = largest_connected_component(mask)
    if opening:
        mask = binary_dilation(mask, iterations=2 * opening)
        mask = binary_erosion(mask, iterations=opening)

    return mask, threshold

def mask_mosaic_plot(mean_epi,mask, outfile):

    # Create a mosaic figure plotting the mask and the mean epi image
        # Determine the grid size for the mosaic

    grid_size = int(np.ceil(np.sqrt(mean_epi.shape[2])))
    plt.style.use('dark_background')
    fig, axes = plt.subplots(grid_size, grid_size, figsize=(20, 20))
    axes = axes.ravel()  # Flatten the 2D array of axes for easier iteration

    # Plot each slice
    mask_masked = np.ma.masked_array(mask, mask<=0)

    for i in range(mean_epi.shape[2]):
        ax = axes[i]
        ax.imshow(mean_epi[:, :, i], cmap='Greys_r', aspect='auto')
        ax.imshow(mask_masked[:,:,i],cmap='Reds_r', alpha=0.7, aspect='auto')
        ax.axis('off')

    # Hide unused axes
    for i in range(mean_epi.shape[2], len(axes)):
        axes[i].axis('off')

    plt.tight_layout()
    fig.savefig(outfile, dpi=300, bbox_inches='tight')
    plt.show()