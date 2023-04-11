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
from scapy import getmacbyip
import regex as re

PLGX_MAC =  0x2169

class prologixEthernet:
    def __init__(self, ipaddr:str, query=False):
        """ 
        ipaddr:str IP Address of Prologix Controller
        """
        self.connected=False # Is this connected?
        # Socket used to handel communication with GPIB/Enet
        self.MAC = self.isGpib(ipaddr)
        
        self.plgx = socket.socket(socket.AF_INET, socket.SOCK_STREAM, socket.IPPROTO_TCP)

    def isGpib(self, addr:str):
        """
        Test if IP address corresponds to prologix controller 

        addr:str Address to query
        """
        try:    # Gets the mac address of the 
            mac = getmacbyip(addr)
        except:
            raise ValueError("Incorrect IP Address")
        else:
            mac = int(re.sub(":", "", mac), 16)
            if not (PLGX_MAC - (mac >> 16)): return mac

            else: raise ValueError(f"Device at {addr} not Prologix device!")

