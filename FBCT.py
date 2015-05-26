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


class FBCT:
    def __init__(self, complete_path):
        temp_filename = complete_path.split('.gz')[0] + 'uzipd'
        with open(temp_filename, "wb") as tmp:
            shutil.copyfileobj(gzip.open(complete_path), tmp)
        dict_fbct = sio.loadmat(temp_filename)
        os.remove(temp_filename)

        self.time_vect = np.float_(np.squeeze(dict_fbct['measStamp']))*1e-3
        self.fbct_mat = dict_fbct['bunchIntensityFast']

    def profile(self, t_obs):
        ind_min = np.argmin(np.abs(self.time_vect-t_obs))
        return self.fbct_mat[ind_min,:]

    def normalized_profile(self, t_obs, bct_total_intensity):
        subtracted_profile = self.subtract_baseline_profile(t_obs)
        integral = np.trapz(subtracted_profile)
        try:
            normalized = subtracted_profile / integral
        except ZeroDivisionError:
            normalized = np.zeros(len(subtracted_profile))
        return normalized * bct_total_intensity

    def subtract_baseline_profile(self, t_obs):
        ind_min = np.argmin(np.abs(self.time_vect-t_obs))
        signal_threshold = 0.2*np.max(self.fbct_mat[ind_min,:])
        below_thresh_idx = np.where(self.fbct_mat[ind_min,:] < signal_threshold)[0]
        baseline = np.mean(self.fbct_mat[ind_min,below_thresh_idx])
        return self.fbct_mat[ind_min,:] - baseline


def sdds_to_dict(in_complete_path):
    us_string = in_complete_path.split('.')[-2]

    try:
        temp = sddsdata(in_complete_path, endian='little', full=True)
    except IndexError:
        print 'Failed to open data file.'
        return
    data = temp.data[0]

    cycleTime = data['cycleTime'].tostring()
    t_stamp_unix = time.mktime(time.strptime(cycleTime.replace('"', '').replace('\n','').split('.')[0], '%Y/%m/%d %H:%M:%S'))

    beamID = np.int_(data['beamID'])
    deviceName = (data['deviceName'].tostring()).split('\n')[0]
    acqState = np.int_(data['acqState'])
    totalIntensity = data['totalIntensity']
    acqTime = data['acqTime'].tostring()
    propType = np.int_(data['propType'])
    totalIntensity_unitExponent = np.int_(data['totalIntensity_unitExponent'])
    bunchIntensitySlow = data['bunchIntensitySlow']
    bunchIntensityFast = data['bunchIntensityFast']
    gateIntensity_unitExponent = np.int_(data['gateIntensity_unitExponent'])
    nbOfMeas = np.int_(data['nbOfMeas'])
    totalIntensityFast = data['totalIntensityFast']
    superCycleNb = np.int_(data['superCycleNb'])
    acqMsg = data['acqMsg'].tostring()
    measStamp = data['measStamp']
    acqDesc = data['acqDesc'].tostring()
    observables = np.int_(data['observables'])
    totalIntensity_unit = np.int_(data['totalIntensity_unit'])

    dict_meas = {
        'beamID':beamID,
        'deviceName':deviceName,
        'acqState':acqState,
        'totalIntensity':totalIntensity,
        'acqTime':acqTime,
        'propType':propType,
        'totalIntensity_unitExponent':totalIntensity_unitExponent,
        'bunchIntensitySlow':bunchIntensitySlow,
        'bunchIntensityFast':bunchIntensityFast,
        'gateIntensity_unitExponent':gateIntensity_unitExponent,
        'nbOfMeas':nbOfMeas,
        'totalIntensityFast':totalIntensityFast,
        'superCycleNb':superCycleNb,
        'cycleTime':cycleTime,
        'acqMsg':acqMsg,
        'measStamp':measStamp,
        'acqDesc':acqDesc,
        'observables':observables,
        'totalIntensity_unit':totalIntensity_unit,
        'SPSuser':us_string,
        't_stamp_unix':t_stamp_unix
            }

    return dict_meas


def sdds_to_file(in_complete_path, mat_filename_prefix='SPSmeas_', outp_folder='fbct/'):

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


def make_mat_files(start_time, end_time='Now', data_folder='/user/slops/data/SPS_DATA/OP_DATA/SPS_FBCT/',
		   device_name=None, SPSuser=None, filename_converted='fbct_converted.txt'):

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
        if device_name == None:
            sdds_folder_list.extend(glob.glob(data_folder + date_string + '/SPS.BCTFR.*@Acquisition/'))
        else:
            device_path = glob.glob(data_folder + date_string + '/SPS.BCTFR.%s*@Acquisition/'%device_name)
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
            except Exception as err:
                print 'Skipped:'
                print complete_path
                print 'Got exception:'
                print err    
