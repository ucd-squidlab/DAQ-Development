# Version 22.03.4

import matplotlib.pyplot as plt
import time
import numpy as np

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


def ReadADC(args):
    v = daq.ReadADC(int(args[1]))
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
    "fancy": StartFancyRamp
}

results = []

def main():
    daq.setup("COM7")
    
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
            input_dictionary[split_inputs[0]](split_inputs)

    #close serial port when program is finished 
    daq.close()



if __name__ == "__main__":
    main()