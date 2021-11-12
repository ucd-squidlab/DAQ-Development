import time
import spidev #Python library for SPI communication
import RPi.GPIO as GPIO  #Python library for using the GPIO pins for the raspberry pi

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

#GPIO pins connected to relevant ADC pins.
ADC_BUSY = 5
ADC_RESET = 6


DACmenu = """Commands:
1 - Set DAC voltage
2 - Set coarse gain
3 - Set fine gain
4 - Reset DAC output
5 - Set DAC offset
6 - Get register data
7 - ADC Talk
8 - ADC Tell
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
            ADCtalk()
        elif command == "8":
            ADCtell()
        elif command == "9":
            GetConversionData(0)

def ADCtalk():
    print("say something.")
    command = 70
    while (command != 0):
        command = int(input())
        if command != 0:
            readADC(command)

def ADCtell():
    print("say something.")
    command = 70
    while (command != 0):
        command = int(input())
        if command != 0:
            print("say something else.")
            data = int(input())
            writeADC(command,data)
            return

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
    AD7606.xfer2([address,data])

def readADC(address):
    print("preparing to send")
    address = address | 0x40
    print(address)
    print(AD7606.xfer2([address,0x00]))
    readout = AD7606.xfer2([address,0x00])
    print(readout)

#Function to get the conversion data. Writes 1 byte to comms, and then writes 0b00 to clock out the data.
def GetConversionData(channel):
    #We ask for 24 bits of data but only need 18
    output = AD7606.xfer2([0x00,0x00,0x00])
    #Separate out the relevant information from the recieved data
    print(output)
    data = (output[0] & 0xFF) << 10 | (output[1] & 0xFF) << 2 | (output[2] & 0xC0) >> 6
    print(data)
    return data

#Function triggers when the ADC_BUSY pin goes low.
#Calls a function to get the conversion data
def ADCDataISR(channel):
    print("ISR triggered")
    GPIO.remove_event_detect(channel)
    data = GetConversionData(0)
    
    print(hex(data))
    GPIO.add_event_detect(ADC_BUSY, GPIO.FALLING, callback=ADCDataISR)

# Enable DAC SPI
AD5764 = spidev.SpiDev(0,0)
AD5764.max_speed_hz = 10000000
AD5764.mode = 1

#Setup ADC GPIO pins
GPIO.setmode(GPIO.BCM)
GPIO.setup(ADC_RESET, GPIO.OUT)
 GPIO.setup(ADC_BUSY, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.add_event_detect(ADC_BUSY, GPIO.FALLING, callback=ADCDataISR)
GPIO.output(ADC_RESET,False)

# Enable ADC SPI
AD7606 = spidev.SpiDev(0,1)
AD7606.max_speed_hz = 10000000
AD7606.mode = 2
#writeADC(0x02,0x00) #Configure data output for DoutA only

main()
AD5764.close
AD7606.close