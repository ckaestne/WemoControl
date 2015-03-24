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
import control_all
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

PORT = "49152"
HTTP = "http://"
IP = 0
FAILCOUNT = 0
HOSTNAME = ""
CHANGECOUNT = 0
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
# functions for defining various requests such as get_all(gets the parameters),get_manu(gets the manufacturing data), turn_on(turns on the wemo), get_state(provides the current state of the wemo)
def get_all(host):
    global PORT
    global FAILCOUNT
    global CHANGECOUNT
    print PORT, "IS THE PORT"
    DIR = "/upnp/control/insight1"
    URL_GETALL =  HTTP+str(host)+":"+PORT+DIR
    try:
        req = urllib2.Request(URL_GETALL,BODY_GETALL,HEADER_GETALL)  
        data= urllib2.urlopen(req,None,5).read()
        params = re.search(r'\<InsightParams\>(.*)\</InsightParams\>',data).group(1)
        get_all_params = parse_params("GETALL",params,host)
	FAILCOUNT = 0
	CHANGECOUNT = 0
        return get_all_params
    except urllib2.URLError as e:
	return FailureHandler(0, host)
      	error_log.write(str(datetime.datetime.now())+"URLError error({0}): {1} ".format(e.errno, e.strerror))
	return "goto poll"
    except urllib2.HTTPError as e:
	return FailureHandler(0, host)
	sys.stdout.write("two\n")
        error_log.write(str(datetime.datetime.now())+"HTTPError error({0}): {1}".format(e.errno, e.strerror))
        return "goto poll"
    except Exception:
	return FailureHandler(0, host)


def turn_on(host):
    global PORT
    global FAILCOUNT
    global CHANGECOUNT
    DIR = "/upnp/control/basicevent1"
    URL_ON =  HTTP+str(host)+":"+PORT+DIR
    try:
        req = urllib2.Request(URL_ON,BODY_ON,HEADER_ON)  
        data= urllib2.urlopen(req,None,5).read()
        params = re.search(r'\<BinaryState\>(.*)\</BinaryState\>',data).group(1)
        #get_all_params = parse_params("GETALL",params,host)
	FAILCOUNT = 0
	CHANGECOUNT = 0
        return params
    except urllib2.URLError as e:
	return FailureHandler(2, host)
        error_log.write(str(datetime.datetime.now())+"URLError error({0}): {1} ".format(e.errno, e.strerror))
	return "goto poll"
    except urllib2.HTTPError as e:
	return FailureHandler(2, host)
	sys.stdout.write("two\n")
        error_log.write(str(datetime.datetime.now())+"HTTPError error({0}): {1}".format(e.errno, e.strerror))        
	return "goto poll"
    except Exception:
	return FailureHandler(2, host)
        error_log.write("Error in getting response from "+host)
	return "goto poll"

      
def FailureHandler(version, host):
	global PORT
	global FAILCOUNT
	global CHANGECOUNT
	global HOSTNAME
	global IP
	intport = int(PORT)
	FAILCOUNT = FAILCOUNT+1	
        if(FAILCOUNT < 5):
		print PORT, "failure", IP, FAILCOUNT, CHANGECOUNT
		time.sleep(1)
		if(version == 0):
                	return get_all(host)
		elif(version == 1):
			return get_manu(host)
		else:
			return turn_on(host)
        else:
            CHANGECOUNT+=1
	    print PORT, "Changeport Failure", IP, FAILCOUNT, CHANGECOUNT
	    intport+=1
	    if(CHANGECOUNT < 40):	
		time.sleep(1)
		if(intport == 49157):
			intport = 49152
		PORT = str(intport)
		if(version == 0):
			return get_all(host)
		elif(version ==1):
			return get_manu(host)
		else:
			return turn_on(host)
	    else:
		#Try IPCHANGE
		try:
	        	newip = socket.gethostbyname(HOSTNAME)
			if(newip == IP):
				FAILCOUNT = 0
				CHANGECOUNT = 0
				return "goto poll"
			
			else:
				FAILCOUNT = 0
				CHANGECOUNT = 0
				IP = newip
				return FaiiureHandler(version)
		except Exception:
			error_log.write("Error in DNS Lookup from "+HOSTNAME)
			return "goto poll"
				
