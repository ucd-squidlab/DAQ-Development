# Version 22.03.3

# DEPRECATED

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

def SetDACChannel(args):
    #expected arguments: DAC channel(1), channel value(2)
    #function code: 0
    if len(args) != 3: 
        print("Passed " + str(len(args)) + " arguments. Expected 3.")
        return
    SetDACVoltage(int(args[1]), float(args[2]))


def SetDACVoltage(channel, voltage, wait=0):
    # print("V={}, ch={}".format(voltage, channel))
    #write serial data, forcing MSB first order
    data = bytes([0 << 4 | int(channel)])
    data = data + Float2DAC(voltage).to_bytes(2, 'big')
    data = data + bytes([+(wait>0)])
    data = data + bytes(12) #write 12 bytes of padding
    ser.write(data)
    response_code = 0
    if (wait>0):
        response = WaitForSerial(wait)
        if (len(response) == 0):
            return -5;
        response_code = response[0]
        # print(response_code)
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
            v = GetADCResults([0, inchannel])
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
    print(SetDACVoltage(ch_out1, limits1[0], wait=1))
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


def StartRamp(args):
    if (len(args) < 4):
        print("Missing arguments.")
        return
    print("Ramping... {} {}".format(args[1], args[2]))
    startV = float(args[1])
    endV = float(args[2])
    steps = int(args[3])
    results = SimpleRamp(0, 0, startV, endV, steps)
    inV = np.linspace(startV, endV, steps+1)
    fig = plt.figure()
    plt.plot(inV, results)
    plt.show()
    np.savetxt("output{}.csv".format(int(time.time()%60)), results, delimiter=",")
    return results

def StartFancyRamp(args):
    if (len(args) < 7):
        print("Missing arguments.")
        return
    print("Fancy ramp...")
    args = list(map(int, args[1:]))
    v1 = np.linspace(args[0], args[1], args[4]+1)
    v2 = np.linspace(args[2], args[3], args[5]+1)
    X, Y = np.meshgrid(v2, v1)
    results = FancyRamp(0, 1, 0, [args[0], args[1]], [args[2], args[3]], args[4], args[5], 
                        settle=0.01)
    plt.figure()
    plt.plot(v2, results[0])
    plt.show()
    
    # THIS DOES NOT WORK. Not sure what the correct method of plotting
    # this would be...
    fig = plt.figure()
    ax = plt.axes(projection='3d')
    ax.plot_wireframe(X, Y, results)
    return results


def GetDither(ch_out, ch_in, V, delta):
    results = []
    return results;

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
    #print("Getting data... {}".format(ser.in_waiting))
    
    starttime = time.time()
    dt = 0
    v = None

    # Assumes all incoming data is ADC data.
    # Formats and prints data as floating point numbers to the terminal
    while ser.in_waiting == 0 and dt < 0.02:
        dt = time.time() - starttime
    
    if ser.in_waiting >= 3:
        buff = ser.read(ser.in_waiting)
        if (len(buff) > 0):
            # data sent from Arduino is MSB first
            v = Twos2Float(buff[0] << 16 | buff[1] << 8 | buff[2])
            

    return v

def ReadADC(args):
    StartADCConversion(args);
    v = GetADCResults(args);
    print(v)
    return v
    


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
    "ramp": StartRamp,
    "fancy": StartFancyRamp
}

results = []

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
    global results;
    results = StartFancyRamp(["", -2.5, 2.5, 0, 1, 20, 20])
    print(results)
    SetDACVoltage(0, 0, wait=2)
    SetDACVoltage(1, 0, wait=2)
    should_close = True

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