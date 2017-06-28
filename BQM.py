import lhc_log_db_query as lldb
import timber_manag3 as tm
import timestamp_helpers as th
from zip_mat import save_zip
#~ from optics_and_betagamma import beta_opt_lib, retrieve_betagamma
#~ 
import os
#~ import time
import numpy as np
import scipy.io as sio
#~ import scipy.optimize as op
import shutil
import gzip
#~ import pickle

       

class BQM(object):

    def __init__(self, complete_path):

        temp_filename = complete_path.split('.gz')[0] + 'uzipd'
        with open(temp_filename, "wb") as tmp:
            shutil.copyfileobj(gzip.open(complete_path), tmp)
        dict_bqm = sio.loadmat(temp_filename)
        os.remove(temp_filename)
        
        self.attenuator_ppm_setting = np.int(np.squeeze(dict_bqm['attenuator_ppm_setting']))
        self.filled_buckets = np.squeeze(dict_bqm['filled_buckets'])
        self.raw_waveform_inj = dict_bqm['raw_waveform_inj'][0]
        
        self.dict_bqm = dict_bqm
        print dict_bqm.keys()  
#~ 
        #~ self.bunch_selection = np.squeeze(dict_ws['bunchSelection'])
        #~ self.bunch_list = self._bunchSelection2bunchList()
        #~ #self.bunch_list_timber = np.squeeze(dict_ws['bunchListTimber'])
        #~ self.device_name = str(dict_ws['device_name'][0])
        #~ self.gain = np.float_(np.squeeze(dict_ws['gain']))
        #~ self.t_stamp_unix = np.float_(np.squeeze(dict_ws['t_stamp_unix']))
        #~ self.cycle_time = str(dict_ws['cycleTime'][0])
        #~ self.acq_time = str(dict_ws['acqTime'][0])
        #~ self.acq_delay = np.float_(np.squeeze(dict_ws['acqDelay']))
        #~ self.acq_type = np.int_(np.squeeze(dict_ws['acqType']))
        #~ #self.beta_fct = np.squeeze(dict_ws['beta'])
        #~ #self.energy_in = np.squeeze(dict_ws['energy1'])
        #~ #self.energy_out = np.squeeze(dict_ws['energy2'])
#~ 
        #~ if self.acq_type == 1:
            #~ self.n_bunches = 1
            #~ #self.bunch_list_timber = np.array([0])
        #~ else:
            #~ self.n_bunches = np.int_(np.squeeze(dict_ws['nbBunches']))
#~ 
        #~ # Scan 'in'
        #~ self.acq_time_in_cycle_set_in = np.float_(np.squeeze(dict_ws['acqTimeInCycleSet1']))
        #~ self.proj_position_set_in = np.float_(np.squeeze(dict_ws['projPositionSet1']))
        #~ if self.acq_type == 1:
            #~ self.proj_profile_set_in = np.float_(np.squeeze(dict_ws['projDataSet1']))
        #~ else:
            #~ self.proj_profile_set_in = np.reshape(np.float_(np.squeeze(dict_ws['projBunchDataSet1'])), (self.n_bunches, -1))
#~ 
        #~ self._p0_in = [None for i in xrange(self.n_bunches)]
        #~ self.p1_in = [None for i in xrange(self.n_bunches)]
        #~ self.sigma_in = [None for i in xrange(self.n_bunches)]
        #~ self.phys_emit_in = [None for i in xrange(self.n_bunches)]
        #~ self.norm_emit_in = [None for i in xrange(self.n_bunches)]
        #~ self.area_in = [None for i in xrange(self.n_bunches)]
#~ 
        #~ # Scan 'out'
        #~ self.acq_time_in_cycle_set_out = np.float_(np.squeeze(dict_ws['acqTimeInCycleSet2']))
        #~ self.proj_position_set_out = np.float_(np.squeeze(dict_ws['projPositionSet2']))
        #~ if self.acq_type == 1:
            #~ self.proj_profile_set_out = np.float_(np.squeeze(dict_ws['projDataSet2']))
        #~ else:
            #~ self.proj_profile_set_out = np.reshape(np.float_(np.squeeze(dict_ws['projBunchDataSet2'])), (self.n_bunches, -1))
