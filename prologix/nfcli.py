"""
NetFinder CLI for UNIX systems 
Taken from https://prologix.biz/downloads/nfcli.tar.gz
This file is free software and cvan be used without restriction for private,
institutional, and comercial purposes. 

This file is not used in the Prologix librairy currently

Added to DAQ 20230426 by Autumn Bauman 
Author unknown
"""



import getopt
import socket
import sys
import os
import platform
from nfutil import *
from enumip import *


#-----------------------------------------------------------------------------
def usage():
    print
    print "Usage: nfcli --list --eth_addr=ADDR --ip_type=TYPE --ip_addr=IP, --netmask=MASK, --gateway=GW"
    print "Search and configure Prologix GPIB-ETHERNET Controllers."
    print "--help          : display this help"
    print "--list          : search for controllers"
    print "--eth_addr=ADDR : configure controller with Ethernet address ADDR"
    print "--ip_type=TYPE  : set controller ip address type to TYPE (\"static\" or \"dhcp\")"
    print "--ip_addr=IP    : set controller address to IP"
    print "--netmask=MASK  : set controller network mask to MASK"
    print "--gateway=GW    : set controller default gateway to GW"


#-----------------------------------------------------------------------------
def enumIp():
    if platform.system() in ('Windows', 'Microsoft'):
        return socket.gethostbyname_ex(socket.gethostname())[2];

    return enumIpUnix()


#-----------------------------------------------------------------------------
def ValidateNetParams(ip_str, mask_str, gw_str):

    try:
        ip = socket.inet_aton(ip_str)
    except:
        print "IP address is invalid."
        return False

    try:
        mask = socket.inet_aton(mask_str)
    except:
        print "Network mask is invalid."
        return False

    try:
        gw = socket.inet_aton(gw_str)
    except:
        print "Gateway address is invalid."
        return False

    # Validate network mask

    # Convert to integer from byte array
    mask = struct.unpack("!L", mask)[0]    

    # Exclude restricted masks
    if (mask == 0) or (mask == 0xFFFFFFFF):
        print "Network mask is invalid."
        return False

    # Exclude non-left-contiguous masks
    if (((mask + (mask & -mask)) & 0xFFFFFFFF) != 0):
        print "Network mask is not contiguous."
        return False


    # Validate gateway address

    octet1 = ord(gw[0])

    # Convert to integer from byte array
    gw = struct.unpack("!L", gw)[0]    

    # Exclude restricted addresses
    # 0.0.0.0 is valid
    if ((gw != 0) and ((octet1 == 0) or (octet1 == 127) or (octet1 > 223))):
        print "Gateway address is invalid."
        return False

    # Validate IP address

    octet1 = ord(ip[0])

    # Convert to integer from byte array
    ip = struct.unpack("!L", ip)[0]    

    # Exclude restricted addresses
    if ((octet1 == 0) or (octet1 == 127) or (octet1 > 223)):
        print "IP address is invalid."
        return False

    # Exclude subnet network address
    if ((ip & ~mask) == 0):
        print "IP address is invalid."
        return False

    # Exclude subnet broadcast address
    if ((ip & ~mask) == (0xFFFFFFFF & ~mask)):
        print "IP address is invalid."
        return False

    return True

#-----------------------------------------------------------------------------
#def ValidateAddress(address):

#    if address is None:
#        return False

#    parts = address.split(".")

#    if len(parts) != 4:
#        return False

#    try:
#        for item in parts:
#            if not 0 <= int(item) <= 255:
#                return False
#    except:
#        return False

#    return True


