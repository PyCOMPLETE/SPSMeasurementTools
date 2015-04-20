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


class BCT:
	def __init__(self, complete_path):
		temp_filename = complete_path.split('.gz')[0] + 'uzipd'
		with open(temp_filename, "wb") as tmp:
			shutil.copyfileobj(gzip.open(complete_path), tmp)
		dict_bct = sio.loadmat(temp_filename)
		os.remove(temp_filename)

		intens_exponent = np.float_(np.squeeze(dict_bct['totalIntensity_unitExponent']))

		self.total_intensity = np.squeeze(dict_bct['totalIntensity'])*10**(intens_exponent)
		self.SPSuser = str(np.squeeze(dict_bct['SPSuser']))
		self.SC_numb = np.int_(np.squeeze(dict_bct['superCycleNb']))

		time_start_cycle_string = dict_bct['cycleTime']
		time_start_cycle_string = time_start_cycle_string.tolist()[0]
		time_start_cycle_string = time_start_cycle_string.split('.')[0]
		time_start_cycle_struct = time.strptime(time_start_cycle_string, '"%Y/%m/%d %H:%M:%S')
		self.time_start_cycle_float = time.mktime(time_start_cycle_struct)
		self.time_vect = np.squeeze(dict_bct['measStamp']*10**np.float_(np.squeeze(dict_bct['measStamp_unitExponent'])))

	def max_inten(self):
		return np.max(self.total_intensity)

	def integral(self):
	    return np.trapz(self.total_intensity, self.time_vect)

	def nearest_sample(self, t_obs):
		ind_min = np.argmin(np.abs(self.time_vect-t_obs))
		return self.total_intensity[ind_min]

	def get_lifetime(self, t_start, t_window_length):

		ind_bct_start = np.where(self.time_vect > t_start)[0][0]
		ind_bct_stop = np.where(self.time_vect < t_start + t_window_length)[0][-1]

		fitfunc = lambda p, x: p[1]*np.exp(-x/p[0])
		errfunc = lambda p, x, y: fitfunc(p, x) - y # Distance to the target function

		# Initial guess for fit parameters.
		bct0 = self.total_intensity[ind_bct_start]
		tau0 = 1.
		p0 = [tau0, bct0]
		p1, success = op.leastsq(errfunc, p0[:], args=(
			self.time_vect[ind_bct_start:ind_bct_stop] - self.time_vect[ind_bct_start],
			self.total_intensity[ind_bct_start:ind_bct_stop]))
		if success:
			return p1[0], p1[1]
		else:
			print 'WARNING: Fit failed!!'
			return 0., 0.


def make_pickle(pickle_name='bct_overview.pkl', mat_folder='bct/', t_obs_1st_inj=1.5):

	if os.path.isfile(pickle_name):
		with open(pickle_name) as fid:
			beams = pickle.load(fid)
			print '\nUpdating file: %s'%pickle_name
	else:
		beams = {}
		print '\nCreating file: %s'%pickle_name

	SPSuser_list = os.listdir(mat_folder)
	for SPSuser in SPSuser_list:

		if not(SPSuser in beams.keys()):
			beams[SPSuser] = {}
			beams[SPSuser]['bct_max_vect'] = np.array([])
			beams[SPSuser]['SC_numb_vect'] = np.array([])
			beams[SPSuser]['timestamp_float'] = np.array([])
			beams[SPSuser]['bct_integrated'] = np.array([])
			beams[SPSuser]['bct_1st_inj'] = np.array([])

		list_bct_files = os.listdir(mat_folder +'/'+ SPSuser)
		N_cycles = len(list_bct_files)
		for ii in xrange(N_cycles):
			filename_bct = list_bct_files[ii]
			tstamp_mat_filename = float((filename_bct.split('_')[-1]).split('.mat')[0])

			if tstamp_mat_filename in beams[SPSuser]['timestamp_float']:
				continue
			try:
				print '%s %d/%d'%(SPSuser, ii, N_cycles - 1)
				curr_bct = BCT(mat_folder +'/'+ SPSuser +'/'+ filename_bct)
				SPSuser = curr_bct.SPSuser

				beams[SPSuser]['bct_max_vect'] = np.append(beams[SPSuser]['bct_max_vect'], curr_bct.max_inten())
				beams[SPSuser]['SC_numb_vect'] = np.append(beams[SPSuser]['SC_numb_vect'], curr_bct.SC_numb)
				beams[SPSuser]['timestamp_float'] = np.append(beams[SPSuser]['timestamp_float'], curr_bct.time_start_cycle_float)
				beams[SPSuser]['bct_integrated'] = np.append(beams[SPSuser]['bct_integrated'], curr_bct.integral())
				beams[SPSuser]['bct_1st_inj'] = np.append(beams[SPSuser]['bct_1st_inj'], curr_bct.nearest_sample(t_obs_1st_inj))
			except IOError as err:
				print err

	for SPSuser in beams.keys():
		ind_sorted = np.argsort(beams[SPSuser]['timestamp_float'])
		for kk in beams[SPSuser].keys():
			beams[SPSuser][kk] = np.take(beams[SPSuser][kk], ind_sorted)

	with open(pickle_name, 'w') as fid:
		pickle.dump(beams, fid)