#~ 
        #~ self._p0_out = [None for i in xrange(self.n_bunches)]
        #~ self.p1_out = [None for i in xrange(self.n_bunches)]
        #~ self.sigma_out = [None for i in xrange(self.n_bunches)]
        #~ self.phys_emit_out = [None for i in xrange(self.n_bunches)]
        #~ self.norm_emit_out = [None for i in xrange(self.n_bunches)]
        #~ self.area_out = [None for i in xrange(self.n_bunches)]
#~ 
        #~ if init_with_fits:
            #~ self.compute_fits(self.scans_in, self.scans_out)
#~ 
        #~ if (self.optics is not None) and (self.cycle_csv_filepath is not None):
                #~ self.beta_opt = beta_opt_lib[self.device_name +':'+ self.optics]
                #~ self.betagamma_in = retrieve_betagamma(self.cycle_csv_filepath, self.acq_time_in_cycle_set_in)
                #~ self.betagamma_out = retrieve_betagamma(self.cycle_csv_filepath, self.acq_time_in_cycle_set_out)
                #~ self.compute_emittances()
#~ 
    #~ def get_fitted_profile_in(self, bunch_index=0):
        #~ return self._fitfunc(self.p1_in[bunch_index], self.proj_position_set_in)
#~ 
    #~ def get_fitted_profile_out(self, bunch_index=0):
        #~ return self._fitfunc(self.p1_out[bunch_index], self.proj_position_set_out)
#~ 
    #~ def _bunchSelection2bunchList(self):
        #~ '''
        #~ The bunch_selection variable stores the selected bunch pattern
        #~ in binary form (two's complement). Each entry in the
        #~ bunch_selection list corresponds to 32 bunch slots (32 bit
        #~ pattern), i.e. entry 0 describes bunches 0-31, entry 1 bunches
        #~ 32-63, etc. The binary patterns are read from the right and they
        #~ must be padded to 32 bits from the left. To generate the full
        #~ boolean mask, the 32 bit patterns (corresponding to one of the
        #~ entries in the bunch_selection list) are reversed and
        #~ concatenated. The mask tells us, which of the bunch slots were
        #~ selected for measurements assuming the following order [ 1, 2, 3,
        #~ ...  32*len(bunch_selection) + 1 ].
        #~ '''
        #~ bin_list = ''
        #~ for selection in self.bunch_selection:
            #~ bin_list += ((bin(selection % (1<<32))[2:]).rjust(32, '0'))[::-1]
        #~ mask = np.bool_(np.array(list(bin_list)))
        #~ return np.array(range(1, 32*len(self.bunch_selection)+1))[mask]
#~ 
    #~ def _compute_single_fit(self, x, y, N_points_ma):
        #~ try:
            #~ if x[-1]<x[0]:
                #~ x=x[::-1]
                #~ y=y[::-1]
#~ 
            #~ indx_max = np.argmax(y)
            #~ mu0 = x[indx_max]
            #~ window = 2*N_points_ma
            #~ x_tmp = x[indx_max-window:indx_max+window]
            #~ y_tmp = y[indx_max-window:indx_max+window]
            #~ offs0 = min(y_tmp)
            #~ ampl = max(y_tmp)-offs0
            #~ x1 = x_tmp[np.searchsorted(y_tmp[:window], offs0+ampl/2)]
            #~ x2 = x_tmp[np.searchsorted(-y_tmp[window:], -offs0+ampl/2)]
            #~ FWHM = x2-x1
            #~ sigma0 = FWHM/2.355
#~ 
            #~ p0 = [offs0,  ampl, mu0, sigma0,0.]
            #~ p1, success = op.leastsq(self._errfunc, p0[:], args=(x,y))
            #~ if not success:
                #~ raise ValueError
        #~ except:
            #~ p0 = 4 * [0.]
            #~ p1 = 4 * [0.]
#~ 
        #~ return p0, p1
