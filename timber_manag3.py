import time
import calendar
#import ws_meas_class as wmc

timb_timestamp2float= lambda time_string: time.mktime(time.strptime(time_string,'%Y-%m-%d %H:%M:%S'))
timb_timestamp2float_UTC= lambda time_string: calendar.timegm(time.strptime(time_string,'%Y-%m-%d %H:%M:%S'))


class timber_data_line:
	def __init__(self,rline, time_input_UTC = False):
		list_values=rline.split(',')
		t_string=list_values[0]
		if time_input_UTC:
			self.timestamp=timb_timestamp2float_UTC(t_string.split('.')[0])
			self.ms=float(t_string.split('.')[-1])
		else:
			self.timestamp=timb_timestamp2float(t_string.split('.')[0])
			self.ms=float(t_string.split('.')[-1])
		self.data_strings=list_values[1:]
		
class timber_variable_list:
	def __init__(self):
		self.t_stamps=[]
		self.ms=[]
		self.values=[]


def parse_timber_file(timber_filename, verbose=True):

	with open(timber_filename) as fid:
		timber_lines=fid.readlines()
		
	time_input_UTC = False

	N_lines=len(timber_lines)

	i_ln=0

	variables={}
	while i_ln<N_lines:
		line=timber_lines[i_ln]
		line=line.split('\n')[0]
		i_ln=i_ln+1
		
		if 'VARIABLE:' in line:
			vname=line.split(': ')[-1]
			if verbose:
				print '\n\nStarting variable: ' + vname
			variables[vname]=timber_variable_list()
		else:
			try:
				currline_obj=timber_data_line(line, time_input_UTC=time_input_UTC)
				variables[vname].t_stamps.append(currline_obj.timestamp)
				variables[vname].values.append(currline_obj.data_strings)
				variables[vname].ms.append(currline_obj.ms)
			except ValueError:
				if 'Timestamp (UTC_TIME)' in line:
					time_input_UTC = True
					if verbose:
						print 'Set time to UTC'
				if verbose:
					print 'Skipped line: '+	line
					
	return variables


	


	




		
	
	

