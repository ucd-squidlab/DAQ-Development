import subprocess
import pandas as pd
import regex as re

def getmac(IP:str):
    oct = IP.rindex(".")
    ip = IP[0:oct+1]
    print(ip, oct)
    ip = ip+"255"
    print(ip)
    subprocess.run(["ping", "-c", "2", "255.255.255.255"])
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
    #arps = arps[1,3a ]