def get_state(host):
    global PORT
    global FAILCOUNT
    global CHANGECOUNT

    DIR = "/upnp/control/basicevent1"
    URL_GETSTATE =  HTTP+str(host)+":"+PORT+DIR
    #print URL_GETSTATE
    try:
        req = urllib2.Request(URL_GETSTATE,BODY_GETSTATE,HEADER_GETSTATE)
        data= urllib2.urlopen(req,None,5).read()
        params = re.search(r'\<BinaryState\>(.*)\</BinaryState\>',data).group(1)
        FAILCOUNT = 0
	CHANGECOUNT = 0
        return params
    except urllib2.URLError as e:
	return FailureHandler(2, host)
        error_log.write(str(datetime.datetime.now())+"URLError error({0}): {1} , {2}".format(e.errno, e.strerror,e.read()))
        #now some error in request , go to polling state , return saying try after sometime
        return "goto poll"
    except urllib2.HTTPError as e:
        return FailureHandler(3, host)
        sys.stdout.write("two\n")
        error_log.write(str(datetime.datetime.now())+"HTTPError error({0}): {1}, {2}".format(e.errno, e.strerror,e.read()))
        return "goto poll"
    except socket.timeout as e:
        print e
	return FailureHandler(3, host)
        return "goto poll"
    except Exception:
	return FailureHandler(3, host)
        error_log.write("Error in getting state from "+host)
        return "goto poll"

def get_manu(host):
        global PORT
	global FAILCOUNT
	global CHANGECOUNT
        DIR = "/upnp/control/manufacture1"
        URL_GETMANU = HTTP+str(host)+":"+PORT+DIR
        try:
            req = urllib2.Request(URL_GETMANU,BODY_GETMANU,HEADER_GETMANU)
            data= urllib2.urlopen(req,None,5).read()
            params = re.search(r'\<ManufactureData\>(.*)\</ManufactureData\>',data).group(1)
            get_manu_params = parse_params("GETMANU",params,host)
	    FAILCOUNT = 0
	    CHANGECOUNT = 0
            return get_manu_params
        except urllib2.URLError as e:
		return FailureHandler(1, host)

		error_log.write(str(datetime.datetime.now())+"URLError error({0}): {1} ".format(e.errno, e.strerror))
        	return "goto poll"
    	except urllib2.HTTPError as e:
		return FailureHandler(1, host)
        	sys.stdout.write("two\n")
	        error_log.write(str(datetime.datetime.now())+"HTTPError error({0}): {1}".format(e.errno, e.strerror))
		return "goto poll"    
	except Exception:
		return FailureHandler(1, host)                                                     

            
#-----------------------------*------------------------------*-----------------------------------------------

def parse_params(cmd,data,host):
    if cmd == "GETALL":
        try:
            param = data.split("|")
            state = param[0]
            currentmw = param[7]
            currenttime= time.strftime("%H:%M:%S")
            currentdate= time.strftime("%d/%m/%Y")
            string = "\n| currentdate: "+str(currentdate)+"| currenttime: "+str(currenttime)
            dictionary = {"| host ":host,"| state ":state,"| currentmw ":currentmw}
            string += ' '.join(['%s: %s' % (key, value) for (key, value) in dictionary.items()])

            return string
        except Exception:
            temp = 1
    elif cmd=="GETMANU":
        try:
            param = data.split(";")
            PF = param[52][0:len(param[52])-3]
            iRMS = param[48][0:len(param[48])-3]
            vRMS = param[40][0:len(param[40])-3]
            Frequency = param[56][0:len(param[56])-3]
            dictionary = {"| host ":host,"| PF ":PF,"| iRMS ":iRMS,"| vRMS ":vRMS,"| Frequency ":Frequency}
            currenttime= time.strftime("%H:%M:%S")
            currentdate= time.strftime("%d/%m/%Y")
            string = "\n| currentdate: "+str(currentdate)+"| currenttime: "+str(currenttime)
            string += ' '.join(['%s: %s' % (key, value) for (key, value) in dictionary.items()])
            return string
        except IndexError:
            print "Error for current instance"
        except Exception:
            temp = 1
    return None

