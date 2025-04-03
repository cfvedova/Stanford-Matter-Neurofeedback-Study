function spm_extrasession_coreg(ses1_dcm_dir,ses2_dcm_dir,ser1,ser2, outdir)

tic

mkdir([outdir '/ExtrasessionCoreg'])

spm('defaults', 'FMRI');
spm_jobman('initcfg');

%convert reference volume of session1 to nifti
matlabbatch{1}.spm.util.import.dicom.data = {[ses1_dcm_dir '/001_' num2str(ser1,'%06.f') '_000001.dcm']};
matlabbatch{1}.spm.util.import.dicom.root = 'flat';
matlabbatch{1}.spm.util.import.dicom.outdir = {[outdir '/ExtrasessionCoreg']};
matlabbatch{1}.spm.util.import.dicom.protfilter = '.*';
matlabbatch{1}.spm.util.import.dicom.convopts.format = 'nii';
matlabbatch{1}.spm.util.import.dicom.convopts.meta = 0;
matlabbatch{1}.spm.util.import.dicom.convopts.icedims = 0;
                                          
spm_jobman('run',matlabbatch);
clear matlabbatch
%rename nifti to ses1*
nii1 = dir([outdir '/ExtrasessionCoreg/f*.nii']);
movefile([nii1.folder '/' nii1.name], [nii1.folder '/ses1' nii1.name(regexp(nii1.name, '-', 'once'):end)])

%convert reference volume of session1 to nifti
matlabbatch{1}.spm.util.import.dicom.data = {[ses2_dcm_dir '/001_' num2str(ser2,'%06.f') '_000001.dcm']};
matlabbatch{1}.spm.util.import.dicom.root = 'flat';
matlabbatch{1}.spm.util.import.dicom.outdir = {[outdir '/ExtrasessionCoreg']};
matlabbatch{1}.spm.util.import.dicom.protfilter = '.*';
matlabbatch{1}.spm.util.import.dicom.convopts.format = 'nii';
matlabbatch{1}.spm.util.import.dicom.convopts.meta = 0;
matlabbatch{1}.spm.util.import.dicom.convopts.icedims = 0;
                                          
spm_jobman('run',matlabbatch);
clear matlabbatch

%rename nifti to ses2*
nii2 = dir([outdir '/ExtrasessionCoreg/f*.nii']);
movefile([nii2.folder '/' nii2.name], [nii2.folder '/ses2' nii2.name(regexp(nii2.name, '-', 'once'):end)])

nii1 = dir([outdir '/ExtrasessionCoreg/ses1*.nii']);
nii1 = [nii1.folder '/' nii1.name];
nii2 = dir([outdir '/ExtrasessionCoreg/ses2*.nii']);
nii2 = [nii2.folder '/' nii2.name];

%initialise spm figure for final display
fig = spm_figure('GetWin','Graphics');
%compute coregistration between ses1 and ses2
flags.sep = [4,2];
flags.params = [0 0 0 0 0 0];
flags.cost_fun = 'ncc';
p = spm_coreg(nii1,nii2,flags);
m = inv(spm_matrix(p(:)'));

chdir([outdir '/ExtrasessionCoreg'])
%save matrix as ascii file
save -ascii ses2_to_ses1.mat m
toc

% reslice map and region
end