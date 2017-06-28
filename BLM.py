import matplotlib.pyplot as plt
from sddsdata import sddsdata
import numpy as np
import scipy.io as sio
import os
import shutil
import gzip
import time
import glob
import pickle
from zip_mat import save_zip
import timestamp_helpers as th
import zipfile


class BLM:
	def __init__(self, complete_path):
		temp_filename = complete_path.split('.gz')[0] + 'uzipd'
		with open(temp_filename, "wb") as tmp:
			shutil.copyfileobj(gzip.open(complete_path), tmp)
		dict_blm = sio.loadmat(temp_filename)
		os.remove(temp_filename)

		self.blm_data = dict_blm['cal2DLosses']
		self.blm_channels = dict_blm['channelNames']
		self.measStamp = dict_blm['measStamp'][0]
		self.SPSuser = str(np.squeeze(dict_blm['SPSuser']))
		self.SC_numb = np.int_(np.squeeze(dict_blm['superCycleNb']))
		# self.dict_blm = dict_blm


	# def plot_blms(self, figure_ax=None):	
	# 	plt.ion()
	# 	if not figure_ax:
	# 		fig = plt.figure()
	# 		figure_ax = plt.subplot2grid((1,1),(0,0))
	# 	figure_ax.pcolormesh(self.blm_data)
	# 	plt.draw()
	# 	return figure_ax


def sdds_to_dict(in_complete_path):
	us_string = in_complete_path.split('.')[-3]
	t_stamp_unix = float(in_complete_path.split('@')[-2])/1e9+1

	zfile = zipfile.ZipFile(in_complete_path)
	filename = zfile.namelist()[0]
	zfile.extract(filename)

	try:
		temp = sddsdata(filename, endian='little', full=True)
	except IndexError:
		print 'Failed to open data file. (save_blmexpert_mat)'
		return
	os.remove(filename)
	data = temp.data[0]

	dict_meas = {
		'totalLoss': data['totalLoss'],
		'cal2DLosses': data['cal2DLosses'],
		'nbOfChannels': data['nbOfChannels'],
		'measStamp': data['measStamp'],
		'nbOfMeas': data['nbOfMeas'],
		'superCycleNb': data['superCycleNb'],
		'channelNames': data['channelNames'],
		'SPSuser':us_string,
		't_stamp_unix':t_stamp_unix
			}	
	return dict_meas


def sdds_to_file(in_complete_path, mat_filename_prefix='SPSmeas_', outp_folder='blm/'):

	dict_meas = sdds_to_dict(in_complete_path)
	us_string = dict_meas['SPSuser']
	t_stamp_unix = dict_meas['t_stamp_unix']

	out_filename = mat_filename_prefix + us_string +'_BLM'+('_%d'%t_stamp_unix)
	out_complete_path = outp_folder + us_string +'/'+ out_filename

	if not os.path.isdir(outp_folder + us_string):
		print 'I create folder: '+ outp_folder + us_string
		os.makedirs(outp_folder + us_string)

	sio.savemat(out_complete_path, dict_meas, oned_as='row')
	save_zip(out_complete_path)


def make_mat_files(start_time, end_time='Now', data_folder='/user/slops/data/SPS_DATA/OP_DATA/BLM/',
		   device_name=None, SPSuser=None, filename_converted='blmexpert_converted.txt'):

	if type(start_time) is str:
		start_tstamp_unix = th.localtime2unixstamp(start_time)
	else:
		start_tstamp_unix = start_time

	if end_time == 'Now':
		end_tstamp_unix = time.mktime(time.localtime())
	elif type(end_time) is str:
		end_tstamp_unix = th.localtime2unixstamp(end_time)
	else:
		end_tstamp_unix = end_time

	try:
		with open(filename_converted, 'r') as fid:
			list_converted = fid.read().split('\n')
	except IOError:
		list_converted = []

	list_date_strings = th.date_strings_interval(start_tstamp_unix, end_tstamp_unix)

	sdds_folder_list = []
	for date_string in list_date_strings:
		sdds_folder_list.extend(glob.glob(data_folder + date_string + '/SPS.BLM@ExpertAcquisition/'))
	print sdds_folder_list
	for sdds_folder in sdds_folder_list:
		print '\nConverting data in folder: %s\n'%sdds_folder
		file_list = os.listdir(sdds_folder)
		for filename in file_list:
			tstamp_filename = int(float(filename.split('@')[-2]) / 1e9)
			if not(tstamp_filename > start_tstamp_unix and tstamp_filename < end_tstamp_unix):
				continue

			if SPSuser != None:
				user_filename = filename.split('.')[-3]
				if user_filename != SPSuser:
					continue

			if filename in list_converted:
				continue

			try:
				complete_path = sdds_folder + filename
				print complete_path

				sdds_to_file(complete_path)
				with open(filename_converted, 'a+') as fid:
					fid.write(filename+'\n')
			except Exception as err:
				print 'Skipped:'
				print complete_path
				print 'Got exception:'
				print err
