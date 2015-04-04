#!/usr/bin/python
#-------#--------#-----------#------------#----------------
# Wemo Control Script 
# Version 0.0.4
# Remotely gathers sample data from belkin Wemo Insight devices 
# Product of Synergy labs, Christian Kaestner


# Modules to import 
import urllib2,datetime,socket
import time,sys,os,re,atexit
from signal import SIGTERM
#---------------------------------SOAP-BODY-----------------------------------------------------------------

class InsightMethod:
    def __init__(self, fun, service, param, returnParamName=None):
        self.request='''<?xml version="1.0" encoding="utf-8"?>
<s:Envelope xmlns:s="http://schemas.xmlsoap.org/soap/envelope/" s:encodingStyle="http://schemas.xmlsoap.org/soap/encoding/">
    <s:Body>
        <u:'''+fun+''' xmlns:u="urn:Belkin:service:'''+service+''':1">
            '''+param+'''
        </u:'''+fun+'''>
    </s:Body>
</s:Envelope>'''
        self.httpdir="/upnp/control/"+service+"1"
        self.header= {"Accept":"",
                    "Content-Type": "text/xml; charset=\"utf-8\"",
                    "SOAPACTION": "\"urn:Belkin:service:"+service+":1#"+fun+"\""}
        self.returnParamName=returnParamName
 
    def call(self):
        global IP
        global PORT
        global FAILCOUNT
        url = "http://"+IP+":"+PORT+self.httpdir
        try:
            req = urllib2.Request(url, self.request, self.header)
            # error("#send "+url+"\n"+str(self.request))
            data= urllib2.urlopen(req,None,5).read()
            # error("#received "+data)
            FAILCOUNT = 0
            if data!=None and self.returnParamName!=None:
                data = re.search(r'\<'+self.returnParamName+r'\>(.*)\</'+self.returnParamName+r'\>',data).group(1)
            return data
        except Exception, e:
            return handleException(e)



PORT = "49152"
IP = "0"
FAILCOUNT = 0

def read_sensors():
    global FAILCOUNT
    data = getAll.call()
    if data != None:
        return parse_params_getall(data)
    return None

     
# measurement or turn_on has just failed.
# do nothing, unless there are more errors in a row.
# after 5 errors, try new ports 
def handleException(exception):
        global PORT
        global FAILCOUNT
        global IP
        global HOST
        FAILCOUNT = FAILCOUNT+1        
        error("#error " + IP +":"+PORT+", " +str(FAILCOUNT)+" tries, "+ str(exception))
        if(FAILCOUNT >= 5):
            intport = int(PORT)
            intport+=1
            if(intport == 49157):
                   intport = 49152
            error("#trying new port: "+str(intport))
            PORT = str(intport)
            try:
               newip = socket.gethostbyname(HOST)
               if(newip != IP):
                    IP = newip
                    error("#found new ip: " + IP)
                    FAILCOUNT = 0
            except Exception:
                  error("Error in DNS Lookup from "+HOST+" (keeping old ip)")
        #longer delays if we see a lot of errors and cannot fix them
        if (FAILCOUNT > 30):
                sleep(10)
                                

            
#-----------------------------*------------------------------*-----------------------------------------------

def parse_params_getall(data):
    try:
        p = data.split("|")
        # r = "state="+p[0]
        # r = r + " secondsSinceStateChange="+p[1]
        # r = r + " lastOn="+str(time.strftime("%Y-%m-%d %H:%M:%S",time.gmtime(int(p[2]))))
        # r = r + " secondsOnToday="+p[3]
        # r = r + " secondsOnTwoWeeks="+p[4]
        # r = r + " secondsOnTotal="+p[5]
        # r = r + " averagePowerW="+p[6]
        # r = r + " instantPowerMW="+p[7]
        # r = r + " powerTodayMWS="+p[8]
        # r = r + " energyTwoWeeksMWS="+p[9]
        # currenttime= time.strftime("%Y-%m-%d %H:%M:%S")
        # string = str(currenttime) + ", " + r
        # return string
        return str(p[7])
    except Exception, e:
        print str(e)
        return None



#----------------------------------------------------------------------------------------------------------------
getAll = InsightMethod("GetInsightParams","insight", "<InsightParams></InsightParams>","InsightParams")
isOn = InsightMethod("GetBinaryState","basicevent","<BinaryState>1</BinaryState>")
turnOn = InsightMethod("SetBinaryState","basicevent","<BinaryState>1</BinaryState>")
getName = InsightMethod("GetFriendlyName","basicevent","","FriendlyName")
getHomeId = InsightMethod("GetHomeId","basicevent","","HomeId")
getMacAddr= InsightMethod("GetMacAddr","basicevent","","MacAddr")
getSerialNo=InsightMethod("GetMacAddr","basicevent","","SerialNo")
getLogFileURL=InsightMethod("GetLogFileURL","basicevent","","LOGURL")
setPowerThreshold0 = InsightMethod("SetPowerThreshold","insight","<PowerThreshold>0</PowerThreshold>","PowerThreshold")  
getPowerThreshold=InsightMethod("GetPowerThreshold","insight","<PowerThreshold></PowerThreshold>","PowerThreshold")
getInsightParams=InsightMethod("GetInsightParams","insight","","InsightParams")
getMetaInfo = InsightMethod("GetMetaInfo","metainfo","","MetaInfo")
getFirmwareVersion = InsightMethod("GetFirmwareVersion","firmwareupdate","","FirmwareVersion")
getAccessPointList = InsightMethod("GetApList","WiFiSetup","")

def init():
    r = None
    i = 100
    error("#establishing connection and turning on")
    while r==None and i>0:
        r=turnOn.call()
        i-=1
    error("#found device "+getName.call())
    error("#meta: "+getMetaInfo.call())
    error("#firmware: "+getFirmwareVersion.call())
    error("#serialno: "+getSerialNo.call())
    error("#reset power threshold: "+setPowerThreshold0.call())


def logEnergy(name):
        i = 0
        while True:
            i+=1
            if(i % 50 == 1):
                r=turnOn.call()
                if (r==None):
                    i = 0
            result = read_sensors()
            if (result!=None):
                    sys.stdout.write(name+" - "+time.strftime("%Y-%m-%d %H:%M:%S")+": "+str(result)+"\n")
                    sys.stdout.flush()
            time.sleep(1)
         
            
def error(msg):
     sys.stderr.write(msg.strip()+"\n")
     sys.stderr.flush()
    
def main(arguments):
    global IP
    global HOST

    try:
        HOST = arguments[1]
        IP = socket.gethostbyname(HOST) 
        name = arguments[2]

        print "listening for "+name+" at "+HOST+" ("+IP+")"

        init()
        logEnergy(name)

    except IndexError:
        print "Insufficient parameters. Expecting hostname (or IP) and a name"
        sys.exit(1)
    
    
    
if __name__ == "__main__":
    main(sys.argv)

