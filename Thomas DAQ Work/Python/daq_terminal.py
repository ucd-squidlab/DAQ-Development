import serial
import struct
import matplotlib
import matplotlib.pyplot as plt
import time

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
    print("quit")

#bit map:
#   function    dac_channel     adc_channel     DATA
#       4           2               2            120

#function for converting a floating point value to a value usable by the DAC
def Float2Binary(f):
    return int((16384 * ((float(f)/5.0) + 2)))

#function for converting a two's complement number from the ADC to a usable floating point value
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
    ser.write(struct.pack('>H', Float2Binary(args[2])))
    #write 13 bytes of padding
    ser.write(13)

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
    print("Getting data... {}".format(ser.in_waiting))
    
    starttime = time.time()
    dt = 0

    # assumes all incoming data is ADC data, formats and prints data as floating point numbers to the terminal
    while ser.in_waiting == 0 and dt < 0.01:
        dt = time.time() - starttime
        
    if ser.in_waiting >= 3:
        buff = ser.read(ser.in_waiting)
        if (len(buff) > 0):
            # data sent from Arduino is MSB first
            print(Twos2Float(buff[0] << 16 | buff[1] << 8 | buff[2]))

    return

def ReadADC(args):
    StartADCConversion(args);
    GetADCResults(args);
    

# input dictionary
input_dictionary = {
    "help" : Help,
    "q"    : Quit,
    "quit" : Quit,
    "exit" : Quit,
    "setdac" : SetDACChannel,
    "startadc" : StartADCConversion,
    "getadc" : GetADCResults,
    "readadc" : ReadADC
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
        usr_input = input("\nWaiting for commands. Type \"help\" for a list of commands.\n")

        #split user input using space delimiters
        split_inputs = usr_input.split()     

        #route user commands using dictionary
        try:
            input_dictionary[split_inputs[0]](split_inputs)
        except:
            print("Unknown command: " + "\"" + usr_input + "\"")

    #close serial port when program is finished 
    ser.close()

if __name__ == "__main__":
    main()