import numpy as np

# thermistor values for TTDO-10KC8-3-1% on battery board
therm_resistances_nom = [169.793, 160.729, 152.217, 144.219,
    136.703, 129.636, 122.987, 116.731, 110.840, 105.292, 100.064, 95.135,
    90.487, 86.101, 81.961, 78.051, 74.358, 70.867, 67.565, 64.442,
    61.487, 58.689, 56.038, 53.527, 51.146, 48.888, 46.746, 44.712,
    42.782, 40.947, 39.204, 37.547, 35.971, 34.472, 33.045, 31.686,
    30.391, 29.158, 27.982, 26.861, 25.791, 24.770, 23.796, 22.865,
    21.976, 21.127, 20.315, 19.538, 18.796, 18.085, 17.405, 16.753,
    16.129, 15.532, 14.959, 14.410, 13.883, 13.378, 12.893, 12.428,
    11.982, 11.553, 11.141, 10.746, 10.365, 10.000, 9.649, 9.311,
    8.986, 8.673, 8.373, 8.083, 7.804, 7.536, 7.277, 7.028,
    6.788, 6.557, 6.334, 6.120, 5.912, 5.713, 5.520, 5.334,
    5.155, 4.982, 4.815, 4.654, 4.499, 4.349, 4.204, 4.066,
    3.933, 3.805, 3.681, 3.563, 3.449, 3.339, 3.233, 3.131,
    3.033, 2.938, 2.847, 2.760, 2.675, 2.594, 2.515, 2.440,
    2.367, 2.296, 2.228, 2.163, 2.100, 2.039, 1.980, 1.923,
    1.869, 1.816, 1.764, 1.715, 1.667, 1.621, 1.577, 1.533,
    1.492, 1.451, 1.412, 1.374, 1.338, 1.302, 1.268, 1.235,
    1.203, 1.172, 1.141, 1.112, 1.084, 1.056, 1.029, 1.003,
    0.978, 0.954, 0.930, 0.907, 0.884, 0.863, 0.842, 0.821,
    0.801, 0.782, 0.763, 0.744, 0.727, 0.709, 0.692, 0.676,
    0.660, 0.644, 0.629, 0.614, 0.600, 0.586, 0.572, 0.559,
    0.546, 0.533, 0.521, 0.509, 0.497, 0.485, 0.474, 0.463,
    0.453, 0.442, 0.432, 0.422][::-1]

therm_temps_nom = np.arange(-40.,136.,1)[::-1]

# from NCR18650B characteristic curves
sampled_charge_state_voltages = np.arange(2.5,4.3,.1)

battery_characteristic_curve_25C = [2.94, 4.41, 5.88, 6.47, 8.82, 13.23, 17.64, 26.47, 38.23, 47.05, 55.88, 67.64, 79.41, 88.23, 97.05, 100, 100, 100]

battery_characteristic_curve_5C = [10.29, 11.76, 12.35, 14.70, 20.58, 25., 30.88, 42.64, 51.47, 55.88, 64.70, 76.47, 91.17, 91.17, 91.17, 91.17, 91.17, 91.17]

battery_characteristic_curve_neg10C = [17.64, 20.58, 23.52, 29.41, 33.82, 38.23, 47.05, 54.41, 63.23, 70.58, 85.29, 85.29, 85.29, 85.29, 85.29, 85.29, 85.29, 85.29]

battery_characteristic_curve_neg20C = [35.29, 38.23, 41.17, 44.11, 47.05, 52.94, 58.82, 64.70, 73.52, 73.52, 73.52, 73.52, 73.52, 73.52, 73.52, 73.52, 73.52, 73.52]

def get_battery_state_of_charge(v_bat, bat_temp):
    
    v_bat = v_bat/2.
    state_of_charge = 0.
    # temps above 20C have similar characteristic curves
    if bat_temp >= 20.:
        state_of_charge = np.interp(np.array([v_bat]), sampled_charge_state_voltages, battery_characteristic_curve_25C)
    # Between 20 and 0 degrees C the curve changes significantly, best estimate
    elif bat_temp >= 0.:
        state_of_charge = np.interp(np.array([v_bat]), sampled_charge_state_voltages, battery_characteristic_curve_5C)
    elif bat_temp >= -15.:
        state_of_charge = np.interp(np.array([v_bat]), sampled_charge_state_voltages, battery_characteristic_curve_neg10C)
    # if below freezing we've got a cold ass battery pack, really should have heater :-(
    else:
        state_of_charge = np.interp(np.array([v_bat]), sampled_charge_state_voltages, battery_characteristic_curve_neg20C)
    
    return state_of_charge[0]

def get_temp_from_thermistor(resistance):
    temp = np.interp(np.array([resistance]), therm_resistances_nom, therm_temps_nom)
    return temp[0]
