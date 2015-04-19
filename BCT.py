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


class BCT:
	def __init__(self, complete_path):
		temp_filename = complete_path.split('.gz')[0] + 'uzipd'
		with open(temp_filename, "wb") as tmp:
			shutil.copyfileobj(gzip.open(complete_path), tmp)
		dict_bct = sio.loadmat(temp_filename)
		os.remove(temp_filename)

		intens_exponent = np.float_(np.squeeze(dict_bct['totalIntensity_unitExponent']))

		self.total_intensity = np.squeeze(dict_bct['totalIntensity'])*10**(intens_exponent)
		self.SPS_user = str(np.squeeze(dict_bct['SPSuser']))
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


def make_pickle(pickle_name='bct_overview.pkl', outp_folder='bct/', t_obs_1st_inj=1.5):

	if os.path.isfile(pickle_name):
		with open(pickle_name) as fid:
			beams = pickle.load(fid)
	else:
		beams = {}

	SPS_user_list = os.listdir(outp_folder)
	for SPS_user in SPS_user_list:

		if not(SPS_user in beams.keys()):
			beams[SPS_user] = {}
			beams[SPS_user]['bct_max_vect'] = np.array([])
			beams[SPS_user]['SC_numb_vect'] = np.array([])
			beams[SPS_user]['timestamp_float'] = np.array([])
			beams[SPS_user]['bct_integrated'] = np.array([])
			beams[SPS_user]['bct_1st_inj'] = np.array([])

		list_bct_files = os.listdir(bct_mat_folder +'/'+ SPS_user)
		N_cycles = len(list_bct_files)
		for ii in xrange(N_cycles):
			filename_bct = list_bct_files[ii]
			tstamp_mat_filename = float(filename_bct.split('_')[-2])

			if tstamp_mat_filename in beams[SPS_user]['timestamp_float']:
				continue
			try:
				print '%s %d/%d'%(SPS_user, ii, N_cycles - 1)
				curr_bct = BCT(bct_mat_folder +'/'+ SPS_user +'/'+ filename_bct)
				SPS_user = curr_bct.SPS_user

				beams[SPS_user]['bct_max_vect'] = np.append(beams[SPS_user]['bct_max_vect'], curr_bct.max_inten())
				beams[SPS_user]['SC_numb_vect'] = np.append(beams[SPS_user]['SC_numb_vect'], curr_bct.SC_numb)
				beams[SPS_user]['timestamp_float'] = np.append(beams[SPS_user]['timestamp_float'], curr_bct.time_start_cycle_float)
				beams[SPS_user]['bct_integrated'] = np.append(beams[SPS_user]['bct_integrated'], curr_bct.integral())
				beams[SPS_user]['bct_1st_inj'] = np.append(beams[SPS_user]['bct_1st_inj'], curr_bct.nearest_sample(t_obs_1st_inj))
			except IOError as err:
				print err

	for SPS_user in beams.keys():
		ind_sorted = np.argsort(beams[SPS_user]['timestamp_float'])
		for kk in beams[SPS_user].keys():
			beams[SPS_user][kk] = np.take(beams[SPS_user][kk], ind_sorted)

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

	beamID=np.int_(data['beamID'])
	deviceName=data['deviceName'].tostring()
	sbfIntensity=np.float_(data['sbfIntensity'])
	acqState=np.int_(data['acqState'])
	totalIntensity=data['totalIntensity']
	acqTime=data['acqTime'].tostring()
	propType=np.int_(data['propType'])
	totalIntensity_unitExponent=np.int_(data['totalIntensity_unitExponent'])
	measStamp_unitExponent=np.float_(data['measStamp_unitExponent'])
	samplingTime=np.int_(data['samplingTime'])
	measStamp_unit=np.int_(data['measStamp_unit'])
	observables=np.int_(data['observables'])
	nbOfMeas=np.int_(data['nbOfMeas'])
	superCycleNb=np.int_(data['superCycleNb'])
	acqMsg=data['acqMsg'].tostring()
	measStamp=data['measStamp']
	acqDesc=data['acqDesc'].tostring()
	totalIntensity_unit=np.int_(data['totalIntensity_unit'])

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


def sdds_to_file(in_complete_path, mat_filename_prefix='SPSmeas_', outp_folder='bct/', suffix_file='bct'):

	dict_meas = sdds_to_dict(in_complete_path)
	us_string = dict_meas['SPSuser']
	t_stamp_unix = dict_meas['t_stamp_unix']

	out_filename = mat_filename_prefix + us_string + ('_%d_'%t_stamp_unix) + suffix_file
	out_complete_path = outp_folder + us_string +'/'+ out_filename

	if not os.path.isdir(outp_folder + us_string):
		print 'I create folder: '+ outp_folder + us_string
		os.makedirs(outp_folder + us_string)

	sio.savemat(out_complete_path, dict_meas, oned_as='row')
	save_zip(out_complete_path)
