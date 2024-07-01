import json

import pandas as pd

import telemetry_utils as tu

import plotly.graph_objects as go

import numpy as np
from datetime import datetime, timezone, timedelta
import sys
import math

df = pd.read_csv("telemetry.csv", sep=",", header=0)

gps_buf = bytearray(6)
time_buf = bytearray(4)



def main():
    output = []
    for index, row in df.iterrows():

        if math.isnan(row['tinygsLuxXNeg']):
            continue
        
        mag_y_plus = row['tinygsLuxYPos']
        mag_y_minus = row['tinygsLuxYNeg']
        mag_x_plus = row['tinygsLuxXPos']
        mag_x_minus = row['tinygsLuxXNeg']
        mag_z_plus = row['tinygsLuxZPos']
        mag_z_minus = row['tinygsLuxZNeg']

        time_str = row['time']
        dt = datetime.strptime(time_str, '%Y-%m-%d %H:%M:%S.%f')
        
        output.append([dt, mag_x_minus, mag_x_plus, mag_y_minus, mag_y_plus, mag_z_minus, mag_z_plus])
    
    output = np.array(output)
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=output[:,0], y=output[:,1], mode='lines', name='X-'))
    fig.show()

if __name__ == '__main__':
    main()