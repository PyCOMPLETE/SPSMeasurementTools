import sys, os 

import numpy as np
from SPSMeasurementTools import Pressures

start_time = '2015_04_13 07:00'
end_time = '2015_04_20 07:00'

#Pressures.csv_to_mat_gauges()
#Pressures.make_cycle_mat_files()
Pressures.make_pickle(SPSuser_blacklist = ['SFTPRO3'])
