import numpy as np
from SPSMeasurementTools import FBCT

start_time = '2015_04_13 07:00:00'
end_time = '2015_04_13 11:00:00'
#end_time = 'Now'

FBCT.make_mat_files(start_time, end_time, device_name='31450')
