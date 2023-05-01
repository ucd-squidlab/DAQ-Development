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
#import pandas as pd
#import subprocess
import regex as re
from time import sleep



EOI = b"EOI"


class prologixEthernet:

    PLGX_MAC =  0x2169  # First three octets of 
    ESC = b"0x27"   #ASCII escape character used to escape values in 

    def __init__(self, ipaddr:str, port:int=1234, timeout:float=5):
        """ 
        Create object to connect to the Prologix GPIB/Enet controller.

        ipaddr:str IP Address of Prologix Controller
        port:str default="1234" Port to use to connect to prologix controller
        timeout:float default=5 Timeout to wait for return from controller
        """
        # Checks to ensure we are looking at the coorrect object

        # Update: This code won't work because there is no easy way to find the mac addresses of  

        # self.MAC = self.isGpib(ipaddr)

        # Creates the web socket, uses IPV4 and TCP protocol
        self.plgx = socket.socket(socket.AF_INET, socket.SOCK_STREAM, socket.IPPROTO_TCP)
        self.plgx.settimeout(timeout)

        #Touple of ip address and port
        address = (ipaddr, port)
        # Open the socket!
        self.plgx.connect(address)



#    def isGpib(self, addr:str):
        """
#        Oh if only this worked...
#        Test if IP address corresponds to prologix controller 

#        addr:str Address to query
        
        try:    # Gets the mac address associated with the IP address
            mac = self.getmac(addr)
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
    """
        """
    def getmac(self, IP:str, subnet:bool = False):
        """
    """
        Function which finds the mac address of a given IP address or subnet

        If subnet is selected then it will return a list of all mac and IP addresses
        on the subnet. 

        IP:str IP address to find mac for. If subnet=True, IP should be of form "192.168.1.x"
        subnet:bool Default:False; if set to true the function will list all MAC and IP addresses on the subnet 
        """ """
        subprocess.run(["ping", "-c", "2", 255.255.255.255])
        arps = pd.DataFrame(
            [a.split(" ") for a in subprocess.run(['arp', '-a'],
                                                stdout=subprocess.PIPE).stdout.decode().split("\n")[0:-2]],
            columns=["host","ip","a1","mac","a5","a6","a7","a8", "a9"])
        iplist = arps.ip.to_list()
        maclist = arps.mac.to_list()
        for i, k in enumerate(iplist):
            iplist[i] = re.sub("[\(\)]", "", k)
        print(iplist)
        try:
            mac = maclist[iplist.index(IP)]
        except:
            raise ValueError(f"IP Address {IP} not found on subnet {ip}")
        else:
            return mac
"""
    @property
    def address(self):
        """
        Creates a property which is the GPIB address
        """
        self.addr = int(self.ask("++addr"))

    @address.setter
    def address(self, new_addr):
        """
        Sets the GPIB address of the bus
        """
        self.addr = new_addr
        self.write(f"++addr {new_addr}")

    @property
    def readafterwrite(self):
        """
        Should the controller have the instrument talk immediately after reading?
        """
        self._auto = bool(int(self.ask("++auto")))
        return self._auto

    @readafterwrite.setter
    def readafterwrite(self, RAW):
        self._auto = bool(RAW)
        self.write(f"++auto {int(self._auto)}", escape=False)


    def writeascii(self, command:str, escape=True):
        """
        Write command string to Plgx controller. If the command contains character of +, \\n, or ESC (\\)
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
        #print(command.hex())
        command = command + b'\x0A'
        self.plgx.send(command)

    def readascii(self):
        """
        Read all bytes from Prologix buffer. This works with datasets up to 2^13 bytes.
        This does not work with binairy data transfer
        """
        try:
            return self.plgx.recv(8192).rstrip()
        except:
            return b"Its dead Jim"
        
    def makeTalk(self):
        """
        Directs instrument at current address to send out response
        """
        self.plgx.send(b"++read eoi\n")
        




    def asciiInstrument(self, addr:int, Auto, term):
        """
        Generator function for asciiInstrument objects. Takes the same arguments as 
        Instrument class

        addr:int Address of GPIB device to access
        Auto:bool address instrument to talk immediately after writing. 
        terminator: EOI by default, we can add ascii terminators later if we need. 
        """
        return asciiInstrument(self, addr, auto=Auto, terminator=term)


class asciiInstrument():

    def __init__(self, controller:prologixEthernet, addr:int, auto:bool=True, terminator:bytes = EOI):
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
        self.auto = auto
    
    def _ControlBus(self, auto:bool=True):
        if (self.bus._auto != self.auto) and auto:
            self.bus.readafterwrite = self.auto
        
        if self.bus.addr != self.address:
            self.bus.address = self.address


    def read(self, flush=True):
        """
        Read data from instrument. Directs instrument to talk and returns bytes object of response
        If the buffer needs to be cleared before reading preface with another read command
        """
        self._ControlBus()
        if not self.auto:
            self.bus.makeTalk()
        return self.bus.readascii()
    
    def write(self, command):
        """
        Writes data to instrument, will not read return. 
        """
        self._ControlBus()
        self.bus.writeascii(command)


    def ask(self, command:str, delay=.1):
        """
        Send command to instrument and read response after delay

        delay:float Seconds to wait after sending command to read
        """
        self.write(command)
        sleep(delay)
        return self.read()
        