#~ 
    #~ def compute_fits(self, scans_in=True, scans_out=False, N_points_ma=50):
        #~ if scans_in:
            #~ for i in xrange(self.n_bunches):
                #~ if self.acq_type == 1:
                    #~ proj_prof = self.proj_profile_set_in
                #~ else:
                    #~ proj_prof = self.proj_profile_set_in[i]
                #~ self._p0_in[i], self.p1_in[i] = self._compute_single_fit(self.proj_position_set_in, proj_prof, N_points_ma)
                #~ self.sigma_in[i] = abs(self.p1_in[i][3]*1e-6)
                #~ self.area_in[i] = abs(self.p1_in[i][1]*self.p1_in[i][3])
#~ 
        #~ if self.scans_out:
            #~ for i in xrange(self.n_bunches):
                #~ if self.acq_type == 1:
                    #~ proj_prof = self.proj_profile_set_out
                #~ else:
                    #~ proj_prof = self.proj_profile_set_out[i]
                #~ self._p0_out[i], self.p1_out[i] = self._compute_single_fit(self.proj_position_set_out, self.proj_profile_set_out[i], N_points_ma)
                #~ self.sigma_out[i] = abs(self.p1_out[i][3]*1e-6)
                #~ self.area_out[i] = abs(self.p1_out[i][1]*self.p1_out[i][3])
#~ 
    #~ def compute_emittances(self):
#~ 
        #~ if self.scans_in:
            #~ if self.p1_in == None:
                #~ self.compute_fits(self.scans_in, False)
            #~ self.phys_emit_in = np.array(self.sigma_in)**2/self.beta_opt
            #~ self.norm_emit_in = self.betagamma_in*self.phys_emit_in
            #~ self.phys_emit_in[np.array(self.sigma_in)==0] = 0.
            #~ self.norm_emit_in[np.array(self.sigma_in)==0] = 0.
#~ 
        #~ if self.scans_out:
            #~ if self.p1_out == None:
                #~ self.compute_fits(False, self.scans_out)
            #~ self.phys_emit_out = np.array(self.sigma_out)**2/self.beta_opt
            #~ self.norm_emit_out = self.betagamma_out*self.phys_emit_out
            #~ self.phys_emit_out[np.array(self.sigma_out)==0] = 0.
            #~ self.norm_emit_out[np.array(self.sigma_out)==0] = 0.


def timber_to_csv(start_time, end_time='Now', filename_prefix='SPSmeas_', outp_folder=None,
                  t_query_interval=1800., t_query_interval_fine=60.,
                  filename_retrieved='bqm_retrieved.txt'):

    try:
        with open(filename_retrieved, 'r') as fid:
            list_retrieved = fid.read().split('\n')
    except IOError:
        list_retrieved = []

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

    if outp_folder == None:
        outp_folder = 'BQM_CSVfromTimberDB'

    if not os.path.exists(outp_folder):
        os.makedirs(outp_folder)

    varlist = get_timber_varlist()
    print 'VARLIST', varlist
    t_queries = np.arange(start_tstamp_unix, end_tstamp_unix, t_query_interval)
 
    for t_query in t_queries:
        outp_compl_path = outp_folder + '/' + filename_prefix + '%d_%d.csv'%(t_query, t_query_interval)
        if outp_compl_path in list_retrieved:
            continue
        lldb.dbquery(varlist, t_query, t_query+t_query_interval, outp_compl_path)
        with open(filename_retrieved, 'a+') as fid:
            fid.write(outp_compl_path + '\n')

        # In case something goes wrong with the request -> use a shorter interval.
        if not os.path.exists(outp_compl_path):
            t_queries_fine = np.arange(t_query, t_query + t_query_interval, t_query_interval_fine)
            for t_query_fine in t_queries_fine:
                time_str = (th.unixstamp2localtime(t_query_fine)).replace(' ', '_')
                outp_compl_path = outp_folder + '/' + filename_prefix + '%d_%d.csv'%(t_query_fine, t_query_interval_fine)
                if outp_compl_path in list_retrieved:
                    continue
                lldb.dbquery(varlist, t_query_fine, t_query_fine+t_query_interval_fine, outp_compl_path)
                with open(filename_retrieved, 'a+') as fid:
                    fid.write(outp_compl_path + '\n')

                if not os.path.exists(outp_compl_path):
                    print '!!! WARNING: Could not retrieve data in %s, %d s'%(time_str, t_query_interval_fine)


