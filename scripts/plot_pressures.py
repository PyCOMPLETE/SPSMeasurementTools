import os
import pylab as pl
import time
import mystyle as ms
import numpy as np
import pickle

gauge_list = [50660, 11959, 11879]
# gauge_list = [50660, 10060, 30060, 50060]
comment_list = ['Arc 5', 'MKP', 'TIDVG']
# comment_list = ['Arc 5', '', '', '']

t_ref_str = '13-04-2015 07:00'
t_ref = time.mktime(time.strptime(t_ref_str, '%d-%m-%Y %H:%M'))	

filename='bct_overview.pkl'
with open(filename) as fid:
    beams_bct = pickle.load(fid)
	
filename='press_overview.pkl'
with open(filename) as fid:
    press_dict = pickle.load(fid)
	
pl.close('all')
ms.mystyle_arial(fontsz=16, dist_tick_lab=10)

for ii in range(len(gauge_list)):
    gauge = gauge_list[ii]
    comment = comment_list[ii]

    fig = pl.figure(figsize=(14,12))
    for SPSuser in press_dict.keys():
        beams = press_dict[SPSuser][gauge]

        N_cycles = len(np.array(beams['timestamp_bct']))

	sp1 = pl.subplot(6,1,1)
	pl.plot((np.array(beams_bct[SPSuser]['timestamp_float'])-t_ref)/3600/24., np.array(beams_bct[SPSuser]['bct_max_vect']),'.', label = SPSuser)
	ms.sciy()
	pl.grid('on')
	pl.ylabel('Total int [p+]')
	pl.legend(loc = 'upper left', prop = {'size':14}, bbox_to_anchor=(1,1))
	# pl.ylim(bottom=0)

	# sp2 = pl.subplot(5,1,2, sharex = sp1)
	# pl.plot((np.array(beams_bct[SPSuser]['timestamp_float']) - t_ref)/3600/24., np.array(beams_bct[SPSuser]['bct_1st_inj'])/72.,'.')
	# ms.sciy()
	# pl.grid('on')
	# pl.ylabel('Av. bunch int @1s [p+]')

	sp2 = pl.subplot(6,1,2, sharex = sp1)
	pl.plot((np.array(beams_bct[SPSuser]['timestamp_float']) - t_ref)/3600/24., np.array(beams_bct[SPSuser]['bct_integrated']),'.')
	ms.sciy()
	pl.grid('on')
	pl.ylabel('BCT integ [p*s]')

	press_rise = np.array(beams['press_max']) - np.array(beams['press_min'])
	press_max = np.array(beams['press_max'])
	press_min = np.array(beams['press_min'])
	press_av = np.array(beams['press_av'])

	sp3 = pl.subplot(6,1,3, sharex = sp1)
	pl.plot((np.array(beams['timestamp_bct']) - t_ref)/3600/24., press_max,'.')
	pl.ylim(0, 1e-6)
	ms.sciy()
	pl.grid('on')
	pl.ylabel('Press %s [mbar]'%'max')

	sp4 = pl.subplot(6,1,4, sharex = sp1)
	pl.plot((np.array(beams['timestamp_bct']) - t_ref)/3600/24., press_min,'.')
	# pl.ylim(0, 2e-7)
	ms.sciy()
	pl.grid('on')
	pl.ylabel('Press %s [mbar]'%'min')

	sp5 = pl.subplot(6,1,5, sharex = sp1)
	pl.plot((np.array(beams['timestamp_bct']) - t_ref)/3600/24., press_rise,'.')
	# pl.ylim(0, 2e-7)
	# pl.ylim(bottom=0)
	ms.sciy()
	pl.grid('on')
	pl.ylabel('Press %s [mbar]'%'rise')
	
	sp6 = pl.subplot(6,1,6, sharex = sp1)
	thresh_beam = 1e12
	# mask_tstamps = []
	# for iit in xrange(len(beams['timestamp_bct'])):
		# mask_tstamps.append(beams['timestamp_bct'][iit] in beams_bct[SPSuser]['timestamp_float'])
	# mask_tstamps = np.array(mask_tstamps)
	# mask_beam = beams_bct[SPSuser]['bct_max_vect'][mask_tstamps] > thresh_beam
	intensity_at_pressures = np.interp(beams['timestamp_bct'],beams_bct[SPSuser]['timestamp_float'],beams_bct[SPSuser]['bct_max_vect'])
	mask_beam = intensity_at_pressures>thresh_beam
	pl.plot((np.array(beams['timestamp_bct'])[mask_beam] - t_ref)/3600/24., press_rise[mask_beam]/intensity_at_pressures[mask_beam],'.')
	pl.ylim(bottom=0)
	#pl.ylim(0, 5e-21)
	ms.sciy()
	pl.grid('on')
	pl.ylabel("Norm. pressure rise")
	pl.ylabel('Press %s [mbar]'%'rise')

    pl.subplots_adjust(left=.12, bottom=.10, right=.84, top=.94, hspace=.32)
    pl.suptitle('gauge %d %s pressure from %s'%(gauge, comment,  t_ref_str))
    pl.savefig('W16_press_evol_%s'%(gauge), dpi=200)
    # ff.set_size_inches(15.725 ,  11.1875)

pl.show()
