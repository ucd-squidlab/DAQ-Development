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

#ADC Registers (Most of these don't matter, but just in case!)
COMMS_REG = 0x00
IOPORT_REG = 0x01
REVISION_REG = 0x02
TEST_REG = 0x03
STATUS_REG = 0x04
CHECKSUM_REG = 0x05
ADC_ZERO_SCALE_CAL_REG = 0x06
ADC_FULL_SCALE_CAL_REG = 0x07
CHANNEL_DATA_REG = 0x08
CHANNEL_ZERO_SCALE_CAL_REG = 0x10
CHANNEL_FULL_SCALE_CAL_REG = 0x18
CHANNEL_STATUS = 0x20
CHANNEL_SETUP = 0x28
CHANNEL_CONVERSION_TIME = 0x30
MODE = 0x38

ADC_READY = 20
ADC_RESET = 21

DACmenu = """Commands:
1 - Set DAC voltage
2 - Set coarse gain
3 - Set fine gain
4 - Reset DAC output
5 - Set DAC offset
6 - Get register data
7 - ADC single conversion
8 - ADC continuous conversion
X - exit"""

def main():
    command = 0
    while (command != "X"):
        print(DACmenu)
        command = input()
        if command == "1":
            setVoltage()
        elif command == "2":
            setCoarse()
        elif command == "3":
            setFine()
        elif command == "4":
            resetDAC()
        elif command == "5":
            setOffset()
        elif command == "6":
            readRegister()
        elif command == "7":
            setADC(false)
        elif command == "8":
            setADC(true)

def setADC(continuous):
    print("Select a channel to set.")
    print("A: 1; B: 2; C: 3; D: 4; All: 5")
    command = int(input())
    if command > 5 or command < 1:
        print("Invalid input.")
        return
    ADC = (command - 1)
    #First, write to the comms register:
    address = MODE | ADC
    #Then write to the mode register:
    data = 0x22 #Single conversion, 24-bit
    if continuous
        data = 0x42 #Continuous conversion, 24-bit
    writeADC(address, data)

def setVoltage():
    print("Select a DAC to set.")
    print("A: 1; B: 2; C: 3; D: 4; All: 5")
    command = int(input())
    if command > 5 or command < 1:
        print("Invalid input.")
        return
    DAC = (command - 1)
    print("Enter the desired voltage in millivolts. Hit space to submit.")
    print("Allowable voltage range is -10,000 < mV < 10,000")
    voltage = float(input()) / 1000 #Convert input() to volts
    if voltage > 10 or voltage < -10:
        print("Invalid input.")
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
        print("Invalid input.")
        return
    DAC = (command - 1)
    print("Enter the desired gain in LSBs. Hit space to submit.")
    print("Allowable gain range is -32 < G < 31")
    gain = int(input())
    if gain > 31 or gain < -32:
        print("Invalid input.")
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
        print("Invalid input.")
        return
    DAC = (command - 1)
    print("Enter the desired offset in LSBs. Hit space to submit.")
    print("Allowable offset range is -16 < G < 15.875")
    offset = float(input())
    if offset > 15.875 or offset < -16:
        print("Invalid input.")
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
        print("Invalid input.")
        return
    DAC = (command - 1)
    print("Choose the desired voltage range.")
    print("1: +/- 10V")
    print("2: +/- 10.2564V")
    print("3: +/- 10.5263V")
    command = int(input()) - 1
    if command > 3 or command < 0:
        print("Invalid input.")
        return
    address = DAC | COARSEGAIN_REG
    writeDAC(address,command)

def writeDAC(address,data):
    global AD5764
    upperbyte = (data & 0xFF00) >> 8
    lowerbyte = data & 0xFF
    msg = [address,upperbyte,lowerbyte]
    print(msg)
    AD5764.xfer2(msg,AD5764.max_speed_hz,10)

def writeADC(address,data):
    AD7734.xfer2([address,data])

def GetConversionData(channel):
    AD7734.xfer([0x48])
    output = AD7734.xfer2([0x00,0x00,0x00])
    data = (output[0] & 0xFF) << 16 | (output[1] & 0xFF) << 8 | (output[2] & 0xFF)
    return data

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