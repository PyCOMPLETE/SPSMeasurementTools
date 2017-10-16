from sddsdata import sddsdata
import numpy as np
import scipy.io as sio
import scipy.optimize as op
import os
import shutil
import gzip
import time
import glob
import pickle
from zip_mat import save_zip
import timestamp_helpers as th


class MountainRange(object):
    def __init__(self, complete_path):

        if complete_path.endswith('.mat.gz'):
            temp_filename = complete_path.split('.gz')[0]
            with open(temp_filename, "wb") as tmp:
                shutil.copyfileobj(gzip.open(complete_path), tmp)
            dict_mr = sio.loadmat(temp_filename)
            os.remove(temp_filename)
        elif complete_path.endswith('.mat'):
            dict_mr = sio.loadmat(complete_path)
        else:
            print('Unknown file extension for MountainRange file. Should be ' +
                  '.mat or .mat.gz')
        self.value = dict_mr['value']
        self.trigger_stamp = dict_mr['triggerStamp']
        self.SC_numb = np.int(np.squeeze(dict_mr['superCycleNb']))
        self.first_trigger_t_stamp_unix = dict_mr['first_trigger_t_stamp_unix']
        self.sample_interval = float(np.squeeze(dict_mr['sampleInterval']))
        self.first_sample_time = dict_mr['firstSampleTime']
        self.sensitivity = dict_mr['sensitivity']
        self.offset = dict_mr['offset']
        self.SPSuser = dict_mr['SPSuser']
        self.t_stamp_unix = dict_mr['t_stamp_unix']

        self.time_axis = np.float_(range(self.value.shape[1]))*self.sample_interval-self.value.shape[1]*self.sample_interval/2.

    def get_average_profile(self):
        average_profile = np.mean(self.value[-20:,:],axis=0)
        baseline = np.mean(average_profile[0:20])
        average_profile -= baseline
        return average_profile

    def fit_sigma_t_first_bunch(self):
        average_profile = self.get_average_profile()
        mask_average_profile = self.time_axis < self.time_axis[np.argmax(average_profile)] + 1.2
        mask_average_profile2 = self.time_axis > self.time_axis[np.argmax(average_profile)] - 1.2
        mask_average_profile = mask_average_profile & mask_average_profile2

        self._fitfunc = lambda p, x: p[0]*np.exp(-((x-p[1])**2)/(2.*p[2]**2))
        self._errfunc = lambda p, x, y: self._fitfunc(p, x) - y # Distance to the target function
        sigma0 = 1.
        ampl = np.max(average_profile[mask_average_profile])
        mu0 = self.time_axis[np.argmax(average_profile)]
        p0 = [ampl, mu0, sigma0]
        p1, success = op.leastsq(self._errfunc, p0[:], args=(self.time_axis[mask_average_profile], 
                average_profile[mask_average_profile]))
        if success:
            sigma_t = p1[2]
        else:
            sigma_t = 0.
            ampl = 0.
            mu0 = 0.
        return sigma_t, ampl, mu0

def sdds_to_dict(in_complete_path):
    try:
        temp = sddsdata(in_complete_path, endian='little', full=True)
    except IndexError:
        print 'Failed to open data file. (save_mr_mat)'
        return
    data = temp.data[0]

    superCycleNb = float(data['SCNumber'])
    cycleTag =  float(data['cycleTag'])
    firstSampleTime = float(data['firstSampleTime'])
    offset =  float(data['offset'])
    sampleInterval = float(data['sampleInterval'])
    sensitivity =  float(data['sensitivity'])
    triggerError = np.float_(data['triggerError'])
    triggerStamp =  data['triggerStamp']
    value = np.float_(data['value'])
    #value_units = data['value_units'].tostring()
    first_trigger_t_stamp_unix =  float(triggerStamp[0])/1e9   
    SPSuser = in_complete_path.split('SPS.USER.')[-1].split('.')[0]

    time_string_filename = in_complete_path.split('@')[3]
    time_string_filename = ':'.join(time_string_filename.split('_')[:-1])
    date_string_path = in_complete_path.split('/')[-3]
    t_stamp_unix = time.mktime(time.strptime(date_string_path + ' ' + time_string_filename, '%Y_%m_%d %H:%M:%S'))

    dict_meas = {
        'superCycleNb': superCycleNb,
        'cycleTag': cycleTag,
        'firstSampleTime': firstSampleTime,
        'offset': offset,
        'sampleInterval': sampleInterval,
        'sensitivity': sensitivity,
        'triggerError': triggerError,
        'triggerStamp': triggerStamp,
        'value': value,
        'first_trigger_t_stamp_unix': first_trigger_t_stamp_unix,
        'SPSuser': SPSuser,
        't_stamp_unix': t_stamp_unix }

    return dict_meas

