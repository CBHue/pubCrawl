
import os

def printR(out): print("\033[91m{}\033[00m" .format("[!] " + out)) 
def printG(out): print("\033[92m{}\033[00m" .format("[*] " + out)) 
def printY(out): print("\033[93m{}\033[00m" .format("[+] " + out)) 
def printP(out): print("\033[95m{}\033[00m" .format("[-] " + out)) 
def printW(out): print("[~] " + out)

def loggER(out,*lvl):			
	if "WARN" in lvl:
		if type(out) == dict:
			for x in out:
				print('\033[91m{0:16}: {1}\033[00m'.format("[*] " + x, out[x]))
		else:
			printR(out)
	elif "STATUS" in lvl:
		if type(out) == dict:
			for x in out:
				print('\033[93m{0:16}: {1}\033[00m'.format("[*] " + x, out[x]))
		else:
			printY(out)

	elif "other" in lvl:
		if type(out) == dict:
			for x in out:
				print('\033[95m{0:16}: {1}\033[00m'.format("[*] " + x, out[x]))
		else:
			printY(out)			

	else:
		if type(out) == dict:
			for x in out:
				print('\033[92m{0:16}: {1}\033[00m'.format("[*] " + x, out[x]))
		else:			
			printG(out) 

def logTXT(out,oF):
	with open(oF, 'a', newline='') as oHandle:
		for x in out:
			oHandle.write('{0:16}: {1}'.format("[*] " + x, out[x] + "\n"))
		if len(out) > 0:
			oHandle.write("Fin		:\n\n")
	oHandle.close()

def logCSV(out,oF):
	import csv
	with open(oF, 'a', newline='') as csvF:
		fieldnames = out.keys()
		writer = csv.DictWriter(csvF, fieldnames=fieldnames)
		if os.stat(oF).st_size == 0:
			writer.writeheader()
		writer.writerow(out)
	csvF.close()
