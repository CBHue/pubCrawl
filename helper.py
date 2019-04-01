
import os
import subprocess
import shlex

def printR(out): print("\033[91m{}\033[00m" .format("[!] " + out)) 
def printG(out): print("\033[92m{}\033[00m" .format("[*] " + out)) 
def printY(out): print("\033[93m{}\033[00m" .format("[+] " + out)) 
def printP(out): print("\033[95m{}\033[00m" .format("[-] " + out)) 
def printW(out): print("[~] " + out)

def loggER(out,txt,verbose,*lvl):
	
	if verbose:
		if "WARN" in lvl:
			printR(out)
		elif "STATUS" in lvl:
			printY(out)
		else:
			printG(out) 
	
	if txt:
		oHandle = open(txt, "a+")
		oHandle.write(out + "\n")
		oHandle.close()

def realTimeMuxER(command):
    p = subprocess.Popen(shlex.split(command), stdout=subprocess.PIPE)
    while True:
        output = p.stdout.readline().decode()
        if output == '' and p.poll() is not None:
            break
        if output:
            print(output.strip())
    rc = p.poll()


def muxER(command):
	result =[]
	FNULL = open(os.devnull, 'w')
	proc = subprocess.Popen([command], stdout=subprocess.PIPE, stderr=FNULL, shell=True)
	(result, err) = proc.communicate()
	return result
