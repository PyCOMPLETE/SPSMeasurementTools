from sddsdata import sddsdata
import numpy as np
import scipy.io as sio
import os
import shutil
import time
import datetime
import glob
#from zip_mat import save_zip
import timestamp_helpers as th
import gzip


class MultiT(object):

	def __init__(self, complete_path):

		if complete_path.endswith('.mat.gz'):
			temp_filename = complete_path.split('.gz')[0]
			with open(temp_filename, "wb") as tmp:
				shutil.copyfileobj(gzip.open(complete_path), tmp)
			dict_multit = sio.loadmat(temp_filename)
			os.remove(temp_filename)
		elif complete_path.endswith('.mat'):
			dict_multit = sio.loadmat(complete_path)
		else:
			print('Unknown file extension for MultiT file. Should be ' +
			      '.mat or .mat.gz')

		nBPMS_v = np.count_nonzero(dict_multit['MonPlanes'])
		nBPMS_h = int(dict_multit['nbOfMonitors'] - nBPMS_v)
		nturns = dict_multit['nbOfTurns']
		monplanes = dict_multit['MonPlanes'][0]
		bpm_delta_h, bpm_sum_h, bpm_names_h, bpm_status_h = [], [], [], []
		bpm_delta_v, bpm_sum_v, bpm_names_v, bpm_status_v = [], [], [], []
		for i, channel in enumerate (dict_multit['ChannelNames']):
			channel = channel.encode('ascii').split(' ')[0]
			if monplanes[i] == 0:	
				bpm_delta_h.append(dict_multit[channel][0])
				bpm_sum_h.append(dict_multit[channel+'-SUM'][0])
				bpm_names_h.append(channel.replace('.H/H', '').replace('SPS.', ''))
				bpm_status_h.append(dict_multit['MonStatus'][0][i])
			else:
				bpm_delta_v.append(dict_multit[channel][0])
				bpm_sum_v.append(dict_multit[channel+'-SUM'][0])
				bpm_names_v.append(channel.replace('.V/V', '').replace('SPS.', ''))
				bpm_status_v.append(dict_multit['MonStatus'][0][i])
		
		bpm_data_h = np.zeros(nBPMS_h, dtype=[('name','a20'),('delta',np.float32,nturns),\
										('sum',np.float32,nturns),('status',np.float32)])
		bpm_data_h['name']   = bpm_names_h
		bpm_data_h['delta']  = bpm_delta_h
		bpm_data_h['sum']    = bpm_sum_h
		bpm_data_h['status'] = bpm_status_h
		
		bpm_data_v = np.zeros(nBPMS_v, dtype=[('name','a20'),('delta',np.float32,nturns),\
										('sum',np.float32,nturns),('status',np.float32)])
		bpm_data_v['name']   = bpm_names_v
		bpm_data_v['delta']  = bpm_delta_v
		bpm_data_v['sum']    = bpm_sum_v
		bpm_data_v['status'] = bpm_status_v		
		
		self.bpm_data  = {'H': bpm_data_h, 'V': bpm_data_v}
		self.bpm_names = {'H': bpm_names_h, 'V': bpm_names_v}
		self.startTime = dict_multit['startTime'][0][0]


	def get_bpm_index(self, bpm_names, plane):
		assert plane in ['H', 'V']
		if isinstance(bpm_names, basestring):
			bpm_names = [bpm_names]
		indx_list = []
		for bpm_name in bpm_names:
			try:
				indx_list.extend([list(self.bpm_data[plane]['name']).index(bpm_name)])
			except ValueError:
				print 'WARNING: BPM ' + bpm_name + ' is not included in the data set of plane ' + plane
		return indx_list

			
	def get_bpm(self, bpm_name, plane):
		return self.bpm_data[plane][self.get_bpm_index(bpm_name, plane)]


	def get_bpms_filtered(self, plane, filter_list = []):
		assert plane in ['H', 'V']
		noisy_bpms_filter = np.where(self.bpm_data[plane]['delta'].min(axis=1) == -27680)[0].tolist()
		if filter_list: 
			noisy_bpms_filter.extend(self.get_bpm_index(filter_list, plane))
			noisy_bpms_filter = np.unique(noisy_bpms_filter)
		good_bpms_filter = np.setdiff1d(range(len(self.bpm_data[plane])), noisy_bpms_filter)
		return self.bpm_data[plane][good_bpms_filter], self.bpm_data[plane][noisy_bpms_filter], good_bpms_filter, noisy_bpms_filter
		

	def get_fft(self, plane, start_turn=None, stop_turn=None, center_data=True):
		''' 
		Use plane='H' for horizontal and plane='V' for vertical
		plane data. 
		'''
		assert plane in ['H', 'V']
		bpm_data = self.bpm_data[plane]['delta'][:,start_turn:stop_turn]
		if center_data:
			bpm_data -= np.mean(bpm_data, axis=1)[:,None]	
		n_meas, n_turns = bpm_data.shape
		ampl = np.zeros((n_meas, n_turns//2 + 1)) # Note: output length of rfft is n//2+1.
		for i in range(n_meas):
			ampl[i,:] = np.abs(np.fft.rfft(bpm_data[i,:]))
		freq = np.fft.rfftfreq(n_turns)
		return freq, ampl


def sdds_to_dict(in_complete_path):
	us_string = in_complete_path.split('.')[-2]

	try:
		temp = sddsdata(in_complete_path, endian='little', full=True)
	except IndexError:
		print 'Failed to open data file. (save_multit_mat)'
		return
	data = temp.data[0]
	nbOfMonitors = float(data['nbOfMonitors'])
	BunchNos = np.float_(data['BunchNos'])
	ChannelNames = data['ChannelNames']
	MonStatus = np.float_(data['MonStatus'])
	startTime = float(data['startTime'])
	date = data['date'].tostring()	
	nbOfTurns = float(data['nbOfTurns'])
	TurnNos = np.float_(data['TurnNos'])
	scNumber = float(data['scNumber'])
	SPSuser = data['user'].tostring().split('\n')[0]
	acqComment = data['acqComment'].tostring()
	MonPlanes = np.float_(data['MonPlanes'])
	MonNames = data['MonNames']
	Time = data['time'].tostring()
	
	t_stamp_unix = float(data['timestampSecond'])+float(data['timestampMilliSecond'])*1e-3
	
	dict_meas = {\
		'BunchNos': BunchNos,
		'ChannelNames': ChannelNames,
		'MonStatus': MonStatus,
		'startTime': startTime,
		'date': date,
		'nbOfTurns': nbOfTurns,
		'TurnNos': TurnNos,
		'scNumber': scNumber,
		'SPSuser': SPSuser,
		'acqComment': acqComment,
		'MonPlanes': MonPlanes,
		'nbOfMonitors': nbOfMonitors,
		'MonNames': MonNames,
		'Time': Time,
		't_stamp_unix': t_stamp_unix\
	}
	
	for channel in ChannelNames:
		dict_meas[channel] = np.float_(data[channel])
		dict_meas[channel+'-SUM'] = np.float_(data[channel+'-SUM'])
		
	return dict_meas


def sdds_to_file(in_complete_path, mat_filename_prefix='SPSmeas_', outp_folder='multit/'):

	dict_meas = sdds_to_dict(in_complete_path)
	us_string = dict_meas['SPSuser']
	t_stamp_unix = dict_meas['t_stamp_unix']

	out_filename = mat_filename_prefix + us_string + ('_%d'%t_stamp_unix)
	out_complete_path = outp_folder + us_string +'/'+ out_filename

	if not os.path.isdir(outp_folder + us_string):
		print 'I create folder: '+ outp_folder + us_string
		os.makedirs(outp_folder + us_string)

	sio.savemat(out_complete_path, dict_meas, oned_as='row')
	
	f_in = open(out_complete_path+'.mat', 'rb')
	f_out = gzip.open(out_complete_path+'.mat.gz', 'wb')
	f_out.writelines(f_in)
	f_out.close()
	f_in.close()
	
	os.remove(out_complete_path+'.mat')


def make_mat_files(start_time, end_time='Now', data_folder='/user/slops/data/SPS_DATA/OP_DATA/multit/',
		   SPSuser=None, filename_converted='multit_converted.txt'):

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

	print '\nConverting data in folder: %s\n'%data_folder
	search_string = '/SPS-MULTIT*'
	if SPSuser:
		search_string += '_' + SPSuser + '_*'
	search_string += '*sdds*'
	complete_path_list = glob.glob(data_folder + search_string)

	for complete_path in complete_path_list:
		filename = complete_path.split('/')[-1]
		#~ print filename
		time_string = ' '.join(filename.split('.')[0].split('_')[-2:])
		tstamp_filename = int(time.mktime(datetime.datetime.strptime(time_string, "%d-%m-%y %H-%M-%S").timetuple()))
		if not(tstamp_filename > start_tstamp_unix and tstamp_filename < end_tstamp_unix):
			continue
		
		if filename in list_converted:
			continue

		try:
			print complete_path

			sdds_to_file(complete_path)
			with open(filename_converted, 'a+') as fid:
				fid.write(filename+'\n')
		except Exception as err:
			print 'Skipped:'
			print complete_path
			print 'Got exception:'
			print err

