import csv
import json

import pandas as pd

import telemetry_utils as tu

df = pd.read_csv("telemetry.csv", sep=",", header=0)

gps_buf = bytearray(6)
time_buf = bytearray(4)
output = []

with open('gps_decoded.csv', 'w+') as g:
    for index, row in df.iterrows():
        # Get values from specific columns by name
        gps_enc = json.loads(row['gps'])
        for j in range(6):
            gps_buf[j] = gps_enc[j]

        time_enc = json.loads(row['gpsTime'])
        for j in range(4):
            time_buf[j] = time_enc[j]
        
        # GPS telemetry is 255, 255, 255, 255, 255, 255 if no fix
        if gps_enc != [255, 255, 255, 255, 255, 255] and time_enc != [255, 255, 255, 255]:
            gps = tu.decode_gps(gps_buf)
            dt = tu.decode_datetime(time_buf)
            dt_fmt = dt.strftime('%y-%m-%d %H:%M:%S')
            new_entry = [*gps, dt_fmt]
            if len(output) > 0 and new_entry != output[-1]:
                output.append(new_entry)
            elif len(output) == 0:
                output.append(new_entry)
    
    write = csv.writer(g)
    write.writerows(output)