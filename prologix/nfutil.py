"""
NetFinder CLI for UNIX systems 
Taken from https://prologix.biz/downloads/nfcli.tar.gz
This file is free software and cvan be used without restriction for private,
institutional, and comercial purposes. 

Discover function is the main useful function here

Added to DAQ 20230426 by Autumn Bauman 
Author unknown
"""

import struct
import random
import socket
import array
import time
import sys
import socket


NETFINDER_SERVER_PORT  = 3040

NF_IDENTIFY                     =  0
NF_IDENTIFY_REPLY               =  1
NF_ASSIGNMENT                   =  2
NF_ASSIGNMENT_REPLY             =  3
NF_FLASH_ERASE                  =  4
NF_FLASH_ERASE_REPLY            =  5
NF_BLOCK_SIZE                   =  6
NF_BLOCK_SIZE_REPLY             =  7
NF_BLOCK_WRITE                  =  8
NF_BLOCK_WRITE_REPLY            =  9
NF_VERIFY                       = 10
NF_VERIFY_REPLY                 = 11
NF_REBOOT                       = 12
NF_SET_ETHERNET_ADDRESS         = 13
NF_SET_ETHERNET_ADDRESS_REPLY   = 14
NF_TEST                         = 15
NF_TEST_REPLY                   = 16

NF_SUCCESS                      = 0
NF_CRC_MISMATCH                 = 1
NF_INVALID_MEMORY_TYPE          = 2
NF_INVALID_SIZE                 = 3
NF_INVALID_IP_TYPE              = 4

NF_MAGIC                        = 0x5A

NF_IP_DYNAMIC                   = 0
NF_IP_STATIC                    = 1

NF_ALERT_OK                     = 0x00
NF_ALERT_WARN                   = 0x01
NF_ALERT_ERROR                  = 0xFF

NF_MODE_BOOTLOADER              = 0
NF_MODE_APPLICATION             = 1

NF_MEMORY_FLASH                 = 0
NF_MEMORY_EEPROM                = 1

NF_REBOOT_CALL_BOOTLOADER       = 0
NF_REBOOT_RESET                 = 1


HEADER_FMT                      = "!2cH6s2x"
IDENTIFY_FMT                    = HEADER_FMT
IDENTIFY_REPLY_FMT              = "!H6c4s4s4s4s4s4s32s"
ASSIGNMENT_FMT                  = "!3xc4s4s4s32x"
ASSIGNMENT_REPLY_FMT            = "!c3x"
FLASH_ERASE_FMT                 = HEADER_FMT
FLASH_ERASE_REPLY_FMT           = HEADER_FMT
BLOCK_SIZE_FMT                  = HEADER_FMT
BLOCK_SIZE_REPLY_FMT            = "!H2x"
BLOCK_WRITE_FMT                 = "!cxHI"
BLOCK_WRITE_REPLY_FMT           = "!c3x"
VERIFY_FMT                      = HEADER_FMT
VERIFY_REPLY_FMT                = "!c3x"
REBOOT_FMT                      = "!c3x"
SET_ETHERNET_ADDRESS_FMT        = "!6s2x"
SET_ETHERNET_ADDRESS_REPLY_FMT  = HEADER_FMT
TEST_FMT                        = HEADER_FMT
TEST_REPLY_FMT                  = "!32s"

MAX_ATTEMPTS                    = 10
MAX_TIMEOUT                     = 0.5


#-----------------------------------------------------------------------------
def MkHeader(id, seq, eth_addr):
    return struct.pack(
        HEADER_FMT,
        chr(NF_MAGIC),
        chr(id),
        seq,
        eth_addr
        );    


#-----------------------------------------------------------------------------
def MkIdentify(seq):
    return MkHeader(NF_IDENTIFY, seq, '\xFF\xFF\xFF\xFF\xFF\xFF')


