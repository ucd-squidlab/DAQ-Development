import time #Explain breifly what this import is
import spidev #Explain briefly what this import is
import RPi.GPIO as GPIO  #Explain briefly what this import is

#DAC channels
DAC_A = 0x00 
DAC_B = 0x01
DAC_C = 0x02
DAC_D = 0x03
DAC_ALL = 0x04 #Used for when writing to all channels at once
#Can one write to select channels by adding addresses? I suppose not, if DAC_D = 0x03...

#DAC Registers - defined in hex
#What are the lengths of these registers?
FUNCTION_REG = 0x00
DATA_REG = 0x10
COARSEGAIN_REG = 0x18
FINEGAIN_REG = 0x20
OFFSET_REG = 0x28

#DAC Function register options
NOP = 0x00
CLEAR = 0x04
READ = 0x80

ADC_READY = 20
ADC_RESET = 21

#Explain; is this a drop-down menu? Entries in a field?
#Why coarse and fine gains? Can't you just specify a value?
DACmenu = """Commands:
1 - Set DAC voltage
2 - Set coarse gain
3 - Set fine gain
4 - Reset DAC output
5 - Set DAC offset
6 - Get register data
7 - ADC test conversion
X - exit"""

#Main is primarily for using the DAC and ADC as standalone devices.
#Only is particularly useful for confirming that SPI communication is functional.
#What is "Only?"
def main():
    command = 0
    while (command != "X"):
        print(DACmenu)
        command = input()
        #Set a single voltage output on the DAC    #This set of comments is fine...
        if command == "1":
            setVoltage()
        #Modify the coarse gain on the DAC
        elif command == "2":
            setCoarse()
        #Modify the fine gain on the DAC
        elif command == "3":
            setFine()
        #Put the DAC into a reset state
        elif command == "4":
            resetDAC()
        #Set the offset for the different DAC channels
        elif command == "5":
            setOffset()
        #Read from a selected channel of the DAC (DOESN'T WORK) #Is this because we're not hooked up for READ (tri-state issues)?
        elif command == "6":
            readRegister()
        #Basic "read channel 1" function on the ADC
        elif command == "7":
            writeADC(0x38,0x40)   #Explain the significance of 0x38 and 0x40.

def setVoltage():
    print("Select a DAC to set.")
    print("A: 1; B: 2; C: 3; D: 4; All: 5")
    command = int(input())
    if command > 5 or command < 1:
        print("Invalid input().")
        return
    DAC = (command - 1)   #What is happening here?
    print("Enter the desired voltage in millivolts. Hit space to submit.")
    print("Allowable voltage range is -10,000 < mV < 10,000")
    voltage = float(input()) / 1000 #Convert input() to volts
    if voltage > 10 or voltage < -10:
        print("Invalid input().")
        return
    data = int((3276.8*(voltage + 10))) #Convert volts into bitstring
    address = DAC | DATA_REG   #Explain this step
    writeDAC(address,data)
    print("Voltage has been set to: " + str(voltage)) #If we can get the "read" working, we can add a step to confirm the setpoint.
    return
    
def setFine():
    print("Select a DAC to set.")
    print("A: 1; B: 2; C: 3; D: 4; All: 5")
    command = int(input())
    if command > 5 or command < 1:
        print("Invalid input().")
        return
    DAC = (command - 1)
    print("Enter the desired gain in LSBs. Hit space to submit.") #Explain how gain and LSBs are related.
    print("Allowable gain range is -32 < G < 31")
    gain = input()
    if gain > 31 or gain < -32:
        print("Invalid input().")
        return
    #Two's Complement conversion:
    #Explain how these steps accomplish the conversion.
    data = gain
    if (gain < 0):
        gain = gain + 32
        data = 0x20 | gain  #Explain this step.
    print("Gain has been set to: " + gain)
    address = DAC | FINEGAIN_REG #Explain this step
    writeDAC(address,data)
  
def setOffset():
    print("Select a DAC to set.")
    print("A: 1; B: 2; C: 3; D: 4; All: 5")
    command = int(input())
    if command > 5 or command < 1:
        print("Invalid input().")
        return
    DAC = (command - 1)
    print("Enter the desired offset in LSBs. Hit space to submit.") #Explain how offset and LSBs are related.
    print("Allowable offset range is -16 < G < 15.875")
    offset = input()
    if offset > 15.875 or offset < -16:
        print("Invalid input().")
        return
    #Two's Complement conversion:
    data = offset * 8
    if (offset < 0):
        offset = offset + 128
        data = 0x80 | offset #Explain this step
    print("Offset has been set to: " + offset)
    address = DAC | OFFSET_REG #Explain this step
    writeDAC(address,data)

def setCoarse():
    print("Select a DAC to set.")
    print("A: 1; B: 2; C: 3; D: 4; All: 5")
    command = int(input())
    if command > 5 or command < 1:
        print("Invalid input().")
        return
    DAC = (command - 1)
    print("Choose the desired voltage range.")
    print("1: +/- 10V")
    print("2: +/- 10.2564V")
    print("3: +/- 10.5263V")
    command = int(input()) - 1
    if command > 3 or command < 0:
        print("Invalid input().")
        return
    address = DAC | COARSEGAIN_REG #Explain this step
    writeDAC(address,command)

#Takes a 1 byte address and 2 bytes of data and sends it to the DAC
def writeDAC(address,data):
    upperbyte = (data & 0xFF00) >> 8 #Explain this step; I assume this is a mask?
    lowerbyte = data & 0xFF #Ditto
    msg = [address,upperbyte,lowerbyte]
    print(msg)
    AD5764.xfer2(msg,AD5764.max_speed_hz,10) #Explain this step

#Takes a 1 byte address and 1 byte of data and sends it to the ADC.
#Only particularly useful for starting conversions
def writeADC(address,data):
    AD7734.xfer2([address,data]) #This step uses variables, next steps use fixed values--why? Generally, avoid embedding fixed values...

#Function to get the conversion data. Writes 1 byte to comms, and then writes 0b00 to clock out the data.
def GetConversionData(channel):
    AD7734.xfer([0x48])
    output = AD7734.xfer2([0x00,0x00]) #Explain this step
    data = (output[0] & 0xFF) << 8 | (output[1] & 0xFF) #Explain what this is accomplishing
    return data

#Function triggers when the ADC_READY pin goes high.
#Calls a function to get the conversion data
def ADCDataISR(channel):
    GPIO.remove_event_detect(channel) #Explain this function/command
    data = GetConversionData(0)
    print(hex(data))
    GPIO.add_event_detect(channel, GPIO.FALLING, callback=ADCDataISR) #Ditto

# Enable DAC SPI
AD5764 = spidev.SpiDev(0,0) #What is this class variable?
AD5764.max_speed_hz = 10000000
AD5764.mode = 1 #What does mode = 1 mean?

#Setup ADC GPIO pins
GPIO.setmode(GPIO.BCM) #What is .bcm?
GPIO.setup(ADC_READY, GPIO.IN, pull_up_down=GPIO.PUD_UP) #Why does setup have different arguments in this line and next?
GPIO.setup(ADC_RESET, GPIO.OUT)
GPIO.output(ADC_RESET,True) #What's the difference between .setup and .output?
GPIO.add_event_detect(ADC_READY, GPIO.FALLING, callback=ADCDataISR) #Explain function & arguments

# Enable ADC SPI
AD7734 = spidev.SpiDev(0,1) #What is this class variable?
AD7734.max_speed_hz = 10000000
AD7734.mode = 3  #What does mode = 3 mean?

main()
AD5764.close
AD7734.close