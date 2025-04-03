import nibabel as nb
import ants
import dicom2nifti
import shutil
import glob
import numpy as np
import os

wdir = 'C:/Users/assun/Desktop/TBVFiles/ROI-integration'
os.makedirs(f'{wdir}/trf', exist_ok=True)
'''
converter = Dcm2nii()
converter.inputs.source_names = [f'{wdir}/ses-01/001_000013_000001.dcm', f'{wdir}/ses-03/001_000011_000001.dcm']
converter.inputs.gzip_output = True
converter.inputs.output_dir = '.'
converter.cmdline

converter.run()
'''

dicom2nifti.convert_directory(f'{wdir}/dcm/ses-01/', f'{wdir}/dcm/ses-01/', compression=True, reorient=True)
dicom2nifti.convert_directory(f'{wdir}/dcm/ses-03/', f'{wdir}/dcm/ses-03/', compression=True, reorient=True)

#rename files
file = glob.glob(f'{wdir}/dcm/ses-01/*nii.gz')[0]
shutil.copyfile(file, f'{wdir}/dcm/ses-01/ses-01_ref.nii.gz')

file = glob.glob(f'{wdir}/dcm/ses-03/*nii.gz')[0]
shutil.copyfile(file, f'{wdir}/dcm/ses-03/ses-03_ref.nii.gz')

# change header of the roi and map files and mean epi (to check)
ses1_ref = nb.load(f'{wdir}/dcm/ses-01/ses-01_ref.nii.gz')

# NOTE: need to flip left and right when putting the affine because it was inverted before when using the identity matrix
mean_epi = nb.load(f'{wdir}/roi/ses-01/mean_epi.nii.gz').get_fdata()[::-1,:,:]
ses1_affine = ses1_ref.affine
nb.save(nb.Nifti1Image(mean_epi, affine=ses1_affine), f'{wdir}/roi/ses-01/mean_epi_affine.nii.gz')

temp = nb.load(f'{wdir}/roi/ses-01/pos-neu_tmap.nii.gz').get_fdata()[::-1,:,:]
nb.save(nb.Nifti1Image(temp, affine=ses1_affine), f'{wdir}/roi/ses-01/pos-neu_tmap_affine.nii.gz')

temp = nb.load(f'{wdir}/roi/ses-01/roi_mask_5%.nii.gz').get_fdata()[::-1,:,:]
nb.save(nb.Nifti1Image(temp, affine=ses1_affine), f'{wdir}/roi/ses-01/roi_mask_5%_affine.nii.gz')



fixed = ants.image_read(f'{wdir}/dcm/ses-03/ses-03_ref.nii.gz' )
moving = ants.image_read(f'{wdir}/dcm/ses-01/ses-01_ref.nii.gz')
fixed.plot(overlay=moving, title='Before Registration') # changed function ants/viz/plot.py, overlay_cmap="hot", overlay_alpha=0.5,
mytx = ants.registration(fixed=fixed , moving=moving, type_of_transform='Affine')
print(mytx)
warped_moving = mytx['warpedmovout']
fixed.plot(overlay=warped_moving,
           title='After Registration')

mywarpedimage = ants.apply_transforms(fixed=fixed, moving=moving,
                                      transformlist=mytx['fwdtransforms'], interpolator='bSpline')

mywarpedimage.plot()
ants.image_write(mywarpedimage, f'{wdir}/trf/ses-01_ref_2_ses-03_ref_affine.nii.gz')
affine_mat = ants.read_transform(mytx['fwdtransforms'][0])
ants.write_transform(affine_mat, f'{wdir}/trf/ses-01_ref_2_ses-03_ref_affine.mat')
ants.write_transform(affine_mat, f'{wdir}/trf/ses-01_ref_2_ses-03_ref_affine.txt')

affine_mat_inv = ants.read_transform(mytx['invtransforms'][0])
ants.write_transform(affine_mat, f'{wdir}/trf/ses-01_ref_2_ses-03_ref_affine_inv.mat')
ants.write_transform(affine_mat, f'{wdir}/trf/ses-01_ref_2_ses-03_ref_affine_inv.txt')

map_file = f'{wdir}/roi/ses-01/pos-neu_tmap_affine.nii.gz'
map_img = ants.image_read(map_file)
mywarpedimage = ants.apply_transforms(fixed=fixed, moving=map_img,
                                      transformlist=mytx['fwdtransforms'],
                                      interpolator='bSpline')
ants.image_write(mywarpedimage, f'{wdir}/trf/ses-01_map_2_ses-03_ref_affine.nii.gz')

roi_file = f'{wdir}/roi/ses-01/roi_mask_5%_affine.nii.gz'
roi_img = ants.image_read(roi_file)
mywarpedimage = ants.apply_transforms(fixed=fixed, moving=roi_img,
                                      transformlist=mytx['fwdtransforms'],
                                      interpolator='nearestNeighbor')
ants.image_write(mywarpedimage, f'{wdir}/trf/ses-01_roi_2_ses-03_ref_affine.nii.gz')