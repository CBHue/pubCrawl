from censys.search import CensysHosts
import util.helper as helper

def cenSYS (ip,cID,cCRET):

	host = dict()
	censysDICT = {}
	ssList = set()

	try:
		c = CensysHosts(cID,cCRET)
		host = c.view(ip)
		helper.printY2("CensysIO", ip)
	except Exception as e:
		helper.printR("CensysIO" + ip + " : " + str(e))
		return censysDICT, ssList

	# Host IP
	censysDICT["Host"] 		= host['ip']

	# OS
	if 'operating_system' in host.keys():
		censysDICT["osName"] = host['operating_system']['product'] + "_" + host['operating_system']['vendor']

	# DNS Names
	if 'dns' in host.keys():
		censysDICT["dnsNames"] = host['dns']['names']

	# Network info
	if 'autonomous_system' in host.keys():
		censysDICT["Network"] 	= host['autonomous_system']['bgp_prefix']
		censysDICT["Desc"] 		= host['autonomous_system']['description']
		censysDICT["Name"] 		= host['autonomous_system']['name']	

	
	# Services
	#Number of ports identified
	pCount = len(host['services'])
	ports = ""
	services = ""

	# add each port to its own Dictionary
	for x in range(pCount):
		
		service = host['services'][x]['extended_service_name']
		services = service + "," + services
		port  = host['services'][x]['port']
		ports = str(port) + "," + ports
		
		censysDICT["Ports"] 					= host['services'][x]['port']
		censysDICT[str(port) + "_Services"] 	= host['services'][x]['extended_service_name']
		censysDICT[str(port) + "_Banner"] 		= host['services'][x]['banner']	

		if 'http' in host['services'][x].keys():
			url = host['services'][x]['http']['request']['uri']

			# Replace the last "/"
			last_char_index = url.rfind("/")
			url = url[:last_char_index] + ":" + url[last_char_index+1:]

			ssList.add(url + str(port))
		

	# Replace the last ","
	last_char_index = ports.rfind(",")
	ports = ports[:last_char_index] + "" + ports[last_char_index+1:]
	censysDICT["Ports"] 	= ports	

	# Replace the last ","
	last_char_index = services.rfind(",")
	services = services[:last_char_index] + "" + services[last_char_index+1:]
	censysDICT["Proto"] 	= services

	return censysDICT, ssList
