from scipy.interpolate import interp1d
from scipy.constants import m_p, e, c
from numpy import array
import numpy as np
import csv

beta_opt_lib={}

beta_opt_lib['SPS.BWS.41677.H_ROT:Q26'] = 38.03
beta_opt_lib['SPS.BWS.41677.V_ROT:Q26'] = 62.96

beta_opt_lib['SPS.BWS.41677.H_ROT:Q20'] = 49.19
beta_opt_lib['SPS.BWS.41677.V_ROT:Q20'] = 71.02

beta_opt_lib['SPS.BWS.51995.H_ROT:Q26'] = 81.49
beta_opt_lib['SPS.BWS.51995.V_ROT:Q26'] = 28.15

beta_opt_lib['SPS.BWS.51995.H_ROT:Q20'] = 86.8
beta_opt_lib['SPS.BWS.51995.V_ROT:Q20'] = 39.6

beta_opt_lib['SPS.BWS.51731.H_LIN:Q26'] = 21.37
beta_opt_lib['SPS.BWS.51731.V_LIN:Q26'] = 101.58

beta_opt_lib['SPS.BWS.51731.H_LIN:Q20'] = 32.55
beta_opt_lib['SPS.BWS.51731.V_LIN:Q20'] = 102.72

beta_opt_lib['SPS.BWS.52171.H_LIN:Q26'] = 47.95
beta_opt_lib['SPS.BWS.52171.V_LIN:Q26'] = 50.53

beta_opt_lib['SPS.BWS.52171.H_LIN:Q20'] = 57.74
beta_opt_lib['SPS.BWS.52171.V_LIN:Q20'] = 60.56


disp_opt_lib={}

disp_opt_lib['SPS.BWS.41677.H_ROT:Q26'] = -0.2524938899
disp_opt_lib['SPS.BWS.41677.V_ROT:Q26'] = 0.0

disp_opt_lib['SPS.BWS.41677.H_ROT:Q20'] = -0.4610950126
disp_opt_lib['SPS.BWS.41677.V_ROT:Q20'] = 0.0

disp_opt_lib['SPS.BWS.51995.H_ROT:Q26'] = -0.015138155
disp_opt_lib['SPS.BWS.51995.V_ROT:Q26'] = 0.0

disp_opt_lib['SPS.BWS.51995.H_ROT:Q20'] = -0.3632436309
disp_opt_lib['SPS.BWS.51995.V_ROT:Q20'] = 0.0

disp_opt_lib['SPS.BWS.51731.H_LIN:Q26'] = -0.3519365215
disp_opt_lib['SPS.BWS.51731.V_LIN:Q26'] = 0.0

disp_opt_lib['SPS.BWS.51731.H_LIN:Q20'] = -0.4985302242
disp_opt_lib['SPS.BWS.51731.V_LIN:Q20'] = 0.0

disp_opt_lib['SPS.BWS.52171.H_LIN:Q26'] = 2.231501629
disp_opt_lib['SPS.BWS.52171.V_LIN:Q26'] = 0.0

disp_opt_lib['SPS.BWS.52171.H_LIN:Q20'] = 1.97391915
disp_opt_lib['SPS.BWS.52171.V_LIN:Q20'] = 0.0


def retrieve_betagamma(cycle_csv_filepath, t_in_cycle_ms):  
    list_values = []
    with open(cycle_csv_filepath) as csf:
        reader = csv.DictReader(csf)
        for row in reader:
            list_values.append(row)
   
    t = []
    momentum = []
    for v in list_values:
        if v['X'] == '' or v['Y'] == '':
            continue
        t.append(float(v['X']))
        momentum.append(float(v['Y']))
    t = np.array(t)
    momentum = np.array(momentum)

    momentum_interp = interp1d(t, momentum, kind='linear')
    m_p_GeV = m_p * c**2 / (1e9*e)
    return momentum_interp(t_in_cycle_ms) / m_p_GeV
