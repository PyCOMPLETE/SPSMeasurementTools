import os
from numpy import array, squeeze, take
import pylab as pl
import time
import mystyle as ms
import numpy as np
import pickle

t_ref_str = '13-04-2015 07:00'
t_ref = time.mktime(time.strptime(t_ref_str, '%d-%m-%Y %H:%M'))	

filename = 'bct_overview.pkl'
with open(filename) as fid:
	beams_bct = pickle.load(fid)

filename='ecm_overview.pkl'
with open(filename) as fid:
	beams_ecm = pickle.load(fid)
	
# ylim_ec_max = 3.5e5
# thresh_max_good_shot = 1.1e11

pl.close('all')
ms.mystyle_arial(fontsz=13, dist_tick_lab=10)
#ms.mystyle(fontsz=13)

for ecm_id in '1a 1b 2a 2b'.split():

	fig = pl.figure()
	for SPS_user in beams_ecm[ecm_id].keys():

		N_cycles = len(np.array(beams_bct[SPS_user]['bct_1st_inj']))

      		# mask_good_shots = np.array(beams_bct[SPS_user]['bct_max_vect']) > thresh_max_good_shot

		sp1 = pl.subplot(4,1,1)
		pl.plot((array(beams_bct[SPS_user]['timestamp_float'])-t_ref)/3600./24., array(beams_bct[SPS_user]['bct_max_vect']),'.', label = SPS_user)
		ms.sciy()
		pl.grid('on')
		pl.ylabel('Total intensity \n[p$^+$]')
		pl.legend(loc = 'upper left', prop = {'size':14}, bbox_to_anchor=(1,1))

		sp2 = pl.subplot(4,1,2, sharex = sp1)
		pl.plot((array(beams_bct[SPS_user]['timestamp_float'])-t_ref)/3600./24., array(beams_bct[SPS_user]['bct_integrated']),'.')
		ms.sciy()
		pl.grid('on')
		pl.ylabel('BCT integ [p*s]')
	
		sp3 = pl.subplot(4,1,3, sharex = sp1)
		pl.plot((array(beams_ecm[ecm_id][SPS_user]['timestamp_bct'])-t_ref)/3600./24., -array(beams_ecm[ecm_id][SPS_user]['ecld_1st_inj']),'.')
		ms.sciy()
		# pl.ylim(-0.1e5, None)
		pl.grid('on')
		pl.ylabel('EC signal @1s \n[ECM units]')
	
		sp4 = pl.subplot(4,1,4, sharex = sp1)
		pl.plot((array(beams_ecm[ecm_id][SPS_user]['timestamp_bct'])-t_ref)/3600./24.,-array(beams_ecm[ecm_id][SPS_user]['ecld_max']),'.')
		pl.xlabel('Time [days]')
		pl.ylabel('Max. EC signal \n[ECM units]')
		# pl.ylim(-0.1e5, None)
		ms.sciy()
		pl.grid('on')
	
	pl.subplots_adjust(left=.12, bottom=.10, right=.84, top=.94, hspace=.32)
	pl.suptitle('ECM %s from %s'%(ecm_id,t_ref_str))
	fig.set_size_inches(15.725*0.75 ,  11.1875*0.75)
	pl.savefig('W16_ecm_evol_ecm%s.png'%ecm_id, dpi=200)

pl.show()
