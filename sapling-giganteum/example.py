import json

import pandas as pd

import telemetry_utils as tu

import numpy as np
from datetime import datetime, timezone, timedelta

df = pd.read_csv("telemetry.csv", sep=",", header=0)

gps_buf = bytearray(6)
time_buf = bytearray(4)
output = []

# %     - 1 -           - 2 -     3   4              - 5 -               - 6 -                 - 7 -
# 26112.586516203704 GPS_PosVec 9014 800         -3575.594419         -5758.828897          1440.891615
# 26112.587210648147 GPS_PosVec 9014 800         -3257.134099         -5984.420574          1265.579859
# 26112.587905092594 GPS_PosVec 9014 800         -2926.558570         -6187.149174          1084.793371
# 26112.588599537037 GPS_PosVec 9014 800         -2585.076391         -6366.230816           899.311591
# 26112.589293981480 GPS_PosVec 9014 800         -2233.950454         -6520.997704           709.941434


# Constants for WGS84 ellipsoid
a = 6378137.0 # semi-major axis (meters)
b = 6356752.314245  # semi-minor axis (meters)
f = (a - b) / a  # flattening
e_sq = f * (2 - f)  # eccentricity squared

def geodetic_to_ecef(lat, lon, alt):
    # Convert latitude and longitude to radians
    lat_rad = np.deg2rad(lat)
    lon_rad = np.deg2rad(lon)

    # Calculate N (the radius of curvature in the prime vertical)
    N = a / np.sqrt(1 - e_sq * np.sin(lat_rad)**2)

    # Calculate x, y, z coordinates
    x = (N + alt) * np.cos(lat_rad) * np.cos(lon_rad) / 1000
    y = (N + alt) * np.cos(lat_rad) * np.sin(lon_rad) / 1000 
    z = (N * (1 - e_sq) + alt) * np.sin(lat_rad) / 1000

    return x, y, z

def utc_to_tai_mjd(utc_dt):
    # TAI-UTC offset in seconds
    tai_utc_offset = 37.0  # as of 2023

    # Convert UTC datetime to TAI datetime
    tai_dt = utc_dt + timedelta(seconds=tai_utc_offset)

    # Convert TAI datetime to TAI Modified Julian Date
    # GMAT epoch: 05 Jan 1941 12:00:00.000
    mjd = (tai_dt - datetime(1941, 1, 5, 12, 0, 0, tzinfo=timezone.utc)) / timedelta(days=1)

    return mjd

def format_skygraph(x, y, z, dt):
    return f"{dt.strftime('%y%j%H%M%S.%f')} {x:.6f} {y:.6f} {z:.6f}"

def format_NASA(x, y, z):
    # Mean Equator J2000.0
    # YYDDDHHMMSS.SSS X Y Z VX VY VZ
    return f"{x:.6f} {y:.6f} {z:.6f}"

def format_GMAT(x, y, z, dt):
    mjd = utc_to_tai_mjd(dt)
    return [mjd, "GPS_PosVec", 9014, 800, x, y, z]


def main(args):

    with open('gmat_gps.gmd', 'w+') as g:
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
                lat, lon, alt = tu.decode_gps(gps_buf)
                x, y, z = (geodetic_to_ecef(lat, lon, alt))
                dt = tu.decode_datetime(time_buf)
                dt_fmt = dt.strftime('%y-%m-%d %H:%M:%S')
                
                if args.nasa:
                    new_entry = format_NASA(x, y, z, dt)
                elif args.gmat:
                    new_entry = format_GMAT(x, y, z, dt)
                
                if len(output) > 0 and new_entry != output[-1]:
                    output.append(new_entry)
                elif len(output) == 0:
                    output.append(new_entry)

        for row in output:
            str_row = ""
            for item in row:
                str_row += str(item) + "    "
            str_row += "\n"
            g.write(str_row)