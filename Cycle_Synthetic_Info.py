import timestamp_helpers as th
import numpy as np
import pickle
import os


def extract_cycle_fundamentals(machine_name, t_start_string, t_stop_string):
    import PyTimber
    
    t_start_unix = th.localtime2unixstamp(t_start_string)
    t_stop_unix = th.localtime2unixstamp(t_stop_string)

    ldb=PyTimber.LoggingDB()

    fundamentals_machine = getattr(ldb.tree.Fundamental_Data, machine_name).get_vars()

    dict_machine_fundamentals = {}
    for var in fundamentals_machine:
        print var
        try:
            dict_machine_fundamentals[var] = ldb.get(var, t_start_unix, t_stop_unix)[var]
        except Exception as err:
            print 'Skipped!!!! Got:'
            print err
    
    
    cycles = {}     
    cycles['t_stamp_list'] = []
    cycles['timing_user_list'] = []
    cycles['lsa_user_list'] = []
    cycles['destination_list'] = []


    for var in dict_machine_fundamentals.keys():
        if len(var.split(':'))==3:
            if len(dict_machine_fundamentals[var])>0:
                timing_user = str(var.split(':')[-1])
                lsa_user = str(var.split(':')[-2])
                t_stamp_list_this_cycle = list(dict_machine_fundamentals[var][0])
                destination_list_this_cycle = map(lambda x : str(x.getDestination()), dict_machine_fundamentals[var][1])
            
                N_played = len(t_stamp_list_this_cycle)
            
                cycles['t_stamp_list'] += t_stamp_list_this_cycle
                cycles['timing_user_list'] += N_played*[timing_user]
                cycles['lsa_user_list'] += N_played*[lsa_user]
                cycles['destination_list'] += destination_list_this_cycle
            
                #print th.unixstamp2localtime(np.max(t_stamp_list_this_cycle))


    #print th.unixstamp2localtime(np.max(cycles['t_stamp_list']))
            
    ind_sorted = np.argsort(cycles['t_stamp_list'])
    for kk in cycles.keys():
        cycles[kk] = np.take(cycles[kk], ind_sorted)
    
    cycles['duration_list'] = list(np.diff(np.array(cycles['t_stamp_list'])))

    #remove the last for which I don't have the length
    N_played_all = len(cycles['duration_list'])

    for kk in cycles.keys():
        cycles[kk] = cycles[kk][:N_played_all-1]

    return cycles



def filter_destinations(cycles, destinations_to_keep):
    indices_keep = np.where(map(lambda dest: (dest in destinations_to_keep),  cycles['destination_list']))[0]
    cycles_filtered = {}
    for kk in cycles.keys():
            cycles_filtered[kk] = np.take(cycles[kk], indices_keep)
    return cycles_filtered



def filter_timing_user(cycles, timing_user_to_keep):
    indices_keep = np.where(map(lambda user: (user in timing_user_to_keep),  cycles['timing_user_list']))[0]
    cycles_filtered = {}
    for kk in cycles.keys():
        cycles_filtered[kk] = np.take(cycles[kk], indices_keep)
    return cycles_filtered



def filter_times(cycles, time_start, time_end):
    start = np.searchsorted(cycles['t_stamp_list'], th.localtime2unixstamp(time_start))
    end = np.searchsorted(cycles['t_stamp_list'], th.localtime2unixstamp(time_end))
    cycles_filtered = {}
    for kk in cycles.keys():
        cycles_filtered[kk] = cycles[kk][start:end]
    return cycles_filtered



def add_intensity_to_PS_cycles(cycles_PS):
    import PyTimber
    
    t_start_unix = cycles_PS['t_stamp_list'][0] - 1.
    t_stop_unix = cycles_PS['t_stamp_list'][-1] + 1.


    ldb=PyTimber.LoggingDB()

    var = 'PR.DCBEFEJE_1:INTENSITY'
    data = ldb.get(var, t_start_unix, t_stop_unix)[var]

    t_stamps_inten = data[0]
    inten = data[1]

    N_cycles_PS = len(cycles_PS['t_stamp_list'])

    cycles_PS['intensity_before_extraction'] = N_cycles_PS*[None]
    for ii in xrange(N_cycles_PS):
        pos_min = np.argmin(np.abs(np.array(t_stamps_inten)-cycles_PS['t_stamp_list'][ii]))
        cycles_PS['intensity_before_extraction'][ii] = inten[pos_min]



