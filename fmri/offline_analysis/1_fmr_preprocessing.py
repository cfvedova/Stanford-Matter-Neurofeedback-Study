'''Run within BV python console. This script create an fmr file from dicom and performs standard preprocessing steps'''


import glob, os
import math
import shutil

wdir = 'D:/MatterNeurofeedback/raw_data/MatterNF'
outdir = 'D:/MatterNeurofeedback/derivatives/rawdata_bv'
sub = 'sub-07'
loc_ser_nr1 = '17'
loc_ser_nr2 = '19'

loc_ser_num = [loc_ser_nr1, loc_ser_nr2]
NR_SLICES = 72
IN_PLANE_RESOLUTION = (110, 110)
mosaic_row =990
mosaic_col =990
HPF_CUTOFF = 0.009

# create temporary directory for the dicom files
if os.path.exists(f'{wdir}/temp'):
    shutil.rmtree(f'{wdir}/temp')

os.makedirs(f'{wdir}/temp', exist_ok=True)

# creating output directory for this subject
subdir = f'{outdir}/{sub}/'
os.makedirs(subdir, exist_ok=True)

os.makedirs(f'{subdir}/ses-01/', exist_ok=True)

procdir = f'{subdir}/ses-01/func/'
os.makedirs(procdir, exist_ok=True)

fmr_names = [f'{sub}_ses-01_dir-AP_task-localiser3_run-03', f'{sub}_ses-01_dir-AP_task-localiser4_run-04']


for i, cur_ser_nr in enumerate([loc_ser_nr1, loc_ser_nr2]):

    dcm_format = f'00*_{cur_ser_nr.zfill(6)}_000*'

    dicom_files = glob.glob(f'{wdir}/{sub}/ses-01/tbv/*/{dcm_format}')
    print(f'\nWorking on series number {cur_ser_nr}')
    print(f'\nFound {len(dicom_files)} files.')

    # copy the dicom files for the current run to a temporary folder to avoid renaming the original files
    for dcm in dicom_files:
        shutil.copy(dcm,f'{wdir}/temp/{os.path.basename(dcm)}')

    first_dcm = f'{wdir}/temp/001_{cur_ser_nr.zfill(6)}_000001.dcm'
    print('\nFirst dicom: ' + first_dcm)

    doc = bv.create_mosaic_fmr(first_dcm.replace("\\", "/"), 660, 0, False, NR_SLICES, fmr_names[i], False,
                                        mosaic_row, mosaic_col, IN_PLANE_RESOLUTION[0], IN_PLANE_RESOLUTION[1], 2,
                                         procdir)
    doc.save_as(f'{procdir}/{fmr_names[i]}')

    doc.close()

    print('\nFile Saved.')
    path_run = f'{procdir}/{fmr_names[i]}.fmr'

    # 1// Correct Slice Timing
    print('\nStart correcting slice time for {}'.format(path_run))
    docFMR = bv.open(path_run)
    docFMR.correct_slicetiming_using_timingtable(1)  # cubic spline (recommended), check subject sub-08
    Fnme_newFMR = docFMR.preprocessed_fmr_name
    docFMR.close()
    print('\nDone with correcting slice timing'.format(path_run))

    if i == 0:
        MOCO_REF_VOL = Fnme_newFMR

    print('\nStart correcting motion for {}'.format(path_run))

    # 2// Motion Correction
    docFMR = bv.open(Fnme_newFMR)
    docFMR.correct_motion_to_run_ext(MOCO_REF_VOL, 0, 2, 1, 100, 1, 1)
    Fnme_newFMR = docFMR.preprocessed_fmr_name
    docFMR.close()
    print('\nDone with correcting motion'.format(path_run))

    # 3// High Pass Filtering
    print('\nStart HPF for {}'.format(path_run))
    docFMR=bv.open(Fnme_newFMR)
    docFMR.filter_temporal_highpass_fft(HPF_CUTOFF,'Hz')
    docFMR.close()

