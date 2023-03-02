"""
Lakeshore 331 Interface 

Module to interface with Lakeshore 331 temperature controller. This is admittedly 
quick and dirty but also I am writing it at 9:55pm and wanting to have somthing ready 
to go tomorrow when I get to school. 

Author: Autumn Bauman
"""

import pyvisa
from pyvisa.constants import Parity
import regex as re
class LS331():
    def __init__(self):
        self.RM = pyvisa.ResourceManager('@py')
        self.baud_rate = 9600
        self.devPath = "/dev/ttyUSB0"
    
    def getResources(self):
        """Just lists resources avalible to Pyvisa"""
        return self.RM.list_resources()


    def connect(self, devicePath:str, baudRate:int=None):
        """
        Connects to device. 

        baudRate:int default 9600
        devicePath:str default "/dev/ttyUSB0
        """
        if baudRate is not None: self.baud_rate = baudRate
        # This will be the temp controller
        self.controller = self.RM.open_resource(devicePath, baud_rate=9600, read_termination='\n\r', write_termination="\n")


        self.controller.parity = Parity.odd
        self.controller.data_bits = 7
        try:
            self.name = self.controller.query("*IDN?")
            print(self.name)
        except: 
            raise Exception("Could not communicate with device!")
        self.controller.write("MODE 2")
        print("Locked controls")
    

    def queryTemp(self):
        atmp = re.sub('[^\d.]', "", self.controller.query("KRDG? A"))
        btmp = re.sub('[^\d.]', "", self.controller.query("KRDG? B"))
        return (atmp, btmp)

    def closeConnection(self):
        self.controller.write("MODE 0")
        self.controller.close()