def sdds_to_dict(in_complete_path):
	us_string = in_complete_path.split('.')[-2]

	try:
		temp = sddsdata(in_complete_path, endian='little', full=True)
	except IndexError:
		print 'Failed to open data file. (save_bct_mat)'
		return
	data = temp.data[0]

	cycleTime = data['cycleTime'].tostring()
	t_stamp_unix = time.mktime(time.strptime(cycleTime.replace('"', '').replace('\n','').split('.')[0], '%Y/%m/%d %H:%M:%S'))

	beamID = np.int_(data['beamID'])
	deviceName = ((data['deviceName'].tostring()).split('\n')[0]).split('SPS.')[-1]
	sbfIntensity = np.float_(data['sbfIntensity'])
	acqState = np.int_(data['acqState'])
	totalIntensity = data['totalIntensity']
	acqTime = data['acqTime'].tostring()
	propType = np.int_(data['propType'])
	totalIntensity_unitExponent = np.int_(data['totalIntensity_unitExponent'])
	measStamp_unitExponent = np.float_(data['measStamp_unitExponent'])
	samplingTime = np.int_(data['samplingTime'])
	measStamp_unit = np.int_(data['measStamp_unit'])
	observables = np.int_(data['observables'])
	nbOfMeas = np.int_(data['nbOfMeas'])
	superCycleNb = np.int_(data['superCycleNb'])
	acqMsg = data['acqMsg'].tostring()
	measStamp = data['measStamp']
	acqDesc = data['acqDesc'].tostring()
	totalIntensity_unit = np.int_(data['totalIntensity_unit'])

	dict_meas = {
		'beamID':beamID,
		'deviceName':deviceName,
		'sbfIntensity':sbfIntensity,
		'acqState':acqState,
		'totalIntensity':totalIntensity,
		'acqTime':acqTime,
		'propType':propType,
		'totalIntensity_unitExponent':totalIntensity_unitExponent,
		'measStamp_unitExponent':measStamp_unitExponent,
		'samplingTime':samplingTime,
		'measStamp_unit':measStamp_unit,
		'observables':observables,
		'nbOfMeas':nbOfMeas,
		'superCycleNb':superCycleNb,
		'cycleTime':cycleTime,
		'acqMsg':acqMsg,
		'measStamp':measStamp,
		'acqDesc':acqDesc,
		'totalIntensity_unit':totalIntensity_unit,
		'SPSuser':us_string,
		't_stamp_unix':t_stamp_unix
			}

	return dict_meas


def sdds_to_file(in_complete_path, mat_filename_prefix='SPSmeas_', outp_folder='bct/'):

	dict_meas = sdds_to_dict(in_complete_path)
	us_string = dict_meas['SPSuser']
	t_stamp_unix = dict_meas['t_stamp_unix']
	device_name = dict_meas['deviceName']

	out_filename = mat_filename_prefix + us_string +'_'+  device_name + ('_%d'%t_stamp_unix)
	out_complete_path = outp_folder + us_string +'/'+ out_filename

	if not os.path.isdir(outp_folder + us_string):
		print 'I create folder: '+ outp_folder + us_string
		os.makedirs(outp_folder + us_string)

	sio.savemat(out_complete_path, dict_meas, oned_as='row')
	save_zip(out_complete_path)


def make_mat_files(start_time, end_time='Now', data_folder='/user/slops/data/SPS_DATA/OP_DATA/SPS_BCT/',
		   device_name=None, SPSuser=None, filename_converted='bct_converted.txt'):

	if type(start_time) is str:
		start_tstamp_unix = th.localtime2unixstamp(start_time)
	if end_time == 'Now':
		end_tstamp_unix = time.mktime(time.localtime())
	elif type(end_time) is str:
		end_tstamp_unix = th.localtime2unixstamp(end_time)

	try:
		with open(filename_converted, 'r') as fid:
			list_converted = fid.read().split('\n')
	except IOError:
		list_converted = []

	list_date_strings = th.date_strings_interval(start_tstamp_unix, end_tstamp_unix)

	sdds_folder_list = []
	for date_string in list_date_strings:
		if device_name == None:
			sdds_folder_list.extend(glob.glob(data_folder + date_string + '/SPS.BCTDC.*@Acquisition/'))
		else:
			device_path = glob.glob(data_folder + date_string + '/SPS.BCTDC.%s*@Acquisition/'%device_name)
			if len(device_path) == 0:
				print 'No data for device %s on %s'%(device_name, date_string)
			else:
				sdds_folder_list.extend(device_path)


	for sdds_folder in sdds_folder_list:
		print '\nConverting data in folder: %s\n'%sdds_folder
		file_list = os.listdir(sdds_folder)
		for filename in file_list:
			tstamp_filename = int(float(filename.split('@')[-2]) / 1e9)
			if not(tstamp_filename > start_tstamp_unix and tstamp_filename < end_tstamp_unix):
				continue

			if SPSuser != None:
				user_filename = filename.split('.')[-2]
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
			except KeyError:#Exception as err:
				print 'Skipped:'
				print complete_path
				print 'Got exception:'
				print err