def add_dynamic_economy_to_SPS_cycles(cycles_SPS):
    import PyTimber

    N_cycles_SPS = len(cycles_SPS['t_stamp_list'])

    cycles_SPS['dynamic_economy_count'] = N_cycles_SPS*[0]

    
    t_start_unix = cycles_SPS['t_stamp_list'][0] - 1.
    t_stop_unix = cycles_SPS['t_stamp_list'][-1] + 1.

    ldb=PyTimber.LoggingDB()

    var = 'SPS:ECONOMY_CYCLE_CNT'
    data = ldb.get(var, t_start_unix, t_stop_unix)[var]

    if data:
        t_stamps_economy = data[0]
        economy_cnt = data[1]

        for i, ts in enumerate(t_stamps_economy):
            try:
                j = cycles_SPS['t_stamp_list'].tolist().index(ts)
                cycles_SPS['dynamic_economy_count'][j] = economy_cnt[i]
            except ValueError:
                print 'timestamp %f of economy counter does not match any SPS cycle' %ts



def add_injections_into_the_SPS(cycles_PS, cycles_SPS):

    cycles_PS_end_time = np.array(cycles_PS['t_stamp_list'])+np.array(cycles_PS['duration_list'])

    N_cycles_SPS = len(cycles_SPS['t_stamp_list'])

    cycles_SPS['PS_cycles_timestamp'] = []
    cycles_SPS['PS_cycles_lsa_user'] = []
    cycles_SPS['PS_cycles_timing_user'] = []
    cycles_SPS['PS_cycles_extracted_intensity'] = []

    for ii in xrange(N_cycles_SPS):
        t_start_present_SPS_cycle = cycles_SPS['t_stamp_list'][ii]
        t_end_present_SPS_cycle = cycles_SPS['t_stamp_list'][ii]+cycles_SPS['duration_list'][ii]
    
        indices_beams_inside = np.where(np.logical_and( cycles_PS_end_time>t_start_present_SPS_cycle, 
                                                        cycles_PS_end_time<t_end_present_SPS_cycle  ))[0]
    
        cycles_SPS['PS_cycles_timestamp'].append([])
        cycles_SPS['PS_cycles_lsa_user'].append([])
        cycles_SPS['PS_cycles_timing_user'].append([])
        cycles_SPS['PS_cycles_extracted_intensity'].append([])
    
        for i_PS in indices_beams_inside:
            if cycles_PS['destination_list'][i_PS] == cycles_SPS['destination_list'][ii]:
                    cycles_SPS['PS_cycles_timestamp'][-1].append(cycles_PS['t_stamp_list'][i_PS])
                    cycles_SPS['PS_cycles_lsa_user'][-1].append(cycles_PS['lsa_user_list'][i_PS])
                    cycles_SPS['PS_cycles_timing_user'][-1].append(cycles_PS['timing_user_list'][i_PS])
                    cycles_SPS['PS_cycles_extracted_intensity'][-1].append(cycles_PS['intensity_before_extraction'][i_PS])

 
    
def make_pickle(date_string, outp_folder='cycle_info', filename_retrieved='cycle_info_retrieved.txt'):

    complete_path = '%s/SPS_cycles_%s.pkl' % (outp_folder, date_string)
    try:
        with open(filename_retrieved, 'r') as fid:
            list_retrieved = fid.read().split('\n')
    except IOError:
        list_retrieved = []
    if complete_path in list_retrieved:
        return

    print 'generating %s' %complete_path

    if not os.path.isdir(outp_folder):
        print 'I create folder: '+ outp_folder
        os.makedirs(outp_folder)

    t_start = date_string+' 00:00:00'
    t_stop = date_string+' 23:59:59'
    cycles = {}
    for machine in ['PS', 'SPS']:
        cycles[machine] = extract_cycle_fundamentals(machine_name=machine, t_start_string=t_start, t_stop_string=t_stop) 
        filter_destinations(cycles=cycles[machine], destinations_to_keep=['SPS_DUMP', 'LHC', 'FTARGET', 'HIRADMAT'])
        if machine == 'PS':
            add_intensity_to_PS_cycles(cycles['PS'])
        elif machine == 'SPS':
            add_injections_into_the_SPS(cycles_PS=cycles['PS'], cycles_SPS=cycles['SPS'])
            add_dynamic_economy_to_SPS_cycles(cycles_SPS=cycles['SPS'])
            
    with open(complete_path, 'wb') as fid:
        pickle.dump(cycles['SPS'], fid)
    
    now = th.time.mktime(th.time.localtime())
    if now - th.localtime2unixstamp(t_stop) > 2*3600:
        with open(filename_retrieved, 'a+') as fid:
            fid.write(complete_path + '\n')



from collections import defaultdict
def load_pickles(file_list):
    
    file_list_sorted = sorted(file_list)
    
    cycles = defaultdict(list)
    for file in file_list_sorted:
        print 'loading file: %s' %file
        with open(file) as fid: 
            d = pickle.load(fid)
        map(lambda key: cycles[key].extend(d[key]), d.keys())

    try:
        assert len(set(len(cycles[key]) for key in cycles.keys())) <= 1
    except AssertionError:
        print '\nERROR: the lists in the cycle dictionary have different length!\n'
    
    return cycles

