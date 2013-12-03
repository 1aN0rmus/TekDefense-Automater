import argparse,re,os

class Parser:
    def __init__(self,desc):
        # Adding arguments
        self._parser = argparse.ArgumentParser(description=desc)
        self._parser.add_argument('target', help='List one IP Addresses, URL or Hash to query or pass the filename of a file containing IP Addresses, URL or Hash to query each separated by a newline.')
        self._parser.add_argument('-o', '--output', help='This option will output the results to a file.')
        self._parser.add_argument('-w', '--web', help='This option will output the results to an HTML file.')
        self._parser.add_argument('-c', '--csv', help='This option will output the results to a CSV file.')
        self._parser.add_argument('-d', '--delay', type=int, default=2, help='This will change the delay to the inputted seconds. Default is 2.')
        self._parser.add_argument('-s', '--source', help='This option will only run the target against a specific source engine to pull associated domains.  Options are defined in the name attribute of the site element in the XML configuration file')
        self._parser.add_argument('--p', action="store_true", help='This option tells the program to post information to sites that allow posting. By default the program will NOT post to sites that require a post.')
        self.args = self._parser.parse_args()        

    def hasHTMLOutFile(self):
        if self.args.web:
            return True
        else:
            return False
    
    @property    
    def HTMLOutFile(self):
        if self.hasHTMLOutFile():
            return self.args.web
        else:
            return None
        
    def hasTextOutFile(self):
        if self.args.output:
            return True
        else:
            return False
    
    @property    
    def TextOutFile(self):
        if self.hasTextOutFile():
            return self.args.output
        else:
            return None
    
    def hasCSVOutSet(self):
        if self.args.csv:
            return True
        else:
            return False
    
    @property
    def CSVOutFile(self):
        if self.hasCSVOutSet():
            return self.args.csv
        else:
            return None    
        
    @property
    def Delay(self):
        return self.args.delay
    
    def print_help(self):
        self._parser.print_help()
    
    def hasTarget(self):
        if self.args.target == None:
            return False
        else:
            return True
    
    def hasNoTarget(self):
        return not(self.hasTarget())
    
    @property
    def Target(self):
        if self.hasNoTarget():
            return None
        else:
            return self.args.target

    def hasInputFile(self):
        if os.path.exists(self.args.target) and os.path.isfile(self.args.target):
            return True
        else:
            return False
        
    @property    
    def Source(self):
        if self.hasSource():
            return self.args.source
        else:
            return None
        
    def hasSource(self):
        if self.args.source:
            return True
        else:
            return False
    
    def hasPost(self):
        if self.args.p:
            return True
        else:
            return False
        
    @property    
    def InputFile(self):
        if self.hasNoTarget():
            return None
        elif self.hasInputFile():
            return self.Target
        else:
            return None
            
class IPWrapper(object):
    
    @classmethod
    def isIPorIPList(self,target):
        #IP Address range using prefix syntax
        ipRangePrefix = re.compile('\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\/\d{1,2}', re.IGNORECASE)
        ipRgeFind = re.findall(ipRangePrefix,target)
        ipRangeDash = re.compile('\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}-\d{1,3}', re.IGNORECASE)
        ipRgeDashFind = re.findall(ipRangeDash,target)
        ipAddress = re.compile('\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}', re.IGNORECASE)
        ipFind = re.findall(ipAddress,target)
        if ((ipRgeFind is None or len(ipRgeFind) == 0) and (ipRgeDashFind is None or len(ipRgeDashFind) == 0) and (ipFind is None and len(ipFind) == 0)):
            return False
        else:
            return True
    
    @classmethod
    def getTarget(self,target):
        #IP Address range using prefix syntax
        ipRangePrefix = re.compile('\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\/\d{1,2}', re.IGNORECASE)
        ipRgeFind = re.findall(ipRangePrefix,target)
        ipRangeDash = re.compile('\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}-\d{1,3}', re.IGNORECASE)
        ipRgeDashFind = re.findall(ipRangeDash,target)
        ipAddress = re.compile('\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}', re.IGNORECASE)
        ipFind = re.findall(ipAddress,target)        
        if ipRgeFind is not None and len(ipRgeFind) > 0:
            #this can be used if we ever get bigger than a class C
            #but truthfully we don't need to split the whole address
            #since we'll only be using the last octet.
            iplist = target[:target.index("/")].split(".")
            ipprefix=givenipprefix=target[target.index("/")+1:]
            #create a bytearry to hold the one byte
            #this would be 4 bytes for IPv4 and gives us the capability to grow
            #if we ever want to go larger than a class C
            bytearr = bytearray(2)
            bytearr[0] = int(iplist[3])
            #prefix must be class C or larger
            if int(givenipprefix) < 24:
                ipprefix = 24
            if int(givenipprefix) > 32 or int(givenipprefix) == 31:
                ipprefix = 32
                bytearr[1]=0
            else:
                bytearr[1]=pow(2,32-int(ipprefix))#-1
            
            if bytearr[0]>bytearr[1]:    
                start=bytearr[0]
                last=bytearr[0]^bytearr[1]
            else:
                start=bytearr[0]
                last=bytearr[1]            
            if start == last:
                yield target[:target.rindex(".")+1]+str(start)
            if start<last:
                for lastoctet in range(start,last):
                    yield target[:target.rindex(".")+1]+str(lastoctet)
            else:
                yield target[:target.rindex(".")+1]+str(start)
        #IP Address range seperated with a dash       
        elif ipRgeDashFind is not None and len(ipRgeDashFind) > 0:
            iplist = target[:target.index("-")].split(".")
            iplast = target[target.index("-")+1:]
            if int(iplist[3])<int(iplast):
                for lastoctet in range(int(iplist[3]),int(iplast)+1):
                    yield target[:target.rindex(".")+1]+str(lastoctet)
            else:
                yield target[:target.rindex(".")+1]+str(iplist[3])
        #it's just an IP address at this point
        else:
            yield target                