#--------------------FILE OBJECTS-----------------------------------------------------------------------------

log = open("log.txt","a")
error_log = open("errorlog.txt","w")
manufacture = open("wemo_manufacture.txt","a")
#state_log = open("wemo_state.txt","w")
poll_log = open("wemo_poll.txt","w")
poll_manufacture = open("wemo_poll_manufacture.txt","w")
#-------------------*------------------------------------------*------------------------------------------------

# Polling function is used for sending the wemos into a polling state where the don't respond, follwing to this we make the sleep for a small peperiod and resume the wemo to get responses. 

def poll(host):
    print "in poll : "+str(host)
    #current = wemothread(host)
    global FAILCOUNT
    global CHANGECOUNT
    poll_log.write(str(datetime.datetime.now())+" Host "+str(host)+" is in poll \n")
    poll_log.flush()
    poll_manufacture.write(str(datetime.datetime.now())+" Host "+str(host)+" is in poll \n")
    poll_manufacture.flush()
    while True:
        time.sleep(120)
        #current = wemothread(host)
        #current.restart()
        #time.sleep(10)
        #os.fysnc(poll_log.fileno())
	FAILCOUNT = 0
	CHANGECOUNT = 0
        all_param = get_all(host)
        if(all_param=="goto poll"):
            poll(host)
            temp = 1
        else:
            poll_log.write(str(datetime.datetime.now())+" Host "+str(host)+" is started again \n")
            poll_log.flush()
            break

#----------------------------------------------------------------------------------------------------------------

	
class wemothread:
    """
    comments      
    """
    def __init__(self, pidfile, stdin='/dev/null', stdout='/dev/null', stderr='/dev/null'):
        self.stdin = stdin
        self.stdout = stdout
        self.stderr = stderr
        self.pidfile = pidfile
#	print "initializing"
        print self.pidfile
        self.stop_flag = 0
        #self.host = pidfile
    def daemonize(self):
        try:
            pid = os.fork()
            if pid > 0:
            # exit first parent
                sys.exit(0)
        except OSError, e:
            print "os error"
            sys.stderr.write("fork #1 failed: %d (%s)\n" % (e.errno, e.strerror))
            sys.exit(1)

        # decouple from parent environment
        cur_directory = os.getcwd()
        tmp_directory = "/tmp"
        os.chdir(tmp_directory)
        os.setsid()
        os.umask(0)

        # do second fork
        try:
            pid = os.fork()
            if pid > 0:
                # exit from second parent
                sys.exit(0)
        except OSError, e:
            sys.stderr.write("fork #2 failed: %d (%s)\n" % (e.errno, e.strerror))
            sys.exit(1)

        # redirect standard file descriptors
        sys.stdout.flush()
        sys.stderr.flush()
        si = file(self.stdin, 'r')
        so = file(self.stdout, 'a+')
        se = file(self.stderr, 'a+', 0)
        #file duplicators
        #os.dup2(si.fileno(), sys.stdin.fileno())
        #os.dup2(so.fileno(), sys.stdout.fileno())
        #os.dup2(se.fileno(), sys.stderr.fileno())
        # write pidfile
        #atexit.register(self.delpid)
 #       pid = str(os.getpid())
  #      file(self.pidfile,'w+').write("%s\n" % pid)
        #return back to current directory
        os.chdir(cur_directory)
        
    def delpid(self):
        os.remove(self.pidfile)

    def wemonew(self,host):    
	i = 0
        while True:
	   		   i+=1
	   		   if(i % 100 == 1):
				turn_on(host)
	   
	   #for i in range(0,100):