#-----------------------------------------------------------------------------
def MkAssignment(seq, eth_addr, ip_type, ip_addr, netmask, gateway):

    return MkHeader(NF_ASSIGNMENT, seq, eth_addr) + \
        struct.pack(
            ASSIGNMENT_FMT,
            chr(ip_type),
            socket.inet_aton(ip_addr),
            socket.inet_aton(netmask),
            socket.inet_aton(gateway)
            )


#-----------------------------------------------------------------------------
def MkFlashErase(seq, eth_addr):
    return MkHeader(NF_FLASH_ERASE, seq, eth_addr)


#-----------------------------------------------------------------------------
def MkBlockSize(seq, eth_addr):
    return MkHeader(NF_BLOCK_SIZE, seq, eth_addr)


#-----------------------------------------------------------------------------
def MkBlockWrite(seq, eth_addr, memtype, addr, data):  
    return MkHeader(NF_BLOCK_WRITE, seq, eth_addr) + \
        struct.pack(
                BLOCK_WRITE_FMT,
                chr(memtype),
                len(data),
                addr,
                ) + \
        data


#-----------------------------------------------------------------------------
def MkVerify(seq, eth_addr):
    return MkHeader(NF_VERIFY, seq, eth_addr)


#-----------------------------------------------------------------------------
def MkReboot(seq, eth_addr, reboottype):  
    return MkHeader(NF_REBOOT, seq, eth_addr) + \
        struct.pack(
            REBOOT_FMT,
            chr(reboottype)
            );


#-----------------------------------------------------------------------------
def MkTest(seq, eth_addr):
    return MkHeader(NF_TEST, seq, eth_addr)


#-----------------------------------------------------------------------------
def MkSetEthernetAddress(seq, eth_addr, new_eth_addr):
    return MkHeader(NF_SET_ETHERNET_ADDRESS, seq, eth_addr) + \
        struct.pack(
            SET_ETHERNET_ADDRESS_FMT,
            new_eth_addr
            );


#-----------------------------------------------------------------------------
def UnMkHeader(msg):
    params = struct.unpack(
        HEADER_FMT,
        msg
        ); 
        
    d = {}
    d['magic'] = ord(params[0])
    d['id'] = ord(params[1])
    d['sequence'] = params[2]
    d['eth_addr'] = params[3]
    return d


#-----------------------------------------------------------------------------
def UnMkIdentifyReply(msg):
    hdrlen = struct.calcsize(HEADER_FMT)
    
    d = UnMkHeader(msg[0:hdrlen])
    
    params = struct.unpack(
        IDENTIFY_REPLY_FMT,
        msg[hdrlen:]
        ); 
        
    d['uptime_days'] = params[0]
    d['uptime_hrs'] = ord(params[1])
    d['uptime_min'] = ord(params[2])
    d['uptime_secs'] = ord(params[3])
    d['mode'] = ord(params[4])
    d['alert'] = ord(params[5])
    d['ip_type'] = ord(params[6])
    d['ip_addr'] = params[7]
    d['ip_netmask'] = params[8]
    d['ip_gw'] = params[9]
    d['app_ver'] = params[10]
    d['boot_ver'] = params[11]
    d['hw_ver'] = params[12]
    d['name'] = params[13]
    return d


#-----------------------------------------------------------------------------
def UnMkAssignmentReply(msg):
    hdrlen = struct.calcsize(HEADER_FMT)
    
    d = UnMkHeader(msg[0:hdrlen])
    
    params = struct.unpack(
        ASSIGNMENT_REPLY_FMT,
        msg[hdrlen:]
        ); 

    d['result'] = ord(params[0])
    return d


#-----------------------------------------------------------------------------
def UnMkFlashEraseReply(msg):
    return UnMkHeader(msg)


#-----------------------------------------------------------------------------
def UnMkBlockSizeReply(msg):
    hdrlen = struct.calcsize(HEADER_FMT)
    
    d = UnMkHeader(msg[0:hdrlen])
    
    params = struct.unpack(
        BLOCK_SIZE_REPLY_FMT,
        msg[hdrlen:]
        ); 
        
    d['size'] = params[0]
    return d


