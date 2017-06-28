import numpy as np
import shlex
import scipy.io as sio
import os
import shutil
import time
import datetime
import glob
#~ from zip_mat import save_zip
import timestamp_helpers as th
import gzip
import zipfile
from sys import stdout
#~ import matplotlib.pyplot as pl
from zip_mat import save_zip

class YASP(object):

	def __init__(self, complete_path):

		if complete_path.endswith('.mat.gz'):
			temp_filename = complete_path.split('.gz')[0]
			with open(temp_filename, "wb") as tmp:
				shutil.copyfileobj(gzip.open(complete_path), tmp)
			yasp_dict = sio.loadmat(temp_filename)
			os.remove(temp_filename)
		elif complete_path.endswith('.mat'):
			yasp_dict = sio.loadmat(complete_path)
		else:
			print('Unknown file extension for YASP file. Should be ' +
			      '.mat or .mat.gz')

		self.dpp = yasp_dict['DPP'][0][0]
		self.mode = str(yasp_dict['MODE'][0])
		self.nb_monitors_H = yasp_dict['MONITOR-H-NUM'][0][0]
		self.nb_monitors_V = yasp_dict['MONITOR-V-NUM'][0][0]
		self.nb_correctors_H = yasp_dict['CORRECTOR-H-NUM'][0][0]
		self.nb_correctors_V = yasp_dict['CORRECTOR-V-NUM'][0][0]
		self.flags = yasp_dict['FLAGS']
		self.t_stamp_unix = yasp_dict['t_stamp_unix'][0][0]
		self.acqtype = str(yasp_dict['TYPE'][0])
		self.twiss = str(yasp_dict['TWISS'][0])
		self.transfer = str(yasp_dict['TRANSFER'][0])
		self.acqtime_in_cycle = float(yasp_dict['CYCTIME'][0][0])
		self.context = str(yasp_dict['CONTEXT'][0])
		
		monitor_dict = {}
		monitor_keys = np.char.strip(yasp_dict['MONITOR-FIELDS'].astype('str'))
		for key in monitor_keys:
			monitor_dict[key] = yasp_dict['MONITOR'][key][0][0].flatten()
			# change the string types from Unicode to str
			if np.issubdtype(monitor_dict[key].dtype, np.dtype('U')): 
				monitor_dict[key] = np.char.strip(monitor_dict[key].astype('str'))
		dtypes = map(lambda key: (key.lower(), monitor_dict[key].dtype), monitor_keys)
		monitor_arr = np.zeros(self.nb_monitors_H + self.nb_monitors_V, dtypes)
		for key in monitor_dict.keys():
			monitor_arr[key.lower()] = monitor_dict[key]
		self.monitors = {'H': monitor_arr.take(np.where(monitor_arr['plane']=='H')).flatten(),
						 'V': monitor_arr.take(np.where(monitor_arr['plane']=='V')).flatten()}
		
		corrector_dict = {}
		corrector_keys = np.char.strip(yasp_dict['CORRECTOR-FIELDS'].astype('str'))
		for key in corrector_keys:
			corrector_dict[key] = yasp_dict['CORRECTOR'][key][0][0].flatten()
			# change the string types from Unicode to str
			if np.issubdtype(corrector_dict[key].dtype, np.dtype('U')): 
				corrector_dict[key] = np.char.strip(corrector_dict[key].astype('str'))
		dtypes = map(lambda key: (key.lower(), corrector_dict[key].dtype), corrector_dict)
		corrector_arr = np.zeros(self.nb_correctors_H + self.nb_correctors_V, dtypes)
		for key in corrector_dict.keys():
			corrector_arr[key.lower()] = corrector_dict[key]
		self.correctors = {'H': corrector_arr.take(np.where(corrector_arr['plane']=='H')).flatten(),
						   'V': corrector_arr.take(np.where(corrector_arr['plane']=='V')).flatten()}
		
		
