import numpy as np
from SPSMeasurementTools import MR
import imp

conf = imp.load_source('config', 'conf.py')
MR.make_mat_files(conf.time_start, conf.time_end, SPSuser=conf.sps_user)
MR.make_pickle()
