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


class ECLDMON:
    def __init__(self, complete_path, ecm_part):
        if ecm_part not in ['a', 'b']:
            raise ValueError

        if complete_path.endswith('.mat.gz'):
            temp_filename = complete_path.split('.gz')[0]
            #print 'temp_filename', temp_filename
            with open(temp_filename, "wb") as tmp:
                shutil.copyfileobj(gzip.open(complete_path), tmp)
            dict_ecld = sio.loadmat(temp_filename)
            os.remove(temp_filename)

        elif complete_path.endswith('.mat'):
            dict_ecld = sio.loadmat(complete_path)
        else:
            print('Unknown file extension for ECLDMON file. Should be ' +
                  '.mat or .mat.gz')

        ecld_mon_rescaled = dict_ecld['eclm_data']

        TOTAL_GAIN = np.float_(np.squeeze(dict_ecld['TOTAL_GAIN']))

        #compensate detector gain
        for ii in range(len(TOTAL_GAIN)):
            ecld_mon_rescaled[:,ii*16:(ii+1)*16] = ecld_mon_rescaled[:,ii*16:(ii+1)*16]/TOTAL_GAIN[ii]

        #compensate integration time
        self.time_vect = np.squeeze(dict_ecld['PROFILE_CYCLE_TIME'])
        self.integ_time = self.time_vect[4]-self.time_vect[3];
        ecld_mon_rescaled = ecld_mon_rescaled/self.integ_time
        self.SC_numb = int(dict_ecld['SC_NUMBER'])
        self.x_channels = 2.17*np.arange(0, 48.)

        if ecm_part == 'a':
            self.ecld_mat = ecld_mon_rescaled[:,0:48]
            self.gain3 = TOTAL_GAIN[0:3]
        else:
            self.ecld_mat = ecld_mon_rescaled[:,48:96]
            self.gain3 = TOTAL_GAIN[3:6]

    def total_vs_channel(self):
        return np.sum(self.ecld_mat,0)

    def total_vs_time(self):
        return np.sum(self.ecld_mat,1)

    def profile(self, t_obs):
        ind_min = np.argmin(np.abs(self.time_vect-t_obs))
        return self.ecld_mat[ind_min,:]

    def total_at_time(self, t_obs, chann_list=None):
        temp = self.profile(t_obs)
        if chann_list == None:
            return np.sum(temp)
        else:
            return np.sum(np.take(temp, chann_list))


