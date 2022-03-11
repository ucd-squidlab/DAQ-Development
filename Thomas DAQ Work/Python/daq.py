# -*- coding: utf-8 -*-
"""
Created on Fri Mar  4 11:19:53 2022

@author: TBaker



"""


import serial
import struct
import time

ser = serial.Serial()

functionCodes = {
    "SETDAC": 0,
    "BEGINADC": 1,
    "GETADC": 2,
    "ICHECK": 3,
    "RESETADC": 4
    }

# Returns -1 if there is an error.
def Setup(port, baudrate="115200", timeout="1"):
    global ser
    # setup and open serial port
    ser.baudrate = baudrate
    #ser.port = '/dev/tty.usbmodemfd141'
    ser.port = port
    ser.timeout = timeout
    try:
        ser.open()
    except:
        return 0
    return -1


#function for converting a floating point value to a value usable by the DAC
def Float2DAC(f):
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

def ReadSerial(timeout=0):
    starttime = time.time()

    # Wait for available data
    while ser.in_waiting == 0:
        if time.time() - starttime > timeout:
            return [] # Timeout
    
    # Read data
    buff = ser.read(ser.in_waiting)
    return buff



def SetDACVoltage(voltage, channel=0, wait=0):
    #write serial data, forcing MSB first order
    data = bytes([0 << 4 | int(channel) << 2])
    data = data + Float2DAC(voltage).to_bytes(2, 'big')
    data = data + bytes([1])
    ser.write(data)
    #write 12 bytes of padding
    ser.write(12)
    response_code = -1
    if (wait>0):
        response = WaitForSerial(wait)
        if (len(response) == 0):
            return -5;
        response_code = response[0]
    return response_code

def StartADCConversion():
    #write serial data, forcing MSB first order
    data = bytearray(16)
    data[0] = bytes([functionCodes["BEGINADC"] << 4])
    ser.write(data)
    return


def ReadADCResult(channel):
    # write serial data, forcing MSB first order 
    data = bytearray(16)
    
    data[0] = [functionCodes["READADC"] << 4 | int(channel)]
    ser.write(data)
    
    v = None
    
    buff = ReadSerial(timeout=0.05)
    
    if (len(buff) >= 3):
        # data sent from Arduino is MSB first
        v = Twos2Float(buff[0] << 16 | buff[1] << 8 | buff[2])
    
    return v
    
    
    