def csv_to_file(in_complete_path, mat_filename_prefix='SPSmeas_', outp_folder='bqm',
                filename_converted='bqm_converted.txt'):

    try:
        with open(filename_converted, 'r') as fid:
            list_converted = fid.read().split('\n')
    except IOError:
        list_converted = []
    if in_complete_path in list_converted:
        return

    variables = tm.parse_timber_file(in_complete_path, verbose=False)

    N_meas = len(variables['SPS.BQM:NO_BUNCHES'].t_stamps)
    for i in [0]: #xrange(N_meas):
        dict_meas = {\
            'attenuator_ppm_setting': np.int_(variables['SPS.APWL.ATTENUATOR:PPM_SETTING'].values[i][0]),
            #~ 'beam_ok': variables['SPS.BQM:BEAM_OK'].values[i][0],
            #'no_bunches': variables['SPS.BQM:NO_BUNCHES'].values[i][0],
            #'bunch_intensities': variables['SPS.BQM:BUNCH_INTENSITIES'].values[i],
            #~ 'bunch_intensity_max_thresh': variables['SPS.BQM:BUNCH_INTENSITY_MAX_THRESH'].values[i][0],
            #~ 'bunch_intensity_min_thresh': variables['SPS.BQM:BUNCH_INTENSITY_MIN_THRESH'].values[i][0],
            #'bunch_intensity_ok': variables['SPS.BQM:BUNCH_INTENSITY_OK'].values[i][0],
            #'bunch_lengths': variables['SPS.BQM:BUNCH_LENGTHS'].values[i],
            #'bunch_lengths_inj': variables['SPS.BQM:BUNCH_LENGTHS_INJ'].values[i],
            #~ 'bunch_lengths_inj_max_thresh': variables['SPS.BQM:BUNCH_LENGTH_INJ_MAX_THRESH'].values[i][0],
            #~ 'bunch_length_max_thresh': variables['SPS.BQM:BUNCH_LENGTH_MAX_THRESH'].values[i][0],
            #~ 'bunch_length_min_thresh': variables['SPS.BQM:BUNCH_LENGTH_MIN_THRESH'].values[i][0],
            #~ 'bunch_length_ok': variables['SPS.BQM:BUNCH_LENGTH_OK'].values[i][0],
            #~ 'bunch_length_stddev_ok': variables['SPS.BQM:BUNCH_LENGTH_STDDEV_OK'].values[i][0],
            #~ 'bunch_length_stddev_thresh': variables['SPS.BQM:BUNCH_LENGTH_STDDEV_THRESH'].values[i][0],
            #~ 'bunch_pattern_ok': variables['SPS.BQM:BUNCH_PATTERN_OK'].values[i][0],
            #'bunch_peaks': variables['SPS.BQM:BUNCH_PEAKS'].values[i],
            #'bunch_peaks_inj': variables['SPS.BQM:BUNCH_PEAKS_INJ'].values[i],
            #~ 'bunch_peak_max_thresh': variables['SPS.BQM:BUNCH_PEAK_MAX_THRESH'].values[i][0],
            #~ 'bunch_peak_min_thresh': variables['SPS.BQM:BUNCH_PEAK_MIN_THRESH'].values[i][0],
            #'bunch_peak_ok': variables['SPS.BQM:BUNCH_PEAK_OK'].values[i][0],
            #'bunch_peak_stddev_ok': variables['SPS.BQM:BUNCH_PEAK_STDDEV_OK'].values[i][0],
            #~ 'bunch_peak_stddev_thresh': variables['SPS.BQM:BUNCH_PEAK_STDDEV_THRESH'].values[i][0],
            #'bunch_positions': variables['SPS.BQM:BUNCH_POSITIONS'].values[i],
            #'bunch_positions_inj': variables['SPS.BQM:BUNCH_POSITIONS_INJ'].values[i],
            #'diagnostics': variables['SPS.BQM:DIAGNOSTIC'].values[i][0],
            #'doublets': variables['SPS.BQM:DOUBLETS'].values[i][0],
            #'doublets_int_splits': variables['SPS.BQM:DOUBLET_INT_SPLITS'].values[i],
            #'doublets_int_splits_max_thres': variables['SPS.BQM:DOUBLET_INT_SPLIT_MAX_THRESH'].values[i][0],
            #'doublets_int_splits_min_thres': variables['SPS.BQM:DOUBLET_INT_SPLIT_MIN_THRESH'].values[i][0],
            #~ 'dump_enabled': variables['SPS.BQM:DUMP_ENABLED'].values[i][0],
            #'doublets_int_splits_ok': variables['SPS.BQM:DOUBLET_INT_SPLIT_OK'].values[i][0],
            'filled_buckets': np.int_(np.float_(variables['SPS.BQM:FILLED_BUCKETS'].values[i])),
            #'first_bunch_pos_inj_ok': variables['SPS.BQM:FIRST_BUNCH_POS_INJ_OK'].values[i][0],
            'raw_waveform_inj': np.float_(variables['SPS.BQM:RAW_WAVEFORM_INJ'].values[i]),
			}
            
        
        t_stamp_unix = variables['SPS.BQM:NO_BUNCHES'].t_stamps[i]
        out_filename = mat_filename_prefix + 'SPS.BQM' + ('_%d'%t_stamp_unix)
        out_complete_path = outp_folder +'/'+ out_filename
        print out_complete_path

        if not os.path.isdir(outp_folder):
            print 'I create folder: '+ outp_folder
            os.makedirs(outp_folder)

        sio.savemat(out_complete_path, dict_meas, oned_as='row')
        save_zip(out_complete_path)
