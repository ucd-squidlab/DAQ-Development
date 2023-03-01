"""
This is a class which sets out instrument interface commands for the CS4-10v 
magnet power supply. In it's current form we will communicate with it over serial
however it will probably be updated to use GPIB eventully.

Requires: Pyvisa, pyvisa_py

Author: Autumn Bauman
"""

import pyvisa
import regex


class CS4Mag():
    def __init__(self, address:str='/dev/ttyUSB0', GPIB:bool=False, baudrate:int=9600, errors:bool=False):
        # Initiate the Resource Manager, using the python backend
        self._rm = pyvisa.ResourceManager('@py')
        # Here is where we attempt to connect to the instrument
        self._cs4in = self._rm.open_resource(address, write_termination="\r", read_termination='\l', baud_rate=(None if GPIB else baudrate))
        # Now we set it to be remote control and lock out the front panel
        self._cs4in.write('REMOTE')
        # checks error status, ensures good communication
        status = int(self._cs4in.query("*ESR?"))


        # Prevents a sweep from running until it's configured
        self.sweepSet = False



    def setIlow(self, Ilow):
        self.Ilow = Ilow

    def setIHigh(): pass


    def defineSweep(self, ISet, ):
        pass

    def magStatus(self):
        self._cs4in.query("IMAG?;IOUT?")




def main():
    magsup = CS4Mag()
