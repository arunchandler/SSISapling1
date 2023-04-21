EXAMPLE = bytearray(b'KN6HCC\x1f\x06\x01\x00\x00\x00\x9c\xa3\xc2v\x00\x00\x05\xf0\xff} \x00\x01 \x00\x90t\x10\x82pz%{\x1f|\xc1{{9\xb5\x92Z\x06\x00\x00\xe8KH')
_buf = memoryview(EXAMPLE)

import telemetry_utils as telem_utils 

def decode(view=None, debug=False):
    place = 0
    if view is not None:
        telem_buffer = view
    else:
        telem_buffer = _buf
    # --------------------------------------------------------------------------
    # Callsign
    # --------------------------------------------------------------------------
    res = []
    callsign = bytes(telem_buffer[0:6])
    print(f"callsign: {callsign}")
    res.append(callsign)
    place += 6
    
    # --------------------------------------------------------------------------
    # State Data
    # --------------------------------------------------------------------------
    
    # 2 bytes
    try:
        state, tx_power, solar_charging, enable_rf = telem_utils.decode_state_tx_power_solar_charging(
            telem_buffer[place:]
        )
    except:
        print("failed to decode state, tx_power, or solar_charging")
        state = None
        tx_power = None
        solar_charging = None
        enable_rf = None
    print(f"state: {state}")
    print(f"tx_power: {tx_power}")
    print(f"solar_charging: {solar_charging}")
    print(f"enable_rf: {enable_rf}")
    res.extend([state, tx_power, solar_charging, enable_rf])
    place += 1
    
    mem_free = telem_buffer[place] * 1000
    print(f"mem_free: {mem_free}")
    res.append(mem_free)
    place += 1

    # --------------------------------------------------------------------------
    # Error Counters
    # --------------------------------------------------------------------------

    # 4 bytes
    boot = telem_buffer[place]
    gs_resp = telem_buffer[place+1] 
    crc_err = telem_buffer[place+2] 
    state_err = telem_buffer[place+3]
    print(f"boot: {boot}")
    print(f"gs_resp: {gs_resp}")
    print(f"crc_err: {crc_err}")
    print(f"state_err: {state_err}")
    res.extend([boot, gs_resp, crc_err, state_err])
    place += 4

    # --------------------------------------------------------------------------
    # Power Data
    # --------------------------------------------------------------------------
    
    # 4 bytes
    try:
        vbatt, vsys, isys = telem_utils.decode_power(
            telem_buffer[place:]
        )
    except:
        print("failed to decode power data")
        vbatt = None
        vsys = None
        isys = None
    tbatt = telem_utils.decode_temp(telem_buffer[place+3:])
    print(f"vbatt: {vbatt}")
    print(f"vsys: {vsys}")
    print(f"isys: {isys}")
    print(f"tbatt: {tbatt}")
    res.extend([vbatt, vsys, isys])
    place += 4
    
    # --------------------------------------------------------------------------
    # Radio Data
    # --------------------------------------------------------------------------
    
    # 2 bytes
    rssi = telem_buffer[place] - 137
    snr_byte = telem_buffer[place+1]
    if snr_byte > 127:
        snr_byte = (256 - snr_byte) * -1
    snr = snr_byte / 4
    print(f"rssi on last packet received by sapling: {rssi}")
    print(f"snr on last packet received by sapling: {snr}")
    res.extend([rssi, snr])
    place += 2

    # --------------------------------------------------------------------------
    # Sensor Data
    # --------------------------------------------------------------------------

    # Light Sensor - 9 bytes 6 directions packed as 12 bit numbers
    try:
        als_values = telem_utils.decode_als(telem_buffer[place:])
    except:
        print("failed to decode als")
        als_values = [None] * 6
    print(f"lux (x+, x-, y+, y-, z+, z-){als_values}")
    res.extend(als_values)
    place += 9
    
    # IMU - 13 bytes
    try:
        mag = telem_utils.decode_mag(telem_buffer[place:], 3)      # 6 bytes
    except:
        print("failed to decode mag")
        mag = [None] * 3
    try:
        gyro = telem_utils.decode_gyro(telem_buffer[place+6:], 3)  # 6 bytes
    except:
        print("failed to decode gyro")
        gyro = [None] * 3
    try:
        imu_temp = telem_utils.decode_temp(telem_buffer[place+12:])              
    except:
        print("failed to decode imu_temp")
        imu_temp = [None] * 3
    
    print(f"mag: {mag}")
    print(f"gyro: {gyro}")
    print(f"imu_temp: {imu_temp}")
    res.extend(mag)
    res.extend(gyro)
    res.append(imu_temp)
    place += 13

    # GPS - 10 bytes
    try:
        lat, lon, alt = telem_utils.decode_gps(telem_buffer[place:])
    except:
        print("failed to decode GPS")
        lat, lon, alt = None, None, None
    print(f"latitude: {lat}")
    print(f"longitude: {lon}")
    print(f"altitude: {alt}")
    datetime = telem_utils.decode_datetime(telem_buffer[place+6:]) # 4 bytes
    print(f"datetime: {datetime}")
    res.extend([lat, lon, alt, datetime])

    place += 10

    return res
