# Version 22.02.4

import serial
import struct
import matplotlib
import matplotlib.pyplot as plt
import time
import numpy as np

should_close = False
ser = serial.Serial()




def Quit(args):
    global should_close
    should_close = True

def Help(args):
    print("\nCommands are listed below:\n")
    print("setdac dac_channel voltage")
    print("startadc adc_channel")
    print("getadc adc_channel")
    print("readadc adc_channel")
    print("ramp endV steps")
    print("quit")

#bit map:
#   function    dac_channel     adc_channel     DATA
#       4           2               2            120

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

def SetDACChannel(args):
    #expected arguments: DAC channel(1), channel value(2)

    #function code: 0
    global ser

    if len(args) != 3: 
        print("Passed " + str(len(args)) + " arguments. Expected 3.")
        return

    #write serial data, forcing MSB first order 
    ser.write(bytearray([0 << 4 | int(args[1]) << 2]))
    ser.write(struct.pack('>H', Float2DAC(args[2])))
    #write 13 bytes of padding
    ser.write(13)

def SetDACVoltage(voltage, channel=4, wait=0):
    #write serial data, forcing MSB first order
    ser.write(bytearray([0 << 4 | int(channel) << 2]))
    ser.write(struct.pack('>H', Float2DAC(voltage)))
    ser.write(bytearray([1]))
    #write 12 bytes of padding
    ser.write(12)
    response_code = -1
    if (wait>0):
        response = WaitForSerial(wait)
        if (len(response) == 0):
            return -5;
        response_code = response[0]
    return response_code
    

def StartADCConversion(args):
    #expected arguments: ADC channel(1)

    #function code: 1
    global ser

    if len(args) != 2:
        print("Passed " + str(len(args)) + " arguments. Expected 2.")
        return

    #write serial data, forcing MSB first order 
    ser.write(bytearray([1 << 4 | int(args[1])]))
    #write 15 bytes of padding
    ser.write(15)

# Steps: how many parts to divide the range into. Min: 1
# A value of 1 will result in a total of two measurements, one at the top
# and the other at the bottom of the range
def Ramp(outchannel, inchannel, startV, endV, steps):
    deltaV = (endV - startV)/steps
    voltage = startV
    results = []
    # Add 1 to to steps so that the ending value is included
    for i in range(steps+1):
        voltage = startV + i*deltaV
        print("Output: {}".format(voltage))
        success = SetDACVoltage(voltage, channel=outchannel, wait=10)
        if (success == 0):
            v = GetADCResults([0, inchannel])
            results.append(v)
        elif (success == -5):
            print("DAQ Not Responding")
            return results
        else:
            print("DAC Error")
            return results
    return results

def WaitForSerial(maxwaittime):
    starttime = time.time()

    while ser.in_waiting == 0:
        if time.time() - starttime > maxwaittime:
            return []
        
    buff = ser.read(ser.in_waiting)
    return buff
    
def GetADCResults(args):
    # expected arguments: ADC channel(1)
    
    # funciton code: 2
    global ser

    if len(args) != 2:
        print("Passed " + str(len(args)) + " arguments. Expected 2.")
        return
        
    # write command to get ADC data
    
    # write serial data, forcing MSB first order 
    ser.write(bytearray([2 << 4 | int(args[1])]))
    # write 15 bytes of padding
    ser.write(15)
    time.sleep(0.01)
    #print("Getting data... {}".format(ser.in_waiting))
    
    starttime = time.time()
    dt = 0
    v = None

    # Assumes all incoming data is ADC data.
    # Formats and prints data as floating point numbers to the terminal
    while ser.in_waiting == 0 and dt < 0.01:
        dt = time.time() - starttime
    
    if ser.in_waiting >= 3:
        buff = ser.read(ser.in_waiting)
        if (len(buff) > 0):
            # data sent from Arduino is MSB first
            v = Twos2Float(buff[0] << 16 | buff[1] << 8 | buff[2])
            print(v)

    return v

def ReadADC(args):
    StartADCConversion(args);
    v = GetADCResults(args);
    return v
    

def StartRamp(args):
    if (len(args) < 3):
        print("Missing arguments.")
        return
    print("Ramping... {} {}".format(args[1], args[2]))
    endV = float(args[1])
    steps = int(args[2])
    results = Ramp(0, 0, 0, endV, steps)
    inV = np.linspace(0, endV, steps+1)
    print(inV)
    print(results)
    fig = plt.figure()
    plt.plot(inV, results)
    fig.show()
    plt.show()


# input dictionary
input_dictionary = {
    "help" : Help,
    "q"    : Quit,
    "quit" : Quit,
    "exit" : Quit,
    "setdac" : SetDACChannel,
    "startadc" : StartADCConversion,
    "getadc" : GetADCResults,
    "readadc" : ReadADC,
    "ramp": StartRamp
}



def main():
    # setup and open serial port
    ser.baudrate = 115200
    #ser.port = '/dev/tty.usbmodemfd141'
    ser.port = 'COM7'
    ser.timeout = 1
    ser.open()

    # cleanup incoming and outgoing bits
    ser.flushInput()
    ser.flushOutput()

    while(should_close != True):
        #wait for user input 
        usr_input = input("\nWaiting for commands."
                          "Type \"help\" for a list of commands.\n")

        #split user input using space delimiters
        split_inputs = usr_input.split()     

        #route user commands using dictionary
        command = split_inputs[0]
        if (command not in input_dictionary):
            print("Unknown command: \"{}\"".format(command))
        else:
            #try:
                input_dictionary[split_inputs[0]](split_inputs)
            #except Exception as e:
             #   print(e)

    #close serial port when program is finished 
    ser.close()



if __name__ == "__main__":
    main()