import os
import re
import socket
import ipaddress

import dns.resolver

import util.osWork 
import util.helper as helper


def validateHost (network):
	hostMAP = {}

	helper.printW2("Validating", network)
	cidr = ""

	# is this a ip/cidr
	match = re.search(r'(\d+.\d+.\d+.\d+)(/\d+)', network)
	if match:
		matchWork = match.group(1)
		helper.printW2("IP Addr", matchWork)
		helper.printW2("Subnet", match.group(2))
		cidr = match.group(2)

		# if it a single Host add it to the hostMAP
		if match.group(2) == '/32':
			ip = confirmIP(matchWork, cidr)
			if not ip:
				return False, False
			hostMAP[ip] = network

		# its not a network ... expand it
		else:	
			helper.printY("Expanding Network: " + network)
			expandedhostFile = ipaddress.ip_network(network)
			cidr = "/32"
			for ip in expandedhostFile:
				confirmIP(ip, cidr)
				helper.printW("Fin		: " + str(ip))
				print('')
				# This is if u have a rate limit for API calls
				helper.printW("Sleeping for a second ...")
				time.sleep( 2 )
				print('')
	
	# its not in cidr notation
	else:
		cidr = "/32"
		match = re.search(r'(\d+.\d+.\d+.\d+)', network)
		# If its a single IP add it to hostMAP 
		if match:
			helper.printG2("Single IP", network)

			matchWork = network	
			ip = confirmIP(matchWork, cidr)
			if not ip:
				return False, False
			# Lets see if we can do a reverse lookup
			name = network
			try:
				n = socket.gethostbyaddr(network)
				name = n[0]
			except Exception as e:
				name = network

			hostMAP[ip] = name

		# Try to resolve the hostname ... 
		else:
			cidr = "/32"
			helper.printW2("Hostname", network)
			sip = resolveHName(network)

			if sip == "NXDOMAIN":
				helper.printR2("No IP found", network)
				return False, False

			helper.printG2("Resolved IP",sip)
			ip = confirmIP(sip, cidr)
			if ip:
				hostMAP.update({ip : network})

	# lets seperate private and public hosts
	privateHostMap = {}
	publicHostMap  = {}
	for key, value in hostMAP.items():
		if ipaddress.ip_address(key).is_private:
			helper.printR2("Address/Netmask is Private", key)
			privateHostMap[key] = value
		else:
			publicHostMap[key] = value

	# At this time we have a private and pulic hostMAP ... returning the public one for shodan/censysIO
	return publicHostMap, privateHostMap

def confirmIP (matchWork, cidr):	
	# Lets see if this is a real IP
	ipFull = str(matchWork) + cidr
	matchWork = str(matchWork)

	try:
		ip = ipaddress.ip_address(matchWork)
	except ValueError:
		helper.printR2("Address/Netmask is invalid", ipFull)
		return False
	except Exception as e:
		helper.printR("[validateHost] " + str(e) + " " + ipFull)
		return False

	# If we got here the IP is valid.
	return matchWork

def resolveHName (hName):
	ip = "NXDOMAIN"

	try:
		result = dns.resolver.query(hName, 'A')
		for ipval in result:
			ip = ipval.to_text()
	except Exception as e:
		ip = "NXDOMAIN"

	return str(ip) 
