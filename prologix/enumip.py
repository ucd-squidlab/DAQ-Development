import socket
import struct
import array

IOCTL_SIOCGIFCONF = 0x8912

# /*
#  * Structure used in SIOCGIFCONF request.
#  * Used to retrieve interface configuration
#  * for machine (useful for programs which
#  * must know all networks accessible).
#  */
#     
# struct  ifconf {
#     int ifc_len;        /* size of associated buffer */
#     union {
#         caddr_t ifcu_buf;
#         struct  ifreq *ifcu_req;
#     } ifc_ifcu;
#     
# /*
#  * Interface request structure used for socket
#  * ioctl's.
#  */
#  
# struct  ifreq {
#     char    ifr_name[16];     /* if name, e.g. "en0" */
#     union {
#         struct  sockaddr ifru_addr;
#         struct  sockaddr ifru_dstaddr;
#         struct  sockaddr ifru_broadaddr;
#         short   ifru_flags;
#         int ifru_metric;
#         caddr_t ifru_data;
#     } ifr_ifru;
# 
# 
# /* Socket address, DARPA Internet style */
# struct sockaddr_in {
#     short sin_family;
#     unsigned short sin_port;
#     struct in_addr sin_addr;
#     char sin_zero[8];
# };    
#
#
# ioctl (fd, SIOCGIFCONF, &ifconf)


def enumIpUnix():
    import fcntl

    inbytes = 128 * 32   # Maximum 128 interfaces
    ifreq = array.array('B', b'\0' * inbytes)

    ifconf = struct.pack('iL', inbytes, ifreq.buffer_info()[0])

    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    ifconf = fcntl.ioctl(s.fileno(), IOCTL_SIOCGIFCONF, ifconf)
    
    outbytes = struct.unpack('iL', ifconf)[0]
    
    iplist = [socket.inet_ntoa(ifreq[i+20:i+24]) for i in range(0, outbytes, 32)] 
    
    return [ip for ip in iplist if ip != '127.0.0.1']
