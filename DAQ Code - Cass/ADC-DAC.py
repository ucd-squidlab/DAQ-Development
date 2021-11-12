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

def setVoltage(voltage,DAC):
    voltage = float(input()) / 1000 #Convert input() to volts
    data = int((3276.8*(voltage + 10))) #Convert volts into bitstring
    address = DAC | DATA_REG
    writeDAC(address,data)
    
def setFine(gain,DAC):
    #Two's Complement conversion:
    data = gain
    if (gain < 0):
        gain = gain + 32
        data = 0x20 | gain
    address = DAC | FINEGAIN_REG
    writeDAC(address,data)
  
def setOffset(offset,DAC):
    #Two's Complement conversion:
    data = offset * 8
    if (offset < 0):
        offset = offset + 128
        data = 0x80 | offset
    address = DAC | OFFSET_REG
    writeDAC(address,data)

def setCoarse(voltage,DAC):
    address = DAC | COARSEGAIN_REG
    writeDAC(address,command)

#Takes a 1 byte address and 2 bytes of data and sends it to the DAC
def writeDAC(address,data):
    upperbyte = (data & 0xFF00) >> 8
    lowerbyte = data & 0xFF
    msg = [address,upperbyte,lowerbyte]
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