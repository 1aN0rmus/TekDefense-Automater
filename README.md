TekDefense-Automater
====================

http://www.tekdefense.com/automater/
http://www.tekdefense.com/news/2013/12/4/finally-the-new-automater-release-is-out.html


AUTOMATER
Description: Automater is a URL/Domain, IP Address, and Md5 Hash OSINT tool aimed at making the analysis process easier for intrusion Analysts. Given a target (URL, IP, or HASH) or a file full of targets Automater will return relevant results from sources like the following: IPvoid.com, Robtex.com, Fortiguard.com, unshorten.me, Urlvoid.com, Labs.alienvault.com, ThreatExpert, VxVault, and VirusTotal. 

*Automater is installed on HoneyDrive and Kali by default but currently have an outdated version.

Installation:

Automater comes in two  flavors, python script that will work for Linux or Windows, and an exe for Windows. 

  Windows:

The Windows client is currently in development. In the meantime the python code will work on Windows with a python 2.7 install

  Linux:

As this is a python script you will need to ensure you have the correct version of python, which for this script is python 2.7. I used mostly standard libraries, but just incase you don't have them, here are the libraries that are required: httplib2, re, sys, argparse, urllib, urllib2

With the python and the libraries out of the way, you can simply use git to clone the tekdefense code to your local machine.

git clone https://github.com/1aN0rmus/TekDefense-Automater.git

If you don't have git installed you can simply download the script from https://github.com/1aN0rmus/TekDefense-Automater/archive/master.zip

Usage:

Once installed the usage is pretty much the same across Windows, Linux, and Kali. 

python Automater.py -h

or if you chmod +x Automater.py you can

./Automater.py -h

usage: Automater.py [-h] [-o OUTPUT] [-w WEB] [-c CSV] [-d DELAY] [-s SOURCE]

                    [--p]

                    target

 

IP, URL, and Hash Passive Analysis tool

 

positional arguments:

  target                List one IP Addresses, URL or Hash to query or pass

                        the filename of a file containing IP Addresses, URL or

                        Hash to query each separated by a newline.

 

optional arguments:

  -h, --help            show this help message and exit

  -o OUTPUT, --output OUTPUT

                        This option will output the results to a file.

  -w WEB, --web WEB     This option will output the results to an HTML file.

  -c CSV, --csv CSV     This option will output the results to a CSV file.

  -d DELAY, --delay DELAY

                        This will change the delay to the inputted seconds.

                        Default is 2.

  -s SOURCE, --source SOURCE

                        This option will only run the target against a

                        specific source engine to pull associated domains.

                        Options are defined in the name attribute of the site

                        element in the XML configuration file

  --p                   This option tells the program to post information to

                        sites that allow posting. By default the program will

                        NOT post to sites that require a post.  

To run Automater against a target ip, hash, url, or file simply type

Python Automater.py <target>

python Automater.py 37.221.161.215

[*] Checking https://robtex.com/37.221.161.215

[*] Checking http://www.fortiguard.com/ip_rep/index.php?data=37.221.161.215&lookup=Lookup

[*] Checking http://www.alienvault.com/apps/rep_monitor/ip/37.221.161.215

[*] Checking https://www.virustotal.com/en/ip-address/37.221.161.215/information/

[*] Checking http://www.ipvoid.com/scan/37.221.161.215

 

____________________     Results found for: 37.221.161.215     ____________________

[+] A records from Robtex.com: vm1033.gigaservers.net

[+] Fortinet URL Category: Unclassified

[+] Found in AlienVault reputation DB: http://www.alienvault.com/apps/rep_monitor/ip/37.221.161.215

No results found for: [+] pDNS data from VirusTotal:

[+] pDNS malicious URLs from VirusTotal: ('2013-12-03', 'http://37.221.161(.)215/')

[+] pDNS malicious URLs from VirusTotal: ('2013-11-30', 'http://37.221.161(.)215/')

[+] pDNS malicious URLs from VirusTotal: ('2013-11-29', 'http://37.221.161(.)215/crypted.exe%5B/')

No results found for: [+] Blacklist from IPVoid:

[+] ISP from IPvoid: Voxility S.R.L.

[+] Country from IPVoid: (RO) Romania

 

python Automater.py 44A6A7D4A039F7CC2DB6E85601F6D8C1

[*] Checking https://www.virustotal.com/vtapi/v2/file/report

[*] Checking http://www.threatexpert.com/report.aspx?md5=44A6A7D4A039F7CC2DB6E85601F6D8C1

[*] Checking http://vxvault.siri-urz.net/ViriList.php?MD5=44A6A7D4A039F7CC2DB6E85601F6D8C1

 

____________________     Results found for: 44A6A7D4A039F7CC2DB6E85601F6D8C1     ____________________

[+] MD5 found on VT: 1

[+] Scan date submitted: 2013-11-29 18:49:10

[+] # of virus engines detected on: 18

[+] # of total scan engines: 48

[+] Malware detected on: ('MicroWorld-eScan', 'Trojan.Downloader.JQGE')

[+] Malware detected on: ('McAfee', 'PWSZbot-FKQ!44A6A7D4A039')

[+] Malware detected on: ('Malwarebytes', 'Trojan.Zbot')