'''
    with open(filename_converted, 'a+') as fid:
        fid.write(in_complete_path + '\n')
'''

def make_mat_files(start_time, end_time='Now', csv_data_folder='BQM_CSVfromTimberDB',
                   filename_converted='bqm_converted.txt', filename_retrieved='bqm_retrieved.txt'):

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

    # 1. Retrieve from timber and save as .csv.
    timber_to_csv(start_tstamp_unix, end_tstamp_unix, outp_folder=csv_data_folder,
                  filename_retrieved=filename_retrieved)

    # 2. Convert from csv to mat in given range.
    file_list = os.listdir(csv_data_folder)
    for filename in file_list:
        tstart_filename = int(filename.split('.csv')[0].split('_')[-2])
        tend_filename = tstart_filename + int(filename.split('.csv')[0].split('_')[-1])

        if (tend_filename < start_tstamp_unix) or (tstart_filename > end_tstamp_unix):
            continue
        in_complete_path = csv_data_folder + '/' + filename
        csv_to_file(in_complete_path, filename_converted=filename_converted)

'''
def make_pickle(start_from_last=True, pickle_name_ws='ws_overview.pkl', pickle_name_bct='bct_overview.pkl',
                mat_folder='wirescanner', mat_file_prefix='SPSmeas_', inj_delay_to_cycle_start=1015e-3,
                cycle_csv_filepath='SPSMeasurementTools/cycle_momenta/MD_SCRUB_26_L26400_Q20_2014_V1.csv'):

    if not os.path.isfile(pickle_name_bct):
        raise RuntimeError('Must have BCT pickle.')
    with open(pickle_name_bct, 'rb') as fid:
        beams = pickle.load(fid)

    if os.path.isfile(pickle_name_ws) or start_from_last:
        with open(pickle_name_ws) as fid:
                ws_dict = pickle.load(fid)
    else:
        ws_dict = {}

    for SPSuser in beams.keys():
        if not(SPSuser in ws_dict.keys()):
            ws_dict[SPSuser] = {}
            ws_dict[SPSuser]['timestamp_bct'] = []
            ws_dict[SPSuser]['timestamp_ws'] = []
            ws_dict[SPSuser]['device_name'] = []
            ws_dict[SPSuser]['bunch_list'] = []
            ws_dict[SPSuser]['norm_emit_in'] = []
            ws_dict[SPSuser]['norm_emit_out'] = []
            ws_dict[SPSuser]['area_in'] = []
            ws_dict[SPSuser]['area_out'] = []
            ws_dict[SPSuser]['acq_time_in_cycle_set_in'] = []
            ws_dict[SPSuser]['acq_time_in_cycle_set_out'] = []
            ws_dict[SPSuser]['acq_type'] = []

    list_files = os.listdir(mat_folder)
    n_files = len(list_files)
    n_files_no_bct = 0
    if n_files == 0:
        print('No ws mat files found.')

    for ctr, filename in enumerate(list_files):
        print('Processing file %d/%d'%(ctr, n_files))
        wsobj = WireScan(mat_folder +'/'+ filename, optics='Q20', cycle_csv_filepath=cycle_csv_filepath,
                         scans_in=True, scans_out=True)
        t_stamp = th.localtime2unixstamp(wsobj.acq_time.split('.')[0], strformat='%Y/%m/%d %H:%M:%S')

        t_stamp_bct = None
        SPSuser = None
        guess_t_stamp_bct = int(t_stamp - inj_delay_to_cycle_start - wsobj.acq_time_in_cycle_set_in/1000.)
        for SPSuser_loop in beams.keys():
            t_stamps_bct = np.int_(beams[SPSuser_loop]['timestamp_float'])
            for jj in xrange(4, -1, -1):
                idx_tstamp = np.where(t_stamps_bct == (guess_t_stamp_bct+jj))[0]
                if len(idx_tstamp) == 1:
                    t_stamp_bct = t_stamps_bct[idx_tstamp]
                    SPSuser = SPSuser_loop
                    break
            if not(t_stamp_bct == None):
                break
#            mask_past = np.array(t_stamps_bct) <= t_stamp
#            if any(mask_past):
#                t_stamp_bct_curr = np.max(np.array(t_stamps_bct)[mask_past])
#                if t_stamp_bct is None:
#                    t_stamp_bct = t_stamp_bct_curr
#                    SPSuser = SPSuser_loop
#                elif t_stamp_bct_curr > t_stamp_bct:
#                    t_stamp_bct = t_stamp_bct_curr
#                    SPSuser = SPSuser_loop
        if t_stamp_bct == None:
            print('No corresponding BCT time stamp found')
            n_files_no_bct += 1
            continue

        if start_from_last and len(ws_dict[SPSuser]['timestamp_ws']) > 0:
            if t_stamp <= ws_dict[SPSuser]['timestamp_ws'][-1]:
                continue
        elif t_stamp in ws_dict[SPSuser]['timestamp_ws']:
            continue

#        if np.abs(t_stamp - t_stamp_bct) > 30:
#            print('WARNING: WS time stamp differs from BCT time stamp by more ' +
#                  'than 30s! Difference is %ds. Saving anyway.'%np.abs(t_stamp-t_stamp_bct))

        ws_dict[SPSuser]['timestamp_bct'].append(t_stamp_bct)
        ws_dict[SPSuser]['timestamp_ws'].append(t_stamp)
        ws_dict[SPSuser]['device_name'].append(wsobj.device_name)
        ws_dict[SPSuser]['bunch_list'].append(wsobj.bunch_list)
        # ws_dict[SPSuser]['bunch_list'].append(wsobj.bunch_list_timber)
        ws_dict[SPSuser]['norm_emit_in'].append(wsobj.norm_emit_in)
        ws_dict[SPSuser]['norm_emit_out'].append(wsobj.norm_emit_out)
        ws_dict[SPSuser]['area_in'].append(wsobj.area_in)
        ws_dict[SPSuser]['area_out'].append(wsobj.area_out)
        ws_dict[SPSuser]['acq_time_in_cycle_set_in'].append(wsobj.acq_time_in_cycle_set_in/1000.-inj_delay_to_cycle_start)
        ws_dict[SPSuser]['acq_time_in_cycle_set_out'].append(wsobj.acq_time_in_cycle_set_out/1000.-inj_delay_to_cycle_start)
        ws_dict[SPSuser]['acq_type'].append(wsobj.acq_type)

    # Sort for ws timestamps.
    for SPSuser in beams.keys():
        ind_sorted = np.argsort(ws_dict[SPSuser]['timestamp_ws'])
        for kk in ws_dict[SPSuser].keys():
            ws_dict[SPSuser][kk] = list(np.take(ws_dict[SPSuser][kk], ind_sorted))

    with open(pickle_name_ws, 'wb') as fid:
        pickle.dump(ws_dict, fid)
    
    print('Done! %d files could not be matched to a BCT timestamp.'%n_files_no_bct)

'''
def get_timber_varlist():

    varlist = [\
        'SPS.APWL.ATTENUATOR:PPM_SETTING',
        #~ 'SPS.APWL.ATTENUATOR:SETTING',
        #~ 'SPS.BQM:1ST_BUNCH_INJ',
        #~ 'SPS.BQM:1ST_BUNCH_POS_FRACT',
        #~ 'SPS.BQM:1ST_BUNCH_POS_OK',
        'SPS.BQM:BEAM_OK',
        'SPS.BQM:BUNCH_INTENSITIES',
        'SPS.BQM:BUNCH_INTENSITY_MAX_THRESH',
        'SPS.BQM:BUNCH_INTENSITY_MIN_THRESH',
        'SPS.BQM:BUNCH_INTENSITY_OK',
        'SPS.BQM:BUNCH_LENGTHS',
        'SPS.BQM:BUNCH_LENGTHS_INJ',
        'SPS.BQM:BUNCH_LENGTH_INJ_MAX_THRESH',
        'SPS.BQM:BUNCH_LENGTH_MAX_THRESH',
        'SPS.BQM:BUNCH_LENGTH_MIN_THRESH',
        'SPS.BQM:BUNCH_LENGTH_OK',
        'SPS.BQM:BUNCH_LENGTH_STDDEV_OK',
        'SPS.BQM:BUNCH_LENGTH_STDDEV_THRESH',
        'SPS.BQM:BUNCH_PATTERN_OK',
        'SPS.BQM:BUNCH_PEAKS',
        'SPS.BQM:BUNCH_PEAKS_INJ',
        'SPS.BQM:BUNCH_PEAK_MAX_THRESH',
        'SPS.BQM:BUNCH_PEAK_MIN_THRESH',
        #~ 'SPS.BQM:BUNCH_PEAK_MOD_INDEX',
        #~ 'SPS.BQM:BUNCH_PEAK_MOD_INDEX_OK',
        #~ 'SPS.BQM:BUNCH_PEAK_MOD_INDEX_THRESH',
        'SPS.BQM:BUNCH_PEAK_OK',
        'SPS.BQM:BUNCH_PEAK_STDDEV_OK',
        'SPS.BQM:BUNCH_PEAK_STDDEV_THRESH',
        'SPS.BQM:BUNCH_POSITIONS',
        'SPS.BQM:BUNCH_POSITIONS_INJ',
        'SPS.BQM:DIAGNOSTIC',
        'SPS.BQM:DOUBLETS',
        'SPS.BQM:DOUBLET_INT_SPLITS',
        'SPS.BQM:DOUBLET_INT_SPLIT_MAX_THRESH',
        'SPS.BQM:DOUBLET_INT_SPLIT_MIN_THRESH',
        'SPS.BQM:DOUBLET_INT_SPLIT_OK',
        'SPS.BQM:DUMP_ENABLED',
        'SPS.BQM:FILLED_BUCKETS',
        'SPS.BQM:FIRST_BUNCH_POS_INJ_OK',
        'SPS.BQM:NO_BUNCHES',
        #~ 'SPS.BQM:NO_SATELLITES_INT',
        #~ 'SPS.BQM:NO_SATELLITES_MID_BUCKET',
        #~ 'SPS.BQM:N_ALLOWED_LONG_BUNCHES',
        #~ 'SPS.BQM:OSCILLATION_DELTA_PCT',
        #~ 'SPS.BQM:OSCILLATION_DELTA_PCT_THRESH',
        #~ 'SPS.BQM:OSCILLATION_PEAK_PCT',
        #~ 'SPS.BQM:OSCILLATION_PEAK_THRESH_PCT',
        #~ 'SPS.BQM:RAW_WAVEFORM_FLATTOP',
        'SPS.BQM:RAW_WAVEFORM_INJ',
        #~ 'SPS.BQM:RAW_WAVEFORM_RAMP',
        #~ 'SPS.BQM:SATELLITES_INT_THRESH',
        #~ 'SPS.BQM:SATELLITES_MID_BUCKET_THRESH',
        #~ 'SPS.BQM:SATELLITES_OK',
        #~ 'SPS.BQM:STABILITY_OK',
        #~ 'SPS.BQM:WHICH_WAVEFORM_INJ'\
        ]

    return varlist