###################3
#~ 
	#~ def plot_fft(self, plane='H', figure_ax=None):	
		#~ pl.ion()
		#~ if not figure_ax:
			#~ fig = pl.figure()
			#~ figure_ax = pl.subplot2grid((1,1),(0,0))
		#~ fr_h, am_h = self.get_fft(plane)
		#~ am_h /= np.amax(am_h)
		#~ figure_ax.pcolormesh(fr_h, 1e-3*self.acqStartTimes, np.log(am_h), vmax=0.25, cmap='rainbow')
		#~ figure_ax.set_xlabel('Tune $Q_'+plane.lower()+'$')
		#~ figure_ax.set_ylabel('Time [s]')
		#~ pl.draw()
		#~ return figure_ax


def yasp_to_dict(in_complete_path):

	with open(in_complete_path) as f:
		content = f.readlines()
	
	yasp_dict={}
	flags = []
	indx = 0
	
	# header
	while content[indx][0] == '@':
		line_split = shlex.split(content[indx].replace("\n", "")) 
		#~ print line_split
		dtype = line_split[-2]
		if dtype == '%s':
			yasp_dict[line_split[1]] = line_split[-1]
		elif dtype == '%d':
 			yasp_dict[line_split[1]] = int(line_split[-1])
 		elif dtype == '%f':
 			yasp_dict[line_split[1]] = float(line_split[-1])
		elif dtype == '@':
			flags.append(line_split[1])
		else:
			print 'ERROR: Cannot interpret ' + ' '.join(line_split)
		indx += 1
	yasp_dict['FLAGS'] = flags
	
	yasp_dict['SPSuser'] = yasp_dict['USER'].split('.USER.')[-1]
	yasp_dict['t_stamp_unix'] = yasp_dict['DATE-CODE']/1000
	
	# monitors
	if not content[indx].split()[1] == 'MONITOR':
		print 'ERROR: Expected the data block "MONITOR" but found "' + content[indx].split()[1] + '"!'
		return
	indx += 1
	monitors_dict = {}
	monitor_keys = content[indx][1:].split()
	yasp_dict['MONITOR-FIELDS'] = monitor_keys
	monitor_data = []
	n_monitors = yasp_dict['MONITOR-H-NUM']+yasp_dict['MONITOR-V-NUM']
	for indx in indx+1+np.arange(n_monitors):
		monitor_data.append(content[indx].split())
		indx += 1
	monitor_data = map(list, zip(*monitor_data))
	for i, key in enumerate(monitor_keys):
		if key in ['POS', 'RMS', 'SUM', 'DISP']:
			monitor_data[i] = np.float_(np.array(monitor_data[i]))
		if key in ['STATUS', 'ENABLE']:
			monitor_data[i] = np.int_(np.array(monitor_data[i]))
		monitors_dict[key] = monitor_data[i]
	yasp_dict['MONITOR'] = monitors_dict
	
	# correctors
	if not content[indx].split()[1] == 'CORRECTOR':
		print 'ERROR: Expected the data block "CORRECTOR" but found "' + content[indx].split()[1] + '"!'
		return
	indx += 1
	correctors_dict = {}
	corrector_keys = content[indx][1:].split()
	yasp_dict['CORRECTOR-FIELDS'] = corrector_keys
	corrector_data = []
	n_correctors = yasp_dict['CORRECTOR-H-NUM']+yasp_dict['CORRECTOR-V-NUM']
	for indx in indx+1+np.arange(n_correctors):
		corrector_data.append(content[indx].split())
		indx += 1
	corrector_data = map(list, zip(*corrector_data))
	for i, key in enumerate(corrector_keys):
		if key in ['KICK', 'RT-KICK']:
			corrector_data[i] = np.float_(np.array(corrector_data[i]))
		correctors_dict[key] = corrector_data[i]
	yasp_dict['CORRECTOR'] = correctors_dict
	return yasp_dict
	


