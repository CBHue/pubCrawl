# pubCrawl
![alt text](https://github.com/CBHue/pubCrawl/blob/master/pubCrawl.png)

<pre>You will need to install shodan and censys:
  sudo apt install python3-pip
  pip3 install selenium
  pip3 install censys
  pip3 install shodan
  pip3 install nslookup
</pre>

Use Shodan &amp; Censys to perform port lookup on a list of ip's

python3 pubCrawl.py -scv --txt --csv --ipList ./pubIP.txt

<pre>usage: pubCrawl.py [-h] [-v] [-s] [-c] [--csv] [--txt] [--ipList IPLIST]

optional arguments:
  -h, --help       show this help message and exit
  -v               Output to screen
  -s               Check Shodan.io
  -c               check Censys.io
  --csv            csv output
  --txt            txt output
  --ipList IP.txt  File with Target ip addresses [one per line]
</pre>
