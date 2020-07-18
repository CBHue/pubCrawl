#!/usr/bin/env python3

'''
 	pubCrawl.py
	This python3 script runs Shodan and Censys api calls
'''

import os
import re
import sys
import time
import configparser
from argparse import ArgumentParser

import util.banner as banner
import util.helper as helper
import util.chromeShot as chromeShot
import util.hostCheck as hostWork
import api.shoNuff as shoNuff 
import api.censei as censei 

def main():

	chromeSHOT = set()
	hostSET = set()
	privHostDIC = {}
	hostDIC = {}

	SoFileTXT = oDir + "/Shodan-IO.txt"
	SoFileCSV = oDir + "/Shodan-IO.csv"
	CoFileCSV = oDir + "/Censys-IO.csv"
	CoFileTXT = oDir + "/Censys-IO.txt"
	pubLog    = oDir + "/Resolved-Public-Hosts.txt"
	privLog   = oDir + "/Resolved-Private-Hosts.txt"

	#  SATGE 0 : Gather the targets 
	if args.hostName:
		CBH = args.hostName
		hostSET.add(CBH.strip())

	#  or a hostlist
	elif args.hostList:
		CBH = args.hostList

		with open(CBH, encoding="utf8", errors='ignore') as f:
			for target in f:
				# lets clean up any non ascii characters
				target = re.sub(r'[^\x00-\x7f]',r'',target)
				target = target.strip()
				hostSET.add(target)

	else:
		helper.printR("I dont know how u got here")
		sys.exit(1)	

	# SATGE 1 : If we have work to do let do it
	workS1 = len(hostSET)
	if workS1 > 0:
		helper.printP2("STAGE1 Validating IP/Hosts", str(workS1))
		for hst in hostSET:
			pubHSTs, privHSTs = hostWork.validateHost(hst)
			if pubHSTs:
				hostDIC = {**pubHSTs, **hostDIC}
			if privHSTs:
				privHostDIC = {**privHSTs, **privHostDIC}

	# Write out the current hosts
	helper.logTXT(hostDIC,pubLog)
	helper.logTXT(privHostDIC,privLog)

	# SATGE 2 : Now we have a list of hosts to ip
	workS2 = len(hostDIC)
	InvalidTargets = workS1 - workS2
	helper.printP2("Invalid Dropped Targets", str(InvalidTargets))
	helper.printP2("Remaining Valid Targets", str(workS2))
	if workS2 > 0:
		if (args.shodan or args.censys):
			for key, value in hostDIC.items():
				Results = {}

				# SHODAN
				if args.shodan:
					Results, scrSHOT = shoNuff.shoNuff(key,sKEY)
					if Results:
						#Now we have results ... Guess we can output it now
						helper.loggER(Results)
						helper.logTXT(Results,SoFileTXT)
						helper.logCSV(Results,SoFileCSV)

					if scrSHOT:
						# Now lets see if we want and need to take screenshots

						for u in scrSHOT:
							match = re.search(r'.*://(.*):(.*)',u)
							
							# replace ip with hostname if available
							hname = hostDIC.get(key, match.group(1))
							u = u.replace(key, hname)
							helper.printP2("Taking Screen Shots",u)

							ssFile = oDir + "/" + hname + "_" + match.group(2) + "_shodan_screenshot.png"
							chromeShot.chromeShot(u,ssFile)

				# CENSYS
				if args.censys:
					Results, scrSHOT  = censei.cenSYS(key,cID,cCRET)
					if Results:
						#Now we have results ... Guess we can output it now
						helper.loggER(Results)
						helper.logTXT(Results,CoFileTXT)
						helper.logCSV(Results,CoFileCSV)

					if scrSHOT:
						# Now lets see if we want and need to take screenshots

						for u in scrSHOT:
							match = re.search(r'.*://(.*):(.*)',u)
							
							# replace ip with hostname if available
							hname = hostDIC.get(key, match.group(1))
							u = u.replace(key, hname)
							helper.printP2("Taking Screen Shots",u)

							ssFile = oDir + "/" + hname + "_" + match.group(2) + "_censys_screenshot.png"
							chromeShot.chromeShot(u,ssFile)

				workS2 = workS2 - 1
				helper.printW2("Fin",value)
				helper.printW2("Hosts Left",str(workS2))

				# Note: All API methods are rate-limited to 1 request/ second. 
				shleep = 5
				helper.printW2("Sleeping for ", str(shleep))
				time.sleep( shleep )
				print('')

	# --sshot without checking censys or shodan
	if (args.sshot and not (args.shodan or args.censys)):

		hostDIC = {**hostDIC, **privHostDIC}
		# We are just going to try screenshotting both HTTP and HTTPs

		Count = len(hostDIC)
		c = 0
		helper.printW2("Screenshoting Host(s)", str(Count))
		for key, value in hostDIC.items():
			c = c + 1
			helper.printW2("Screenshot " + str(c) + " / " + str(Count) , value)
			
			u = "http://" + value			
			ssFile = oDir + "/" + value + "_http_screenshot.png"
			chromeShot.chromeShot(u,ssFile)
			
			u = "https://" + value
			ssFile = oDir + "/" + value + "_https_screenshot.png"
			chromeShot.chromeShot(u,ssFile)

	# Done !
	print('')
	helper.printY2("Output Files are located at:", oDir + "/")
	print('')