def sdds_to_file(in_complete_path, mat_filename_prefix='SPSmeas_', outp_folder='mr/'):

    dict_meas = sdds_to_dict(in_complete_path)
    us_string = dict_meas['SPSuser']
    t_stamp_unix = dict_meas['t_stamp_unix']

    out_filename = mat_filename_prefix + us_string + ('_%d'%t_stamp_unix)
    out_complete_path = outp_folder + us_string +'/'+ out_filename

    if not os.path.isdir(outp_folder + us_string):
        print 'I create folder: '+ outp_folder + us_string
        os.makedirs(outp_folder + us_string)

    sio.savemat(out_complete_path, dict_meas, oned_as='row')
    save_zip(out_complete_path)

def make_mat_files(start_time, end_time='Now', data_folder='/user/slops/data/SPS_DATA/OP_DATA/MR/',
        SPSuser=None, filename_converted='mr_converted.txt'):

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
        sdds_folder_list.extend(glob.glob(data_folder + date_string + '/SMR.SCOPE13.CH01@Acquisition/'))
    
    for sdds_folder in sdds_folder_list:
        print '\nConverting data in folder: %s\n'%sdds_folder
        file_list = os.listdir(sdds_folder)
        for filename in file_list:
            tstamp_filename = int(float(filename.split('@')[-2]) / 1e9)
            if not(tstamp_filename > start_tstamp_unix and tstamp_filename < end_tstamp_unix):
                continue

            if SPSuser != None:
                user_filename = filename.split('.')[-3]
                print user_filename
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
            except Exception as err:
                print 'Skipped:'
                print complete_path
                print 'Got exception:'
                print err

def make_pickle(pickle_name='mr_overview.pkl', mat_folder='mr/'):
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
            beams[SPSuser]['sigma_t'] = np.array([])
            beams[SPSuser]['mu0'] = np.array([])
            beams[SPSuser]['ampl'] = np.array([])
            beams[SPSuser]['timestamp_float'] = np.array([])

        list_mr_files = os.listdir(mat_folder +'/'+ SPSuser)
        N_cycles = len(list_mr_files)
        for ii in xrange(N_cycles):
            filename_mr = list_mr_files[ii]
            tstamp_mat_filename = float((filename_mr.split('_')[-1]).split('.mat')[0])

            if tstamp_mat_filename in beams[SPSuser]['timestamp_float']:
                continue
            try:
                print '%s %d/%d'%(SPSuser, ii, N_cycles - 1)
                curr_mr = MountainRange(mat_folder +'/'+ SPSuser +'/'+ filename_mr)
                SPSuser = curr_mr.SPSuser[0]
                sigmat, ampl, mu0 = curr_mr.fit_sigma_t_first_bunch()
                beams[SPSuser]['ampl'] = np.append(beams[SPSuser]['ampl'], ampl)
                beams[SPSuser]['mu0'] = np.append(beams[SPSuser]['mu0'], mu0)
                beams[SPSuser]['sigma_t'] = np.append(beams[SPSuser]['sigma_t'], sigmat)
                beams[SPSuser]['timestamp_float'] = np.append(beams[SPSuser]['timestamp_float'], curr_mr.t_stamp_unix)

            except IOError as err:
                print err

        ind_sorted = np.argsort(beams[SPSuser]['timestamp_float'])
        for kk in beams[SPSuser].keys():
            beams[SPSuser][kk] = np.take(beams[SPSuser][kk], ind_sorted)

        with open(pickle_name, 'w') as fid:
            pickle.dump(beams, fid)
