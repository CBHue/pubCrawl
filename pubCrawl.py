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

	if args.txt:
		oFileTXT = oFile + ".txt"
		helper.printP("CensysIO 	: " + oFileTXT)
	else:
		oFileTXT = False

	try:
		c = censys.ipv4.CensysIPv4(censys_apiID, censys_apiSECRET)
		host = c.view(ip)
	except Exception as e:
		helper.loggER("CensysIO 	: " + ip + " : " + str(e),oFileTXT,True,"WARN")
		return

	helper.loggER("Network 	: " + host['autonomous_system']['routed_prefix'],oFileTXT,args.verbose)
	helper.loggER("Host   	: " + host['ip']								,oFileTXT,args.verbose)
	helper.loggER("Desc   	: " + host['autonomous_system']['description']	,oFileTXT,args.verbose)
	helper.loggER("Name  	: " + host['autonomous_system']['name']			,oFileTXT,args.verbose)
	helper.loggER("Proto   	: " + str(host.get('protocols', 'n/a'))			,oFileTXT,args.verbose)
	helper.loggER("Ports 	: " + str(host.get('ports', 'n/a'))				,oFileTXT,args.verbose)

	# HTTP Ports 	
	for p in host['protocols']:
		match = re.search(r'(\d+)\/(\w+)', p)
		if match:
			port  = match.group(1)
			proto = match.group(2)

			helper.loggER("------------------",oFileTXT,args.verbose,"STATUS")
			helper.loggER("Details 	: " + str(p),oFileTXT,args.verbose,"STATUS")
			helper.loggER("------------------",oFileTXT,args.verbose,"STATUS")

			if proto == "https":
				try:
					otherNames = host[str(port)][str(proto)]['tls']['certificate']['parsed']['names']
					dns_names  = host[str(port)][str(proto)]['tls']['certificate']['parsed']['extensions']['subject_alt_name']['dns_names']
					helper.loggER("Names 	: " + str(otherNames),oFileTXT,args.verbose)
					helper.loggER("DNS Names 	: " + str(dns_names),oFileTXT,args.verbose)

				except KeyError:
					continue

			try:
				if 'title' in host[str(port)][str(proto)]['get'].keys():
					title = host[str(port)][str(proto)]['get']['title']
					helper.loggER("Title 	: " + str(title),oFileTXT,args.verbose)
				if 'status_code' in host[str(port)][str(proto)]['get'].keys():
					status = host[str(port)][str(proto)]['get']['status_code']
					helper.loggER("Status 	: " + str(status),oFileTXT,args.verbose)
			except Exception as error:
				continue

def shoNuff (ip):
	api = shodan.Shodan(shodan_apiKEY)

	global oDir
	oFile = oDir + "/" + ip + "-shodan"
	
	if args.csv:
		oFileJGZ = oFile + ".json.gz"
		helper.printP("Shodan 	: " + oFileJGZ)	
		cmd = "shodan download " + oFile + " net:" + ip
		res = helper.muxER(cmd)
		
		# We need to check to see if the download worked
		if not os.path.isfile(oFileJGZ):
			helper.printR("Issue with download: " + str(res))
			return

		oFileCSV = oFile + ".csv"
		helper.printP("Shodan 	: " + oFileCSV)	
		cmd = "shodan convert " + oFileJGZ + " csv"
		helper.muxER(cmd)

	if args.txt:
		oFileTXT = oFile + ".txt"
		helper.printP("Shodan 	: " + oFileTXT)
	else:
		oFileTXT = False

	try:
		host = api.host(ip)
		helper.loggER("Host 	: " + host['ip_str']			,oFileTXT,args.verbose)
		helper.loggER("HostName 	: " + str(host['hostnames']),oFileTXT,args.verbose)
		helper.loggER("Org 	: " + host.get('org', 'n/a')		,oFileTXT,args.verbose)
		helper.loggER("OS 		: " + str(host.get('os', 'n/a')),oFileTXT,args.verbose)
		helper.loggER("Ports 	: " + str(host['ports'])		,oFileTXT,args.verbose)

		for item in host['data']:
			helper.loggER("------------------"					,oFileTXT,args.verbose,"STATUS")	
			helper.loggER("Response 	: " + str(item['port'])	,oFileTXT,args.verbose,"STATUS")
			helper.loggER("------------------"					,oFileTXT,args.verbose,"STATUS")
			helper.loggER(item['data'].strip()					,oFileTXT,args.verbose)

	except shodan.APIError as e:
		helper.loggER("Shodan 	: " + str(e),oFileTXT,True,"WARN")

def confirmIP (matchWork, cidr):	
	# Lets see if this is a real IP
	ipFull = str(matchWork) + cidr

	try:
		ip = ipaddress.ip_address(matchWork)

	except ValueError:
		helper.printR("Address/Netmask is invalid: "+ ipFull)
		return False
	except Exception as e:
		helper.printR("[validateHost] " + str(e) + " " + ipFull)
		return False

	if not ip.is_private:
		helper.printG("Public IP   : " + matchWork)

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
			
	helper.printP("Output Files are located at: " + oDir + "/")

if __name__ == "__main__":
    
    if sys.version_info <= (3, 0):
        sys.stdout.write("This script requires Python 3.x\n")
        sys.exit(1)

    banner.banner()
    banner.title()

    parser = ArgumentParser()
    parser.add_argument("-v",   dest="verbose",   help="Output to screen",    action="store_true")
    parser.add_argument("-s",   dest="shodan",    help="Check Shodan.io",     action="store_true")
    parser.add_argument("-c",   dest="censys",    help="check Censys.io",     action="store_true")
    parser.add_argument("--csv",	dest="csv",  	help="csv output",  	  action="store_true")
    parser.add_argument("--txt",	dest="txt",  	help="txt output",		  action="store_true")
    parser.add_argument("--ipList", dest="ipList",  help="Target ip addresses")

    args = parser.parse_args()

    if (args.ipList is None):
        parser.print_help()
        exit()

    if not os.path.isfile(args.ipList):
        helper.printR("Check File: " + args.ipList)
        exit()  
    
    # Load the keys
    PSconfigFile = os.path.abspath(os.path.dirname(__file__)) + "/api-keys.ini"
    if not os.path.isfile(PSconfigFile):
        helper.printR("Check API key File: " + PSconfigFile)
        exit()    	

    config = configparser.ConfigParser()
    config.read(PSconfigFile)
    shodan_apiKEY 	 = config.get('shodan.io', 'shodan_apiKEY',		fallback='Not-Configured')
    censys_apiID 	 = config.get('censys.io', 'censys_apiID',		fallback='Not-Configured')
    censys_apiSECRET = config.get('censys.io', 'censys_apiSECRET',	fallback='Not-Configured')
    
    pubIP = list()
    # Working directory
    ts = time.strftime("%m%d%Y_%H_%M_%S", time.gmtime())
    oDir = os.path.abspath(os.path.dirname(__file__)) + "/DATA/" + ts
    if not os.path.exists(oDir):
        os.makedirs(oDir);
    helper.printP("Working directory: " + oDir)
    print('')

    main()
