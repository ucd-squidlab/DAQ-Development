# Version 22.05.1

# This is just a terminal interface for accessing the DAQ functions
# from daq.py
#
# Mostly, this particular program is just for testing purposes.
# Ideally, somebody would write a separate Python program
# with a GUI.

import matplotlib.pyplot as plt
import time
import numpy as np
import traceback

# import daq module
import daq

should_close = False


def Quit(args):
    global should_close
    should_close = True

def Help(args):
    print("\nCommands are listed below:\n")
    print("setdac dac_channel voltage")
    print("readadc adc_channel")
    print("ramp endV steps")
    print("quit")


# Set output for a DAC channel
def SetDAC(args):
    #expected arguments: DAC channel(1), channel value(2)
    #function code: 0
    if len(args) != 3: 
        print("Passed " + str(len(args)) + " arguments. Expected 3.")
        return
    daq.SetDACVoltage(int(args[1]), float(args[2]))
    return

# Start a single-channel ramp
# Arguments:
# startV, endV, steps
def StartRamp(args):
    if (len(args) < 4):
        print("Missing arguments.")
        return
    print("Ramping... {} {}".format(args[1], args[2]))
    startV = float(args[1])
    endV = float(args[2])
    steps = int(args[3])
    results = daq.SimpleRamp(0, 0, startV, endV, steps)
    inV = np.linspace(startV, endV, steps+1)
    
    plt.figure()
    plt.plot(inV, results)
    plt.show()
    np.savetxt("output{}.csv".format(int(time.time()%60)), results, delimiter=",")
    return results

# Start a ramp on two channels.
# Arguments:
# start1, end1, start2, end2, step1, step2
def StartRamp2D(args):
    if (len(args) < 7):
        print("Missing arguments.")
        return
    print("Fancy ramp...")
    args = list(map(int, args[1:]))
    v1 = np.linspace(args[0], args[1], args[4]+1)
    v2 = np.linspace(args[2], args[3], args[5]+1)
    X, Y = np.meshgrid(v2, v1)
    results = daq.Ramp2D(0, 1, 0,
                            [args[0], args[1]], [args[2], args[3]],
                            args[4], args[5],
                            settle=0)
    plt.figure()
    plt.plot(v2, results[0])
    
    plt.figure()
    ax = plt.axes(projection='3d')
    ax.plot_wireframe(X, Y, results)
    plt.show()
    return results

# Capture a fast sample from the ADC.
# (no arguments)
def GetFastSample(args):
    dmicro = 5
    count = 50000
    print("Initializing...")
    daq.StartFastSample(dmicro=dmicro, count=count)
    print("Started.")
    print(" Collecting data...")
    time.sleep(count*dmicro*1e-6+0.001)
    result = daq.GetFastSampleResult(timeout=2, count=count)
    print(len(result))
    plt.figure()
    plt.plot(range(len(result)), result)
    plt.show()
    return

# def GetFFT_old(args):
#     size = 800
#     count = 800
#     offset = 80
#     dmicro = 10
#     # dmicro = int(args[1])
    
#     repeat = 2
    
    
#     fft = np.zeros(int(size/2)+1)
#     total_samples = size+(count-1)*offset
#     daq.StartFastSample(dmicro=dmicro, count=total_samples)
    
#     for r in range(repeat):
#         data = daq.GetFastSampleResult(timeout=1, count=3)
#         daq.StartFastSample(dmicro=dmicro, count=size+(count-1)*offset)
#         for i in range(count):
#             fft_sample = np.fft.rfft(data[offset*i:size+offset*i])
#             # fft_sample = fft_sample * np.conjugate(fft_sample)
#             fft_sample = np.abs(fft_sample)
#             fft = fft + fft_sample/(count*repeat)
#         print(len(fft))
        
#     T = size*dmicro*1e-6
#     freq = np.array(range(int(size/2)+1)) / T
    
