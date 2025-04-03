# -*- coding: utf-8 -*-
"""
Created on Mon Jan 23 16:19:00 2023

@author: assun
"""
import glob, os, pickle
from .roi import read_roi, write_roi
import numpy as np
import nibabel as nb
from .rdm_utils import plot_rdm

def create_extrasession_roi_wrong(sub_dir, rtRSA_obj):

    
    #assuming 
    # (assuming sub_dir = /....dicom_folder...../TBVFiles/rtRSA_output)
    idx =[i for i, x in enumerate(sub_dir) if x == '/']
    print('Sub_dir: ',sub_dir)
    img1 = glob.glob(sub_dir[:idx[-1]]+'/ExtrasessionCoreg/ses1*.nii')[0]
    img2 = glob.glob(sub_dir[:idx[-1]]+'/ExtrasessionCoreg/ses2*.nii')[0]
    
    img1 = nb.load(img1)
    img2 = nb.load(img2)
    
    dimx = rtRSA_obj.vol_dim[0]
    dimy= rtRSA_obj.vol_dim[1]
    dimz = rtRSA_obj.vol_dim[2]
    
    #coords of the original VOI in the session1 space
    coords1 = read_roi(sub_dir+'/selected_voxels.roi')
    
    affine1 = img1.affine
    affine2 = img2.affine
    
    spm_trf = np.loadtxt(sub_dir[:idx[-1]]+'/ExtrasessionCoreg/ses2_to_ses1.mat')
    spm_trf_inv = np.linalg.inv(spm_trf)
    trf_mat = np.linalg.inv(affine2) @ spm_trf_inv @ affine1 #this should be the right one
    
    coords2_from_aff =[]
    for coord in coords1:
        coords2_from_aff.append(np.squeeze(np.dot(trf_mat,np.hstack((coord,1)).reshape(-1,1))))
    
    coords2_from_aff_round = np.round(np.array(coords2_from_aff))
    coords2_from_aff_unique, index,inverse, count = np.unique(coords2_from_aff_round,axis=0,return_counts=True, return_index=True,return_inverse=True)
    
    coords2_from_aff_unique = coords2_from_aff_unique.astype(int)[:,:3]
    
    write_roi(sub_dir+'/selected_voxels_trf.roi', coords2_from_aff_unique)
    print('Number of selected voxels session1: ',len(coords1))
    print('Number of selected voxels after affine transformation: ',len(coords2_from_aff_unique))
#%%  
    patterns_ses1_to_ses2=[]
    patterns_ses1 = np.array(rtRSA_obj.sel_base_patterns)
    
    for i,orig_idx in enumerate(index): # index of ses1 space (forst occurence)
        
        if count[i]== 2:
            #idx_ses1 = np.where((coords1 == coords1[orig_idx,:]).all(axis=1))
            #idx_ses1 = np.array([orig_idx,orig_idx+1])
            idx_ses1 = np.where(inverse == i)[0]
            temp = patterns_ses1[:,idx_ses1]
            temp_mean = np.mean(temp,axis=1) 
            patterns_ses1_to_ses2.append(temp_mean)
            
        else:
            patterns_ses1_to_ses2.append(patterns_ses1[:,orig_idx])
            
    patterns_ses1_to_ses2 = np.array(patterns_ses1_to_ses2).T
    
    #store old patterns and coords
    #pickle.dump(patterns_ses1,open(wdir+'/sel_base_patterns_ses1.pkl','wb'))           
    #pickle.dump(rtRSAObj.sel_func_coords,open(wdir+'/sel_func_coords_ses1.pkl','wb'))  
    
    RDM = np.corrcoef(patterns_ses1_to_ses2)
       
    plot_rdm(RDM, rtRSA_obj.conditions,'RDM trf',sub_dir[:idx[-1]]+'/ExtrasessionCoreg/RDM_trf.jpg')
       
    #save rdm and new transformed patterns 
    rtRSA_obj.RDM = 1-RDM #the original rtRSA_obj is also updated         
    
    rtRSA_obj.sel_base_patterns = patterns_ses1_to_ses2
    rtRSA_obj.sel_func_coords = coords2_from_aff_unique
    #compute the representational space at the first NF run 
    rtRSA_obj.mds()
    rtRSA_obj.save(sub_dir)
    
