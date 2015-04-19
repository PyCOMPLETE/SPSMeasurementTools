import sys, os 
BIN=os.path.expanduser('../../') 
sys.path.append(BIN) 

import numpy as np
from SPSMeasurementTools import BCT

start_time = '2015_04_13 07:00'
end_time = '2015_04_13 11:00'

BCT.make_mat_files(start_time, end_time, device_name='31832')
BCT.make_pickle()
