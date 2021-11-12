import time
import spidev
import RPi.GPIO as GPIO  

#DAC channels
DAC_A = 0x00
DAC_B = 0x01
DAC_C = 0x02
DAC_D = 0x03
DAC_ALL = 0x04

#DAC Registers - defined in hex
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
def main():
    command = 0
    while (command != "X"):
        print(DACmenu)
        command = input()
        #Set a single voltage output on the DAC
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
        #Read from a selected channel of the DAC (DOESN'T WORK)
        elif command == "6":
            readRegister()
        #Basic "read channel 1" function on the ADC
        elif command == "7":
            writeADC(0x38,0x40)

def setVoltage():
    print("Select a DAC to set.")
    print("A: 1; B: 2; C: 3; D: 4; All: 5")
    command = int(input())
    if command > 5 or command < 1:
        print("Invalid input().")
        return
    DAC = (command - 1)
    print("Enter the desired voltage in millivolts. Hit space to submit.")
    print("Allowable voltage range is -10,000 < mV < 10,000")
    voltage = float(input()) / 1000 #Convert input() to volts
    if voltage > 10 or voltage < -10:
        print("Invalid input().")
        return
    data = int((3276.8*(voltage + 10))) #Convert volts into bitstring
    address = DAC | DATA_REG
    writeDAC(address,data)
    print("Voltage has been set to: " + str(voltage))
    return
    
def setFine():
    print("Select a DAC to set.")
    print("A: 1; B: 2; C: 3; D: 4; All: 5")
    command = int(input())
    if command > 5 or command < 1:
        print("Invalid input().")
        return
    DAC = (command - 1)
    print("Enter the desired gain in LSBs. Hit space to submit.")
    print("Allowable gain range is -32 < G < 31")
    gain = input()
    if gain > 31 or gain < -32:
        print("Invalid input().")
        return
    #Two's Complement conversion:
    data = gain
    if (gain < 0):
        gain = gain + 32
        data = 0x20 | gain
    print("Gain has been set to: " + gain)
    address = DAC | FINEGAIN_REG
    writeDAC(address,data)
  
def setOffset():
    print("Select a DAC to set.")
    print("A: 1; B: 2; C: 3; D: 4; All: 5")
    command = int(input())
    if command > 5 or command < 1:
        print("Invalid input().")
        return
    DAC = (command - 1)
    print("Enter the desired offset in LSBs. Hit space to submit.")
    print("Allowable offset range is -16 < G < 15.875")
    offset = input()
    if offset > 15.875 or offset < -16:
        print("Invalid input().")
        return
    #Two's Complement conversion:
    data = offset * 8
    if (offset < 0):
        offset = offset + 128
        data = 0x80 | offset
    print("Offset has been set to: " + offset)
    address = DAC | OFFSET_REG
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
    address = DAC | COARSEGAIN_REG
    writeDAC(address,command)

#Takes a 1 byte address and 2 bytes of data and sends it to the DAC
def writeDAC(address,data):
    upperbyte = (data & 0xFF00) >> 8
    lowerbyte = data & 0xFF
    msg = [address,upperbyte,lowerbyte]
    print(msg)
    AD5764.xfer2(msg,AD5764.max_speed_hz,10)

#Takes a 1 byte address and 1 byte of data and sends it to the ADC.
#Only particularly useful for starting conversions
def writeADC(address,data):
    AD7734.xfer2([address,data])

#Function to get the conversion data. Writes 1 byte to comms, and then writes 0b00 to clock out the data.
def GetConversionData(channel):
    AD7734.xfer([0x48])
    output = AD7734.xfer2([0x00,0x00])
    data = (output[0] & 0xFF) << 8 | (output[1] & 0xFF)
    return data

#Function triggers when the ADC_READY pin goes high.
#Calls a function to get the conversion data
def ADCDataISR(channel):
    GPIO.remove_event_detect(channel)
    data = GetConversionData(0)
    print(hex(data))
    GPIO.add_event_detect(channel, GPIO.FALLING, callback=ADCDataISR)

# Enable DAC SPI
AD5764 = spidev.SpiDev(0,0)
AD5764.max_speed_hz = 10000000
AD5764.mode = 1

#Setup ADC GPIO pins
GPIO.setmode(GPIO.BCM)
GPIO.setup(ADC_READY, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(ADC_RESET, GPIO.OUT)
GPIO.output(ADC_RESET,True)
GPIO.add_event_detect(ADC_READY, GPIO.FALLING, callback=ADCDataISR)

# Enable ADC SPI
AD7734 = spidev.SpiDev(0,1)
AD7734.max_speed_hz = 10000000
AD7734.mode = 3

main()
AD5764.close
AD7734.close