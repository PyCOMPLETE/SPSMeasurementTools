from sddsdata import sddsdata
import numpy as np
import scipy.io as sio
import os
import shutil
import time
import datetime
import glob
from zip_mat import save_zip
import timestamp_helpers as th
import gzip
import matplotlib.pyplot as pl

class MultiQ(object):

	def __init__(self, complete_path):

		if complete_path.endswith('.mat.gz'):
			temp_filename = complete_path.split('.gz')[0]
			with open(temp_filename, "wb") as tmp:
				shutil.copyfileobj(gzip.open(complete_path), tmp)
			dict_multiq = sio.loadmat(temp_filename)
			os.remove(temp_filename)
		elif complete_path.endswith('.mat'):
			dict_multiq = sio.loadmat(complete_path)
		else:
			print('Unknown file extension for MultiQ file. Should be ' +
			      '.mat or .mat.gz')

		self.rawData_H = dict_multiq['rawData_H']
		self.rawData_V = dict_multiq['rawData_V']
		self.acqStartTimes = np.squeeze(dict_multiq['acqStartTimes'])
		self.excitationAmplitudeH = dict_multiq['excitationAmplitudeH']
		self.excitationAmplitudeV = dict_multiq['excitationAmplitudeV']

	def get_fft(self, plane='H'):
		''' Use plane='H' for horizontal and plane='V' for vertical
		plane data. '''
		
		if plane=='H':
			rawData = self.rawData_H
		elif plane=='V':
			rawData = self.rawData_V
		else:
			print 'unknown plane argument'
			return -1

		n_meas, n_turns = rawData.shape
		ampl = np.zeros((n_meas, n_turns//2 + 1)) # Note: output length of rfft is n//2+1.
		for i in range(n_meas):
			ampl[i,:] = np.abs(np.fft.rfft(rawData[i,:]))
		freq = np.fft.rfftfreq(n_turns)

		return freq, ampl
		
	def plot_fft(self, plane='H', figure_ax=None):	
		pl.ion()
		if not figure_ax:
			fig = pl.figure()
			figure_ax = pl.subplot2grid((1,1),(0,0))
		fr_h, am_h = self.get_fft(plane)
		am_h /= np.amax(am_h)
		figure_ax.pcolormesh(fr_h, 1e-3*self.acqStartTimes, np.log(am_h), vmax=0.25, cmap='rainbow')
		figure_ax.set_xlabel('Tune $Q_'+plane.lower()+'$')
		figure_ax.set_ylabel('Time [s]')
		pl.draw()
		return figure_ax



def sdds_to_dict(in_complete_path):
	us_string = in_complete_path.split('.')[-2]

	try:
		temp = sddsdata(in_complete_path, endian='little', full=True)
	except IndexError:
		print 'Failed to open data file. (save_multiq_mat)'
		return
	data = temp.data[0]

	BBQ_Version = data['BBQ-Version'].tostring()
	acqOffset = float(data['acqOffset'])
	acqPeriod = float(data['acqPeriod'])
	acqStartTimes = np.float_(data['acqStartTimes'])
	acqTimes = np.float_(data['acqTimes'])
	chirpStartFreqH = float(data['chirpStartFreqH'])
	chirpStartFreqV = float(data['chirpStartFreqV'])
	chirpStopFreqH = float(data['chirpStopFreqH'])
	chirpStopFreqV = float(data['chirpStopFreqV'])
	date = data['date'].tostring()
	enableExcitationH = bool(data['enableExcitationH'])
	enableExcitationV = bool(data['enableExcitationV'])
	exDelay = float(data['exDelay'])
	exOffset = float(data['exOffset'])
	exPeriod = float(data['exPeriod'])
	excitationAmplitudeH = float(data['excitationAmplitudeH'])
	excitationAmplitudeV = float(data['excitationAmplitudeV'])
	fullNumberOfTurns = float(data['fullNumberOfTurns'])
	nbOfMeas = float(data['nbOfMeas'])
	nbOfTurns = float(data['nbOfTurns'])
	superCycleNb = float(data['scNumber'])
	Time = data['time'].tostring()
	triggerName = data['triggerName'].tostring()
	tuneDataH = data['tuneDataH']
	tuneDataV = data['tuneDataV']
	SPSuser = data['user'].tostring().split('\n')[0]
	window = data['window'].tostring()
	windowFunction = float(data['windowFunction'])
	
	t_stamp_unix = float(data['timestampSecond'])+float(data['timestampMilliSecond'])*1e-3
	rawData_H=[]
	rawData_V=[]
	for ii in xrange(int(nbOfMeas)):
		rawData_H.append(data['rawData-H-%d'%(ii+1)])
		rawData_V.append(data['rawData-V-%d'%(ii+1)])

	rawData_H = np.float_(np.array(rawData_H))
	rawData_V = np.float_(np.array(rawData_V))

	dict_meas = {\
		'BBQ_Version': BBQ_Version,
		'acqOffset':  acqOffset,
		'acqPeriod':  acqPeriod,
		'acqStartTimes':acqStartTimes,
		'acqTimes': acqTimes,
		'chirpStartFreqH': chirpStartFreqH,
		'chirpStartFreqV': chirpStartFreqV,
		'chirpStopFreqH ':chirpStopFreqH,
		'chirpStopFreqV':chirpStopFreqV,
		'date':date,
		'enableExcitationH':enableExcitationH,
		'enableExcitationV':enableExcitationV,
		'exDelay':exDelay,
		'exOffset':exOffset,
		'exPeriod': exPeriod,
		'excitationAmplitudeH':excitationAmplitudeH,
		'excitationAmplitudeV': excitationAmplitudeV,
		'fullNumberOfTurns': fullNumberOfTurns,
		'nbOfMeas':nbOfMeas,
		'nbOfTurns':nbOfTurns,
		'superCycleNb': superCycleNb,
		'Time': Time,
		'triggerName': triggerName,
		'tuneDataH': tuneDataH,
		'tuneDataV': tuneDataV,
		'SPSuser': SPSuser,
		'window ':window,
		'windowFunction': windowFunction,
		'rawData_H':rawData_H,
		'rawData_V':rawData_V,
		't_stamp_unix':t_stamp_unix\
		}

	return dict_meas

def sdds_to_file(in_complete_path, mat_filename_prefix='SPSmeas_', outp_folder='multiq/'):

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


def make_mat_files(start_time, end_time='Now', data_folder='/user/slops/data/SPS_DATA/OP_DATA/multiQ/',
		   SPSuser=None, filename_converted='multiq_converted.txt'):

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
		sdds_folder_list.extend(glob.glob(data_folder + date_string))

	for sdds_folder in sdds_folder_list:
		print '\nConverting data in folder: %s\n'%sdds_folder
		file_list = os.listdir(sdds_folder)
	
		for filename in file_list:
			# print filename
			time_string = ' '.join(filename.split('.')[0].split('_')[-2:])
			tstamp_filename = int(time.mktime(datetime.datetime.strptime(time_string, "%d%b%y %H-%M-%S").timetuple()))
			if not(tstamp_filename > start_tstamp_unix and tstamp_filename < end_tstamp_unix):
				continue

			if SPSuser != None:
				user_filename = filename.split('_')[1]
				if user_filename != SPSuser:
					continue
			
			if filename in list_converted:
				continue

			try:
				complete_path = sdds_folder + '/' + filename
				print complete_path

				sdds_to_file(complete_path)
				with open(filename_converted, 'a+') as fid:
					fid.write(filename+'\n')
			except Exception as err:
				print 'Skipped:'
				print complete_path
				print 'Got exception:'
				print err
			
