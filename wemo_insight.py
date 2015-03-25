#!/usr/bin/python
#-------#--------#-----------#------------#----------------
# Wemo Control Script 
# Version 0.0.2
# Remotely gathers sample data from belkin Wemo Insight devices 
# Product of Synergy labs
# Version 0.0.3
# Remotely gathers sample data from belkin Wemo Insight devices 
# Product of Synergy labs

#-------#--------#-----------#------------#-----------------
#
# We define a class of Wemo Thread which is our backbone structure of Wemo threads
# Each thread uniquely identifies a wemo Insight device located in a building
# The thread collects the sample data over the time and stores it locally on the file
#------*----------*-----------*-----------*----------*------

# Modules to import 
import urllib2,datetime,socket
import time,sys,os,re,atexit
from signal import SIGTERM
#---------------------------------SOAP-BODY-----------------------------------------------------------------

BODY_GETALL='''<?xml version="1.0" encoding="utf-8"?>
<s:Envelope xmlns:s="http://schemas.xmlsoap.org/soap/envelope/" s:encodingStyle="http://schemas.xmlsoap.org/soap/encoding/">
    <s:Body>
        <u:GetInsightParams xmlns:u="urn:Belkin:service:insight:1">
            <InsightParams>
            </InsightParams>
        </u:GetInsightParams>
    </s:Body>
</s:Envelope>'''
BODY_GETMANU = '''
<?xml version="1.0" encoding="utf-8"?>
    <s:Envelope xmlns:s="http://schemas.xmlsoap.org/soap/envelope/" s:encodingStyle="http://schemas.xmlsoap.org/soap/encoding/">
        <s:Body>
            <u:GetManufactureData xmlns:u="urn:Belkin:service:manufacture:1">
                <ManufactureData>
                </ManufactureData>
            </u:GetManufactureData>
        </s:Body>
    </s:Envelope>
'''
BODY_GETSTATE = '''
<?xml version="1.0" encoding="utf-8"?>
    <s:Envelope xmlns:s="http://schemas.xmlsoap.org/soap/envelope/" s:encodingStyle="http://schemas.xmlsoap.org/soap/encoding/">
        <s:Body>
            <u:GetBinaryState xmlns:u="urn:Belkin:service:basicevent:1">
                <BinaryState>
                    1
                </BinaryState>
            </u:GetBinaryState>
        </s:Body>
    </s:Envelope>
'''

BODY_ON = '''
<?xml version="1.0" encoding="utf-8"?>
    <s:Envelope xmlns:s="http://schemas.xmlsoap.org/soap/envelope/" s:encodingStyle="http://schemas.xmlsoap.org/soap/encoding/">
        <s:Body>
            <u:SetBinaryState xmlns:u="urn:Belkin:service:basicevent:1">
                <BinaryState>
                    1
                </BinaryState>
            </u:SetBinaryState>
        </s:Body>
    </s:Envelope>
'''


#------------------------------*-------------------------------*-----------------------------------------------

#---------------------------------SOAP-ALLOWED-PORTS---------------------------------------------------------------------

#URL_GETALL = "http://128.237.230.120:49153/upnp/control/insight1"
#URL_GETMANU = "http://128.237.230.120:49153/upnp/control/manufacture1"

PORT = "49153"
HTTP = "http://"
IP = "0"
FAILCOUNT = 0
#------------------------------*-------------------------------*-----------------------------------------------

#---------------------------------SOAP-HEADER------------------------------------------------------------------

HEADER_GETALL = {"Accept":"",
                "Content-Type": "text/xml; charset=\"utf-8\"",
                "SOAPACTION": "\"urn:Belkin:service:insight:1#GetInsightParams\""}
HEADER_GETSTATE = {"Accept":"",
                "Content-Type": "text/xml; charset=\"utf-8\"",
                "SOAPACTION": "\"urn:Belkin:service:basicevent:1#GetBinaryState\""}
HEADER_GETMANU = {"Accept":"",
                "Content-Type": "text/xml; charset=\"utf-8\"",
                "SOAPACTION": "\"urn:Belkin:service:manufacture:1#GetManufactureData\""}
HEADER_ON = {"Accept":"",
                "Content-Type": "text/xml; charset=\"utf-8\"",
                "SOAPACTION": "\"urn:Belkin:service:basicevent:1#SetBinaryState\""}
#-----------------------------*-------------------------------*-------------------------------------------

#---------------------------------------GET-PARAMS-FUNCTIONS----------------------------------------------
def read_sensors():
    global HOST
    global IP
    global PORT
    global FAILCOUNT
    DIR = "/upnp/control/insight1"
    URL_GETALL =  HTTP+IP+":"+PORT+DIR
    try:
        req = urllib2.Request(URL_GETALL,BODY_GETALL,HEADER_GETALL)  
        data= urllib2.urlopen(req,None,5).read()
        params = re.search(r'\<InsightParams\>(.*)\</InsightParams\>',data).group(1)
        get_all_params = parse_params_getall(params)
        FAILCOUNT = 0
        return get_all_params + " -- " + params
    except Exception, e:
        return handleException(e)


def turn_on():
    global IP
    global HOST
    global PORT
    global FAILCOUNT
    DIR = "/upnp/control/basicevent1"
    URL_ON =  HTTP+IP+":"+PORT+DIR
    try:
        req = urllib2.Request(URL_ON,BODY_ON,HEADER_ON)  
        data= urllib2.urlopen(req,None,5).read()
        params = re.search(r'\<BinaryState\>(.*)\</BinaryState\>',data).group(1)
        FAILCOUNT = 0
        error("#debug "+params)
        return params
    except Exception, e:
        return handleException(e)

     
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
            param = data.split("|")
            state = param[0]
            currentmw = param[7]
            currenttime= time.strftime("%Y-%m-%d %H:%M:%S")
            string = str(currenttime) + ", " + currentmw+", "+state
            return string
        except Exception, e:
            print str(e)
            return None



#----------------------------------------------------------------------------------------------------------------


def logEnergy(name):    
        i = 0
        while True:
			i+=1
			if(i % 100 == 1):
				r=turn_on()
                                if (r==None):
                                      i = 0
                        result = read_sensors()
                        if (result!=None):
                           sys.stdout.write(name+": "+str(result)+"\n")
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

        logEnergy(name)

    except IndexError:
        print "Insufficient parameters. Expecting hostname (or IP) and a name"
        sys.exit(1)
    
    
    
if __name__ == "__main__":
    main(sys.argv)

