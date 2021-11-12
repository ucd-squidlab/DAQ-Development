import serial
import time
import matplotlib.pyplot as mplt #for plotting
import numpy as np

COMPort = 'COM28'  #Set COMPort for DACADC, look up on device manager
Baudrate = 115200  #Baudrate set in Arduino

ser = serial.Serial(COMPort, Baudrate, timeout = 0)#Define serial communication


def Set_Voltage(Port, Voltage): #Set voltage with port and Voltage
    ser.write('SEt, %i, %f\r'%(Port, Voltage))
    message = ser.readline()
    print message

def Read_Voltage(Port): #Read Voltage with port
    ser.write("GET_ADC,%i\r" %(Port))
    voltage = ser.readline()
    return voltage

'''
Look up firmware for Buffer_ramp functions, but what it does is it takes output ports, input ports and initial voltage and final voltage
It can also ramp a list of ports and read a list of ADC ports but I will go for simplicity
'''
def Buffer_Ramp(dacPorts, adcPorts, Init_voltages, Fin_voltages, steps, delay, nReadings = 1):

    ser.write('BUFFER_RAMP, %s, %s, %s, %s, %i, %i, %i\r' % (dacPorts, adcPorts, Init_voltages, Fin_voltages, steps, delay, nReadings))
    totalbytes = steps * 2

    initdata = ''
    while initdata == '':
        initdata = ser.read()

    bufferdata = initdata
    data = ''
    while len(data) < totalbytes:
        data = data + bufferdata
        bufferdata = ser.read()
    data = list(data)
    voltages = []
    for x in range(0, len(data), 2):
        b1 = int(data[x].encode('hex'),16)
        b2 = int(data[x + 1].encode('hex'), 16)
        decimal = twoByteToInt(b1, b2)
        voltage = map2(decimal, 0, 65536, -10.0, 10.0)
        voltages.append(voltage)

    return voltages

'''
Ramp without taking data
'''
def Ramp(port, Init_voltages, Fin_voltages, steps, delay):
    ser.write("RAMP1,%i,%f,%f,%i,%i\r"%(port, Init_voltages, Fin_voltages, steps, delay))
    
#Convert number to voltage
def map2(x, in_min, in_max, out_min, out_max):
  return (x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min;

#attach 2 bytes to 8bits
def twoByteToInt(DB1,DB2): # This gives a 16 bit integer (between +/- 2^16)
  return 256*DB1 + DB2

#Flush all the useless reading in DACADC
def Flush():
    while True:
        read = ser.read()
        if read =='':
            break

DACPort = 0
ADCPort = 0
Voltage_Start = -5.0
Voltage_End = 5.0
Number_of_Steps = 100
Delay = 100 #unit in microsecond

XValues = np.linspace(Voltage_Start, Voltage_End, Number_of_Steps)

Flush() # Clear previous data
Ramp(DACPort, 0.0, Voltage_Start, Number_of_Steps, Delay)
time.sleep(1)
Flush() #Clear incase there are data
Data = Buffer_Ramp(DACPort, ADCPort, Voltage_Start, Voltage_End, Number_of_Steps, Delay)
time.sleep(1)
Flush() #Clear incase there are data

Ramp(DACPort, Voltage_End, 0.0, Number_of_Steps, Delay)

mplt.plot(XValues, Data)
mplt.show()
print Data