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
ADC_CONVST = 13

#Takes a voltage in millivolts and a channel from 1-4
def setDAC(voltage,channel):
  DAC = channel - 1
  address = DAC | DATA_REG
  voltage = voltage / 1000
  data = int((3276.8*(voltage + 10))) #Convert volts into 2's comp bitstring
  writeDAC(address,data)

#Takes a 1 byte address and 2 bytes of data and sends it to the DAC
def writeDAC(address,data):
  upperbyte = (data & 0xFF00) >> 8
  lowerbyte = data & 0xFF
  msg = [address,upperbyte,lowerbyte]
  AD5764.xfer2(msg)

def writeADC(address,data):
  AD7606.xfer2([address,data])

def readADC(address):
  address = address | 0x40
  AD7606.xfer2([address,0x00])
  readout = AD7606.xfer2([0x00,0x00])
  print(readout)

#Function to get the conversion data. Writes 1 byte to comms, and then writes 0b00 to clock out the data.
def GetConversionData():
  #Prompt a data readout
  GPIO.output(ADC_CONVST,True)
  GPIO.output(ADC_CONVST,False)
  #Wait for data to be ready
  #print("waiting")
  #GPIO.wait_for_edge(ADC_BUSY,GPIO.FALLING)
  #We ask for 24 bits of data but only need 18
  output = AD7606.xfer2([0x00,0x00,0x00])
  #Separate out the relevant information from the recieved data
  data = (output[0] & 0xFF) << 10 | (output[1] & 0xFF) << 2 | (output[2] & 0xC0) >> 6
  #Convert from two's complement
  if data & (1 << 17) != 0:
    data = data - (1 << 17)
  print(data)
  voltage = data / 13107.2
  return voltage

def GetSpectralData(maxfreq=35000,numsecs=5):
  #Grab five seconds of data at 200KHz- a total of 1 million data points
  datapoints = (maxfreq * numsecs)
  data = [0] * datapoints
  delay = 1 / maxfreq #basically just converting frequency to seconds
  print(delay)
  conversiontime = time.time()
  conversiontime2 = time.time()
  print(conversiontime2 - conversiontime)
  for i in range(0,datapoints):
    #Prompt a data readout
    GPIO.output(ADC_CONVST,True)
    GPIO.output(ADC_CONVST,False)
    #We ask for 24 bits of data but only need 18
    data[i] = AD7606.xfer2([0x00,0x00,0x00])
    #We don't want to do a lot of work here to help ensure we keep our timings straight.
    conversiontime2 = time.time()
    while (conversiontime2 - conversiontime) < delay:
      conversiontime2 = time.time()
      print("fast")
    conversiontime = time.time()
  return data



def main():
  writeADC(0x02,0x18) #Configure data output for all lines
  readADC(0x02)
  setDAC(5000,1)
  time.sleep(0.001)
  print(GetConversionData())
  setDAC(500,1)
  time.sleep(0.001)
  print(GetConversionData())
  setDAC(50,1)
  time.sleep(0.001)
  GetSpectralData()


def main2():
  #Get information from the user
  bias_steps = float(input("Enter the number of bias steps"))
  bias_min = float(input("Enter the minimum bias point"))
  bias_max = float(input("Enter the maximum bias point"))
  flux_steps = float(input("Enter the number of flux steps"))
  flux_min = float(input("Enter the minimum flux point"))
  flux_max = float(input("Enter the maximum flux point"))
  if input("Collect noise data? Y/N") == Y: getNoise = True
  if input("Add flux dither? Y/N") == Y: ditherFlux = True
  #Get the amount to increment with each step
  bias_step = (bias_max - bias_min) / bias_steps
  flux_step = (flux_max - flux_min) / flux_steps
  data = [] #Big data array to read all of our data into

  #Outer loop (bias) code
  for bstep in range(0,bias_steps):
    bias_point = bias_step * bstep + bias_min   #Calculates the value to set the bias point to
    bias_point = min(bias_point,bias_max)   #Ensures the bias isn't set over the desired maximum
    setDAC(bias_point,1)
    #Inner loop (flux) code
    for fstep in range(0,flux_steps):
      flux_point = flux_step * fstep + flux_min   #Calculates the value to set the flux point to
      flux_point = min(flux_point,flux_max)   #Ensures the flux isn't set over the desired maximum
      setDAC(flux_point,2)
      #With both outputs set, we read the data from the ADC
      if getNoise == true:
        data[bstep][fstep][0] = readADCSpectrum()
      else:
        data[bstep][fstep][0] = GetConversionData()
      if ditherFlux == True:
        setDAC(flux_point + dither,2)
        data[bstep][fstep][1] = GetConversionData()
        setDAC(flux_point - dither,2)
        data[bstep][fstep][2] = GetConversionData()

  
# Enable DAC SPI
AD5764 = spidev.SpiDev(0,0)
AD5764.max_speed_hz = 10000000
AD5764.mode = 1

#Setup ADC GPIO pins
GPIO.setmode(GPIO.BCM)
GPIO.setup(ADC_RESET, GPIO.OUT)
GPIO.setup(ADC_CONVST, GPIO.OUT)
GPIO.setup(ADC_BUSY,GPIO.IN)
GPIO.output(ADC_RESET,False)
GPIO.output(ADC_CONVST,False)

# Enable ADC SPI
AD7606 = spidev.SpiDev(0,1)
AD7606.max_speed_hz = 60000000
AD7606.mode = 2 
 
main()
AD5764.close
AD7606.close