[+] Malware detected on: ('Symantec', 'Trojan.Gen.2')

[+] Malware detected on: ('Norman', 'Suspicious_Gen4.FLCRK')

[+] Malware detected on: ('Avast', 'Win32:Agent-ASJS [Trj]')

[+] Malware detected on: ('BitDefender', 'Trojan.Downloader.JQGE')

[+] Malware detected on: ('Ad-Aware', 'Trojan.Downloader.JQGE')

[+] Malware detected on: ('Sophos', 'Mal/Generic-S')

[+] Malware detected on: ('McAfee-GW-Edition', 'PWSZbot-FKQ!44A6A7D4A039')

[+] Malware detected on: ('Emsisoft', 'Trojan.Downloader.JQGE (B)')

[+] Malware detected on: ('AhnLab-V3', 'Spyware/Win32.Zbot')

[+] Malware detected on: ('GData', 'Trojan.Downloader.JQGE')

[+] Malware detected on: ('Fortinet', 'W32/Injector.ASCL!tr')

[+] Hash found at ThreatExpert: 29 November 2013, 06:03:06

[+] Malicious Indicators from ThreatExpert: Downloads/requests other files from Internet.

[+] Date found at VXVault: 11-29

[+] URL found at VXVault: 37.221.161.215/crypted(.)exe

 

Automater.py diablo3keygen(.)net

[*] Checking http://www.fortiguard.com/ip_rep/index.php?data=diablo3keygen.net&lookup=Lookup

[*] Checking http://unshort.me/index.php?r=diablo3keygen.net

[*] Checking http://www.urlvoid.com/scan/diablo3keygen.net

[*] Checking https://www.virustotal.com/en/domain/diablo3keygen.net/information/

 

____________________     Results found for: diablo3keygen(.)net     ____________________

[+] Fortinet URL Category: Unclassified

[+] URL redirects to: http://diablo3keygen(.)net

[+] IP from URLVoid: 182.18.143.140

[+] Blacklist from URLVoid: http://www.mywot.com/en/scorecard/diablo3keygen.net"

[+] Blacklist from URLVoid: http://trafficlight.bitdefender.com/info?url=http://diablo3keygen.net"

[+] Domain Age from URLVoid: 2013-08-26 (3 months ago)

[+] Geo Coordinates from URLVoid: 20 / 77

[+] Country from URLVoid:  (IN) India

[+] pDNS data from VirusTotal: ('2013-11-28', '182.18.143.140')

[+] pDNS data from VirusTotal: ('2012-12-01', '31.3.152.106')

[+] pDNS malicious URLs from VirusTotal: ('2013-12-02', 'http://diablo3keygen(.)net/')

[+] pDNS malicious URLs from VirusTotal: ('2013-11-28', 'http://diablo3keygen(.)net/')

Checking a single source can be done by using –s

python Automater.py -s ipvoid 11.11.11.11

[*] Checking http://www.ipvoid.com/scan/11.11.11.11

 

____________________     Results found for: 11.11.11.11     ____________________

No results found for: [+] Blacklist from IPVoid:

[+] ISP from IPvoid: DoD Network Information Center

[+] Country from IPVoid: (US) United States

By default, if Automater does not find data available it will not submit the target to that site to get data. If you would like Automater to use an HTTP POST to send target data to a source like IPVoid or URLVoid use –p

c:\downloads\TekDefense-Automater-Private-master\TekDefense-Automater-Private-master>python Automater.py 11.11.12.56 --p

[*] Checking https://robtex.com/11.11.12.56

[*] Checking http://www.fortiguard.com/ip_rep/index.php?data=11.11.12.56&lookup=Lookup

[*] Checking http://www.alienvault.com/apps/rep_monitor/ip/11.11.12.56

[*] Checking https://www.virustotal.com/en/ip-address/11.11.12.56/information/

[*] Checking http://www.ipvoid.com/scan/11.11.12.56

[-] This target requires a submission. Submitting now, this may take a moment.

 

____________________     Results found for: 11.11.12.56     ____________________

No results found in the RobTex DNS

[+] Fortinet URL Category: Unclassified

[+] Found in AlienVault reputation DB: http://www.alienvault.com/apps/rep_monitor/ip/11.11.12.56

No results found for: [+] pDNS data from VirusTotal:

No results found for: [+] pDNS malicious URLs from VirusTotal:

No results found for: [+] Blacklist from IPVoid:

[+] ISP from IPvoid: DoD Network Information Center

[+] Country from IPVoid: (US) United States

There are also new output methods. –o will output to a file in the same format that is printed to screen, -c will output a csv, and –w will output an html file.

python Automater.py test.txt -o test.out -c test.csv -w test.html


As you may have noticed, it does take Automater a little longer to run then it used to. That is because we implemented a delay of 2 seconds between requests to ensure we don’t bog down the sources. You can modify this delay with a –d <number of seconds>.

python Automater.py test.txt -o test.out -c test.csv -w test.html –d 5

Sites.xml

Automater is now very easily extensible even for those that are not familiar with python. All the sources that are queried and what they are queried for are contained in sites.xml. This must be in the same directory as Automater.py and all the other .py’s that Automater ships with. I will update this page soon with instructions on how to modify the xml file, but in the meantime if you take a look at the current entries it is pretty self-explanatory.
