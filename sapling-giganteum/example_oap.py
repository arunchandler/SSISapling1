import json
import power as pwr
import pandas as pd

import telemetry_utils as tu

import numpy as np
from datetime import datetime, timezone, timedelta

df = pd.read_csv("telemetry.csv", sep=",", header=0)

soc_arr = []

# format

# datetime,battery_voltage,battery_temperature...
# 2023-02-26 21:40:00,7.04888,-40.0,...



def main():
    charge_count = 0
    not_charge_count = 0

    with open(f"power_data.csv", 'w+') as clean:
        clean.write('datetime,voltage,battery_temp,battery_soc\n')
        for index, row in df.iterrows():
            # Get values from specific columns by name
            voltage = row['tinygsBatVoltage']
            temp = row['tinygsTemp']
            charging = row['tinygsCharging']
            charge_count += bool(charging)
            not_charge_count += not bool(charging)

            time = row['time']
            
            soc = pwr.get_battery_state_of_charge(voltage, temp)
            soc_arr.append(soc)
            line = ",".join([time, str(voltage), str(temp), str(soc), "\n"])
            clean.write(line)
    
    print(charge_count/(not_charge_count + charge_count))

if __name__ == "__main__":
    main()
   