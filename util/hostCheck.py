import os
import re
import dns
import socket
import ipaddress

import util.osWork 
import util.helper as helper

def resolveHName (hName):
	ip = "NXDOMAIN"

	try:
		result = dns.resolver.query(hName, 'A')
		for ipval in result:
			ip = ipval.to_text()
	except Exception as e:
		ip = "NXDOMAIN"

	return str(ip) 

def validateHost (network):
	hostMAP = {}

	helper.printW("Validating 	: " +  network)
	cidr = ""

	# is this a ip/cidr
	match = re.search(r'(\d+.\d+.\d+.\d+)(/\d+)', network)
	if match:
		matchWork = match.group(1)
		helper.printW("IP Addr: " + matchWork)
		helper.printW("Subnet : " + match.group(2))
		cidr = match.group(2)

		# is it one host or more
		if match.group(2) == '/32':
			if ipaddress.ip_address(matchWork).is_private:
				helper.printR("Private Network ... Skipping")
				return
			
			ip = confirmIP(matchWork, cidr)
			if not ip:
				return
			hostMAP[ip] = network

		else:
			if ipaddress.ip_address(matchWork).is_private:
				helper.printR("Private Network ... Skipping")
				return
			
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
	
	# its not a network/cidr so its either a single IP or Hostname
	else:
		cidr = "/32"
		match = re.search(r'(\d+.\d+.\d+.\d+)', network)
		if match:
			helper.printG("Single IP 	: " + network)

			matchWork = network	
			ip = confirmIP(matchWork, cidr)
			if not ip:
				return
			# Lets see if we can do a reverse lookup
			name = network
			try:
				n = socket.gethostbyaddr(network)
				name = n[0]
			except Exception as e:
				name = network

			hostMAP[ip] = name

		# Must be a hostname
		else:
			cidr = "/32"
			helper.printW("Hostname 	: " + network)
			sip = resolveHName(network)

			if sip is "NXDOMAIN":
				helper.printR("No IP found : " + network)
				return

			helper.printG("Resolved IP : " + sip)
			ip = confirmIP(sip, cidr)
			if ip:
				hostMAP.update({ip : network})

	return hostMAP

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
	if ipaddress.ip_address(matchWork).is_private:
		helper.printR("Address/Netmask is Private: "+ ipFull)
		return False
		
	# If we got here the IP is valid.
	return matchWork
