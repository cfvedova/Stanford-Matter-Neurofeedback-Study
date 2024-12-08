from utils import map
import matplotlib
import matplotlib.pyplot as plt
matplotlib.use('Qt5Agg')
import numpy as np
import nibabel as nb
from bvbabel import fmr

# load map file

wdir = 'E:/Matter_project/NF_project/NFPilot3Data/offline_analysis/glm'

hdr, data = map.read_map(f'{wdir}/pos-neu.map')

fig, ax=plt.subplots()
ax.imshow(data[:,:,40], vmin=-1, vmax=1)

temp = nb.Nifti1Image(data, affine=np.eye(4))
nb.save(nb.Nifti1Image(data, affine=np.eye(4)),f'{wdir}/pos-neu_tmap.nii.gz' )

# save also the first volume of the reference fmr as nifti to check the map orientation
hdr, fmr_data = fmr.read_fmr('E:/Matter_project/NF_project/NFPilot3Data/offline_analysis/localiser1/localiser1_firstvol.fmr')
nb.save(nb.Nifti1Image(fmr_data[::-1,:,:,0], affine=np.eye(4)),f'{wdir}/localiser1_firstvol.nii.gz')







