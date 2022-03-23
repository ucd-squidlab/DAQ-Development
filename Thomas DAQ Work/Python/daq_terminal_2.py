# Version 22.03.6

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


def SetDAC(args):
    #expected arguments: DAC channel(1), channel value(2)
    #function code: 0
    if len(args) != 3: 
        print("Passed " + str(len(args)) + " arguments. Expected 3.")
        return
    daq.SetDACVoltage(int(args[1]), float(args[2]))
    return

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

def StartFancyRamp(args):
    if (len(args) < 7):
        print("Missing arguments.")
        return
    print("Fancy ramp...")
    args = list(map(int, args[1:]))
    v1 = np.linspace(args[0], args[1], args[4]+1)
    v2 = np.linspace(args[2], args[3], args[5]+1)
    X, Y = np.meshgrid(v2, v1)
    results = daq.FancyRamp(0, 1, 0, [args[0], args[1]], [args[2], args[3]], args[4], args[5], 
                        settle=0)
    plt.figure()
    plt.plot(v2, results[0])
    plt.show()
    
    plt.figure()
    ax = plt.axes(projection='3d')
    ax.plot_wireframe(X, Y, results)
    return results


def GetFastSample(args):
    print("Initializing...")
    daq.StartFastSample(count=65000)
    print("Started.")
    print(" Collecting data...")
    result = daq.GetFastSampleResult(timeout=3)
    print(len(result))
    plt.figure()
    plt.plot(range(len(result)), result)
    plt.show()
    return

def GetFFT(args):
    size = 800
    count = 200
    offset = 200
    dmicro = int(args[1])
    
    repeat = 4
    
    
    fft = np.zeros(int(size/2)+1)
    daq.StartFastSample(dmicro=dmicro, count=size+(count-1)*offset)
    
    for r in range(repeat):
        data = daq.GetFastSampleResult(timeout=10)
        daq.StartFastSample(dmicro=dmicro, count=size+(count-1)*offset)
        for i in range(count):
            fft_sample = np.fft.rfft(data[offset*i:size+offset*i])
            # fft_sample = fft_sample * np.conjugate(fft_sample)
            fft_sample = np.abs(fft_sample)
            fft = fft + fft_sample/(count*repeat)
        print(len(fft))
        
    T = size*dmicro*1e-6
    freq = np.array(range(int(size/2)+1)) / T
    
    fig = plt.figure()
    ax = fig.add_subplot()
    ax.plot(freq[4:int(len(fft))], fft[4:int(len(fft))])
    ax.set_xscale('log')
    ax.set_yscale('log')
    plt.show()
    return


def GetFFT2(args):
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
    avgnum = 50
    offset_factor = 0.125
    
    dmicro = 10
    
    # We can repeat this process to get around the upper limit
    repeat = 3
    
    fft = np.zeros(int(size/2)+1)
    
    # Take the FFTs and average them
    for r in range(repeat):
        fft_sample = daq.GetFFT(size, avgnum,
                                dmicro=dmicro, offset_factor=offset_factor)
        fft = fft + fft_sample/repeat
    
    # Take the magnitude
    fft = np.abs(fft)
    
    # Calculate frequencies. For a bin n, the frequency is given by:
    #        f = n / T
    # where T is the total sampling time
    T = size*dmicro*1e-6
    freq = np.array(range(int(size/2)+1)) / T
    
    # Plot the FFT
    fig = plt.figure()
    ax = fig.add_subplot()
    ax.plot(freq[4:int(len(fft))], fft[4:int(len(fft))])
    ax.set_xscale('log')
    ax.set_yscale('log')
    plt.show()
    return
    

def ReadADC(args):
    v = daq.ReadADC(int(args[1]))
    print(v)
    return v

def StartDitherRamp(args):
    ch_out = [0, 1]
    ch_in = 0
    limits = [(0, 10), (0, 10)]
    steps = [10, 10]
    results = daq.DitherRamp(ch_out, ch_in, limits, steps)
    # Pull out the middle item from each tuple
    select_data = [[a[3] for a in b] for b in results]
    select_data = np.array(select_data)
    
    v1 = np.linspace(limits[0][0], limits[0][1], steps[0])
    v2 = np.linspace(limits[1][0], limits[1][1], steps[1])
    
    X, Y = np.meshgrid(v2, v1)
    
    plt.figure()
    ax = plt.axes(projection='3d')
    ax.plot_wireframe(X, Y, select_data)
    
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
    "fancy": StartFancyRamp,
    "ditherramp": StartDitherRamp,
    "fast": GetFastSample,
    "fft": GetFFT,
    "fft2": GetFFT2
    }


results = []

def main():
    daq.setup("COM7", baudrate=115200)
    global should_close
    
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