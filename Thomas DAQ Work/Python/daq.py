# -*- coding: utf-8 -*-
""" daq.py - 22.03.4

A module containing basic DAQ methods:
    - Setting a voltage on a DAC channel
    - Beginning an ADC conversion
    - Reading a conversion result
    - Beginning a conversion and then reading result
    
Also some more advanced methods:
    - SimpleRamp
    - FancyRamp


Created on Fri Mar  4 11:19:53 2022

@author: TBaker

"""


import serial
import time
import numpy as np


ser = serial.Serial()

functionCodes = {
    "SETDAC": 0,
    "BEGINADC": 1,
    "GETADC": 2,
    "ICHECK": 3,
    "RESETADC": 4
    }

# Returns -1 if there is an error.
def setup(port, baudrate=115200, timeout=1):
    global ser
    # setup and open serial port
    ser.baudrate = baudrate
    #ser.port = '/dev/tty.usbmodemfd141'
    ser.port = port
    ser.timeout = timeout
    try:
        ser.open()
    except:
        return -1
    ser.flushInput()
    ser.flushOutput()
    return 0

def close():
    global ser
    ser.close()
    return
    


#function for converting a floating point value to a value usable by the DAC
def Float2DAC(f):
    f = min(9.9995, f)
    f = max(-9.9995, f)
    return int((16384 * ((float(f)/5.0) + 2)))

# Function for converting a two's complement number from the ADC to a usable
# floating point value
def Twos2Float(i):
    
    RES = 18 # Bit depth of the ADC
    FSR = 20.0 #full scale voltage range, can take 4 different values

    val = (i >> (24-RES))/(2**RES)*FSR
    if (i & (1<<23) > 0):
        val -= FSR
    return val

def _WaitForSerial(timeout=0):
    starttime = time.time()

    while ser.in_waiting == 0:
        if time.time() - starttime > timeout:
            return []
        
    buff = ser.read(ser.in_waiting)
    return buff

def SetDACVoltage(channel, voltage, wait=0):
    # print("V={}, ch={}".format(voltage, channel))
    #write serial data, forcing MSB first order
    data = bytes([0 << 4 | int(channel)])
    data = data + Float2DAC(voltage).to_bytes(2, 'big')
    data = data + bytes([+(wait>0)])
    data = data + bytes(12) # 12 bytes of padding
    ser.write(data)
    response_code = 0
    if (wait>0):
        response = _WaitForSerial(wait)
        if (len(response) == 0):
            return -5;
        response_code = response[0]
        # print(response_code)
    return response_code

def StartADCConversion():
    global ser
    
    #write serial data, forcing MSB first order
    data = bytearray(16)
    data[0] = bytes([functionCodes["BEGINADC"] << 4])[0]
    ser.write(data)
    return

def GetADCResult(channel):
    # Send command 
    data = bytearray(16)
    data[0] = functionCodes["GETADC"] << 4 | int(channel)
    ser.write(data)
    
    v = None
    
    buff = _WaitForSerial(timeout=0.05)
    
    if (len(buff) >= 3):
        # data sent from Arduino is MSB first
        v = Twos2Float(buff[0] << 16 | buff[1] << 8 | buff[2])
    
    return v

# Can pass an array of channels to get readings from multiple channels.
def ReadADC(channel):
    StartADCConversion()
    if (hasattr(channel, "__len__")):
        v = []
        for c in channel:
            v.append(GetADCResult(c))
    else:
        v = GetADCResult(channel)
    return v





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
            print("Channel {}".format(outchannel))
            return results
    return results


# ch_out1: Slow
# ch_out2: Fast
def FancyRamp(ch_out1, ch_out2, ch_in, limits1, limits2, steps1, steps2,
              settle=0):
    results = np.empty((0, steps2+1), float)
    SetDACVoltage(ch_out1, limits1[0], wait=1)
    print("Initialization complete.")
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

def GetDither(ch_out, ch_in, V, delta):
    results = []
    return results;