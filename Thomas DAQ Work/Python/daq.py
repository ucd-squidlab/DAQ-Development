# -*- coding: utf-8 -*-
""" daq.py - 22.03.5

A module containing basic DAQ methods:
    - Setting a voltage on a DAC channel
    - Beginning an ADC conversion
    - Reading a conversion result
    - Beginning a conversion and then reading result
    
Also some more advanced methods:
    - SimpleRamp
    - FancyRamp
    - 

Created on Fri Mar  4 11:19:53 2022

@author: TBaker

"""


import serial
import time
import numpy as np

# Initialize serial object
ser = serial.Serial()

# Maximum number of samples for continuous sampling
maxsamples = 100000

# DAQ serial function codes
functionCodes = {
    "SETDAC": 0,
    "BEGINADC": 1,
    "GETADC": 2,
    "ICHECK": 3,
    "RESETADC": 4,
    "STARTFAST": 5,
    "GETFASTRESULT": 6
    }

# Prepare serial communication with the DAQ
# Mac: port = "/dev/tty.usbmodemfd141"
# Windows: port = "COM7"
# Returns -1 if there is an error.
def setup(port="COM7", baudrate=115200, timeout=1):
    global ser
    # setup and open serial port
    ser.baudrate = baudrate
    ser.port = port
    ser.timeout = timeout
    try:
        ser.open()
    except:
        return -1
    ser.flushInput()
    ser.flushOutput()
    return 0

# Close the serial port
def close():
    global ser
    ser.close()
    return

# Convert a floating point value to a value usable by the DAC
def Float2DAC(f):
    f = min(9.9995, f)
    f = max(-9.9995, f)
    return int((16384 * ((float(f)/5.0) + 2)))

# Convert two's complement number from the ADC to a usable
# floating point value
def Twos2Float(i):
    
    RES = 18 # Bit depth of the ADC
    FSR = 20.0 #full scale voltage range, can take 4 different values

    val = (i >> (24-RES))/(2**RES)*FSR
    
    # Loop to -FSR/2 if the first bit was a 1
    val = val - (i & (1<<23) > 0)*FSR
    # if (i & (1<<23) > 0):
    #     val -= FSR
    return val

# Wait for the DAQ to send something over serial
# timeout: number of seconds to wait before giving up.
# If the DAQ sends some data, this function will wait
# an additional factor x of the timeout period and then check for
# more data. This repeats until nothing else is sent.
def _WaitForSerial(timeout=0):
    x = 0.3
    starttime = time.time()
    buff = b""
    
    # Wait for the data to come, up to a maximum of `timeout` seconds
    while ser.in_waiting == 0:
        time.sleep(timeout*0.001)
        if time.time() - starttime > timeout:
            return b""
        
    # Keep reading data until nothing else is sent
    while ser.in_waiting > 0:
        # Read data and add it to the buffer
        buff = buff + ser.read(ser.in_waiting)
        # Wait a bit for more data to enter the queue
        # time.sleep(x*timeout)
        starttime = time.time()
        while ser.in_waiting == 0 and time.time() - starttime < timeout*x:
            time.sleep(timeout*0.001)
        
    return buff

# Set the voltage on the DAQ.
# wait: How long to wait for a completion alert
def SetDACVoltage(channel, voltage, wait=0):
    # print("V={}, ch={}".format(voltage, channel))
    #write serial data, forcing MSB first order
    # First byte: function code and channel
    data = bytes([functionCodes["SETDAC"] << 4 | int(channel)])
    # Next two bytes: Voltage
    data = data + Float2DAC(voltage).to_bytes(2, 'big')
    # Next byte: whether to send a completion alert
    data = data + bytes([+(wait>0)])
    # 12 bytes of padding
    data = data + bytes(12)
    # Send command
    ser.write(data)
    
    response_code = 0
    # Wait for a completion alert (if we need to)
    if (wait>0):
        # Get response code
        response = _WaitForSerial(wait)
        # If the response is empty - error!
        if (len(response) == 0):
            return -5;
        response_code = response[0]
    return response_code


