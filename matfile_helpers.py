import time
import glob
import SPSMeasurementTools.timestamp_helpers as th

def generate_matfile_dict(mat_folder, start_time=0, end_time='Now'):
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

	file_list = glob.glob(mat_folder + '/*.mat*')
	file_dict = {}
	for filename in file_list:
		time_tmp_unix = float(filename.split('/')[-1].split('.mat')[0].split('_')[-1])
		if ((time_tmp_unix < start_tstamp_unix) or (time_tmp_unix > end_tstamp_unix)):
			continue
		file_dict[int(time_tmp_unix)] = filename
	return file_dict