#-----------------------------------------------------------------------------
def UnMkBlockWriteReply(msg):
    hdrlen = struct.calcsize(HEADER_FMT)
    
    d = UnMkHeader(msg[0:hdrlen])
    
    params = struct.unpack(
        BLOCK_WRITE_REPLY_FMT,
        msg[hdrlen:]
        ); 
        
    d['result'] = ord(params[0])
    return d


#-----------------------------------------------------------------------------
def UnMkVerifyReply(msg):
    hdrlen = struct.calcsize(HEADER_FMT)
    
    d = UnMkHeader(msg[0:hdrlen])
    
    params = struct.unpack(
        VERIFY_REPLY_FMT,
        msg[hdrlen:]
        ); 
        
    d['result'] = ord(params[0])
    return d


#-----------------------------------------------------------------------------
def UnMkTestReply(msg):
    hdrlen = struct.calcsize(HEADER_FMT)
    
    d = UnMkHeader(msg[0:hdrlen])
    
    params = struct.unpack(
        TEST_REPLY_FMT,
        msg[hdrlen:]
        ); 

    result = ''
    for i in params[0]:
        if ord(i) == 0:
            break
        result = result + i
        
    d['result'] = result
    return d


#-----------------------------------------------------------------------------
def UnMkSetEthernetAddressReply(msg):
    return UnMkHeader(msg)


#-----------------------------------------------------------------------------
def SendMsg(s, msg):

    try:
        s.sendto(msg, ('<broadcast>', NETFINDER_SERVER_PORT))
    except socket.error:
        print(socket.error)
        return False;

    return True;
    
#-----------------------------------------------------------------------------
def RecvMsg(s):
    try:
        return s.recv(256)
    except socket.error: # ignore socket errors
        return ''

#-----------------------------------------------------------------------------
def Discover(s, r):
    """
    Function to discover all Prologix devices on a network
    """
    
    devices = {}  

    attempts = 2    
    while attempts > 0:
        attempts = attempts - 1

        seq = random.randint(1, 65535) 
        msg = MkIdentify(seq)

        if (SendMsg(s, msg)):
            exp = time.time() + MAX_TIMEOUT
            while time.time() < exp:
                sys.stdout.write('.')
                reply = RecvMsg(r)
                if len(reply) != struct.calcsize(HEADER_FMT) + struct.calcsize(IDENTIFY_REPLY_FMT):
                    continue

                d = UnMkIdentifyReply(reply)

                if d['magic'] != NF_MAGIC:
                    continue
                if d['id'] != NF_IDENTIFY_REPLY:
                    continue
                if d['sequence'] != seq:
                    continue

                devices[d['eth_addr']]  = d

    return devices


#-----------------------------------------------------------------------------
def Identify(s, r, eth_addr):
    
    attempts = 2
    while attempts > 0:
        attempts = attempts - 1

        seq = random.randint(1, 65535)
        msg = MkIdentify(seq)

        if (SendMsg(s, msg)):
            exp = time.time() + 2 # Longer timeout

            while time.time() < exp:
                sys.stdout.write('.')
                reply = RecvMsg(r)
                if len(reply) != struct.calcsize(HEADER_FMT) + struct.calcsize(IDENTIFY_REPLY_FMT):
                    continue

                d = UnMkIdentifyReply(reply)

                if d['magic'] != NF_MAGIC:
                    continue
                if d['id'] != NF_IDENTIFY_REPLY:
                    continue
                if d['sequence'] != seq:
                    continue
                if d['eth_addr'] != eth_addr:
                    continue

                return d

    return {}

    
