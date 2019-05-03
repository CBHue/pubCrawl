#!/usr/bin/env python3

'''
 
	PyFuscation.py
	This python3 script obfuscates powershell function, variable and parameters in an attempt to bypass AV blacklists 

'''
import os
import re
import sys
import time
import ipaddress
import shodan
import censys.ipv4
import configparser
from argparse import ArgumentParser

import banner
import helper

def cenSYS (ip):
	global oDir
	oFile = oDir + "/" + ip + "-censys"
	host = dict()
	censysDICT = {}

	try:
		c = censys.ipv4.CensysIPv4(censys_apiID, censys_apiSECRET)
		host = c.view(ip)
	except Exception as e:
		helper.printR("CensysIO 	: " + ip + " : " + str(e))

		if args.txt:
			censysDICT["Host"] 		= ip
			censysDICT["Error"] 	= str(e)
			if args.combine:
				oFileTXT = oDir + "/Censys-IO.txt"
			else:
				oFileTXT = oFile + ".txt"
			helper.printP("Censys 	: " + oFileTXT)
			helper.logTXT(censysDICT,oFileTXT)
		
		return

	censysDICT["Host"] 		= host['ip']
	censysDICT["Network"] 	= host['autonomous_system']['routed_prefix']
	censysDICT["Desc"] 		= host['autonomous_system']['description']
	censysDICT["Name"] 		= host['autonomous_system']['name']	
	censysDICT["Proto"] 	= str(host.get('protocols', 'n/a'))	
	censysDICT["Ports"] 	= str(host.get('ports', 'n/a'))	

	# HTTP Ports 	
	for p in host['protocols']:
		match = re.search(r'(\d+)\/(\w+)', p)
		if match:
			port  = match.group(1)
			proto = match.group(2)

			if proto == "https":
				try:
					otherNames = host[str(port)][str(proto)]['tls']['certificate']['parsed']['names']
					dns_names  = host[str(port)][str(proto)]['tls']['certificate']['parsed']['extensions']['subject_alt_name']['dns_names']
					censysDICT[str(port) + "_Names"] 		= str(otherNames)
					censysDICT[str(port) + "_DNS"] 		= str(dns_names)
				except KeyError:
					continue

			try:
				if 'title' in host[str(port)][str(proto)]['get'].keys():
					title = host[str(port)][str(proto)]['get']['title']
					censysDICT[str(port) + "_title"] 		= str(title)
				else:
					censysDICT[str(port) + "_title"] 		= "N/A"
				if 'status_code' in host[str(port)][str(proto)]['get'].keys():
					status = host[str(port)][str(proto)]['get']['status_code']
					censysDICT[str(port) + "_status"] 		= str(status)
				else:
					censysDICT[str(port) + "_status"] 		= "N/A"
			except Exception as error:
				continue

	if args.csv:
		if args.combine:
			oFileCSV = oDir + "/Censys-IO.csv"
		else:
			oFileCSV = oFile + ".csv"
		helper.printP("Censys 	: " + oFileCSV)
		helper.logCSV(censysDICT,oFileCSV)

	if args.txt:
		if args.combine:
			oFileTXT = oDir + "/Censys-IO.txt"
		else:
			oFileTXT = oFile + ".txt"
		helper.printP("Censys 	: " + oFileTXT)
		helper.logTXT(censysDICT,oFileTXT)

	if args.verbose:
		helper.loggER(censysDICT)

def shoNuff (ip):
	global oDir
	oFile = oDir + "/" + ip + "-shodan"
	
	api = shodan.Shodan(shodan_apiKEY)
	shodanDICT = {}
	
	try:
		host = api.host(ip)
		shodanDICT["Host"] 		= host['ip_str']
		shodanDICT["HostName"] 	= str(host['hostnames'])
		shodanDICT["Org"] 		= host.get('org', 'n/a')
		shodanDICT["OS"] 		= str(host.get('os', 'n/a'))
		shodanDICT["Ports"] 	= str(host['ports'])
		for item in host['data']:
			shodanDICT[str(item['port'])] = item['data'].strip()
	except shodan.APIError as e:
		helper.printR("Shodan 	: " + str(e))

		if args.txt:
			shodanDICT["Host"] 		= ip
			shodanDICT["Error"] 	= str(e)
			if args.combine:
				oFileTXT = oDir + "/Shodan-IO.txt"
			else:
				oFileTXT = oFile + ".txt"
			helper.printP("Shodan 	: " + oFileTXT)
			helper.logTXT(shodanDICT,oFileTXT)
		
		return

	if args.csv:
		if args.combine:
			oFileCSV = oDir + "/Shodan-IO.csv"
		else:
			oFileCSV = oFile + ".csv"
		helper.printP("Shodan 	: " + oFileCSV)
		helper.logCSV(shodanDICT,oFileCSV)
	if args.txt:
		if args.combine:
			oFileTXT = oDir + "/Shodan-IO.txt"
		else:
			oFileTXT = oFile + ".txt"
		helper.printP("Shodan 	: " + oFileTXT)
		helper.logTXT(shodanDICT,oFileTXT)
	if args.verbose:
		helper.loggER(shodanDICT)

