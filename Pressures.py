import time
import numpy as np
import os
import scipy.io as sio
import slots_n_vs_s as nvss
import pickle


class Pressure:
    def __init__(self,complete_path):

        self.complete_path = complete_path
        dict_press = sio.loadmat(self.complete_path)

        self.t_start_cycle = np.float(np.squeeze(dict_press['t_start_cycle']))
        self.s_gau = np.float_(np.squeeze(dict_press['s_gau']))
        self.gau_numb_vect = np.int_(np.squeeze(dict_press['gau_numb_vect']))
        self.SPSuser = str(dict_press['SPSuser'][0])

        self.time_vect = np.float_(np.squeeze(dict_press['t']))
        if not hasattr(self.time_vect, '__iter__'):
            self.time_vect = [self.time_vect]
        self.press_mat = np.float_(np.squeeze(dict_press['press_mat']))

    def extract_gauges(self, list_gau_numb=None):
        if list_gau_numb == None:
                submat = self.press_mat
                sub_gau_numb = self.gau_numb_vect
                sub_gau_s = self.s_gau
        else:
            submat = np.zeros((len(list_gau_numb), len(self.time_vect)))
            kk = 0
            sub_gau_numb = np.zeros(len(list_gau_numb), dtype=int)
            sub_gau_s = np.zeros(len(list_gau_numb))
            for gau_numb in list_gau_numb:
                if gau_numb not in self.gau_numb_vect:
                    sub_gau_numb[kk] = gau_numb
                else:
                    index = np.where(self.gau_numb_vect == gau_numb)
                    submat[kk,:] = self.press_mat[index,:]
                    sub_gau_numb[kk] = self.gau_numb_vect[index]
                    sub_gau_s[kk] = self.s_gau[index]
    
                kk = kk + 1

        if len(list_gau_numb) == 1:
            submat = np.squeeze(submat)
            sub_gau_numb = sub_gau_numb[0]
            sub_gau_s = sub_gau_s[0]

        return submat, sub_gau_numb, sub_gau_s

    def get_p_init(self, list_gau_numb=None):
        p_temp,_,_  = self.extract_gauges(list_gau_numb)
        if len(p_temp.shape) > 1:
            return np.squeeze(p_temp[:,0])
        else:   
            return [np.squeeze(p_temp[0])]

    def get_p_final(self, list_gau_numb=None):
        p_temp,_,_  = self.extract_gauges(list_gau_numb)
        if len(p_temp.shape) > 1:
            return np.squeeze(p_temp[:,-1])
        else:   
            return [np.squeeze(p_temp[-1])]

    def get_min_max(self, min_cut=0, max_cut=0, list_gau_numb=None):
        p_temp,_,_  = self.extract_gauges(list_gau_numb)
        if len(p_temp.shape) > 1:
            p_sorted = np.sort(p_temp, axis=1)
        else:
            p_sorted = np.array([np.sort(p_temp)])
        p_min = np.squeeze(p_sorted[:,min_cut])
        p_max = np.squeeze(p_sorted[:,-1-max_cut])

        if p_min.shape == ():
            p_min = [float(p_min)]
            p_max = [float(p_max)]

        return p_min, p_max

    def get_aver(self, list_gau_numb=None):
        p_temp,_,_ = self.extract_gauges(list_gau_numb)
        if len(p_temp.shape) > 1:
            return np.mean(p_temp, axis=1)
        else:
            return [np.mean(p_temp)]
        
        
        
