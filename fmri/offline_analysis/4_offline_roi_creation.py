from utils.map import read_map
import matplotlib
import matplotlib.pyplot as plt
matplotlib.use('Qt5Agg')
import numpy as np
import nibabel as nb
from bvbabel import fmr
import os
from utils.roi import write_roi, read_roi
from scipy.ndimage import binary_dilation, binary_erosion, label
import nibabel as nb
from utils.roi_prep import *


# load map file
wdir = 'D:/MatterNeurofeedback/derivatives/rawdata_bv'

sub = 'sub-07'
ses = 1
RUNS = ['3','4']
func_dir = f'{wdir}/{sub}/ses-0{ses}/func'


# Make ROI directory where the output will be saved
outdir = f'{func_dir}/ROI'
os.makedirs(outdir, exist_ok=True)

# get localiser2 and localiser3 to compute the average epi
fmr_sum = []
vol_nr = 0
for run in RUNS:
    hdr, fmr_data = fmr.read_fmr(f'{func_dir}/{sub}_ses-0{ses}_dir-AP_task-localiser{run}_run-0{run}_SCCTBL_3DMCTS_LTR_THPFFT0.0090Hz_SD3DSS3.60mm.fmr') #change this
    fmr_sum.append(np.sum(fmr_data, axis=3)[:,:,:,None])
    vol_nr += fmr_data.shape[-1]

mean_epi = np.squeeze(np.sum(fmr_sum, axis=0))/vol_nr #shift left and right???

# save mean image and mask as nifti
nb.save(nb.Nifti1Image(mean_epi[::-1,:,], affine=np.eye(4)), f'{outdir}/mean_epi.nii.gz')

epi_mask, threshold = heuristic_epi_mask(mean_epi,
                                         lower_cutoff=0.25,
                                         upper_cutoff=0.8,
                                         exclude_zeros=True,
                                         opening=3,
                                         connected=True,
                                         threshold_factor=0.5,
                                         outdir=outdir)

# Save mean epi mask
coords = np.where(epi_mask[:, ::-1, :] != 0)
coords = np.array([[x, y, z] for x, y, z in zip(coords[0], coords[1], coords[2])])
write_roi(f'{outdir}/epimask.roi', coords)

print(f'EPI intensity threshold: {threshold}')
print(f'Created EPI mask ROI file: epimask.roi')

mask_mosaic_plot(mean_epi, epi_mask, f'{outdir}/epi_mask.jpg')

print(f'\nMasking EMONET ROI recovering subcortical structures...')

# get ROI from localiser2
emonet = read_roi(f'{func_dir}/EMONET_loc2.roi')
subcort = read_roi(f'{func_dir}/SUBCORT_loc2.roi')

emo_mask = np.zeros(epi_mask.shape)
for coord in emonet:
    emo_mask[coord[0], coord[1], coord[2]] = 1

emo_mask = emo_mask[:, ::-1, :]
nb.save(nb.Nifti1Image(emo_mask.astype(int), affine=np.eye(4)), f'{outdir}/emo_mask.nii.gz')
mask_mosaic_plot(mean_epi, emo_mask, f'{outdir}/emo_mask.jpg')


subcort_mask = np.zeros(epi_mask.shape)
for coord in subcort:
    subcort_mask[coord[0], coord[1], coord[2]] = 1

#subcort_mask = subcort_mask[:, ::-1, :]
subcort_mask = subcort_mask[:,::-1, :]
nb.save(nb.Nifti1Image(subcort_mask.astype(int), affine=np.eye(4)), f'{outdir}/subcort_mask.nii.gz')

# mask emonet with epi mask
masked_emonet = emo_mask * epi_mask
nb.save(nb.Nifti1Image(masked_emonet.astype(int), affine=np.eye(4)), f'{outdir}/emo_mask_epi_masked.nii.gz')

# add subcortical and merge
masked_emonet_subcort = np.logical_or(masked_emonet, subcort_mask)
nb.save(nb.Nifti1Image(masked_emonet_subcort.astype(int)[::-1,:,:], affine=np.eye(4)),
        f'{outdir}/emo_mask_epi_masked_subcort.nii.gz')

coords = np.where(masked_emonet_subcort[:,::-1,:] != 0)
coords = np.array([[x, y, z] for x, y, z in zip(coords[0], coords[1], coords[2])])
write_roi(f'{outdir}/emo_mask_epi_masked_subcort.roi', coords)

mask_mosaic_plot(mean_epi, masked_emonet_subcort, f'{outdir}/emo_mask_epi_masked_subcort.jpg')

print('Get map data from offline GLM...')

mask_perc = 5
min_clust_size = 50

# save as nifti
hdr, map_data = read_map(f'{func_dir}/GLM/pos-neu.map')
nb.save(nb.Nifti1Image(map_data, affine=np.eye(4)),f'{outdir}/pos-neu_tmap.nii.gz' )

tmap = map_data[masked_emonet_subcort[::-1,:,:]]

# create 3D mask from functional coordinates
vol_mask = np.zeros(mean_epi.shape)

# eliminate mask_thr% of voxels with lowest activity level
thr = (100 - mask_perc) / 100
num_excluded_voxels = np.round(thr * len(tmap)).astype(int)

print(f'\nNumber of requested voxels : {len(tmap) - num_excluded_voxels}')

flatten_mask = np.ones(len(tmap))

idx = np.argsort(tmap)  # sort in ascending order
idx = idx[:num_excluded_voxels]
flatten_mask[idx] = 0

coords = np.where(masked_emonet_subcort[::-1,:,:] != 0)
coords = np.array([[x, y, z] for x, y, z in zip(coords[0], coords[1], coords[2])])

for coord in coords:
    vol_mask[coord[0], coord[1], coord[2]] = 1

# save the masked map
temp = vol_mask.copy()
temp[vol_mask==1] = tmap

nb.save(nb.Nifti1Image(temp, affine=np.eye(4)),
        f'{outdir}/masked_map.nii.gz')

new_vol_mask, new_flatten_mask = remove_small_clusters(vol_mask, coords[np.logical_not(flatten_mask), :],
                                                       int(min_clust_size))

nb.save(nb.Nifti1Image(new_vol_mask.astype(int), affine=np.eye(4)),
        f'{outdir}/roi_mask_5%.nii.gz')

sel_tmap = np.array(tmap)[new_flatten_mask]

# save the tvalues and the roi coordinates:

coords = np.where(new_vol_mask[::-1,::-1,:] != 0)
sel_func_coords = np.array([[x, y, z] for x, y, z in zip(coords[0], coords[1], coords[2])])

mask_mosaic_plot(mean_epi, new_vol_mask[::-1,:,:], f'{outdir}/NFTarger_roi.jpg')

write_roi(f'{outdir}/NFTarget.roi', sel_func_coords)
print(f'Number of selected voxels: {len(sel_tmap)}\n')
print(f'T-value threshold: {np.min(sel_tmap[sel_tmap != 0]):.2}\n')
print(f'NF Target ROI saved to file: {outdir}/NFTarget.roi')









