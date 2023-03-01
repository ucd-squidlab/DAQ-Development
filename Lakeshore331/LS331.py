"""
Lakeshore 331 Interface 

Module to interface with Lakeshore 331 temperature controller. This is admittedly 
quick and dirty but also I am writing it at 9:55pm and wanting to have somthing ready 
to go tomorrow when I get to school. 

Author: Autumn Bauman
"""

import pyvisa

class LS331():
    def __init__(self):
        self.RM = pyvisa.ResourceManager('@py')
        self.baud_rate = 9600
        self.devPath = "/dev/ttyUSB0"
    
    def getResources(self):
        """Just lists resources avalible to Pyvisa"""
        return self.RM.list_resources()


    def connect(self, baudRate:int=None, devicePath:str=None):
        """
        Connects to device. 

        baudRate:int default 9600
        devicePath:str default "/dev/ttyUSB0
        """
        if baudRate is not None: self.baud_rate = baudRate
        if devicePath is not None: self.devPath = devicePath
        # This will be the temp controller
        try:
            self.controller = self.RM.open_resource(devicePath, baud_rate=self.baud_rate,
                read_termination="\r\l", write_termination="\r\l")
        except:
            raise Exception("Cannot open resouece!")
        try:
            self.name = self.controller.query("*IDN?")
            print(self.name())
        except: 
            raise Exception("Could not communicate with device!")
        self.controller.write("MODE 2")
        print("Locked controls")
    

    def queryTemp(self):
        atmp = self.controller.query("KRDG? A")
        btmp = self.controller.query("KRDG? B")
        return (atmp, btmp)

    def closeConnection(self):
        self.controller.write("MODE 0")