def create_extrasession_roi(sub_dir, rtRSA_obj):

    
    #assuming 
    # (assuming sub_dir = /....dicom_folder...../TBVFiles/rtRSA_output)
    idx =[i for i, x in enumerate(sub_dir) if x == '/']
    print('Sub_dir: ',sub_dir)
    img1 = glob.glob(sub_dir[:idx[-1]]+'/ExtrasessionCoreg/ses1*.nii')[0]
    img2 = glob.glob(sub_dir[:idx[-1]]+'/ExtrasessionCoreg/ses2*.nii')[0]
    
    img1 = nb.load(img1)
    img2 = nb.load(img2)
    
    dimx = rtRSA_obj.vol_dim[0]
    dimy= rtRSA_obj.vol_dim[1]
    dimz = rtRSA_obj.vol_dim[2]

    #this additional transformation is needed if the extrasession registration is computed using SPM
    #to match the coordinates space conventions between SPM (LAS+) and TBV (LPS+)
    las_to_lps_mtx = np.array([[1,0,0,0],
                           [0,-1,0,dimy-1], # flip y axis (for 0 based coordinates)
                           [0,0,1,0],
                           [0,0,0,1]])
    
    #coords of the original VOI in the session1 space
    coords1 = read_roi(sub_dir+'/selected_voxels.roi')
    
    affine1 = img1.affine
    affine2 = img2.affine
    
    spm_trf = np.loadtxt(sub_dir[:idx[-1]]+'/ExtrasessionCoreg/ses2_to_ses1.mat')
    spm_trf_inv = np.linalg.inv(spm_trf)
    trf_mat = las_to_lps_mtx @ np.linalg.inv(affine2) @ spm_trf_inv @ affine1 @ np.linalg.inv(las_to_lps_mtx)
    
    coords2_from_aff =[]
    for coord in coords1:
        coords2_from_aff.append(np.squeeze(np.dot(trf_mat,np.hstack((coord,1)).reshape(-1,1))))
    
    coords2_from_aff_round = np.round(np.array(coords2_from_aff))
    coords2_from_aff_unique, index,inverse, count = np.unique(coords2_from_aff_round,axis=0,return_counts=True, return_index=True,return_inverse=True)
    
    coords2_from_aff_unique = coords2_from_aff_unique.astype(int)[:,:3]
    
    write_roi(sub_dir+'/selected_voxels_trf.roi', coords2_from_aff_unique)
    print('Number of selected voxels session1: ',len(coords1))
    print('Number of selected voxels after affine transformation: ',len(coords2_from_aff_unique))
#%%  
    patterns_ses1_to_ses2=[]
    patterns_ses1 = np.array(rtRSA_obj.sel_base_patterns)
    
    for i,orig_idx in enumerate(index): # index of ses1 space (forst occurence)
        
        if count[i]== 2:
            #idx_ses1 = np.where((coords1 == coords1[orig_idx,:]).all(axis=1))
            #idx_ses1 = np.array([orig_idx,orig_idx+1])
            idx_ses1 = np.where(inverse == i)[0]
            temp = patterns_ses1[:,idx_ses1]
            temp_mean = np.mean(temp,axis=1) 
            patterns_ses1_to_ses2.append(temp_mean)
            
        else:
            patterns_ses1_to_ses2.append(patterns_ses1[:,orig_idx])
            
    patterns_ses1_to_ses2 = np.array(patterns_ses1_to_ses2).T
    
    #store old patterns and coords
    #pickle.dump(patterns_ses1,open(wdir+'/sel_base_patterns_ses1.pkl','wb'))           
    #pickle.dump(rtRSAObj.sel_func_coords,open(wdir+'/sel_func_coords_ses1.pkl','wb'))  
    
    RDM = np.corrcoef(patterns_ses1_to_ses2)
       
    plot_rdm(RDM, rtRSA_obj.conditions,'RDM trf',sub_dir[:idx[-1]]+'/ExtrasessionCoreg/RDM_trf.jpg')
       
    #save rdm and new transformed patterns 
    rtRSA_obj.RDM = 1-RDM #the original rtRSA_obj is also updated         
    
    rtRSA_obj.sel_base_patterns = patterns_ses1_to_ses2
    rtRSA_obj.sel_func_coords = coords2_from_aff_unique
    #compute the representational space at the first NF run 
    rtRSA_obj.mds()
    rtRSA_obj.save(sub_dir)
    
