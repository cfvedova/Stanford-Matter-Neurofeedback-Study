import os 
from expyriment_stash.extras.expyriment_io_extras import tbvnetworkinterface


def extrasession_coreg(ses1_dcm_dir,ser1,ser2):
    
    tbv = tbvnetworkinterface.TbvNetworkInterface('localhost',55555)
    ses2_dcm_dir = tbv.get_watch_folder()[0][:-1]

    print(ses2_dcm_dir)
    os.chdir(os.getcwd()+'/utils')
    os.system("matlab -minimize -nosplash -nodesktop -r spm_extrasession_coreg('"+ses1_dcm_dir+\
    	"','"+ses2_dcm_dir+"',"+ser1+","+ser2+")")
    
    print('Switching to matlab engine...')
    
    
