# Version 22.03.4

import matplotlib.pyplot as plt
import time
import numpy as np
import traceback

# import daq
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
    count = 600
    offset = 100
    
    repeat = 4
    
    fft = np.zeros(size)
    daq.StartFastSample(count=size+(count-1)*offset)
    
    for r in range(repeat):
        data = daq.GetFastSampleResult()
        daq.StartFastSample(count=size+(count-1)*offset)
        for i in range(count):
            fft_sample = np.fft.fft(data[offset*i:size+offset*i])
            # fft_sample = fft_sample * np.conjugate(fft_sample)
            fft_sample = np.abs(fft_sample)
            fft = fft + fft_sample/count
        print(len(fft))
    fig = plt.figure()
    ax = fig.add_subplot()
    ax.plot(np.array(range(int(len(fft)/2)-4))/(800*10e-6), fft[4:int(len(fft)/2)])
    ax.set_xscale('log')
    # ax.set_yscale('log')
    plt.show()
    return
    
    

def ReadADC(args):
    v = daq.ReadADC(int(args[1]))
    print(v)
    return v
    


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
    "fast": GetFastSample,
    "fft": GetFFT
    }


results = []

def main():
    daq.setup("COM7")
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