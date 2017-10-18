from SPSMeasurementTools import TRIM
import glob

SPSuser = 'LHC3'

for file in glob.glob('trim_history/*_' + SPSuser + '.csv'):
    TRIM.make_mat_files(file, SPSuser)