#-----------------------------------------------------------------------------
def Assignment(s, r, eth_addr, ip_type, ip_addr, netmask, gateway):
    
    attempts = MAX_ATTEMPTS
    while attempts > 0:
        attempts = attempts - 1

        seq = random.randint(1, 65535)
        msg = MkAssignment(seq, eth_addr, ip_type, ip_addr, netmask, gateway)

        if (SendMsg(s, msg)):
            exp = time.time() + MAX_TIMEOUT 

            while time.time() < exp:
                sys.stdout.write('.')
                reply = RecvMsg(r) 

                if len(reply) != struct.calcsize(HEADER_FMT) + struct.calcsize(ASSIGNMENT_REPLY_FMT):
                    continue

                d = UnMkAssignmentReply(reply)

                if d['magic'] != NF_MAGIC:
                    continue
                if d['id'] != NF_ASSIGNMENT_REPLY:
                    continue
                if d['sequence'] != seq:
                    continue
                if d['eth_addr'] != eth_addr:
                    continue

                return d

    return {} 
    
    
#-----------------------------------------------------------------------------
def FlashErase(s, r, eth_addr):
    
    attempts = MAX_ATTEMPTS
    while attempts > 0:
        attempts = attempts - 1

        seq = random.randint(1, 65535)
        msg = MkFlashErase(seq, eth_addr)

        if (SendMsg(s, msg)):
            exp = time.time() + 10 # Flash erase could take a while

            while time.time() < exp:
                sys.stdout.write('.')
                reply = RecvMsg(r)
                if len(reply) != struct.calcsize(HEADER_FMT):
                    continue

                d = UnMkFlashEraseReply(reply)

                if d['magic'] != NF_MAGIC:
                    continue
                if d['id'] != NF_FLASH_ERASE_REPLY:
                    continue
                if d['sequence'] != seq:
                    continue
                if d['eth_addr'] != eth_addr:
                    continue

                return d

    return {}  


#-----------------------------------------------------------------------------
def BlockSize(s, r, eth_addr):

    attempts = MAX_ATTEMPTS
    while attempts > 0:
        attempts = attempts - 1

        seq = random.randint(1, 65535)
        msg = MkBlockSize(seq, eth_addr)

        if (SendMsg(s, msg)):
            exp = time.time() + MAX_TIMEOUT

            while time.time() < exp:
                sys.stdout.write('.')
                reply = RecvMsg(r)
                if len(reply) != struct.calcsize(HEADER_FMT) + struct.calcsize(BLOCK_SIZE_REPLY_FMT):
                    continue

                d = UnMkBlockSizeReply(reply)

                if d['magic'] != NF_MAGIC:
                    continue
                if d['id'] != NF_BLOCK_SIZE_REPLY:
                    continue
                if d['sequence'] != seq:
                    continue
                if d['eth_addr'] != eth_addr:
                    continue

                return d

    return {} 


#-----------------------------------------------------------------------------
def BlockWrite(s, r, eth_addr, memtype, addr, data):
    
    attempts = MAX_ATTEMPTS
    while attempts > 0:
        attempts = attempts - 1

        seq = random.randint(1, 65535)
        msg = MkBlockWrite(seq, eth_addr, memtype, addr, data)

        if (SendMsg(s, msg)):
            exp = time.time() + MAX_TIMEOUT

            while time.time() < exp:
                #sys.stdout.write('.'),
                reply = RecvMsg(r)
                if len(reply) != struct.calcsize(HEADER_FMT) + struct.calcsize(BLOCK_WRITE_REPLY_FMT):
                    continue

                d = UnMkBlockWriteReply(reply)

                if d['magic'] != NF_MAGIC:
                    continue
                if d['id'] != NF_BLOCK_WRITE_REPLY:
                    continue
                if d['sequence'] != seq:
                    continue
                if d['eth_addr'] != eth_addr:
                    continue

                return d

    return {} 


