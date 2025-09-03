# -*- coding: utf-8 -*-
"""
Created on Wed Jun 15 11:06:08 2022

@author: aciarlo@unisa.it
"""


import numpy as np



def write_roi(filename, coords):
    '''

    Parameters
    ----------
    filenames : string
        output filename
    coords : numpy array
        functional coordinates 

    Returns
    -------
    None.

    '''
    
    #to be sure that the coordinates are int
    coords = coords.astype(int)
    
    from_slice = min(coords[:,2]) + 1 
    left = min(coords[:,0]) + 1 
    right = max(coords[:,0]) + 2
    top = min(coords[:,1]) + 1
    bottom = max(coords[:,1]) + 2
    num_voxels = coords.shape[0]
    
    # Read non-empty lines of the input text file
    with open(filename, 'w') as f:
      
        f.write("FileVersion:           5\n")
        f.write("\n")
        
        
        f.write("SaveVoxelsInROIs:      1\n")
        f.write("\n")
        
        f.write("SaveSortedVoxelList:   0\n")
        f.write("\n")
        
        f.write("SaveROIMaxPSC:         0\n")
        f.write("\n")
        
        f.write("NrOfTCPlots:           1\n")
        f.write("\n")
        
        f.write("NrOfTCs:               1\n")
        f.write("FromSlice:             {}\n".format(from_slice))
        f.write("Left:                  {}\n".format(left))
        f.write("Right:                 {}\n".format(right))
        f.write("Top:                   {}\n".format(top))
        f.write("Bottom:                {}\n".format(bottom))
        f.write("NrOfVoxels:            {}\n".format(num_voxels))

        
        for c in coords:
            f.write(' '+str(c[0])+'  '+str(c[1])+'  '+str(c[2])+'\n')
            
        f.write('\n')    
        
        

def read_roi(filename): 
    
    '''

    Parameters
    ----------
    filenames : string
        output filename

    Returns
    -------
    coords : numpy array
        functional coordinates
    

    '''     
    
    
    with open(filename, 'r') as f:
       lines = [line for line in f] 
    coords = []
    for i in range(17,len(lines)-1):
       coords.append(np.array(lines[i][1:-1].split('  ')).astype(int))
    
    return np.array(coords)   



def read_roi2(filename): 
    
    '''

    Parameters
    ----------
    filenames : string
        output filename

    Returns
    -------
    coords : numpy array
        functional coordinates
    

    '''     
    
    
    with open(filename, 'r') as f:
       lines = [line for line in f] 
    coords = []
    for i in range(17,len(lines)-1):
        coords.append(np.array(lines[i].split('\t')[:-1]).astype(int))

    
    return np.array(coords)   
