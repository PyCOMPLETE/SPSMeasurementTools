import os
import pylab as pl
import time
import mystyle as ms
import numpy as np
import pickle

t_ref_str = '13-04-2015 07:00'
t_ref = time.mktime(time.strptime(t_ref_str, '%d-%m-%Y %H:%M'))	

filename='bct_overview.pkl'
with open(filename) as fid:
    beams_bct = pickle.load(fid)
	
filename='ws_overview.pkl'
with open(filename) as fid:
    ws_dict = pickle.load(fid)
	
list_SPSusers = [ 'MD3' ]

pl.close('all')
ms.mystyle_arial(fontsz=16, dist_tick_lab=10)
fig = pl.figure(figsize=(14,12))

for SPSuser in list_SPSusers:
    n_ws_meas = len(ws_dict[SPSuser]['timestamp_ws'])

    for ii in range(n_ws_meas):
        try:
            pl.clf()
            sp1 = pl.subplot2grid((3,2), (0,0), colspan=2, rowspan=1)
            for SPSuser_ in beams_bct.keys():
                pl.plot((np.array(beams_bct[SPSuser_]['timestamp_float'])-t_ref)/3600/24., np.array(beams_bct[SPSuser_]['bct_max_vect']),'.', label=SPSuser_)
        
            timestamp_bct = ws_dict[SPSuser]['timestamp_bct'][ii]
            timestamp_ws = ws_dict[SPSuser]['timestamp_ws'][ii]
            sp1.axvline(x=(timestamp_bct- t_ref)/24./3600, color = 'k', linestyle='--', linewidth = 3)
        
            ms.sciy()
            pl.grid('on')
            pl.ylabel('Total int [p+]')
            pl.xlabel('Time [days]')
            pl.legend(loc='upper left', prop = {'size':14}, bbox_to_anchor=(1,1))

            sp2 = pl.subplot2grid((3,2), (1,0), colspan=1, rowspan=1)
            pl.plot(np.array(ws_dict[SPSuser]['bunch_list'][ii]), np.array(ws_dict[SPSuser]['norm_emit_in'][ii])*1e6, '.-g') 
            pl.plot(np.array(ws_dict[SPSuser]['bunch_list'][ii]), np.array(ws_dict[SPSuser]['norm_emit_out'][ii])*1e6, '.-m')
            pl.grid('on')
            pl.ylabel('Norm. emit. [um]')
            pl.xlabel('25ns slot')

            sp3 = pl.subplot2grid((3,2), (2,0), colspan=1, rowspan=1)
            pl.plot(np.array(ws_dict[SPSuser]['bunch_list'][ii]), np.array(ws_dict[SPSuser]['area_in'][ii])*1e6, '.-g')
            pl.plot(np.array(ws_dict[SPSuser]['bunch_list'][ii]), np.array(ws_dict[SPSuser]['area_out'][ii])*1e6, '.-m')
            pl.grid('on')
            pl.ylabel('Area [a.u.]')
            pl.xlabel('25ns slot')

#	sp2 = pl.subplot(5,1,2, sharex = sp1)
#	pl.plot((np.array(beams_bct[SPSuser]['timestamp_float']) - t_ref)/3600/24., np.array(beams_bct[SPSuser]['bct_integrated']),'.')
#	ms.sciy()
#	pl.grid('on')
#	pl.ylabel('BCT integ [p*s]')

            pl.subplots_adjust(left=.12, bottom=.10, right=.84, top=.90, hspace=.32)
            device_name = ws_dict[SPSuser]['device_name'][ii]
            pl.suptitle('Wirescan %s, timestamp_bct=%d, timestamp_ws=%d\nfrom %s'%(device_name, timestamp_bct,
                                                                                   timestamp_ws, t_ref_str))
            pl.savefig('ws_pngs_test/ws_%s_%s_%d.png'%(SPSuser, device_name, timestamp_ws), dpi=100)
        except Exception as err:
            with open('ws_errors.txt', 'a+') as fid:
                fid.write('%s %s %d %d %s'%(SPSuser, device_name, timestamp_ws, timestamp_bct, err.message) + '\n')
            
    # ff.set_size_inches(15.725 ,  11.1875)

#pl.show()
