#!/bin/bash
# variable (peasead@gmail.com)

# If you need a test MD5 for this, use this one: 4831523792d2758368af543d9dca748e

# Set the framework for the for loop, ideally you'd have just the malware in the folder, but you may need to adjust to "*.exe" or "*.pdf" or whatever if you have more than just badness in the folder
for i in $( /bin/ls /path/to/malware/folder/ ); do

# Set the variable as "hash" for the MD5 hash of the malware you're going to check, the "md5" command returns 4 rows, the 4th row has the hash, we're selecting that with "awk"
hash=$( /sbin/md5 $i | /usr/bin/awk '{print $4}' )

# Calling the Automator script and sending the value of the "hash" variable to VirusTotal, returning only TrendMicro, and only the TM malware name. Feel free to adjust this as you see fit, just picked TM at random
# YOU MUST BE IN THE AUTOMATER DIRECTORY, THIS CANNOT BE CALLED REMOTELY - SEE "TO BE DONE" BELOW
# During testing, if you need a test MD5 for this, use this one: 4831523792d2758368af543d9dca748e
/usr/bin/python /path/to/automater/script/automater.py -s virustotal $hash | grep -iwE \'trendmicro\' | awk '{print $6}' | sed -e 's/[^a-zA-Z*0-9\-\_\.\(\)]//g'

# You can only send a hash to VT every 15 seconds with the public API, so we're going to sleep for 16-seconds
/bin/sleep 16
done

# To Be Done
# Automater requires you're in the Automater directory. Issue submitted on TekDefense GitHub repo for this