def confirmIP (matchWork, cidr):	
	# Lets see if this is a real IP
	ipFull = str(matchWork) + cidr
	matchWork = str(matchWork)

	try:
		ip = ipaddress.ip_address(matchWork)
	except ValueError:
		helper.printR("Address/Netmask is invalid: "+ ipFull)
		return False
	except Exception as e:
		helper.printR("[validateHost] " + str(e) + " " + ipFull)
		return False

	if not ip.is_private:
		helper.printG("Public IP   : " + ipFull)
		if args.shodan:
			shoNuff(matchWork)		
		if args.censys:
			cenSYS(matchWork)
	else:
		helper.printR("Private Network ... Skipping")
		return

def validateHost (network):
	helper.printW("Validating 	: " +  network)
	cidr = ""

	match = re.search(r'(\d+.\d+.\d+.\d+)(/\d+)', network)
	if match:
		matchWork = match.group(1)
		helper.printY("IP Addr: " + matchWork)
		helper.printY("Subnet : " + match.group(2))
		cidr = match.group(2)

		if match.group(2) == '/32':
			if ipaddress.ip_address(matchWork).is_private:
				helper.printR("Private Network ... Skipping")
				return
			confirmIP(matchWork, cidr)
		else:
			if ipaddress.ip_address(matchWork).is_private:
				helper.printR("Private Network ... Skipping")
				return
			helper.printY("Expanding Network: " + network)
			expandedIPList = ipaddress.ip_network(network)
			cidr = "/32"
			for ip in expandedIPList:
				confirmIP(ip, cidr)
				helper.printW("Fin		: " + str(ip))
				print('')
				# This is if u have a rate limit for API calls
				helper.printW("Sleeping for a second ...")
				time.sleep( 2 )
				print('')
	else:
		helper.printY("Single IP 	: " + network)
		matchWork = network	
		cidr = "/32"	
		confirmIP(matchWork, cidr)

def main():
	ipList = args.ipList

	with open(ipList, "r") as f:
		for ip in f:
			ip = ip.strip()
			validateHost(ip)
			helper.printW("Fin		: " + ip)
			print('')
			# This is if u have a rate limit for API calls
			helper.printW("Sleeping for a second ...")
			time.sleep( 2 )
			print('')
			
	helper.printP("Output Files are located at: " + oDir + "/")

if __name__ == "__main__":
    
    if sys.version_info <= (3, 0):
        sys.stdout.write("This script requires Python 3.x\n")
        sys.exit(1)

    banner.banner()
    banner.title()

    # parse all the args
    parser = ArgumentParser()
    parser.add_argument("-v",   dest="verbose",   help="Output to screen",    action="store_true")
    parser.add_argument("-s",   dest="shodan",    help="Check Shodan.io",     action="store_true")
    parser.add_argument("-c",   dest="censys",    help="check Censys.io",     action="store_true")
    parser.add_argument("--csv",	dest="csv",  	help="csv output",  	  action="store_true")
    parser.add_argument("--txt",	dest="txt",  	help="txt output",		  action="store_true")
    parser.add_argument("--ipList", dest="ipList",  help="Target ip addresses")
    parser.add_argument("--combine",dest="combine", help="Combine output types",	  action="store_true")
    args = parser.parse_args()
    if (args.ipList is None):
        parser.print_help()
        exit()

    if not os.path.isfile(args.ipList):
        helper.printR("Check File: " + args.ipList)
        exit()  
    
    # Load the keys from config file 
    PSconfigFile = os.path.abspath(os.path.dirname(__file__)) + "/api-keys.ini"

    if not os.path.isfile(PSconfigFile):
        helper.printR("Check API key File: " + PSconfigFile)
        exit()    	
    config = configparser.ConfigParser()
    config.read(PSconfigFile)
    shodan_apiKEY 	 = config.get('shodan.io', 'shodan_apiKEY',		fallback='Not-Configured')
    censys_apiID 	 = config.get('censys.io', 'censys_apiID',		fallback='Not-Configured')
    censys_apiSECRET = config.get('censys.io', 'censys_apiSECRET',	fallback='Not-Configured')
    
    # Setup Working directory
    ts = time.strftime("%m%d%Y_%H_%M_%S", time.gmtime())
    oDir = os.path.abspath(os.path.dirname(__file__)) + "/DATA/" + ts
    if not os.path.exists(oDir):
        os.makedirs(oDir);
    helper.printP("Working directory: " + oDir)
    print('')

    main()
