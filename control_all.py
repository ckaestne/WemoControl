#!/usr/bin/env python
#Get the IP Address
import wemo_insight
import time,os
import socket

def start_all():
    hostfile = "host.txt"
   # ipfile = "ip.txt"
    fo1 = open(hostfile,'r')
   # fo2 = open(ipfile,'r')
    for hostline in fo1:
	print "starting "+hostline.strip()
        try:
            hostline = hostline.strip()               
            newip = socket.gethostbyname(hostline)    
    #        for ipline in fo2: 
     #           ipline = ipline.strip()               
      #          if (newip == ipline):                  
       #             return ipline                      
        #        elif(newip != ipline):                 
         #           ipline = newip                     
          #          return ipline
            os.system("python wemo_insight.py --start "+newip+" "+hostline)
#	    os.system("python wemo_insight.py --start "+ipline)
        except Exception, e:
            print "failed" + str(e)
            temp = 1
def stop_all():
    hostfile = "host.txt"
   # ipfile = "ip.txt"
    fo1 = open(hostfile,'r')
  #  fo2 = open(ipfile,'r')
    for hostline in fo1:
        try:
            hostline = hostline.strip()               
            newip = socket.gethostbyname(hostline)    
#            for ipline in fo2: 
 #               ipline = ipline.strip()               
  #              if (newip == ipline):                  
   #                 return ipline                      
    #            elif(newip != ipline):                 
     #               ipline = newip                     
      #              return ipline
            os.system("python wemo_insight.py --stop "+newip+" "+hostline)
#	    os.system("python wemo_insight.py --start "+ipline)
        except Exception:
            temp = 1
def main(cmd):
    if(cmd=="STARTALL"):
        start_all()
    elif(cmd=="STOPALL"):
        stop_all()