def make_pickle(start_from_last=True, pickle_name_press='press_overview.pkl', pickle_name_bct='bct_overview.pkl', mat_folder='press_mat_cycles/', mat_file_prefix='SPSmeas_', t_obs_1st_inj=1.5, SPSuser_blacklist = [], list_gauges=[10660, 20660, 30660, 40660, 50660, 60660, 11879, 11959, 51080, 51140, 51280, 51340, 10060, 20060, 30060, 40060, 50060, 60060]):

    with open(pickle_name_bct) as fid:
	beams_bct = pickle.load(fid)

    try:
        with open(pickle_name_press) as fid:
	        press_dict = pickle.load(fid)
    except IOError:
        print "I CREATE (!) the pressure pickle file"
        press_dict = {}

    for SPSuser in beams_bct.keys():
        if SPSuser in SPSuser_blacklist:
            continue

        if not SPSuser in press_dict.keys():
            press_dict[SPSuser] = {}
        beams = press_dict[SPSuser]

        max_tstamps = []
        for gauge in list_gauges:
            if not gauge in beams.keys():
                beams[gauge] = {}
                beams[gauge]['timestamp_bct'] = []
                beams[gauge]['press_max'] = []
                beams[gauge]['press_min'] = []
                beams[gauge]['press_av'] = []
                beams[gauge]['press_first'] = []
                beams[gauge]['press_last'] = []
                max_tstamps.append(0)
            else:
                max_tstamps.append(max(beams[gauge]['timestamp_bct']))

        N_cycles = len(beams_bct[SPSuser]['timestamp_float'])

        for ii in range(N_cycles):
            t_stamp = beams_bct[SPSuser]['timestamp_float'][ii]
            if start_from_last and len(max_tstamps) > 0:
                if t_stamp <= min(max_tstamps):
                    continue

            print '%s %d/%d'%(SPSuser, ii, N_cycles-1)

            try:
                press_filename = mat_file_prefix + SPSuser + '_press_' + ('%d'%t_stamp)
                press_curr = Pressure(mat_folder + SPSuser +'/'+ press_filename)
                press_min, press_max = press_curr.get_min_max(min_cut=0, max_cut=0, list_gau_numb=list_gauges)
                press_av = press_curr.get_aver(list_gau_numb=list_gauges)
                press_init = press_curr.get_p_init(list_gau_numb=list_gauges)
                press_final = press_curr.get_p_final(list_gau_numb=list_gauges)

                for iig in range(len(list_gauges)):
                    gauge = list_gauges[iig]
                    if t_stamp in beams[gauge]['timestamp_bct']:
                        continue

                    beams[gauge]['timestamp_bct'].append(t_stamp)
                    beams[gauge]['press_max'].append(press_max[iig])
                    beams[gauge]['press_min'].append(press_min[iig])
                    beams[gauge]['press_av'].append(press_av[iig])
                    beams[gauge]['press_first'].append(press_init[iig])
                    beams[gauge]['press_last'].append(press_final[iig])
                    # print 'Pressure OK'

            except IOError as ioerror:
                print 'Pressure: Nofile'
                print ioerror
            except IndexError as indexerror:
                print 'Index Error!'
                print indexerror
            # except ValueError as valueerror:
                # print 'Value Error!'
                # print valueerror

        for gauge in list_gauges:
            ind_sorted = np.argsort(beams[gauge]['timestamp_bct'])
            for kk in beams[gauge].keys():
                beams[gauge][kk] = list(np.take(beams[gauge][kk], ind_sorted))

        with open(pickle_name_press, 'w') as fid:
            pickle.dump(press_dict,fid)