# Trigger an ADC conversion
def StartADCConversion():
    global ser
    
    #write serial data, forcing MSB first order
    data = bytearray(16)
    data[0] = bytes([functionCodes["BEGINADC"] << 4])[0]
    ser.write(data)
    return

# Get result for the last ADC conversion
def GetADCResult(channel):
    # Send command 
    data = bytearray(16)
    data[0] = functionCodes["GETADC"] << 4 | int(channel)
    ser.write(data)
    
    v = None
    
    # Wait for the response...
    buff = _WaitForSerial(timeout=0.05)
    
    if (len(buff) >= 3):
        # data sent from Arduino is MSB first
        v = Twos2Float(buff[0] << 16 | buff[1] << 8 | buff[2])
    
    return v

# Start conversion and read result.
# `Channel` may be an array or a scalar.
# If an array, readings will be taken from multiple channels.
def ReadADC(channel):
    StartADCConversion()
    if (hasattr(channel, "__len__")):
        v = []
        for c in channel:
            v.append(GetADCResult(c))
    else:
        v = GetADCResult(channel)
    return v


# Initiate a fast sample
# Defaults:
# Time between samples = 10 us
# (Total time = 4 ms)
def StartFastSample(dmicro=10, count=400):
    ser.flushInput()
    ser.flushOutput()
    data = bytearray(16)
    data[0] = functionCodes["STARTFAST"] << 4
    data[1] = dmicro & 0xff
    data[2] = (count >> 16) & 0xff
    data[3] = (count >> 8) & 0xff
    data[4] = (count) & 0xff
    ser.write(data)

# Collect the fast sample results
def _GetFastSampleData(timeout=1):
    # First get rid of any serial stuff that's hanging around
    ser.flushInput()
    ser.flushOutput()
    
    # Send command to get data back
    data = bytearray(16)
    data[0] = functionCodes["GETFASTRESULT"] << 4
    ser.write(data)
    
    # Wait for response
    result = _WaitForSerial(timeout=timeout)
    val = int(len(result)/3)*3
    result = result[:val]
    if (len(result) > 3):
        result = np.array(list(result))
        result = (result[0::3] << 16) + (result[1::3] << 8) + result[2::3]
        result = Twos2Float(result)
    return result

# Collect the fast sample results
# count: expected number of samples
# max_retries: How many times to re-request missing data
def GetFastSampleResult(timeout=1, count=0, max_retries=5):
    retries = 0
    result = []
    while (retries < max_retries and len(result) < count) or retries == 0:
        result = _GetFastSampleData(timeout=timeout)
        retries += 1
    
    return result


# Set an output voltage on one or more DAC channels and
# get a reading from one or more ADC channels
def GetPoint(ch_out, v_out, ch_in, settle=0):
    if (hasattr(ch_out, "__len__")):
        for i in range(len(ch_out)):
            SetDACVoltage(ch_out[i], v_out[i])
    else:
        SetDACVoltage(ch_out, v_out)
    time.sleep(settle)
    return ReadADC(ch_in)



# Take a set of measurements around a point as shown below:
# (ch_out1 is the vertical axis)
#    1
# 2  3  4
#    5
def GetDither(ch_out1, ch_out2, ch_in, vout1, vout2, d1, d2, settle=0):
    results = []
    points = [(vout1-d1, vout2),
            (vout1, vout2 - d2), (vout1, vout2), (vout1, vout2 + d2),
            (vout1+d1, vout2)]
    
    for p in points:
        # SetDACVoltage(ch_out1, p[0])
        # SetDACVoltage(ch_out2, p[1])
        # results.append(ReadADC(ch_in))
        sample = GetPoint((ch_out1, ch_out2), p, ch_in, settle=settle)
        results.append(sample)
    
    return results;

# Steps: how many parts to divide the range into. Min: 1
# A value of 1 will result in a total of two measurements, one at the top
# and the other at the bottom of the range
# settle (seconds): wait time after each step before taking a measurement
def SimpleRamp(outchannel, inchannel, startV, endV, steps, settle=0):
    deltaV = (endV - startV)/steps
    voltage = startV
    results = []
    # Add 1 to to steps so that the ending value is included
    for i in range(steps+1):
        voltage = startV + i*deltaV
        #print("Output: {}".format(voltage))
        success = SetDACVoltage(outchannel, voltage, wait=0)
        if (success == 0):
            time.sleep(settle)
            v = ReadADC(inchannel)
            results.append(v)
        elif (success == -5):
            print("DAQ Not Responding")
            return results
        else:
            print("DAC Error {}".format(success))
            return results
    return results


