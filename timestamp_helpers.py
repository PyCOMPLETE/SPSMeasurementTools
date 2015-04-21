import time
import numpy as np

def unixstamp2datestring(t_stamp):
	return time.strftime("%Y_%m_%d", time.localtime(t_stamp))

def unixstamp_of_midnight_before(t_stamp):
	day_string = unixstamp2datestring(t_stamp)
	return time.mktime(time.strptime(day_string+' 00:00:00', '%Y_%m_%d %H:%M:%S'))

def date_strings_interval(start_tstamp_unix, end_tstamp_unix):
	list_date_strings = []
	for t_day in np.arange(unixstamp_of_midnight_before(start_tstamp_unix), end_tstamp_unix+1., 24*3600.):
		list_date_strings.append(unixstamp2datestring(t_day))
	return list_date_strings

def localtime2unixstamp(local_time_str, strformat='%Y_%m_%d %H:%M:%S'):
	return time.mktime(time.strptime(local_time_str, strformat))

def unixstamp2localtime(t_stamp, strformat='%Y_%m_%d %H:%M:%S'):
	return time.strftime(strformat, time.localtime(t_stamp))
