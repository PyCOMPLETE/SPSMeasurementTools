import csv
import numpy as np
import scipy.io as sio
import time
import os
import timestamp_helpers as th
import matplotlib.pyplot as pl
import timestamp_helpers as th

class TrimDataSet(object):

	def __init__(self, trim_file_list, min_time=None, max_time=None):
		if type(min_time) is str:
			min_time = th.localtime2unixstamp(min_time)
		if type(max_time) is str:
			max_time = th.localtime2unixstamp(max_time)
		self.trim_obj_dict = {}
		for file in trim_file_list:
			trim_obj = TrimData(file)
			if min_time and (trim_obj.timestamp_unix < min_time):
				continue
			if max_time and (trim_obj.timestamp_unix > max_time):
				continue
			self.trim_obj_dict[int(trim_obj.timestamp_unix)] = trim_obj
			self.trim_t_stamps = np.sort(np.int_(self.trim_obj_dict.keys()))
	
	def get_trim_times(self):
		return self.trim_t_stamps[self.trim_t_stamps>0]
	
	def print_trim_history(self):
		for trim_time in self.get_trim_times():
			trim_obj = self.trim_obj_dict[trim_time]
			print th.unixstamp2localtime(float(trim_obj.timestamp_unix))+': '+trim_obj.trim_variable
			
	def get_last_trim_before(self, t):
		if type(t) is str:
			tstamp_unix = th.localtime2unixstamp(t)
		else:
			tstamp_unix = t
		trim_t_stamps = self.trim_t_stamps[self.trim_t_stamps>0]
		indx_before_t = np.searchsorted(trim_t_stamps - tstamp_unix,0) - 1
		if indx_before_t < 0:
			print 'ERROR: The requested time is before the first trim!'
			return None
		else:
			return self.trim_obj_dict[trim_t_stamps[indx_before_t]]	
		
	def plot_trims(self, figure_ax=None, use_cycletime=False):
		pl.ion()
		if not figure_ax:
			fig = pl.figure()
			figure_ax = pl.subplot2grid((1,1),(0,0))
		trim_times = self.trim_t_stamps[self.trim_t_stamps>0]
		for trim_time in trim_times:
			trim_obj = self.trim_obj_dict[trim_time]
			line_label = trim_obj.trim_variable+': '+th.unixstamp2localtime(float(trim_obj.timestamp_unix))
			if use_cycletime:
				figure_ax.plot(trim_obj.cycletime_vect, trim_obj.value_vect, label=line_label)
				figure_ax.set_xlabel('Cycle time [ms]')
			else:
				figure_ax.plot(trim_obj.time_vect, trim_obj.value_vect, label=line_label)
				figure_ax.set_xlabel('Time [ms]')
		figure_ax.set_ylabel('value')
		pl.draw()
		return figure_ax
	
class TrimData(object):

	def __init__(self, complete_path):
		if complete_path.endswith('.mat'):
			dict_trim_data = sio.loadmat(complete_path)
		else:
			print('Unknown file extension for TrimData file. Should be ' +
				  '.mat')
		
		self.trim_variable = str(dict_trim_data['trim_variable'][0])
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
		
	def plot_trim(self, figure_ax=None, use_cycletime=False):
		pl.ion()
		if not figure_ax:
			fig = pl.figure()
			figure_ax = pl.subplot2grid((1,1),(0,0))
		if self.timestamp_unix:
			line_label=th.unixstamp2localtime(float(self.timestamp_unix))		
			if use_cycletime:
				figure_ax.plot(self.cycletime_vect, self.value_vect, label=line_label)
				figure_ax.set_xlabel('Cycle time [ms]')
			else:
				figure_ax.plot(self.time_vect, self.value_vect, label=line_label)
				figure_ax.set_xlabel('Time [ms]')
		figure_ax.set_ylabel('value')
		pl.draw()
		return figure_ax


def make_mat_files(trim_data_file, SPSuser, trim_variable=None, trim_data_mat_folder='trim_data'):
	print 'converting file "' + trim_data_file + '"'
	list_trim_hist = []
	with open(trim_data_file, 'r') as cfile:
		spr = csv.reader(cfile)
		for row in spr:
			if filter(None, row):
				list_trim_hist.append(row)

	if not trim_variable:
		trim_variable = list_trim_hist[0][0].replace('/','_').replace('.','_')
		
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
			'data_value_vect' : data_value_vect,
			'trim_variable' : trim_variable},
			oned_as='row')