def yasp_to_file(in_complete_path, mat_filename_prefix='SPSmeas_', outp_folder='yasp/', outfile_suffix=''):

	dict_meas = yasp_to_dict(in_complete_path)
	us_string = dict_meas['SPSuser']
	t_stamp_unix = dict_meas['t_stamp_unix']
	mode = dict_meas['MODE']
	transfer = dict_meas['TRANSFER']
	
	out_filename = mat_filename_prefix + mode + '_' + transfer + '_' + us_string + ('_%d'%t_stamp_unix) + outfile_suffix
	out_complete_path = outp_folder + us_string +'/'+ out_filename

	if not os.path.isdir(outp_folder + us_string):
		print 'I create folder: '+ outp_folder + us_string
		os.makedirs(outp_folder + us_string)

	sio.savemat(out_complete_path, dict_meas, oned_as='row')
	save_zip(out_complete_path)
	return out_complete_path+'.mat.gz'


def make_mat_files(start_time, end_time='Now', data_folder='/user/slops/data/SPS_DATA/OP_DATA/steering/sps',
		   SPSuser=None, filename_converted='yasp_converted.txt'):

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
	search_string = '/*'
	if SPSuser:
		search_string += '_' + SPSuser + '_*'
	complete_path_list = glob.glob(data_folder + search_string)


	for complete_path in complete_path_list:
		filename = complete_path.split('/')[-1]
		#~ print filename.split('_')
		try:
			if 'MULTIACQ' in filename:
				 time_string = ' '.join(filename.split('.')[-2].split('_')[-2:])
				 is_multiacq = True
			else:
				time_string = ' '.join(filename.split('_')[2:4])
				is_multiacq = False
			tstamp_filename = int(time.mktime(datetime.datetime.strptime(time_string, "%d-%m-%y %H-%M-%S").timetuple()))
			#~ print tstamp_filename
		except Exception as err:
			print '\nSkipped:'
			print complete_path
			print 'Got exception:'
			print err
			continue
			
		if not(tstamp_filename > start_tstamp_unix and tstamp_filename < end_tstamp_unix):
			continue		

		if filename in list_converted:
			continue

		try:
			complete_path = data_folder + '/' + filename
			print complete_path
			if is_multiacq:
				print '\nTreating multi-acquisition data set: '
				temp_path = complete_path.split('.zip')[0].split('/')[-1] + '_tmp'
				with zipfile.ZipFile(complete_path, "r") as z:
					z.extractall(temp_path)
				subfile_list = os.listdir(temp_path)
				outfile_list = []
				for subfile in subfile_list:
					stdout.write('\r\t'+temp_path+'/'+subfile)
					stdout.flush()
					outfile_suffix = '_%03d'%int(subfile.split('-')[-1])
					outfile_list.append(yasp_to_file(temp_path+'/'+subfile, outfile_suffix=outfile_suffix))
				stdout.write("\n")
				outfile_path = outfile_list[-1].split(outfile_suffix)[0]+'_mulitacqu/'
				if not os.path.isdir(outfile_path):
					os.makedirs(outfile_path)
				stdout.write('\r\tMoving files to %s ... ' %outfile_path)
				stdout.flush()
				for outfile in outfile_list:
					shutil.copy(outfile, outfile_path)
					os.remove(outfile)
				shutil.rmtree(temp_path)
				stdout.write('\r\tMoving files to %s ... DONE' %outfile_path)
				stdout.write("\n")
			else:
				if complete_path.endswith('.gz'):
					temp_filename = complete_path.split('.gz')[0].split('/')[-1]
					with open(temp_filename, "wb") as tmp:
						shutil.copyfileobj(gzip.open(complete_path), tmp)		
					yasp_to_file(temp_filename)
					os.remove(temp_filename)
				elif complete_path.endswith('.data'):
					yasp_to_file(complete_path)
				else:
					print('Unknown file extension for YASP file. Should be ' +
						  '.data or .data.gz')
			with open(filename_converted, 'a+') as fid:
				fid.write(filename+'\n')
		except Exception as err:
			print 'Skipped:'
			print complete_path
			print 'Got exception:'
			print err