#            try:
            
#                try:
#                   state = get_state(host)
#                    #print state
#                   if state=="0":
#                       par = turn_on(host)
#                   state_log.write(str(datetime.datetime.now())+"host | "+host+" | state "+state+"\n")
#                   state_log.flush()
                    #os.fysnc(state_log.fileno())
#                except Exception:
#                    state_log.write(str(datetime.datetime.now())+host+" * Error in getting state\n")
#                    state_log.flush()            
                  
#                try:
			   all_param = get_all(host)
	                   #all_param[i] = get_all(host)
        	           print all_param
			   if(all_param == "goto poll"):
				poll(host)
		           log.write(all_param)
			   log.flush()
			   time.sleep(1)
		#	   manu_param = get_manu(host)
		#	   print manu_param
		#	   if(manu_param == "goto poll"):
		#		poll(host)
		#	   manufacture.write(manu_param)
		#	   manufacture.flush()
	
                       #os.fysnc(log.fileno()) 
#                except Exception:
#                    print "all param problem"
         #          	   time.sleep(2)
	 
            
    def start(self):
        """
        Start the daemon
        """
        # Check for a pidfile to see if the daemon already runs
        try:
            pf = file(self.pidfile,'r')
            pid = int(pf.read().strip())
            pf.close()
            print str(pid)+"in start pid"
        except IOError:
            pid = None

        if pid:
            message = "pidfile %s already exist. Daemon already running !\n"
            print message
            sys.stderr.write(message % self.pidfile)
            sys.exit(1)

        # Start the daemon
        self.daemonize()
        self.run()

    def stop(self):
        """
        Stop the daemon
        """
        # Get the pid from the pidfile , remember to surf to the directory where the file is present
        try:
            tmp_directory = "/tmp"
            os.chdir(tmp_directory)
            pf = file(self.pidfile,'r')
            pid = int(pf.read().strip())
            pf.close()
        except IOError:
                pid = None

        if not pid:
            message = "pidfile %s does not exist. Daemon not running?\n"
            sys.stderr.write(message % self.pidfile)
            return # not an error in a restart

        # Try killing the daemon process       
        try:
            while 1:
                os.kill(pid, SIGTERM)
                time.sleep(0.1)
        except OSError, err:
            err = str(err)
            if err.find("No such process") > 0:
                if os.path.exists(self.pidfile):
                    os.remove(self.pidfile)
            else:
                print str(err)
                sys.exit(1)

    def restart(self):
        """
        Restart the daemon
        """
        self.stop()
        self.start()

    def run(self):
        """
        You should override this method when you subclass Daemon. It will be called after the process has been
        daemonized by start() or restart().
        """
        host = self.pidfile
        #print "run"
        self.wemonew(host)

def start_all():
    control_all.main("STARTALL")
    sys.exit(1)

def stop_all():
    control_all.main("STOPALL")
    sys.exit(1)
    
def main(arguments):
    print arguments
    cmd = arguments[1]
    global IP
    global HOSTNAME
    if cmd == "--startall":
        start_all()   
    elif cmd == "--stopall":
        stop_all()
        sys.exit(1)

    try:
        host = arguments[2]
	IP = host
	HOSTNAME = arguments[3]
        current = wemothread(host)
	print "found thread: "+str(current)
    except IndexError:
        print "Insufficient parameters. Please add a supporting string"
        sys.exit(1)
    except Exception, e:
        print "could not find thread: "+str(e)
        current = None
        temp = 1
        
    if len(arguments) == 4:
        if '--start' == cmd:
            current.start()
        elif '--stop'==cmd:
            current.stop()              
        elif '--restart'==cmd:
            current.restart()
    
if __name__ == "__main__":
    main(sys.argv)

