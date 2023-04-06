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
		product = host['operating_system'].get('product', 'n/a')
		vendor  = host['operating_system'].get('vendor', 'n/a')
		censysDICT["osName"] = product + "_" + vendor

	# DNS Names
	if 'dns' in host.keys():
		censysDICT["dnsNames"] = host['dns'].get('names', 'n/a')


	# Network info
	if 'autonomous_system' in host.keys():
		censysDICT["Network"] 	= host['autonomous_system'].get('bgp_prefix', 'n/a')
		censysDICT["Desc"] 		= host['autonomous_system'].get('description', 'n/a')
		censysDICT["Name"] 		= host['autonomous_system'].get('name', 'n/a')	

	
	# Services
	#Number of ports identified
	pCount = len(host['services'])
	ports = ""
	services = ""

	# add each port to its own Dictionary
	for x in range(pCount):
		
		service = host['services'][x].get('extended_service_name', 'n/a')
		services = service + "," + services
		port  = host['services'][x].get('port', 'n/a')
		ports = str(port) + "," + ports
		
		censysDICT[str(port) + "_Services"] 	= service
		censysDICT[str(port) + "_Banner"] 		= host['services'][x].get('banner', 'n/a')	

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