#-----------------------------------------------------------------------------
def main():

    invalid_args = False
    showhelp = False
    search = False
    ip_type = None
    ip_addr = None
    netmask = None
    gateway = None
    eth_addr = None

    try:
        opts, args = getopt.getopt(sys.argv[1:], '', ['help', 'list', 'eth_addr=', 'ip_type=', 'ip_addr=', 'netmask=', 'gateway='])
    except getopt.GetoptError, err:
        print str(err) 
        sys.exit(1)

    # Check for unparsed parameters
    if len(args) != 0:
        usage()
        sys.exit(1)

    for o, a in opts:
        if o == "--help":   
            showhelp = True
        elif o == "--list":
            search = True
        elif o == "--eth_addr":
            eth_addr = a
        elif o == "--ip_type":
            ip_type = a
        elif o == "--ip_addr":
            ip_addr = a
        elif o == "--netmask":
            netmask = a
        elif o == "--gateway":
            gateway = a

    if (len(opts) == 0) or (showhelp):
        usage()
        sys.exit(1)
       
    if search:
        if not eth_addr is None:
            print "--list and --eth_addr are not compatible."
            invalid_args = True
        if not ip_type is None:
            print "--list and --ip_type are not compatible."
            invalid_args = True
        if not ip_addr is None:
            print "--list and --ip_addr are not compatible."
            invalid_args = True
        if not netmask is None:
            print "--list and --netmask are not compatible."
            invalid_args = True
        if not gateway is None:
            print "--list and --gateway are not compatible."
            invalid_args = True
    else:

        try:
            eth_addr = eth_addr.strip().replace(":", "").replace("-", "")
            eth_addr = eth_addr.decode('hex')
        except:
            print "Invalid Ethernet address."
            sys.exit(1)

        if len(eth_addr) != 6:
            print "Invalid Ethernet address."
            sys.exit(1)

        if ip_type in ["Static", "static"]:
            ip_type = NF_IP_STATIC
        elif ip_type in ["Dynamic", "dynamic", "Dhcp", "dhcp"]:
            ip_type = NF_IP_DYNAMIC
        else:
            print "--ip_type must be 'static' or 'dhcp'."
            sys.exit(1)

        if ip_type == NF_IP_STATIC:

            if not ValidateNetParams(ip_addr, netmask, gateway):
                invalid_args = True


#            if not ValidateIP(ip_addr):
#                print "Invalid, or no, IP address specified."
#                invalid_args = True

#            if not ValidateIP(netmask):
#                print "Invalid, or no, netmask specified."
#                invalid_args = True

#            if not ValidateIP(gateway):
#                print "Invalid, or no, gateway address specified."
#                invalid_args = True
        else:
            if ip_addr is None:
                ip_addr = "0.0.0.0"
            else:
                print "--ip_addr not allowed when --ip_type=dhcp."
                invalid_args = True
            if netmask is None:
                netmask = "0.0.0.0"
            else:
                print "--netmask not allowed when --ip_type=dhcp."
                invalid_args = True
            if gateway is None:
                gateway = "0.0.0.0"
            else:
                print "--gateway not allowed when --ip_type=dhcp."
                invalid_args = True

    if invalid_args:
        sys.exit(1)



    global seq
    sys.stdout = os.fdopen(sys.stdout.fileno(), 'w', 0)
    
    iplist = enumIp();
    if len(iplist) == 0:
        print "Host has no IP address."
        sys.exit(1)
    

    devices = {}
    
    for ip in iplist:      
        print "Searching through network interface:", ip
               
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

        port = 0
        
        try:
            s.bind((ip, port))
        except socket.error, e:
            print("Bind error on send socket:", e)
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
        print

        for k in d:
            d[k]['host_ip'] = ip
            devices[k] = d[k]

        s.close()
        r.close()

    if search:
        print
        print "Found", len(devices), "Prologix GPIB-ETHERNET Controller(s)."
        for key in devices:
            PrintDetails(devices[key])
            print
    else:
        if eth_addr in devices:

            print "Updating network settings of Prologix GPIB-ETHERNET Controller", FormatEthAddr(eth_addr)

            device = devices[eth_addr]

            if (device['ip_type'] == NF_IP_STATIC) or (ip_type == NF_IP_STATIC):
                s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

                port = 0

                try:
                    s.bind((device['host_ip'], port))
                except socket.error, e:
                    print "Bind error on send socket:", e
                    sys.exit(1)

                port = s.getsockname()[1]       

                r = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                r.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

                r.setblocking(1)
                r.settimeout(0.100)

                try:
                    r.bind(('', port))
                except socket.error, e:
                    print "Bind error on receive socket:", e
                    sys.exit(1)

                result = Assignment(s, r, eth_addr, ip_type, ip_addr, netmask, gateway)
                print

                if len(result) == 0:
                    print "Network settings update failed."
                else:
                    if result['result'] == NF_SUCCESS:
                        print "Network settings updated successfully."
                    else:
                        print "Network settings update failed."
            else:
                print "Prologix GPIB-ETHERNET Controller", FormatEthAddr(eth_addr), "already configured for DHCP."  
        else:
            print "Prologix GPIB-ETHERNET Controller", FormatEthAddr(eth_addr), "not found."
        

    
#-----------------------------------------------------------------------------
if __name__ == "__main__":
    main()