# def FunctionRamp(outchannel, inchannel, startV, endV, steps, settle=0,
#                  f=GetPoint):
#     deltaV = (endV - startV)/steps
#     voltage = startV
#     results = []
#     # Add 1 to to steps so that the ending value is included
#     for i in range(steps+1):
#         voltage = startV + i*deltaV
#         #print("Output: {}".format(voltage))
#         point = f(outchannel, voltage, settle=settle)
#         results.append(point)
#     return results


# ch_out1: Slow
# ch_out2: Fast
def FancyRamp(ch_out1, ch_out2, ch_in, limits1, limits2, steps1, steps2,
              settle=0):
    # Initialization...
    results = np.empty((0, steps2+1), float)
    SetDACVoltage(ch_out1, limits1[0], wait=1)
    # print("Initialization complete.")
    
    for v1 in np.linspace(limits1[0], limits1[1], steps1+1):
        success = SetDACVoltage(ch_out1, v1, wait=0)
        if (success == 0):
            nextRow = SimpleRamp(ch_out2, ch_in, limits2[0], limits2[1],
                                 steps2, settle=settle)
            results = np.vstack((results, nextRow))
        else:
            print("Error. {}".format(success))
            return results
    return results


# Incomplete.
def DitherRamp(ch_out, ch_in, limits, steps, d1=0.01, d2=0.01, settle=0):
    # Prepare an empty array to hold data
    # Each element will be a list of 5 values, so we need to specify
    # the dtype as "object"
    results = np.empty((0, steps[1]+1), dtype="object")
    
    for v1 in np.linspace(limits[0][0], limits[0][1], steps[0]+1):
        # Prepare an empty array to hold the next row of data
        nextRow = np.empty(steps[1]+1, dtype="object")
        nextRowArray = []
        # Get next row of data
        for v2 in np.linspace(limits[1][0], limits[1][1], steps[1]+1):
            nextRowArray.append(GetDither(
                ch_out[0], ch_out[1], ch_in, v1, v2, d1, d2, settle=settle))
        # Convert data to NumPy array
        nextRow[:] = nextRowArray
        results = np.vstack((results, nextRow))
        
    return results
            

    
# Take an FFT with averaging.
# The averaging works by taking several overlapping sample ranges,
# computing the FFT for each one, and averaging the results.
# For the FFT function from the daq module, we need to specify:
# - size: the number of samples for each FFT
# - avgnum: the number of averages (this has an upper limit due to
#          finite DAQ storage space)
# - offset_factor: the offset for each overlapping sample range
#                  (0 = complete overlap, 1 = no overlap)
# - dmicro: Delay between samples, in microseconds
def GetFFT(size, avgnum, offset_factor=0.1, dmicro=10):
    global maxsamples
    
    # Absolute size of the offset
    offsetnum = int(offset_factor*size)
    
    # Make sure we won't go over the 100,000 sample limit...
    if (size > maxsamples):
        print(f"""Warning: Too many samples.
              Decreasing FFT size to {maxsamples}...""")
        size = maxsamples
    
    max_avgnum = int((maxsamples-size)/offsetnum) + 1
    if (avgnum > max_avgnum):
        print(f"""Warning: Averaging number requires too many samples.
              Decreasing number of averages to {max_avgnum}...""")
        avgnum = max_avgnum
    
    
    # Total number of samples we'll take
    samples = size + (avgnum-1)*offsetnum
    
    StartFastSample(count=samples, dmicro=dmicro)
    fft = np.zeros(int(size/2)+1)
    data = GetFastSampleResult(count=2)
    for i in range(avgnum):
        fft_sample = np.fft.rfft(data[offsetnum*i:size+offsetnum*i])
        # fft_sample = fft_sample * np.conjugate(fft_sample)
        fft_sample = np.abs(fft_sample)
        fft = fft + fft_sample/avgnum
    return fft