if __name__ == "__main__":
    
    if sys.version_info <= (3, 0):
        sys.stdout.write("This script requires Python 3.x\n")
        sys.exit(1)

    banner.banner()
    banner.title()

    # parse all the args
    parser = ArgumentParser()
    parser.add_argument("-s",   		dest="shodan",    	help="Check Shodan.io",     					action="store_true")
    parser.add_argument("-c",   		dest="censys",    	help="Check Censys.io",     					action="store_true")
    parser.add_argument("--sshot",   	dest="sshot",    	help="Take Screenshot",     					action="store_true")
    parser.add_argument("--csv",		dest="csv",  		help="csv output",  	  						action="store_true")
    parser.add_argument("--txt",		dest="txt",  		help="txt output",		  						action="store_true")
    parser.add_argument("--full",		dest="full",  		help="Censys + Shodan + Screenshot + Combine", 	action="store_true")
    parser.add_argument("--hostList", 	dest="hostList",  	help="Host list")
    parser.add_argument("--host", 		dest="hostName",  	help="Individual host")
    parser.add_argument("--combine",	dest="combine", 	help="Combine output types",					action="store_true")
    args = parser.parse_args()

    # Its either a hostfile or a single host
    if (args.hostList is None) and (args.hostName is None):
        parser.print_help()
        exit()

    if (args.hostList):
	    if not os.path.isfile(args.hostList):
	        helper.printR("Check File: " + args.hostList)
	        exit()  
      
    # Load the keys from config file 
    #PSconfigFile = os.path.abspath(os.path.dirname(__file__)) + "/api-keys.ini"
    # Moved keys to a not git controled directory
    PSconfigFile = "/home/cb/Documents/api-keys.ini"

    if not os.path.isfile(PSconfigFile):
        helper.printR("Check API key File: " + PSconfigFile)
        exit()    	
    config = configparser.ConfigParser()
    config.read(PSconfigFile)
    sKEY  = config.get('shodan.io', 'shodan_apiKEY',	fallback='Not-Configured')
    cID   = config.get('censys.io', 'censys_apiID',		fallback='Not-Configured')
    cCRET = config.get('censys.io', 'censys_apiSECRET',	fallback='Not-Configured')
    
    # Setup Working directory
    ts = time.strftime("%m%d%Y_%H_%M_%S", time.gmtime())
    global oDir
    oDir = os.path.abspath(os.path.dirname(__file__)) + "/DATA/" + ts
    if not os.path.exists(oDir):
        os.makedirs(oDir);
    helper.printY2("Working directory", oDir)
    print('')

    main()
