import getopt
import socket
import sys
import os
import platform
from nfutil import *
from enumip import *
import fcntl

def main():
    
    
    iplist = enumIp();
    if len(iplist) == 0:
        print("Host has no IP address.")
        sys.exit(1)
    
    devices = {}
    
    for ip in iplist:      
        print("Searching through network interface:", ip)
               
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

        port = 0
        
        try:
            s.bind((ip, port))
        except socket.error:
            print("Bind error on send socket:", socket.error)
            sys.exit(1)

        port = s.getsockname()[1]       
        
        r = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        r.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        r.setblocking(1)
        r.settimeout(0.100)

        try:
            r.bind(('', port))
        except socket.error:
            print("Bind error on receive socket:", socket.error)
            sys.exit(1)
            
        d = Discover(s, r)

        for k in d:
            d[k]['host_ip'] = ip
            devices[k] = d[k]

        s.close()
        r.close()

    print("Found", len(devices), "Prologix GPIB-ETHERNET Controller(s).")
    for key in devices:
        PrintDetails(devices[key])



def enumIp():
    if platform.system() in ('Windows', 'Microsoft'):
        return socket.gethostbyname_ex(socket.gethostname())[2];

    return enumIpUnix()

def all_interfaces():
    max_possible = 128 # arbitrary. raise if needed.
    bytes = max_possible * 32
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    names = array.array('B', [0]) * bytes
    outbytes = struct.unpack('iL', fcntl.ioctl(
        s.fileno(),
        0x8912, # SIOCGIFCONF
        struct.pack('iL', bytes, names.buffer_info()[0])
        ))[0]
    namestr = names.tostring()
    lst = []
    for i in range(0, outbytes, 40):
        name = namestr[i:i+16].split(b'\x00', 1)[0]
        ip = namestr[i+20:i+24]
        lst.append((name, ip))
    return lst

all_interfaces()
