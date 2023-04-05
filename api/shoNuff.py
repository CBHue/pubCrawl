import re
import shodan
import util.helper as helper

def shoNuff (ip,sKEY):

	api = shodan.Shodan(sKEY)
	shodanDICT = {}
	ssList = set()

	try:
		helper.printY2("Shodan", ip)
		host = api.host(ip)

	except shodan.APIError as e:
		helper.printR("Shodan 	: " + str(e))
		return shodanDICT, ssList

	shodanDICT["Host"] 		= host['ip_str']
	shodanDICT["HostName"] 	= str(host['hostnames'])
	shodanDICT["Org"] 		= host.get('org', 'n/a')
	shodanDICT["OS"] 		= str(host.get('os', 'n/a'))
	shodanDICT["Ports"] 	= str(host['ports'])
	shodanDICT["vulns"] 	= str(host.get('vulns', 'n/a'))
	for item in host['data']:
		shodanDICT[str(item['port'])] = item['data'].strip()

		# Add to the screen shot list if we got an http response
		CBH = item['data'].strip()
		if re.search('http', CBH, re.IGNORECASE):
			url = "http://" + ip + ":" + str(item['port'])
			ssList.add(url)

	return shodanDICT, ssList
