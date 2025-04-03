from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
import os, glob
from time import sleep
import numpy as np
from bvbabel import fmr
import warnings
from scipy.ndimage import binary_dilation, binary_erosion, label
import nibabel as nb
import matplotlib.pyplot as plt
import matplotlib
from utils.roi import write_roi, read_roi
import glob, os, sys
from utils.expyriment_io_extras import tbvnetworkinterface
import logging
import ants
import dicom2nifti
import shutil



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
    fig, axes = plt.subplots(grid_size, grid_size, figsize=(10, 10))
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


class Window(QMainWindow):
    
    def __init__(self, parent=None):

        QMainWindow.__init__(self, parent)
        self.showed = 0
        self.setWindowTitle("NF ROI Preparation")
        self.resize(550, 400)
        self.top = 250
        self.left = 500
        self.width = 550
        self.height = 400
        self.setGeometry(self.left, self.top, self.width, self.height)
        self.create_main_frame()
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowMaximizeButtonHint)


    def set_log(self,path,filename):
        
        '''
        Function to log user's actions on both terminal and log file.
        The log file is opended in appending mode and saved in the rtRSA_output
        folder.
        
        Parameters
        ----------
        path: string
            path where the log file will be saved
        filename: string
            name of the log file
            
        Returns
        ----------
        rootLogger : RootLogger class
            logging object
        
        
        '''
        #create logging
        logFormatter = logging.Formatter("%(asctime)s   %(levelname)s    %(message)s")
        rootLogger = logging.getLogger()
        
        if not rootLogger.handlers:
            
            fileHandler = logging.FileHandler("{0}/{1}.log".format(path, filename))
            fileHandler.setFormatter(logFormatter)
            rootLogger.addHandler(fileHandler)
            
            consoleHandler = logging.StreamHandler()
            consoleHandler.setFormatter(logFormatter)
            rootLogger.addHandler(consoleHandler)
            rootLogger.setLevel(logging.INFO)
        
        return rootLogger


    def log_message(self, message, color='#d2d2d5'):

        # Get the current cursor
        cursor = self.log_window.textCursor()

        # Move the cursor to the end of the document
        cursor.movePosition(QTextCursor.End)

        # Save the current color (optional, if you want to restore it later)
        current_color = self.log_window.textColor()

        # Set the text color for the new message
        self.log_window.setTextColor(QColor(color))
        self.log_window.append(message)

        
        # Restore the previous text color
        self.log_window.setTextColor(current_color)

        # Set the cursor back to the end (optional)
        self.log_window.setTextCursor(cursor)

        #update also the log file with the same message TO DO add log
        #self.

    def openDirectoryDialog(self, msg, step=''):

        try:
            # Open the directory selection dialog
            directory = QFileDialog.getExistingDirectory(self, msg)

            # If a directory was selected, display its path in the line edit
            if directory:
                if step == 'SWD': # set working directory
                    self.directoryLineEdit.setText(directory)
                    self.log_message(f'Set working directory: {directory}')
                    self.wdir = directory
                    self.get_roi_files()
                if step == 'ROI-update':
                    self.roi_integration_dir.setText(directory)
                    self.log_message(f'Found ROI-integration directory: {directory}')

            else:
                self.log_message(f'No directory selected')


        except Exception as e:
            self.log_message(f'\n{str(e)}\n')
            return


    def openFileDialog(self, msg, filter_fmt, step=''):

        try:
            # Open the directory selection dialog
            file = QFileDialog.getOpenFileName(self, msg, filter=filter_fmt) # it returns a tuple, the first element is the filename

            # If a directory was selected, display its path in the line edit
            if file[0]:

                self.log_message(f'{msg}: {file[0]}')
                if step=='EPI':
                    self.fileLineEdit.setText(file[0])
                    self.epi_ref = file[0]
                elif step=='BVS':
                    self.bvsbutton.setEnabled(True)
                    self.roiFileLineEdit.setText(file[0])
                elif step=='ROI-update':
                    self.roiIntegrationButton.setEnabled(True)
                    self.currentRoiFile.setText(file[0])

            else:
                self.log_message(f'No file selected.')

        except Exception as e:
            self.log_message(f'\n{str(e)}\n')
            return

        return file


    def get_roi_files(self):

        file = glob.glob(f'{self.wdir}/EMONET.roi')
        found_emonet =False

        if file:
            self.emonet_roifile = file[0].replace('\\','/')
            self.log_message(f'Found ROI file: {self.emonet_roifile}')
            found_emonet = True
        else:
            self.log_message('EMONET.roi file not found in the current working directory')

        file = glob.glob(f'{self.wdir}/SUBCORT.roi')
        found_subcort = False

        if file:
            self.subcort_roifile = file[0].replace('\\','/')
            self.log_message(f'Found ROI file: {self.subcort_roifile}')
            found_subcort = True
        else:
            self.log_message('SUBCORT.roi file not found in the current working directory')

        if found_subcort and found_emonet:
            self.maskbutton.setEnabled(True)


    def mask_emonet_with_epi(self):

        # review nifti save (left and righht is flipped)

        self.log_message('\n'+'='*80)
        self.log_message('\nMasking Emonet ROI using EPI mask ... ')


        self.outdir = f'{self.wdir}/roi_opening{self.opening.text()}_lc{self.low_cutoff.text()}_uc{self.upper_cutoff.text()}_thr{self.thr.text()}'
        self.log_message(f'\nOutput directory: {self.outdir}')

        os.makedirs(self.outdir, exist_ok=True)

        self.file_logger = self.set_log(self.outdir, 'masking_info_.log')

        self.log_message(f'\nEPI masking parameters:')
        self.log_message(f'Lower CutOff: {self.low_cutoff.text()}')
        self.log_message(f'Upper CutOff: {self.upper_cutoff.text()}')
        self.log_message(f'Threshold: {self.thr.text()}')
        self.log_message(f'Opening Iterations: {self.opening.text()}')

        # create mean epi image
        fmr_hdr, data = fmr.read_fmr(self.epi_ref)

        mean_epi = np.mean(data, axis=3)

        # save mean image and mask as nifti
        nb.save(nb.Nifti1Image(mean_epi[::-1,:,], affine=np.eye(4)), f'{self.outdir}/mean_epi.nii.gz')

        epi_mask, threshold = heuristic_epi_mask(mean_epi,
                                                    lower_cutoff=float(self.low_cutoff.text()),
                                                    upper_cutoff=float(self.upper_cutoff.text()), 
                                                    exclude_zeros=True,
                                                    opening=float(self.opening.text()),
                                                    connected=True,
                                                    threshold_factor=float(self.thr.text()),
                                                    outdir=self.outdir)

        # Save mean epi mask
        coords = np.where(epi_mask[:,::-1,:] != 0)
        coords = np.array([[x,y,z] for x,y,z in zip(coords[0],coords[1],coords[2])])
        write_roi(f'{self.outdir}/epimask.roi', coords)

        self.log_message(f'EPI intensity threshold: {threshold}')
        self.log_message(f'Created EPI mask ROI file: epimask.roi')

        mask_mosaic_plot(mean_epi,epi_mask, f'{self.outdir}/epi_mask.jpg')

        self.log_message(f'\nMasking EMONET ROI recovering subcortical structures...')

        emonet = read_roi(self.emonet_roifile)
        subcort = read_roi(self.subcort_roifile)

        emo_mask = np.zeros(epi_mask.shape)
        for coord in emonet:
            emo_mask[coord[0],coord[1],coord[2]]=1

        emo_mask = emo_mask[:,::-1,:]
        nb.save(nb.Nifti1Image(emo_mask.astype(int)[::-1,:,], affine=np.eye(4)), f'{self.outdir}/emo_mask.nii.gz')

        subcort_mask = np.zeros(epi_mask.shape)
        for coord in subcort:
            subcort_mask[coord[0],coord[1],coord[2]]=1

        subcort_mask = subcort_mask[:,::-1,:]

        nb.save(nb.Nifti1Image(subcort_mask.astype(int)[::-1,:,], affine=np.eye(4)), f'{self.outdir}/subcort_mask.nii.gz')

        # mask emonet with epi mask
        masked_emonet = emo_mask*epi_mask
        nb.save(nb.Nifti1Image(masked_emonet.astype(int)[::-1,:,], affine=np.eye(4)), f'{self.outdir}/emo_mask_epi_masked.nii.gz')

        # add subcortical and merge
        masked_emonet_subcort = np.logical_or(masked_emonet, subcort_mask)
        nb.save(nb.Nifti1Image(masked_emonet_subcort.astype(int)[::-1,:,], affine=np.eye(4)), f'{self.outdir}/emo_mask_epi_masked_subcort.nii.gz')

        coords = np.where(masked_emonet_subcort[:,::-1,:] != 0)
        coords = np.array([[x,y,z] for x,y,z in zip(coords[0],coords[1],coords[2])])
        write_roi(f'{self.outdir}/emo_mask_epi_masked_subcort.roi', coords)

        self.log_message(f'Created EMONET masked ROI file: emo_mask_epi_masked_subcort.roi')

        mask_mosaic_plot(mean_epi,masked_emonet_subcort,f'{self.outdir}/emo_mask_epi_masked_subcort.jpg')

        self.roiFileLineEdit.setText(f'{self.outdir}/emo_mask_epi_masked_subcort.jpg')
        self.bvsbutton.setEnabled(True)


    def best_voxel_selection(self):

        self.log_message('\n'+'='*80)
        self.log_message('\nRunning Best Voxel Selection ...')

        try:
            TBV = tbvnetworkinterface.TbvNetworkInterface('localhost',55555)
        except Exception as e:
            self.log_message('\nCould not connect to TBV!')
            self.log_message(str(e))
            return

        # connect to TBV
        self.emonet_masked_file = self.roiFileLineEdit.text()
        outdir = os.path.dirname(self.emonet_masked_file)

        try:
            coords = read_roi(self.emonet_masked_file)

            self.tmap = [TBV.get_map_value_of_voxel(0,coord)[0] # it assumes that the right contrast is selected from the TBV gui
                                    for coord in coords]

            self.vol_dim = TBV.get_dims_of_functional_data()[0]

            #create 3D mask from functional coordinates
            vol_mask = np.zeros(self.vol_dim)

            #eliminate mask_thr% of voxels with the lowest activity level
            thr = (100-int(self.mask_perc.text()))/100
            num_excluded_voxels = np.round(thr*len(self.tmap)).astype(int)

            self.log_message(f'\nNumber of requested voxels : {len(self.tmap)-num_excluded_voxels}')
            
            flatten_mask = np.ones(len(self.tmap))

            idx = np.argsort(self.tmap) # sort in ascending order
            idx = idx[:num_excluded_voxels]
            flatten_mask[idx]=0

            for coord in coords:
                vol_mask[coord[0],coord[1],coord[2]]=1

            new_vol_mask, new_flatten_mask = remove_small_clusters(vol_mask,coords[np.logical_not(flatten_mask),:],int(self.min_clust_size.text()))

            self.sel_tmap = np.array(self.tmap)[new_flatten_mask]

            # save the tvalues and the roi coordinates:

            coords = np.where(new_vol_mask != 0)
            sel_func_coords = np.array([[x, y, z] for x, y, z in zip(coords[0], coords[1], coords[2])])

            print(self.sel_tmap)

            write_roi(f'{outdir}/NFTarget.roi',sel_func_coords)
            self.log_message(f'Number of selected voxels: {len(self.sel_tmap)}\n')
            self.log_message(f'T-value threshold: {np.min(self.sel_tmap[self.sel_tmap != 0]):.2}\n')
            self.log_message(f'NF Target ROI saved to file: {outdir}/NFTarget.roi')


        except Exception as e:
            self.log_message(print(e))

    def roi_update(self):

        self.log_message('\n' + '=' * 80)
        self.log_message('\nPerform across-session ROI integration ...\n')

        try:
            TBV = tbvnetworkinterface.TbvNetworkInterface('localhost', 55555)
        except Exception as e:
            self.log_message('\nCould not connect to TBV!')
            self.log_message(str(e))
            return


        # chekc files in the ROI-integration directory

        try:

            # -------------------------- ANTS transformation ses-01 to ses-03  ------------------------#

            self.log_message('\nPerform across-session registration (ANTS) ...')
            wdir = self.roi_integration_dir.text()
            self.log_message(f'Working directory: {wdir}')

            # transform roi and map from ses-01 to ses-03 using ANTS (relies on dicom2nifti)
            dicom2nifti.convert_directory(f'{wdir}/dcm/ses-01/', f'{wdir}/dcm/ses-01/', compression=True, reorient=True)
            dicom2nifti.convert_directory(f'{wdir}/dcm/ses-03/', f'{wdir}/dcm/ses-03/', compression=True, reorient=True)

            # rename NIFTI files
            file = glob.glob(f'{wdir}/dcm/ses-01/*nii.gz')[0]
            shutil.copyfile(file, f'{wdir}/dcm/ses-01/ses-01_ref.nii.gz')

            file = glob.glob(f'{wdir}/dcm/ses-03/*nii.gz')[0]
            shutil.copyfile(file, f'{wdir}/dcm/ses-03/ses-03_ref.nii.gz')

            ses1_ref = nb.load(f'{wdir}/dcm/ses-01/ses-01_ref.nii.gz')
            ses1_affine = ses1_ref.affine

            ses3_ref = nb.load(f'{wdir}/dcm/ses-03/ses-03_ref.nii.gz')
            ses3_affine = ses3_ref.affine

            # Copy correct affine transformation to the other files (map and roi mask)
            temp = nb.load(f'{wdir}/roi/ses-01/pos-neu_tmap.nii.gz').get_fdata()[::-1,:,:]
            nb.save(nb.Nifti1Image(temp, affine=ses1_affine), f'{wdir}/roi/ses-01/pos-neu_tmap_affine.nii.gz')

            temp = nb.load(f'{wdir}/roi/ses-01/roi_mask_5%.nii.gz').get_fdata()[::-1,:,:]
            nb.save(nb.Nifti1Image(temp, affine=ses1_affine), f'{wdir}/roi/ses-01/roi_mask_5%_affine.nii.gz')

            # perform Affine transformation using ANTS
            fixed = ants.image_read(f'{wdir}/dcm/ses-03/ses-03_ref.nii.gz')
            moving = ants.image_read(f'{wdir}/dcm/ses-01/ses-01_ref.nii.gz')
            fixed.plot(overlay=moving,
                       title='Before Registration')  # changed function ants/viz/plot.py, overlay_cmap="hot", overlay_alpha=0.5,
            mytx = ants.registration(fixed=fixed, moving=moving, type_of_transform='Affine')
            #print(mytx)
            warped_moving = mytx['warpedmovout']
            fixed.plot(overlay=warped_moving,
                       title='After Registration')

            mywarpedimage = ants.apply_transforms(fixed=fixed, moving=moving,
                                                  transformlist=mytx['fwdtransforms'], interpolator='bSpline')

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

            # Apply transformation to map and mask file
            roi_file = f'{wdir}/roi/ses-01/roi_mask_5%_affine.nii.gz'
            roi_img = ants.image_read(roi_file)
            mywarpedimage = ants.apply_transforms(fixed=fixed, moving=roi_img,
                                                  transformlist=mytx['fwdtransforms'],
                                                  interpolator='nearestNeighbor')
            ants.image_write(mywarpedimage, f'{wdir}/trf/ses-01_roi_2_ses-03_ref_affine.nii.gz')

            self.log_message('\nDone.\n')

            # -------------------------------------------- ROI integration ---------------------------------------------#

            self.log_message('\nStarting ROI integration ...\n')

            self.current_roi_file = self.currentRoiFile.text()

            cur_coords = read_roi(self.current_roi_file)

            cur_tmap = [TBV.get_map_value_of_voxel(0, coord)[0]
                         # it assumes that the right contrast is selected from the TBV gui
                         for coord in cur_coords]

            self.vol_dim = TBV.get_dims_of_functional_data()[0]

            # create 3D mask from functional coordinates
            cur_tmap_vol = np.zeros(self.vol_dim)

            self.log_message(f'Number of voxels of the current ROI: {len(cur_tmap)}\n')

            for i,coord in enumerate(cur_coords):
                cur_tmap_vol[coord[0],coord[1],coord[2]]=cur_tmap[i]

            # save map to nifti
            nb.save(nb.Nifti1Image(cur_tmap_vol[:,::-1,:], affine=ses3_affine), f'{wdir}/ses-03_roi_tmap.nii.gz' )
            self.log_message(f'Current ROI t-map saved to file: {wdir}/ses-03_roi_tmap.nii.gz\n')

            cur_tmap_vol = cur_tmap_vol[::-1,:,:] # since it was created from TBV coordinates

            # import new transformed map and coordinates as nifti and convert to TBV convention
            prev_tmap_vol = nb.load(f'{wdir}/trf/ses-01_map_2_ses-03_ref_affine.nii.gz').get_fdata()[::-1,::-1,:]
            prev_roi_mask = nb.load(f'{wdir}/trf/ses-01_roi_2_ses-03_ref_affine.nii.gz').get_fdata()[::-1,::-1,:]

            prev_trf_coords = np.where(prev_roi_mask[::-1,:,:] != 0)
            prev_trf_coords = np.array([[x, y, z] for x, y, z in zip(prev_trf_coords[0], prev_trf_coords[1], prev_trf_coords[2])])

            self.log_message(f'Number of voxels of the ses-01 (transformed) ROI: {np.sum(prev_roi_mask).astype(int)}\n')

            write_roi(f'{wdir}/ses-01_roi_2_ses-03_ref_affine.roi', prev_trf_coords)
            self.log_message(f'ses-01 (transformed) ROI saved to file: {wdir}/ses-01_roi_2_ses-03_ref_affine.roi\n')

            # mask transformed ses-01 tmap and save to nifti
            prev_tmap_vol = prev_tmap_vol * prev_roi_mask

            nb.save(nb.Nifti1Image(prev_tmap_vol[::-1,::-1,:], affine=ses3_affine), f'{wdir}/ses-01_trf_roi_tmap.nii.gz' )
            self.log_message(f'ses-01 (transfromed) ROI t-map saved to file: {wdir}/ses-01_trf_roi_tmap.nii.gz\n')

            # new ROI average dimension
            update_roi_dim = np.mean([len(prev_trf_coords),len(cur_tmap)]).astype(int)
            self.log_message(f'Max number of voxels of the updated ROI: {update_roi_dim}\n')

            # merge maps from to sessions with a sum to weight more the common areas
            # use effect size map cohen's d = t/sqrt(df_res+1)
            merged_map = cur_tmap_vol/np.sqrt(650 +1) + prev_tmap_vol/np.sqrt(1302 +1)
            #merged_map = cur_tmap_vol + prev_tmap_vol

            merged_map_flatten = merged_map[merged_map!=0]

            flatten_mask = np.zeros(len(merged_map_flatten))

            idx = np.argsort(merged_map_flatten)[::-1] # sort in descending order
            print(merged_map_flatten[idx[0]])
            print(merged_map_flatten[idx[-1]])

            idx = idx[:update_roi_dim]
            flatten_mask[idx] = 1

            # create 3D mask from functional coordinates\
            merged_coords = np.where(merged_map != 0)
            merged_coords = np.array([[x, y, z] for x, y, z in zip(merged_coords[0], merged_coords[1], merged_coords[2])])

            vol_mask = np.zeros(self.vol_dim)
            for i, coord in enumerate(merged_coords):
                vol_mask[coord[0], coord[1], coord[2]] = 1

            new_vol_mask, new_flatten_mask = remove_small_clusters(vol_mask,merged_coords[np.logical_not(flatten_mask),:],int(self.min_clust_size2.text()))

            # selected values from the current t-map
            sel_tmap = np.array(cur_tmap_vol[merged_map!=0])[new_flatten_mask]

            # save the tvalues and the roi coordinates:
            coords = np.where(new_vol_mask[::-1,:,:] != 0)
            sel_func_coords = np.array([[x, y, z] for x, y, z in zip(coords[0], coords[1], coords[2])])

            write_roi(f'{wdir}/NFTarget_updated.roi', sel_func_coords)
            self.log_message(f'Number of selected voxels: {len(sel_tmap)}\n')
            self.log_message(f'T-value threshold: {np.min(sel_tmap[sel_tmap != 0]):.2}\n')
            self.log_message(f'NF Target ROI saved to file: {wdir}/NFTarget_updated.roi')

            # save new roi to nifti
            nb.save(nb.Nifti1Image(new_vol_mask[::-1, ::-1, :].astype(int), affine=ses3_affine),f'{wdir}/NFTarget_updated.nii.gz')
            self.log_message(f'NF Target ROI saved to file: {wdir}/NFTarget_updated.nii.gz')


        except Exception as e:
            self.log_message(print(e))



    def create_main_frame(self):
        
        self.main_frame = QWidget()

        # Create a line edit to display the selected directory path
        self.fileLineEdit = QLineEdit(self)
        self.fileLineEdit.setPlaceholderText("FMR File")

        # Create a button to open the directory dialog
        self.browseButton0 = QPushButton('Load FMR', self)
        msg1 = "Select .fmr file" 
        self.browseButton0.clicked.connect(lambda: self.openFileDialog(msg1,'*.fmr', step='EPI'))

         # Create a line edit to display the selected directory path
        self.directoryLineEdit = QLineEdit(self)
        self.directoryLineEdit.setPlaceholderText("Working directory")

        # Create a button to open the directory dialog
        self.browseButton1 = QPushButton("Select Working Directory", self)
        msg2 = "Select Working Directory (where the .roi files are stored)" 
        self.browseButton1.clicked.connect(lambda: self.openDirectoryDialog(msg2, step='SWD'))

        hbox0 = QHBoxLayout()
        hbox0.setDirection(QBoxLayout.LeftToRight)        
        hbox0.addWidget(self.fileLineEdit)      
        hbox0.addWidget(self.browseButton0)

        hbox1 = QHBoxLayout()
        hbox1.setDirection(QBoxLayout.LeftToRight)        
        hbox1.addWidget(self.directoryLineEdit)      
        hbox1.addWidget(self.browseButton1)
        
        vbox1 = QVBoxLayout()
        vbox1.addLayout(hbox0)
        vbox1.addLayout(hbox1)  

        # Define heuristic threshold parameters
        param_box = QLabel(self)
        param_box.setText('Paramaters for heuristic EPI masking')   

        hbox2 = QHBoxLayout()
        hbox2.setDirection(QBoxLayout.LeftToRight)
        hbox2.addWidget(param_box)

        lower_cutoff_lb = QLabel(self)
        lower_cutoff_lb.setText('Lower CutOff')
        self.low_cutoff = QLineEdit(self)
        self.low_cutoff.setValidator(QDoubleValidator(0,1,2))
        self.low_cutoff.setText('0.2')

        upper_cutoff_lb = QLabel(self)
        upper_cutoff_lb.setText('Upper CutOff')
        self.upper_cutoff = QLineEdit(self)
        self.upper_cutoff.setValidator(QDoubleValidator(0,1,2))
        self.upper_cutoff.setText('0.85')

        thr_lb = QLabel(self)
        thr_lb.setText('Hist Threshold')
        self.thr = QLineEdit(self)
        self.thr.setValidator(QDoubleValidator(0,1,2))
        self.thr.setText('0.5')

        opening_lb = QLabel(self)
        opening_lb.setText('Opening Iter')
        self.opening = QLineEdit(self)
        self.opening.setValidator(QDoubleValidator(0,10,0))
        self.opening.setText('3')

        #Compute epi mask
        self.maskbutton = QPushButton("Mask EmoNet with EPI",self)
        self.maskbutton.setEnabled(False) 
        self.maskbutton.clicked.connect(self.mask_emonet_with_epi)

        hbox3 = QHBoxLayout()
        hbox3.setDirection(QBoxLayout.LeftToRight)        
        hbox3.addWidget(lower_cutoff_lb)
        hbox3.addWidget(self.low_cutoff)
        hbox3.addStretch()

        hbox3.addWidget(upper_cutoff_lb)
        hbox3.addWidget(self.upper_cutoff)
        hbox3.addStretch()

        hbox3.addWidget(thr_lb)
        hbox3.addWidget(self.thr)
        hbox3.addStretch()

        hbox3.addWidget(opening_lb)
        hbox3.addWidget(self.opening)
        hbox3.addStretch()

        hbox3.addWidget(self.maskbutton)
        hbox3.addStretch()

        vbox1.addLayout(hbox2)
        vbox1.addLayout(hbox3)

        group1 = QGroupBox('')
        group1.setLayout(vbox1)

        #-------------------------- Best Voxel Selection ------------------------#

        #run best voxel selection
        hbox4 = QHBoxLayout()
        hbox4.setDirection(QBoxLayout.LeftToRight) 

        param_box2 = QLabel(self)
        param_box2.setText('Paramaters for Best Voxel Selection') 
        hbox4.addWidget(param_box2)

        self.roiFileLineEdit = QLineEdit(self)
        self.roiFileLineEdit.setPlaceholderText("Masked EMONET ROI File")

        # Create a button to open the file dialog
        self.roiBrowseButton = QPushButton('Load ROI', self)
        msg3 = "Select EMONET .roi masked file to perform BVS"
        self.roiBrowseButton.clicked.connect(lambda: self.openFileDialog(msg3, '*.roi', step='BVS'))

        #run best voxel selection
        hbox5 = QHBoxLayout()
        hbox5.setDirection(QBoxLayout.LeftToRight)   
        hbox5.addWidget(self.roiFileLineEdit)
        hbox5.addStretch()
        hbox5.addWidget(self.roiBrowseButton)      

        mask_perc_lb = QLabel(self)
        mask_perc_lb.setText('Mask %')
        self.mask_perc = QLineEdit(self)
        self.mask_perc.setValidator(QDoubleValidator(0,100,0))
        self.mask_perc.setText('5')

        min_clust_lb = QLabel(self)
        min_clust_lb.setText('Min Cluster Size')
        self.min_clust_size = QLineEdit(self)
        self.min_clust_size.setValidator(QDoubleValidator(0,1000,0))
        self.min_clust_size.setText('50')

        crt_idx_lb = QLabel(self)
        crt_idx_lb.setText('TBV CTR Index [0-based]')
        self.ctr_idx = QLineEdit(self)
        self.ctr_idx.setValidator(QDoubleValidator(0,100,0))
        self.ctr_idx.setText('2')

        self.bvsbutton = QPushButton("Best Voxel Selection",self)
        self.bvsbutton.setEnabled(False) 
        self.bvsbutton.clicked.connect(self.best_voxel_selection)

        hbox6 = QHBoxLayout()
        hbox6.setDirection(QBoxLayout.LeftToRight)        
        hbox6.addWidget(mask_perc_lb)
        hbox6.addWidget(self.mask_perc)
        hbox6.addStretch()

        hbox6.addWidget(min_clust_lb)
        hbox6.addWidget(self.min_clust_size)
        hbox6.addStretch()

        hbox6.addWidget(crt_idx_lb)
        hbox6.addWidget(self.ctr_idx)
        hbox6.addStretch()
        hbox6.addWidget(self.bvsbutton)
        hbox6.addStretch()

        vbox2 = QVBoxLayout()
        vbox2.addLayout(hbox4)
        vbox2.addLayout(hbox5)
        vbox2.addLayout(hbox6)

        group2 = QGroupBox('')
        group2.setLayout(vbox2)

        #-------------------------- Integrate ROI across sessions ------------------------#

        param_box3 = QLabel(self)
        param_box3.setText('Inter-session ROI integration')

        # Create a line edit to display the selected directory path
        self.roi_integration_dir = QLineEdit(self)
        self.roi_integration_dir.setPlaceholderText("ROI-integration directory")
        # Create a button to open the directory dialog
        self.browseButton2 = QPushButton("Select ROI-integration directory", self)
        msg4 = "Select ROI-integration directory"
        self.browseButton2.clicked.connect(lambda: self.openDirectoryDialog(msg4, step='ROI-update'))

        self.currentRoiFile = QLineEdit(self)
        self.currentRoiFile.setPlaceholderText("Select the NFTarget.roi file from the current session.")

        # Create a button to open the file dialog
        self.roiBrowseButton2 = QPushButton('Load Current ROI', self)
        msg5 = "Select the NFTarget.roi file from the current session."
        self.roiBrowseButton2.clicked.connect(lambda: self.openFileDialog(msg5, '*.roi', step='ROI-update'))


        crt_idx_lb2 = QLabel(self)
        crt_idx_lb2.setText('TBV CTR Index [0-based]')
        self.ctr_idx2 = QLineEdit(self)
        self.ctr_idx2.setValidator(QDoubleValidator(0, 100, 0))
        self.ctr_idx2.setText('2')

        min_clust_lb2 = QLabel(self)
        min_clust_lb2.setText('Min Cluster Size')
        self.min_clust_size2 = QLineEdit(self)
        self.min_clust_size2.setValidator(QDoubleValidator(0, 1000, 0))
        self.min_clust_size2.setText('50')

        self.roiIntegrationButton = QPushButton("Update ROI", self)
        self.roiIntegrationButton.setEnabled(False)
        self.roiIntegrationButton.clicked.connect(self.roi_update)

        hbox7 = QHBoxLayout()
        hbox7.setDirection(QBoxLayout.LeftToRight)
        hbox7.addWidget(param_box3)

        hbox8 = QHBoxLayout()
        hbox8.setDirection(QBoxLayout.LeftToRight)
        hbox8.addWidget(self.roi_integration_dir)
        hbox8.addWidget(self.browseButton2)

        hbox9 = QHBoxLayout()
        hbox9.setDirection(QBoxLayout.LeftToRight)
        hbox9.addWidget(self.currentRoiFile)
        hbox9.addWidget(self.roiBrowseButton2)

        hbox10 = QHBoxLayout()
        hbox10.setDirection(QBoxLayout.LeftToRight)
        hbox10.addWidget(crt_idx_lb2)
        hbox10.addWidget(self.ctr_idx2)
        hbox10.addStretch()
        hbox10.addWidget(min_clust_lb2)
        hbox10.addWidget(self.min_clust_size2)
        hbox10.addStretch()
        hbox10.addWidget(self.roiIntegrationButton)

        vbox3 = QVBoxLayout()
        vbox3.addLayout(hbox7)
        vbox3.addLayout(hbox8)
        vbox3.addLayout(hbox9)
        vbox3.addLayout(hbox10)

        group3 = QGroupBox('')
        group3.setLayout(vbox3)

        #-------------------------- Define log window ------------------------#
        
        # Log window
        self.log_window = QTextEdit()
        self.log_window.setReadOnly(True)

        scrollArea = QScrollArea()
        scrollArea.setWidget(self.log_window)
        scrollArea.setWidgetResizable(True)

        #-------------------------- Set Window Layout ------------------------#

        vbox = QVBoxLayout()
        vbox.addWidget(group1)
        vbox.addWidget(group2)
        vbox.addWidget(group3)
        vbox.addWidget(scrollArea)

        self.main_frame.setLayout(vbox)  
        
        self.setCentralWidget(self.main_frame)

        self.setMinimumSize(vbox.sizeHint())


        self.main_frame.setLayout(vbox1)
        
        self.setCentralWidget(self.main_frame)


