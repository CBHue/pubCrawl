import re
import censys.ipv4
import util.helper as helper

def cenSYS (ip,cID,cCRET):

	host = dict()
	censysDICT = {}
	ssList = set()

	try:
		c = censys.ipv4.CensysIPv4(cID,cCRET)
		host = c.view(ip)
		helper.printW("CensysIO 	: " + ip)
	except Exception as e:
		helper.printR("CensysIO 	: " + ip + " : " + str(e))
		return censysDICT, ssList

	censysDICT["Host"] 		= host['ip']
	if 'autonomous_system' in host.keys():
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

			# Add to the screen shot list if its http
			if re.search('http', proto, re.IGNORECASE):
				url = proto + "://" + ip + ":" + port
				ssList.add(url)
			
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
				if 'status_code' in host[str(port)][str(proto)]['get'].keys():
					status = host[str(port)][str(proto)]['get']['status_code']
					censysDICT[str(port) + "_status"] 		= str(status)
				if 'metadata' in host[str(port)][str(proto)]['get'].keys():
					metadata = host[str(port)][str(proto)]['get']['metadata']
					censysDICT[str(port) + "_metadata"] 		= str(metadata)
				if 'headers' in host[str(port)][str(proto)]['get'].keys():
					headers = host[str(port)][str(proto)]['get']['headers']
					censysDICT[str(port) + "_headers"] 		= str(headers)
			except Exception as error:
				continue

	return censysDICT, ssList