def make_pickle(start_from_last=True, pickle_name_ecm='ecm_overview.pkl', pickle_name_bct='bct_overview.pkl', mat_folder='ecm/', mat_file_prefix='SPSmeas_', t_obs_1st_inj=1.5, n_points_to_cut=10, SPSuser_blacklist = []):

    with open(pickle_name_bct) as fid:
	    beams_bct = pickle.load(fid)
    
    semcloud_lists = get_ecm_tstamps_from_filenames(mat_folder, SPSuser_blacklist, beams_bct)

    try:
        with open(pickle_name_ecm) as fid:
	        ecm_dict = pickle.load(fid)
    except IOError:
        print "I CREATE (!) the ecm pickle file"
        ecm_dict = {'1a':{}, '1b':{}, '2a':{}, '2b':{}}

    
    for ecm_id in '1a 1b 2a 2b'.split():

        ecm_device = int(ecm_id[0])
        ecm_part = ecm_id[-1]
            
        beams_ecm = ecm_dict[ecm_id]

        for SPSuser in beams_bct.keys():
            if SPSuser in SPSuser_blacklist:
               continue

            t_stamps_ecm = np.array(semcloud_lists[ecm_device][SPSuser])
            if len(t_stamps_ecm) == 0:
                print 'No ECM data for user: %s'%SPSuser
                continue

            if not(SPSuser in beams_ecm.keys()):
                beams_ecm[SPSuser] = {}
                beams_ecm[SPSuser]['timestamp_bct'] = []
                beams_ecm[SPSuser]['timestamp_ecm'] = []
                beams_ecm[SPSuser]['ecld_1st_inj'] = []
                beams_ecm[SPSuser]['ecld_max'] = []
                beams_ecm[SPSuser]['int_time'] = []
                beams_ecm[SPSuser]['gain_av'] = []
                beams_ecm[SPSuser]['gain_sigma'] = []

            N_cycles = len(beams_bct[SPSuser]['timestamp_float'])
		    
            for ii in range(N_cycles):

                t_stamp = beams_bct[SPSuser]['timestamp_float'][ii]
                if start_from_last and len(beams_ecm[SPSuser]['timestamp_bct']) > 0:
                    if t_stamp <= beams_ecm[SPSuser]['timestamp_bct'][-1]:
                        continue
                elif t_stamp in beams_ecm[SPSuser]['timestamp_bct']:
                    continue
                print '%s %s %d/%d'%(ecm_id, SPSuser, ii, N_cycles - 1)
                idx_nearest = np.argmin(np.abs(t_stamps_ecm - t_stamp))
                difference = t_stamps_ecm[idx_nearest] - t_stamp
                print 'difference %s s'%difference

                found = False
                for jj in [0,1,-1,2,-2,3,-3,4,-4,5,-5,6,-6,7,-7]:
                    if (idx_nearest+jj > 0) and (idx_nearest+jj) < len(t_stamps_ecm):
	                    filename_ecm = mat_file_prefix + SPSuser + '_SEMCLOUD%d'%int(ecm_device) + ('_%d.mat.gz'%t_stamps_ecm[idx_nearest+jj])

	                    curr_ecm = ECLDMON(mat_folder + '%s/SEMCLOUD%d/'%(SPSuser, ecm_device) + filename_ecm, ecm_part)
	                    print curr_ecm.SC_numb, beams_bct[SPSuser]['SC_numb_vect'][ii]
	                    if curr_ecm.SC_numb == beams_bct[SPSuser]['SC_numb_vect'][ii]:
		                    beams_ecm[SPSuser]['ecld_1st_inj'].append(curr_ecm.total_at_time(t_obs_1st_inj))
		                    beams_ecm[SPSuser]['int_time'].append(curr_ecm.integ_time)
		                    beams_ecm[SPSuser]['gain_av'].append(np.mean(curr_ecm.gain3))
		                    beams_ecm[SPSuser]['gain_sigma'].append(np.mean(curr_ecm.gain3))
		                    beams_ecm[SPSuser]['ecld_max'].append(np.min(curr_ecm.total_vs_time()[:-n_points_to_cut]))
		                    beams_ecm[SPSuser]['timestamp_bct'].append(t_stamp)
		                    beams_ecm[SPSuser]['timestamp_ecm'].append(t_stamps_ecm[idx_nearest+jj])
		                    print 'OK', jj
		                    found = True
		                    break
                if not found:
                    print 'Nofile', t_stamp

            ind_sorted = np.argsort(beams_ecm[SPSuser]['timestamp_bct'])
            for kk in beams_ecm[SPSuser].keys():
                beams_ecm[SPSuser][kk] = list(np.take(beams_ecm[SPSuser][kk], ind_sorted))

            with open(pickle_name_ecm, 'w') as fid:
                pickle.dump(ecm_dict,fid)


           
def get_ecm_tstamps_from_filenames(ecm_mat_folder, SPSuser_blacklist, beams_bct):            
    
    semcloud_lists = {1:{},2:{}}

    for SPSuser in beams_bct.keys():
        if SPSuser in SPSuser_blacklist:
          continue

        for ecm_device in [1,2]:
            semcloud_lists[ecm_device][SPSuser] = []
            try:
                list_ecm_files = os.listdir(ecm_mat_folder+'/%s/SEMCLOUD%d/'%(SPSuser, ecm_device))
                for filen in list_ecm_files:
                    t_stamp_curr = float((filen.split('_')[-1]).split('.mat')[0])
                    semcloud_lists[ecm_device][SPSuser].append(t_stamp_curr)

            except OSError as err:
                print err

            semcloud_lists[ecm_device][SPSuser] = np.sort(semcloud_lists[ecm_device][SPSuser])            

    return semcloud_lists


