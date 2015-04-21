import os
import time

def UnixTimeStamp2UTCTimberTimeString(t):
	return time.strftime('%Y-%m-%d %H:%M:%S.000', time.gmtime(t))

def dbquery(varlist, t_start, t_stop, filename):
	
	if type(t_start) is not str:
		t_start_str_UTC = UnixTimeStamp2UTCTimberTimeString(t_start)
	else:
		t_start_str_UTC = t_start
		
	if type(t_stop) is not str:
		t_stop_str_UTC = UnixTimeStamp2UTCTimberTimeString(t_stop)
	else:
		t_stop_str_UTC = t_stop
	
	if type(varlist) is not list:
		raise TypeError
		
	varlist_str = ''
	for var in varlist:
		varlist_str += var+','
	varlist_str = varlist_str[:-1]

	execut = 'java -jar ./SPSMeasurementTools/accsoft-cals-extractor-client-nodep.jar '
	config = ' -C ./SPSMeasurementTools/ldb_UTC.conf '
	time_interval = ' -t1 "'+ t_start_str_UTC +'" -t2 "'+t_stop_str_UTC + '"' 
	variables = '-vs "%s"'%(varlist_str)
	outpfile = ' -N .//'+filename
	command = execut+config+variables+time_interval+outpfile
	os.system(command)
