import csv
import numpy as np
import scipy.io as sio
import time
import os
import matplotlib.pyplot as pl

'''
filename_FRQ_trim = None
if len(t_stamps_QPV_trim) != 0:
	diff_t_stamps = t_stamps_FRQ_trim - t_stamp_bct
	ind_nearest_t = np.argmin(np.abs(diff_t_stamps))
	if diff_t_stamps[ind_nearest_t] <= 0:
		t_stamp_trim_file = t_stamps_FRQ_trim[ind_nearest_t]
	else:
		t_stamp_trim_file = t_stamps_FRQ_trim[ind_nearest_t-1]

	filename_QPV_trim = (trim_data_mat_folder + SPS_user + '/' + trim_mat_file_prefix + SPS_user +
						 '_%d_QPV.mat'%t_stamp_trim_file)
					 
	curr_QPV_trim = SPSc.TrimData(filename_QPV_trim)
	ind_chroma = np.where((curr_QPV_trim.time_vect*1e-3 - injection_delay_to_cycle_start) \
						 > scan_time)[0][0]
	chroma = curr_QPV_trim.value_vect[ind_chroma]
	
	tau, bct0 = curr_bct.get_lifetime(start_scan_time, fit_window)

	if chroma not in bct_dict.keys():
		bct_dict[chroma] = []
		tau_dict[chroma] = []
	bct_dict[chroma].append(curr_bct.total_intensity)
	tau_dict[chroma].append(tau)
'''

import timestamp_helpers as th

class TrimDataSet(object):

	def __init__(self, trim_file_list):
		self.trim_obj_dict = {}
		for file in trim_file_list:
			trim_obj = TrimData(file)
			self.trim_obj_dict[trim_obj.timestamp_unix] = trim_obj
		
	def get_last_trim_before(self, t):
		
		if type(t) is str:
			tstamp_unix = th.localtime2unixstamp(t)
		else:
			tstamp_unix = t
		trim_t_stamps = np.sort(np.int_(self.trim_obj_dict.keys()))
		trim_t_stamps = trim_t_stamps[trim_t_stamps>0]
		indx_before_t = np.searchsorted(trim_t_stamps - tstamp_unix,0) - 1
		if indx_before_t < 0:
			print 'ERROR: The requested time is before the first trim!'
			return None
		else:
			return self.trim_obj_dict[trim_t_stamps[indx_before_t]]	
		

class TrimData(object):

	def __init__(self, complete_path):
		
		if complete_path.endswith('.mat'):
			dict_trim_data = sio.loadmat(complete_path)
		else:
			print('Unknown file extension for TrimData file. Should be ' +
				  '.mat')

		self.timestamp_unix = dict_trim_data['timestamp'][0][0]
		self.value_vect = np.squeeze(dict_trim_data['data_value_vect'])
		self.time_vect = np.squeeze(dict_trim_data['data_time_vect'])
		# if the first entry in time_vect is negative, the data is provided using Injection time 
		if self.time_vect[0]<0:
			self.cycletime_vect = self.time_vect - self.time_vect[0]
		else:
			self.cycletime_vect = None
			print 'WARNING: The trim data is for a beam process or is given in cycle time'
		
	def get_value_at(self, t_after_injection):
		
		return np.interp(t_after_injection, self.time_vect, self.value_vect)


def make_mat_files(trim_data_file, SPSuser, trim_variable=None, trim_data_mat_folder='trim_data'):

	print 'converting file "' + trim_data_file + '"'
	list_trim_hist = []
	with open(trim_data_file, 'r') as cfile:
		spr = csv.reader(cfile)
		for row in spr:
			list_trim_hist.append(row)

	if not trim_variable:
		trim_variable = list_trim_hist[0][0].replace('/','_')
	
	# check if data is provided using Injection time
	if not float(list_trim_hist[2][0]):
		print('ERROR: The trim history must be provided using Injection Time as reference !')

	# Build dictionary and dump to mat file.
	for trim_set_n in xrange(0, len(list_trim_hist[0]), 2):
		time_list = []
		trim_value_list = []
			
		for trim_point_n in xrange(2, len(list_trim_hist)):
			# Remove empty entries.
			if list_trim_hist[trim_point_n][trim_set_n] == '':
				break
			time_list.append(list_trim_hist[trim_point_n][trim_set_n])
			trim_value_list.append(list_trim_hist[trim_point_n][trim_set_n+1])

		timestamp_str = ((list_trim_hist[0][trim_set_n]).split('@'))[-1]
		data_time_vect = np.float_(np.array(time_list))
		data_value_vect = np.float_(np.array(trim_value_list))
		
		try:
			timestamp_unix = time.mktime(time.strptime(timestamp_str, '%Y-%m-%d %H:%M:%S'))
		except ValueError:
			timestamp_unix = '0'
		filename = SPSuser + '_' + str(int(timestamp_unix)) + '_' + trim_variable + '.mat'

		out_complete_path = trim_data_mat_folder + '/' + SPSuser + '/'
		if not os.path.isdir(out_complete_path):
			print 'I create folder: ' + out_complete_path
			os.makedirs(out_complete_path)

		sio.savemat(out_complete_path + filename, {
			'timestamp' : timestamp_unix,
			'data_time_vect' : data_time_vect,
			'data_value_vect' : data_value_vect},
			oned_as='row')
