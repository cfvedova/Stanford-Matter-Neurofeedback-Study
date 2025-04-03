import os, shutil, glob
from utils.prt import read_prt

sub_name = input('Insert the subject name: ')
ses = input('Insert the session number: ')

subdir_stim = f'C:/Users/assun/Documents/GitHub/MatterNeurofeedbackStudy/example_data/stim_prep/{sub_name}/ses-0{ses}'
outdir = f'C:/Users/assun/Documents/GitHub/MatterNeurofeedbackStudy/example_data/tbv_prep/{sub_name}'
temp_dir = 'C:/Users/assun/Documents/GitHub/MatterNeurofeedbackStudy/TBVData/temp_ctr'

# Create a folder for this subject in data_TBV
subdir_ctr = f'{outdir}/ses-0{ses}/TBVFiles/ctr'

NFruns = sorted(glob.glob(f'{subdir_stim}/runNF*/runNF*.txt'))

for i, run_order in enumerate(NFruns):

    first_image =''
    with open(run_order, 'r') as f:
       first_image = f.readline()


    if 'scrambled' in first_image:
        print(f'{subdir_ctr}/nf{i+1}.ctr')
        shutil.copyfile(f'{temp_dir}/nf_ctrl-pos.ctr', f'{subdir_ctr}/nf{i+1}.ctr')
    else:
        print(f'{subdir_ctr}/nf{i+1}.ctr')
        shutil.copyfile(f'{temp_dir}/nf_pos-ctrl.ctr', f'{subdir_ctr}/nf{i+1}.ctr')


LOCruns = sorted(glob.glob(f'{subdir_stim}/Localiser*.txt'))

for i, run_order in enumerate(LOCruns):

    first_image = ''
    with open(run_order, 'r') as f:
        first_image = f.readline()

    if 'neutral' in first_image:
        print(f'{subdir_ctr}/loc{i+1}.ctr')
        shutil.copyfile(f'{temp_dir}/loc_neu-pos.ctr', f'{subdir_ctr}/loc{i + 1}.ctr')
    else:
        print(f'{subdir_ctr}/loc{i+1}.ctr')
        shutil.copyfile(f'{temp_dir}/loc_pos-neu.ctr', f'{subdir_ctr}/loc{i + 1}.ctr')

TRANSruns = sorted(glob.glob(f'{subdir_stim}/Transfer*.txt'))

for i, run_order in enumerate(TRANSruns):

    first_image = ''
    with open(run_order, 'r') as f:
        first_image = f.readline()

    if 'neutral' in first_image:
        print(f'{subdir_ctr}/trans{i+1}.ctr')
        shutil.copyfile(f'{temp_dir}/trans_ctrl-pos.ctr', f'{subdir_ctr}/trans{i + 1}.ctr')
    else:
        print(f'{subdir_ctr}/trans{i+1}.ctr')
        shutil.copyfile(f'{temp_dir}/trans_pos-ctrl.ctr', f'{subdir_ctr}/trans{i + 1}.ctr')



