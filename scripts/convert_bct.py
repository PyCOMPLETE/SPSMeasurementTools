import sys, os 
BIN=os.path.expanduser('../../') 
sys.path.append(BIN) 

import time
import numpy as np

from SPSMeasurementTools.timestamp_helpers import date_strings_interval
from SPSMeasurementTools import BCT


start_tstamp_unix=1429460800
end_tstamp_unix='Now'
data_folder = '/user/slops/data/SPS_DATA/OP_DATA/SPS_BCT/'
device_name = '31832'
filename_converted = 'bct_converted.txt'

print 'Looking for data in folder %s'%data_folder

if end_tstamp_unix=='Now':
	end_tstamp_unix = time.mktime(time.localtime())

try:
	with open(filename_converted, 'r') as fid:
		list_converted = fid.read().split('\n')
except IOError:
	list_converted = []

list_date_strings = date_strings_interval(start_tstamp_unix, end_tstamp_unix)

for date_string in list_date_strings:

	sdds_folder = data_folder + date_string + '/SPS.BCTDC.' + device_name + '@Acquisition/'

	print '\nSaving data in folder: %s'%sdds_folder 
	file_list = os.listdir(sdds_folder)
	for filename in file_list:
		tstamp_filename = int(float(filename.split('@')[-2]) / 1e9)
		if not(tstamp_filename > start_tstamp_unix and tstamp_filename < end_tstamp_unix):
			continue

		if filename in list_converted:
			continue

		try:
			complete_path = sdds_folder + filename
			print complete_path

			BCT.sdds_to_file(complete_path)
			with open(filename_converted, 'a+') as fid:
				fid.write(filename+'\n')
		except KeyError:#Exception as err:
			print 'Skipped:'
			print complete_path
			print 'Got exception:'
			print err
