'''

Create MDM files for FFX analysis (of the 2 localiser runs of session 1) in BV

This script will MDM files (a file containing a list of single SDM files) but first changes the order of the SDM conditions
(they might be different due to randomisation in the PRT).

NOTE: Currently, only the change of the condition order and zscoring of the SDM is performed. MDM creation was done via BV GUI.
Run the FFX muli-run GLM from BV GUI: z-score, SPST, AR2 using the zscored SDMs

'''

import numpy as np
from bvbabel import prt, sdm

def reorder_sdm_conditions(sdm_file, cond_order):

    hdr, sdm_data = sdm.read_sdm(sdm_file)

    if sdm_data[0]['NameOfPredictor'] != cond_order[0]:
        print(f'Changing condition order of file {sdm_file}')

        sdm_data_sorted = [sdm_data[1]] + [sdm_data[0]] + sdm_data[2:]
        sdm.write_sdm(sdm_file,hdr,sdm_data_sorted)

wdir = 'D:/MatterNeurofeedback/derivatives/rawdata_bv'

sub = 'sub-12'
ses = 1
RUNS = ['2','3']

cond_order = ["EmoRecall-Neutral", "EmoRecall-Positive"]

FMR = f'{wdir}/{sub}/ses-0{ses}/func/{sub}_ses-0{ses}_dir-AP_task-localiser3_run-03_SCCTBL_3DMCTS_LTR_THPFFT0.0090Hz_SD3DSS3.60mm.fmr'
#doc = bv.open(FMR)

#doc.clear_multistudy_glm_definition()

print('Creating .MDM')
    
for run in RUNS:

    fmr_file =  f'{wdir}/{sub}/ses-0{ses}/func/{sub}_ses-0{ses}_dir-AP_task-localiser{run}_run-0{run}_SCCTBL_3DMCTS_LTR_THPFFT0.0090Hz_SD3DSS3.60mm.fmr'
    sdm_file = f'{fmr_file[:-4]}_z.sdm'

    reorder_sdm_conditions(sdm_file, cond_order)
    #doc.add_study_and_dm(fmr_file, sdm_file)

#doc.save_multistudy_glm_definition_file(f'{sub}_ses-0{ses}_STC_N-2_SPST_ZT_AR-2.mdm')

# TO DO: Add saving of the MDM and creation of the GLM folder
# FFX mulirun GLM: z-score, SPST, AR2 using the zscored sdms