# Style settings

qss = """

QWidget { background: #0d0e0f;
} 

QMessageBox{ 
            background: #0d0e0f;
} 

QTextEdit {
            background: #0d0e0f;
            color: #d2d2d5;
            border: 2px solid  #0d0e0f;
            font: 14px;
} 
 
QGroupBox{ 
            background-color: #0d0e0f;
            border: 2px solid  #0d0e0f;
}

QPushButton{
            border: 1px solid black;
            border-radius: 2px;
            background-color: #404040;
            font: 14px;
            padding:4px;
            color: #d2d2d5;
}

QPushButton:hover {
            background-color: #595959;
}

QPushButton:disabled {
            color: #6e6e6e;
}

QLabel{     font: 14px; 
            color: #d2d2d5;
            background-color: #0d0e0f;
}


QLineEdit {  color: #d2d2d5 ;
            font: 14px;
            background: #2a2a2a;
            border: 1px ;  
            padding: 1px;
}

QScrollBar {
           width: 10px; 
           background:  #505050;

}


QScrollBar::handle {
            background:  #505050;
}

QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
                background: #0d0e0f;         /* Background color of the scrollbar area */
            }

"""

if __name__ == "__main__":
    app = QApplication([])
    app.setStyleSheet(qss)

    window = Window()
    window.show()
    sys.exit(app.exec())
    


   