#     fig = plt.figure()
#     ax = fig.add_subplot()
#     ax.plot(freq[4:int(len(fft))], fft[4:int(len(fft))])
#     ax.set_xscale('log')
#     ax.set_yscale('log')
#     plt.show()
#     return


def GetFFT(args):
    # The FFT function from the daq module uses averaging for the FFTs.
    # The averaging works by taking several overlapping sample ranges,
    # computing the FFT for each one, and averaging the results.
    # For the FFT function from the daq module, we need to specify:
    # - size: the number of samples for each FFT
    # - count: the number of averages (this has an upper limit due to
    #          finite DAQ storage space)
    # - offset_factor: the offset for each overlapping sample range
    #                  (0 = complete overlap, 1 = no overlap)
    # - dmicro: Delay between samples, in microseconds
    
    size = 800
    avgnum = 800
    offset_factor = 0.125
    
    dmicro = 6
    
    # We can repeat this process to get around the upper limit
    repeat = 5
    
    fft = np.zeros(int(size/2)+1)
    
    # Take the FFTs and average them
    for r in range(repeat):
        print(r)
        fft_sample = daq.GetFFT(size, avgnum,
                                dmicro=dmicro, offset_factor=offset_factor)
        fft = fft + fft_sample/repeat
    
    # Take the magnitude
    fft = np.abs(fft)
    
    # Calculate frequencies. For a bin n, the frequency is given by:
    #        f = n / T
    # where T is the total sampling time
    T = size*dmicro*1e-6
    freq = np.array(range(len(fft))) / T
    
    # Plot the FFT
    fig = plt.figure()
    ax = fig.add_subplot()
    ax.plot(freq[4:], fft[4:])
    ax.set_xscale('log')
    ax.set_yscale('log')
    plt.show()
    return
    
# Read a value from the ADC
# Arguments:
# channel number (0-3)
def ReadADC(args):
    v = daq.ReadADC(int(args[1]))
    print(v)
    return v

# Start a "dither" ramp
# Arguments: none
def StartDitherRamp(args):
    ch_out = [0, 1]
    ch_in = 0
    limits = [(0, 10), (0, 10)]
    steps = [7, 7]
    
    # Get a 2-dimensional array. Each element is a list of length 5
    results = daq.DitherRamp(ch_out, ch_in, limits, steps)
    
    # Pull out the middle item from each list
    select_data = [[a[2] for a in b] for b in results]
    select_data = np.array(select_data)
    
    v1 = np.linspace(limits[0][0], limits[0][1], steps[0]+1)
    v2 = np.linspace(limits[1][0], limits[1][1], steps[1]+1)
    
    X, Y = np.meshgrid(v2, v1)
    print(np.shape(select_data))
    print(select_data)
    # print(X)
    # print(Y)
    
    plt.figure()
    ax = plt.axes(projection='3d')
    ax.plot_wireframe(X, Y, select_data)
    plt.show()
    
    return results


# input dictionary
input_dictionary = {
    "help" : Help,
    "q"    : Quit,
    "quit" : Quit,
    "exit" : Quit,
    "setdac" : SetDAC,
    "readadc" : ReadADC,
    "ramp": StartRamp,
    "ramp2d": StartRamp2D,
    "ditherramp": StartDitherRamp,
    "fast": GetFastSample,
    "fft": GetFFT,
    # "fftold": GetFFT_old
    }


results = []

def main():
    global should_close
    print("Initializing")
    
    
    success = daq.setup(port="COM8", baudrate=115200)
    if (success == -1):
        print("Error initializing serial port.")
        should_close = True
    
    global results;
    # results = StartFancyRamp(["", -2.5, 2.5, 0, 1, 15, 15])
    # print(results)
    daq.SetDACVoltage(0, 0, wait=2)
    daq.SetDACVoltage(1, 0, wait=2)
    # should_close = True
    

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
            try:
                input_dictionary[split_inputs[0]](split_inputs)
            except:
                print(traceback.format_exc())
                should_close = True
                
    #close serial port when program is finished 
    daq.close()



if __name__ == "__main__":
    main()