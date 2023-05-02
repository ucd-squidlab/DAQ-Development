"""
This is a simple terminal based program to read and display a trace from the SR770
"""


import numpy as np
import matplotlib.pyplot as plt
import regex as re
from plgxgpib import prologixEthernet
import time

# First we connect to the interface
plgx = prologixEthernet("10.20.4.31")
# Then we create an instrumrnt (in this case SR770) at GPIB address 3
sa = plgx.asciiInstrument(3)
# Now we query the instrument, see who it is!
#plgx.flushRead()
print(sa.read(), "DEBUG L18")
print(sa.ask("*IDN?"), "DEBUG L19")
# The ask command sends a command to the instrument, waits a certian delay,
# then reads out the return value as a bytes object.

# We can send multiple instructions in a single line to the instrument, in 
# this case seperating them by semicolons. If there are multiple commands 
# we are expecting returns from we can recieve them all at once by setting 
# the multi argument to the number of returns we are expecting.
# This returns a list of everything. 
print(sa.ask("*ESR?"))
print(sa.ask("FFTS?"))
print(sa.ask("ERRS?"))
# Now we need to set up some stuff on the instrument. 
# The goal here is to read out a 50kHz spectrum centered 
# at 75kHz on a linear scale. We are looking at trace zero.
sa.write("ACTG 0;MEAS 0,1;SPAN 18;CTRF 75E3;XAXS 0,0;AUTS 0;ARNG 1")
# Now we will setup the averaging
#sa.write("AVGO 1;NAVG 100; AVGT 0;AVGM 0")
# Now we need to test to make sure our ranges are correct!
print(sa.read(), "DEBUG L38")
spans = sa.ask("SPAN?;STRF?;UNIT?;XAXS? 0;STRT", multi=4)
print("spans", spans)
# This lets it stabilize and average
#time.sleep(5)
#data = sa.ask("SPEC? 0")
#print(data)