#-----------------------------------------------------------------------------
def Verify(s, r, eth_addr):

    attempts = MAX_ATTEMPTS
    while attempts > 0:
        attempts = attempts - 1

        seq = random.randint(1, 65535)
        msg = MkVerify(seq, eth_addr)

        if (SendMsg(s, msg)):
            exp = time.time() + MAX_TIMEOUT

            while time.time() < exp:
                sys.stdout.write('.')
                reply = RecvMsg(r)
                if len(reply) != struct.calcsize(HEADER_FMT) + struct.calcsize(VERIFY_REPLY_FMT):
                    continue

                d = UnMkVerifyReply(reply)

                if d['magic'] != NF_MAGIC:
                    continue
                if d['id'] != NF_VERIFY_REPLY:
                    continue
                if d['sequence'] != seq:
                    continue
                if d['eth_addr'] != eth_addr:
                    continue

                return d

    return {} 


#-----------------------------------------------------------------------------
def Reboot(s, eth_addr, reboottype):
    seq = random.randint(1, 65535)
    msg = MkReboot(seq, eth_addr, reboottype)
    
    if (SendMsg(s, msg)):
        return

            
#-----------------------------------------------------------------------------
def Test(s, r, eth_addr):
    seq = random.randint(1, 65535)
    msg = MkTest(seq, eth_addr)    

    if (SendMsg(s, msg)):        
        exp = time.time() + MAX_TIMEOUT

        while time.time() < exp:
            sys.stdout.write('.')
            reply = RecvMsg(r)                   
            if len(reply) != struct.calcsize(HEADER_FMT) + struct.calcsize(TEST_REPLY_FMT):
                continue

            d = UnMkTestReply(reply)

            if d['magic'] != NF_MAGIC:
                continue
            if d['id'] != NF_TEST_REPLY:
                continue
            if d['sequence'] != seq:
                continue
            if d['eth_addr'] != eth_addr:
                continue

            return d

    return {} 


#-----------------------------------------------------------------------------
def SetEthernetAddress(s, r, eth_addr, new_eth_addr):
    seq = random.randint(1, 65535)
    msg = MkSetEthernetAddress(seq, eth_addr, new_eth_addr)    

    if (SendMsg(s, msg)):        
        exp = time.time() + MAX_TIMEOUT

        while time.time() < exp:
            sys.stdout.write('.')
            reply = RecvMsg(r)                   
            if len(reply) != struct.calcsize(HEADER_FMT):
                continue

            d = UnMkSetEthernetAddressReply(reply)

            if d['magic'] != NF_MAGIC:
                continue
            if d['id'] != NF_SET_ETHERNET_ADDRESS_REPLY:
                continue
            if d['sequence'] != seq:
                continue
            if d['eth_addr'] != eth_addr:
                continue

            return d

    return {} 

#-----------------------------------------------------------------------------
def FormatEthAddr(a):
    return "%02X-%02X-%02X-%02X-%02X-%02X" % (ord(a[0]), ord(a[1]), ord(a[2]), ord(a[3]), ord(a[4]), ord(a[5]))


#-----------------------------------------------------------------------------
def PrintDetails(d):

    print()
    print("Ethernet Address:", FormatEthAddr(d['eth_addr']))
    print("Hardware:", socket.inet_ntoa(d['hw_ver']), "Bootloader:", socket.inet_ntoa(d['boot_ver']), "Application:", socket.inet_ntoa(d['app_ver']))
    print("Uptime:", d['uptime_days'], 'days', d['uptime_hrs'], 'hours', d['uptime_min'], 'minutes', d['uptime_secs'], 'seconds')
    if d['ip_type'] == NF_IP_STATIC:
        print( "Static IP")
    elif d['ip_type'] == NF_IP_DYNAMIC:
        print("Dynamic IP")
    else: 
        print("Unknown IP type")
    print("IP Address:", socket.inet_ntoa(d['ip_addr']), "Mask:", socket.inet_ntoa(d['ip_netmask']), "Gateway:", socket.inet_ntoa(d['ip_gw']))
    print("Mode:")
    if d['mode'] == NF_MODE_BOOTLOADER:
        print('Bootloader')
    elif d['mode'] == NF_MODE_APPLICATION:
        print('Application')
    else:
        print('Unknown')
    