def sdds_to_dict(in_complete_path):
	
    try:
	    temp = sddsdata(in_complete_path, endian='little', full=True)
    except IndexError:
	    print 'Failed to open data file. (save_bct_mat)'
	    return
    data = temp.data[0]

    acq_comment = data['ACQ-COMMENT'].tostring()
    cycle_length = np.float_(data['CYCLE-LENGTH'])
    date = data['DATE'].tostring()
    device_name = data['DEVICE-NAME'].tostring()
    number_profiles = np.int_(data['NUMBER-PROFILES'])
    number_strips = np.int_(data['NUMBER-STRIPS'])
    profile_cycle_time = np.float_(data['PROFILE-CYCLE-TIME']) / 1e3
    sc_number = np.int_(data['SC-NUMBER'])
    time = data['TIME'].tostring()
    timestamp_millisecond = np.int_(data['TIMESTAMP-MILLISECOND'])
    timestamp_second = np.int_(data['TIMESTAMP-SECOND'])
    timing_user = data['TIMING-USER'].tostring()
    total_gain = data['TOTAL-GAIN']

    eclm_data = np.zeros((number_profiles, number_strips))
    for ii in range(number_profiles):
        key_string = 'SEM-PROFILE-%d'%(ii+1)
        eclm_data[ii,:] = data[key_string]

    device_name = in_complete_path.split('-')[0].split('/')[-1]
    us_string = in_complete_path.split('-')[1].split('.')[-1]

    dict_meas =  {
    'ACQ_COMMENT':acq_comment,
    'DATE':date,
    'DEVICE_NAME':device_name,
    'NUMBER_PROFILES':number_profiles,
    'NUMBER_STRIPS':number_strips,
    'PROFILE_CYCLE_TIME':profile_cycle_time,
    'SC_NUMBER':sc_number,
    'TIME':time,
    'TIMESTAMP_MILLISECOND':timestamp_millisecond,
    'TIMESTAMP_SECOND':timestamp_second,
    'TIMING_USER':timing_user,
    'TOTAL_GAIN':total_gain,
    'eclm_data':eclm_data,
    'device_name':device_name,
    'SPSuser':us_string
    }

    return dict_meas


def sdds_to_file(in_complete_path, mat_filename_prefix='SPSmeas_', outp_folder='ecm/'):

    dict_meas = sdds_to_dict(in_complete_path)
    us_string = dict_meas['SPSuser']
    t_stamp_unix = dict_meas['TIMESTAMP_SECOND']
    device_name = dict_meas['device_name']

    out_directory = outp_folder + us_string +'/'+ device_name
    out_filename = '%s%s_%s_%d'%(mat_filename_prefix, us_string, device_name, t_stamp_unix)
    out_complete_path = out_directory +'/'+ out_filename

    if not os.path.isdir(out_directory):
	    print 'I create folder: '+ out_directory
	    os.makedirs(out_directory)

    sio.savemat(out_complete_path, dict_meas, oned_as='row')
    save_zip(out_complete_path)


def make_mat_files(start_time, end_time='Now', data_folder='/user/slops/data/SPS_DATA/OP_DATA/SEM_CLOUD/',
		  SPSuser=None, filename_converted='ecm_converted.txt'):

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


    print '\nConverting data in folder: %s\n'%data_folder
    file_list = glob.glob(data_folder + '*.sdds*')
    for filename in file_list:
        
        complete_path = filename

        t_str_sdds = complete_path.split('.sdds')[0].split('_')[-2] +' '+ complete_path.split('.sdds')[0].split('_')[-1]
        tstamp_filename = time.mktime(time.strptime(t_str_sdds,'%d-%m-%y %H-%M-%S'))
        if not(tstamp_filename > start_tstamp_unix and tstamp_filename < end_tstamp_unix):
            continue

        if SPSuser != None:
            user_filename = filename.split('.')[-2]
            if user_filename != SPSuser:
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



