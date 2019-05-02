# pubCrawl
![alt text](https://github.com/CBHue/pubCrawl/blob/master/pubCrawl.png)

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
  --ipList IPLIST  Target ip addresses
</pre>
