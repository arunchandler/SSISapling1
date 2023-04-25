import struct
try:
    from datetime import datetime, timedelta, timezone
except:
    from adafruit_datetime import datetime, timedelta

# --------------------------------------------------------------------------
# Gyro, Mag
# --------------------------------------------------------------------------

def encode_gyro(data_vals, buf):
    for i in range(3):
        gyro_val = data_vals[i]
        if gyro_val > 32:
            gyro_val = int((32 + 31) * 1024)
        elif gyro_val < -32:
            gyro_val = 0
        else:
            gyro_val = int((gyro_val + 31) * 1024)
        buf[2*i] = gyro_val & 0xff
        buf[2*i+1] = gyro_val >> 8
 
    return buf

def decode_gyro(buf, num_vals):
    data_vals = []
    for i in range(num_vals):
        val = int(buf[2*i]) | int(buf[2*i+1]) << 8
        data_vals.append(val / 1024 - 31)
    return data_vals

def encode_mag(data_vals, buf):
    for i in range(3):
        mag_val = data_vals[i]
        if mag_val > 128:
            mag_val = 65535
        elif mag_val < -127:
            mag_val = 0
        mag_val = int((mag_val + 127) * 256)
        buf[2*i] = mag_val & 0xff
        buf[2*i+1] = mag_val >> 8
 
    return buf

def decode_mag(buf, num_vals):
    data_vals = []
    for i in range(num_vals):
        val = int(buf[2*i]) | int(buf[2*i+1]) << 8
        data_vals.append(val / 256 - 127)
    return data_vals

# --------------------------------------------------------------------------
# ALS
# --------------------------------------------------------------------------

def encode_als(als_vals, buf):
    for i in range(3):
        pos = als_vals[2*i]
        neg = als_vals[2*i+1]
        if pos > 32760:
            pos = 4095
        else:
            pos = int(pos) >> 3
        if neg > 32760:
            neg = 4095
        else:
            neg = int(neg) >> 3
        buf[i*3] = neg & 0b11111111                                        # lower 8 bits of neg
        buf[i*3+1] = ((pos << 4) & 0b11110000) | ((neg >> 8) & 0b00001111) # top 4 bits of neg and bottom 4 bits of pos
        buf[i*3+2] = (pos >> 4) & 0b11111111                               # upper 8 bits of pos
        
    return buf

def decode_als(buf):
    out = []
    for i in range(3):
        neg = (int(buf[i*3]) | ((int(buf[i*3+1]) & 0b00001111) << 8)) << 3 # lower 8 bits is byte 1, upper 4 bits is lower 4 bits of byte 2
        pos = (int(buf[i*3+2]) << 4 | (int(buf[i*3+1]) >> 4)) << 3         # lower 4 bits is upper 4 of byte 2 and upper 8 bits is byte 3
        out.extend([pos, neg])
    return out

# --------------------------------------------------------------------------
# Temperatures
# --------------------------------------------------------------------------

def encode_temp(temp_val, buf):
    if temp_val < -100:
        temp_val = 0
    elif temp_val > 155:
        temp_val = 255
    else:
        temp_val = int(temp_val + 100)
    buf[0] = temp_val
        
    return buf

def decode_temp(buf):
    temp_val = buf[0]
    return temp_val - 100

# --------------------------------------------------------------------------
# State, TX power, Solar Charging
# --------------------------------------------------------------------------

def encode_state_tx_power_solar_charging(state, tx_power, solar_charging, enable_rf, buf):
    val = int(state == 'Idle')  # bit 1
    val |= ((tx_power - 5) << 1) & 0b111110       # bits 2-5
    val |= solar_charging << 6  # bit 6
    val |= enable_rf << 7 # bit 7
    print(val)
    buf[0] = val
    return buf

def decode_state_tx_power_solar_charging(buf):
    val = buf[0]
    if val & 1:
        state = "Idle"
    else:
        state = "Safe"
    tx_power = ((val >> 1) & 0b11111) + 5
    solar_charging = val >> 6 & 0b1 # bit 6
    enable_rf = val >> 7 # bit 7
    return state, tx_power, solar_charging, enable_rf

# --------------------------------------------------------------------------
# Power Data
# --------------------------------------------------------------------------

def encode_power(vbatt, vsys, isys, buf):
    if vbatt is None or vbatt < 5:
        vbatt = 5
    elif vbatt > 8.4:
        vbatt = 8.4
    if vsys is None or vsys < 5:
        vsys = 5
    elif vsys > 8.4:
        vsys = 8.4
    if isys is None:
        isys = 0
    elif isys > 70:
        isys = 70

    buf[0] = int((vbatt - 5) * 75)  # 5-8.4V
    buf[1] = int((vsys - 5) * 75)   # 5-8.4V
    buf[2] = int(isys * 255/70)     # 0-70 (in mA)
    
    return buf

def decode_power(buf):
    vbatt = buf[0]/75 + 5
    vsys = buf[1]/75 + 5
    isys = buf[2]*70/255
    return [vbatt, vsys, isys]

# --------------------------------------------------------------------------
# Time Data
# --------------------------------------------------------------------------

def encode_datetime(curr_time, buf):
    _epoch = datetime(2023, 3, 1, 0, 0, 0)
    dt = datetime(*curr_time) - _epoch
    buf[:4] = struct.pack("f", dt.total_seconds())
    return buf

def decode_datetime(buf):
    _epoch = datetime(2023, 3, 1, 0, 0, 0, tzinfo=timezone.utc)
    try:
        dt_sec = timedelta(seconds=struct.unpack("f", buf[0:4])[0])
    except:
        print("failed to decode datetime")
        dt_sec = timedelta(seconds=0)
    return _epoch + dt_sec

# --------------------------------------------------------------------------
# GPS
# --------------------------------------------------------------------------

def encode_gps(lat, lon, alt, buf):
    lat = int(lat*364)
    buf[0] = lat & 0xff
    buf[1] = lat >> 8

    lon = int((lon + 180) * 182)
    buf[2] = lon & 0xff
    buf[3] = lon >> 8

    if alt > 600000:
        alt = 600000
    elif alt < 0:
        alt = 0
    else:
        alt = int(alt/9.155)
    buf[4] = alt & 0xff
    buf[5] = alt >> 8
        
    return buf

def decode_gps(buf):
    data_vals = []
    
    val = int(buf[0]) | int(buf[1]) << 8
    data_vals.append(val / 364)

    val = int(buf[2]) | int(buf[3]) << 8
    data_vals.append(val / 182 - 180)

    val = int(buf[4]) | int(buf[5]) << 8
    data_vals.append(val * 9.155)

    return data_vals