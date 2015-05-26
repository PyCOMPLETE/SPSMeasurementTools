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


class QMeter(object):
	
    def __init__(self, complete_path):
        temp_filename = complete_path.split('.gz')[0] + 'uzipd'
        with open(temp_filename, "wb") as tmp:
            shutil.copyfileobj(gzip.open(complete_path), tmp)
        dict_qmeter = sio.loadmat(temp_filename)
        os.remove(temp_filename)

        self.doneNbMeas = np.squeeze(dict_qmeter['doneNbOfMeas'])
        self.reqNbMeas = np.squeeze(dict_qmeter['requestedNbOfMeas'])

        if self.doneNbMeas == self.reqNbMeas and self.doneNbMeas < 3:
            measStamp = np.squeeze(dict_qmeter['measStamp'])
            self.nTurnsAcq = dict_qmeter['nbOfTurns'][0][0]

            self.rawData_H = np.zeros((self.doneNbMeas, self.nTurnsAcq))
            self.rawData_V = np.zeros((self.doneNbMeas, self.nTurnsAcq))
            self.acqTimeStamp = np.zeros(self.doneNbMeas)

            for j in xrange(self.doneNbMeas):
                i_turn, f_turn = j*self.nTurnsAcq, (j+1)*self.nTurnsAcq
                self.rawData_H[j,:] = np.squeeze(dict_qmeter['rawDataH'])[i_turn:f_turn]
                self.rawData_V[j,:] = np.squeeze(dict_qmeter['rawDataV'])[i_turn:f_turn]
                self.acqTimeStamp[j] = np.squeeze(dict_qmeter['acqOffset']) + j*np.squeeze(dict_qmeter['acqPeriod'])
        else:
            print("QMeter: reqNbMeas does not correspond to doneNbMeas.")

    def get_fft(self, meas_no=0, plane='H'):
        ''' Use plane='H' for horizontal and plane='V' for vertical
        plane data. '''

        if plane=='H':
            rawData = self.rawData_H[meas_no,:]
        elif plane=='V':
            rawData = self.rawData_V[meas_no,:]
        else:
            print 'unknown plane argument'
            return -1

        n_turns = len(rawData)
        ampl = np.abs(np.fft.rfft(rawData))
        freq = np.fft.rfftfreq(n_turns)

        return freq, ampl

def sdds_to_dict(in_complete_path):
    try:
        temp = sddsdata(in_complete_path, endian='little', full=True)
    except IndexError:
        print 'Failed to open data file.'
        return
    data = temp.data[0]

    filename = in_complete_path.split('/')[-1]
    date_string = in_complete_path.split('/')[-3]
    us_string = filename.split('SPS.USER.')[-1].split('.sdds')[0]
    time_string = filename.split('Acquisition@')[-1].split('@')[0]  

    temp_timest_string = date_string+'_'+time_string
    ms = float(temp_timest_string.split('_')[-1])
    t_stamp_unix = time.mktime(time.strptime(temp_timest_string[:-4], '%Y_%m_%d_%H_%M_%S'))+ms*1e-3
    t_stamp_string = temp_timest_string

    rawDataH = np.float_(data['rawDataH'])
    rawDataV = np.float_(data['rawDataV'])

    deviceName = str(data['deviceName']).split('\n')[0]
    triggerName = str(data['triggerName']).split('\n')[0]
    acqPeriod = np.int(data['acqPeriod'])
    dataMode = np.int(data['dataMode'])
    stopCycleTime = np.int(data['stopCycleTime'])
    requestedNbOfMeas = np.int(data['requestedNbOfMeas'])
    doneNbOfMeas = np.int(data['doneNbOfMeas'])
    cycleNumber = np.int(data['cycleNumber'])
    nbOfTurns = np.int(data['nbOfTurns'])
    acqOffset = np.int(data['acqOffset'])
    cycleLength = np.uint64(data['cycleLength'])
    measStamp = np.int_(data['measStamp'])

    propType = np.int(data['propType'])
    frevSource = np.int(data['frevSource'])
    doneNbOfIRQs = np.int(data['doneNbOfIRQs'])
    observables = np.int(data['observables'])

    exOffset = np.int(data['exOffset'])
    exDelay = np.int(data['exDelay'])
    exPeriod = np.int(data['exPeriod'])
    exMode = np.int(data['exMode'])

    windowFunction = np.int(data['windowFunction'])
    minSearchWindowFreqV = np.float(data['minSearchWindowFreqV'])
    minSearchWindowFreqH = np.float(data['minSearchWindowFreqH'])
    maxSearchWindowFreqV = np.float(data['maxSearchWindowFreqV'])
    maxSearchWindowFreqH = np.float(data['maxSearchWindowFreqH'])
    ring = np.int(data['ring'])

    chirpMode = np.int(data['chirpMode'])
    chirpStartFreqH = np.float(data['chirpStartFreqH'])
    chirpStartFreqV = np.float(data['chirpStartFreqV'])
    chirpStopFreqH = np.float(data['chirpStopFreqH'])
    chirpStopFreqV = np.float(data['chirpStopFreqV'])
    enableExcitationH = np.int(data['enableExcitationH'])
    enableExcitationV = np.int(data['enableExcitationV'])
    excitationAmplitudeV = np.float(data['excitationAmplitudeV'])
    excitationAmplitudeH = np.float(data['excitationAmplitudeH'])

    dict_meas = {
        't_stamp_unix':t_stamp_unix,
        't_stamp_string':t_stamp_string,
        'SPSuser':us_string,
        'deviceName':deviceName,
        'rawDataH':rawDataH,
        'rawDataV':rawDataV,
        'triggerName':triggerName,
        'acqPeriod':acqPeriod,
        'dataMode':dataMode,
        'stopCycleTime':stopCycleTime,
        'requestedNbOfMeas':requestedNbOfMeas,
        'doneNbOfMeas':doneNbOfMeas,
        'cycleNumber':cycleNumber,
        'nbOfTurns':nbOfTurns,
        'acqOffset':acqOffset,
        'cycleLength':cycleLength,
        'measStamp':measStamp,
        'propType':propType,
        'frevSource':frevSource,
        'doneNbOfIRQs':doneNbOfIRQs,
        'observables':observables,
        'exOffset':exOffset,
        'exDelay':exDelay,
        'exPeriod':exPeriod,
        'exMode':exMode,
        'windowFunction':windowFunction,
        'minSearchWindowFreqV':minSearchWindowFreqV,
        'minSearchWindowFreqH':minSearchWindowFreqH,
        'maxSearchWindowFreqV':maxSearchWindowFreqV,
        'maxSearchWindowFreqH':maxSearchWindowFreqH,
        'ring':ring,
        'chirpMode':chirpMode,
        'chirpStartFreqH':chirpStartFreqH,
        'chirpStartFreqV':chirpStartFreqV,
        'chirpStopFreqH':chirpStopFreqH,
        'chirpStopFreqV':chirpStopFreqV,
        'enableExcitationH':enableExcitationH,
        'enableExcitationV':enableExcitationV,
        'excitationAmplitudeV':excitationAmplitudeV,
        'excitationAmplitudeH':excitationAmplitudeH
            }

    return dict_meas

def sdds_to_file(in_complete_path, mat_filename_prefix='SPSmeas_', outp_folder='qmeter/'):

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

def make_mat_files(start_time, end_time='Now', data_folder='/user/slops/data/SPS_DATA/OP_DATA/QMETER/',
				   SPSuser=None, filename_converted='qmeter_converted.txt'):

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
		sdds_folder_list.extend(glob.glob(data_folder + date_string + '/SPSBQSB2@Acquisition/'))

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
