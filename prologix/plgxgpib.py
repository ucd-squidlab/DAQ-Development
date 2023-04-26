"""
This is the CU Denver SQUID lab module for communicating with our PrologixGPIB ethernet adapter

This will draw from the wanglib prologix module however the instrument object will be handeled diffrently 
and be designed for use with a python defined code. This is a base class which will be inherited by any 
instruments we will need to communicate with over GPIB. This module will not be used for serial communications.

Author: Autumn Bauman autumn.bauman@ucdenver.edu 

This program is free software licensed under the apache license

(c) 2023 CU Denver SQUID lab, Martin E Huber
"""

import socket
from scapy.all import getmacbyip
import regex as re



EOI = b"EOI"


class prologixEthernet:

    PLGX_MAC =  0x2169  # First three octets of 
    ESC = b"0x27"   #ASCII escape character used to escape values in 

    def __init__(self, ipaddr:str, port:int=1234, timeout:float=5):
        """ 
        Create object to connect to the Prologix GPIB/Enet controller.

        ipaddr:str IP Address of Prologix Controller
        port:str default="1234" Port to use to connect to prologix controller
        timeout:float default=5 Timeout to wait for command
        """
        #Checks to ensure we are looking at the coorrect object
        """
        self.MAC = self.isGpib(ipaddr)

        # Creates the web socket, uses IPV4 
        self.plgx = socket.socket(socket.AF_INET, socket.SOCK_STREAM, socket.IPPROTO_TCP)
        self.plgx.settimeout(timeout)

        #Touple of ip address and port
        address = (ipaddr, port)
        # Open the socket!
        self.plgx.connect(address)
"""



    def isGpib(self, addr:str):
        """
        Test if IP address corresponds to prologix controller 

        addr:str Address to query
        """
        try:    # Gets the mac address associated with the IP address
            mac = getmacbyip(addr)
        except:  # If it doesn't connect returns error
            raise ValueError("Incorrect IP Address")
        else: # if it doesn't error out above this compares the mac addresses
            #Convert string of mac address to base 16 integer
            mac = int(re.sub(":", "", mac), 16)
            # Shifts the mac address over by three octets or 24 bits (isolates the first three octets) 
            # then subtracts the first three octets of the prologix controller. If it is zero it
            # evaluates to false which means that the device was made by prologix and so returns the mac address
            if not (self.PLGX_MAC - (mac >> 24)): return mac
            else: raise ValueError(f"Device at {addr} not Prologix device!")

    @property
    def address(self):
        pass
        self.addr

    @property
    def readafterwrite(self):
        self._auto = bool(int(self.ask("++auto")))
        return self._auto

    @readafterwrite.setter
    def readafterwrite(self, RAW:bool):
        self._auto = bool(RAW)
        self.write(f"++auto {int(self._auto)}", escape=False)


    def write(self, command:str, auto:bool=False, escape=True):
        """
        Sends command to instrument and does not read response

        command:str Command to send to instrument
        auto:bool False If True this will direct instrument to talk after command is written
        escape:bool True if command contains [+ \\n \\r] characters this escapes them with \\x1B character so they will be passed to instrument and not captured by Prologix
        """
        # Make it into an ascii string stored as a bytearray
        command = command.encode(encoding='ascii')
        #If it is set to escape special characters then this will do it, used for 
        # + \n and \r and escapes them using the ascii character \x1B. 

        #print(command.hex())
        #print(bool(re.search(b"[\x0A\x0D\x2b]", command)))
        #print(re.search(b"[\x0A\x0D\x2b]", command))
        if escape and bool(re.search(b"[\x0A\x0D\x2b]", command)):
            #print(True)
            command = re.sub(rb"(\x0A)", rb"\x1B\1", command)
            command = re.sub(rb"(\x0D)", rb"\x1B\1", command)
            command = re.sub(rb"(\x2B)", rb"\x1B\1", command)

        # Appends ethernet termination character to command
        command = command+b"\n"

        if auto:
            self.plgx.send(b"++auto 1\n")
        else:
            self.plgx.send(b"++auto 0\n")

        #print(command.hex())
        # Sends command to instrument and stores number of bytes sent 
        bts = self.plgx.send(command)

        # Returns zero if it transmitted all bites 
        return bts-len(command)



    def read(self):
        pass
    def ask(self, command):
        pass
        




    def instrument(self, addr:int, terminator:bytes=EOI):
        """
        Generator function for Instrument objects. Takes the same arguments as 
        Instrument class

        addr:int Address of GPIB device to access
        terminator
        """
        return Instrument(self, addr, terminator)


class Instrument():

    def __init__(self, controller:object, addr, terminator:bytes = EOI):
        """
        Instrument object 
        addr:int Address of GPIB device to access
        terminator
        """
        #GPIB bus to use
        self.bus = controller
        # Termiator
        self.term = terminator
        self.address = addr
        #GPIB Identifier
        self.IDN = 3
    
    def _ControlBus(self):
        pass

