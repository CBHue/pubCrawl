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

python3 pubCrawl.py --host example.com
python3 pubCrawl2.py --hostList sampleHostList.txt --full

<pre>usage: pubCrawl.py [-h] [-s] [-c] [--sshot] [--csv] [--txt] [--full] [--hostList HOSTLIST] [--host HOSTNAME] [--combine]

optional arguments:
  -h, --help           show this help message and exit
  -s                   Check Shodan.io
  -c                   Check Censys.io
  --sshot              Take Screenshot
  --csv                csv output
  --txt                txt output
  --full               Censys + Shodan + Screenshot + Combine
  --hostList HOSTLIST  Host list
  --host HOSTNAME      Individual host
  --combine            Combine output types
</pre>
