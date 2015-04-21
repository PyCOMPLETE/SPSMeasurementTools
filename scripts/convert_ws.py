import numpy as np
from SPSMeasurementTools import WireScans

start_time = '2015_04_13 07:00:00'
#end_time = '2015_04_22 17:00:00'
end_time = 'Now'

WireScans.make_mat_files(start_time, end_time)
WireScans.make_pickle(False)