def csv_to_mat_gauges(csv_data_folder='pressure_data', mat_folder='press_mat'):

    list_press_files = os.listdir(csv_data_folder)

    gauges={}

    for filename in list_press_files:

	    print filename

	    complete_path = csv_data_folder+'/'+filename

	    with open(complete_path) as fid:
		    file_lines = fid.readlines()

	    file_content = []

	    for line in file_lines:
                append_vec = line.split('\t')
                append_vec[-1] = (append_vec[-1]).split('\n')[0]
                append_vec[-1] = (append_vec[-1]).split('\r')[0]

                file_content.append(append_vec)
	
	    header = file_content[0]
	
	    file_content = file_content[1:]
	    # build timestamp vect
	    vect_tstamp_strings = map(lambda x: x[0], file_content)
	    vect_tstamp_float = map(lambda s: time.mktime(time.strptime(s, '%Y-%m-%d %H:%M:%S.000') ), vect_tstamp_strings)
	
	
	    press_data = {}
		
	    for ii in range(1, len(header)):
		    press_data[header[ii]] = map(lambda lis: float(lis[ii]), file_content)
		
	    for kk in press_data.keys():
		    if kk not in gauges.keys():
			    gauges[kk] = {'t':[], 'press':[]}
		    gauges[kk]['t'] = gauges[kk]['t'] + vect_tstamp_float
		    gauges[kk]['press'] = gauges[kk]['press'] + press_data[kk]
		
    if not os.path.isdir(mat_folder):
        print 'I create folder: '+ mat_folder
        os.makedirs(mat_folder)   
 
    for kk in gauges.keys():
	    t = np.array(gauges[kk]['t'])
	    press = np.array(gauges[kk]['press'])
	
	    indices = np.argsort(t)
	    t = np.take(t, indices)
	    press = np.take(press, indices)
	
	    sio.savemat(mat_folder +'/'+ kk, {'t':t, 'press':press}, oned_as='row')
	
	

def make_cycle_mat_files(mat_folder='press_mat/', mat_file_prefix='SPSmeas_', outp_folder='press_mat_cycles/', pickle_name_bct='bct_overview.pkl'):

    list_gauges_filenames = os.listdir(mat_folder)

    with open(pickle_name_bct) as fid:
	beams = pickle.load(fid)

    gau_numb_vect = []
    N_gauges = len(list_gauges_filenames)
 
    for ii in xrange(0, N_gauges):	
        filename = list_gauges_filenames[ii]
        gau_numb = filename.split('.')[0]
        gau_numb = int(gau_numb.split('_')[-1])
        print gau_numb
	
        dict_press_curr = sio.loadmat(mat_folder + filename)

        t = np.squeeze(dict_press_curr['t'])
        press = np.squeeze(dict_press_curr['press'])
	
        if ii == 0:
            t_vect_ref = t
            press_mat = np.zeros((N_gauges, len(t_vect_ref)))
	
        press = np.interp(t_vect_ref, t, press)
        press_mat[ii, :] = press
	
        gau_numb_vect.append(gau_numb)
	
    indices = np.argsort(gau_numb_vect)
    press_mat = np.take(press_mat, indices, axis=0)
    gau_numb_vect = np.take(gau_numb_vect, indices)

    slot_n_vect = nvss.slot_n
    s_vect = nvss.slot_s
    s_gau = np.interp(gau_numb_vect, slot_n_vect, s_vect)

    SPSuser_list = beams.keys()

    for SPSuser in SPSuser_list:
        if not os.path.isdir(outp_folder + SPSuser):
            print 'I create folder: '+ outp_folder + SPSuser
            os.makedirs(outp_folder + SPSuser)   

	N_iter = len(beams[SPSuser]['timestamp_float'])
	for ii in xrange(N_iter):
            t_stamp = beams[SPSuser]['timestamp_float'][ii]
            print '%s %d/%d'%(SPSuser, ii, N_iter - 1)
		
            t_start_cycle = t_stamp
            t_stop_cycle = t_start_cycle + beams[SPSuser]['acqusition_time_length'][ii]
		
            indices_curr = np.where(np.logical_and(t_vect_ref > t_start_cycle, t_vect_ref < t_stop_cycle))[0]
		
            if len(indices_curr) > 0:
                t = np.take(t_vect_ref, indices_curr)
                t = t - t[0]
			
                press_mat_curr = np.take(press_mat, indices_curr, axis=1)
			
                out_filename = mat_file_prefix + SPSuser + '_press_' + ('%d'%t_stamp)
                out_complete_path = outp_folder + SPSuser +'/'+ out_filename
			
                sio.savemat(out_complete_path, {
                        'press_mat':press_mat_curr, 
                        's_gau':s_gau,  
                        'gau_numb_vect':gau_numb_vect,
                        't':t,
                        't_start_cycle':t_start_cycle, 
                        'SPSuser':SPSuser})
            else:
                print time.localtime(t_start_cycle)
		
		
