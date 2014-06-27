"""
The utilities.py module handles all utility functions that Automater
requires.

Class(es):
Parser -- Class to handle standard argparse functions with
a class-based structure.
IPWrapper -- Class to provide IP Address formatting and parsing.

Function(s):
No global exportable functions are defined.

Exception(s):
No exceptions exported.
"""
import argparse
import re
import os

class Parser(object):
    """
    Parser represents an argparse object representing the
    program's input parameters.

    Public Method(s):
    hasHTMLOutFile
    (Property) HTMLOutFile
    hasTextOutFile
    (Property) TextOutFile
    hasCSVOutSet
    (Property) CSVOutFile
    (Property) Delay
    hasProxy
    (Property) Proxy
    print_help
    hasTarget
    hasNoTarget
    (Property) Target
    hasInputFile
    (Property) Source
    hasSource
    hasPost
    (Property) InputFile
    (Property) UserAgent

    Instance variable(s):
    _parser
    args
    """

    def __init__(self, desc):
        """
        Class constructor. Adds the argparse info into the instance variables.

        Argument(s):
        desc -- ArgumentParser description.

        Return value(s):
        Nothing is returned from this Method.
        """
        # Adding arguments
        self._parser = argparse.ArgumentParser(description = desc)
        self._parser.add_argument('target', help = 'List one IP Address (CIDR or dash notation accepted), URL or Hash to query or pass the filename of a file containing IP Address info, URL or Hash to query each separated by a newline.')
        self._parser.add_argument('-o', '--output', help = 'This option will output the results to a file.')
        self._parser.add_argument('-w', '--web', help = 'This option will output the results to an HTML file.')
        self._parser.add_argument('-c', '--csv', help = 'This option will output the results to a CSV file.')
        self._parser.add_argument('-d', '--delay', type=int, default = 2, help = 'This will change the delay to the inputted seconds. Default is 2.')
        self._parser.add_argument('-s', '--source', help = 'This option will only run the target against a specific source engine to pull associated domains.  Options are defined in the name attribute of the site element in the XML configuration file')
        self._parser.add_argument('--p', '--post', action = "store_true", help = 'This option tells the program to post information to sites that allow posting. By default the program will NOT post to sites that require a post.')
        self._parser.add_argument('--proxy', help = 'This option will set a proxy to use (eg. proxy.example.com:8080)')
        self._parser.add_argument('-a', '--useragent', default = 'Automater/2.1', help = 'This option allows the user to set the user-agent seen by web servers being utilized. By default, the user-agent is set to Automater/version')
        self.args = self._parser.parse_args()

    def hasHTMLOutFile(self):
        """
        Checks to determine if user requested an output file formatted in HTML.
        Returns True if user requested HTML output, False if not.

        Argument(s):
        No arguments are required.

        Return value(s):
        Boolean.

        Restriction(s):
        The Method has no restrictions.
        """
        if self.args.web:
            return True
        else:
            return False

    @property
    def HTMLOutFile(self):
        """
        Checks if there is an HTML output requested.
        Returns string name of HTML output file if requested
        or None if not requested.

        Argument(s):
        No arguments are required.

        Return value(s):
        string -- Name of an output file to write to system.
        None -- if web output was not requested.

        Restriction(s):
        This Method is tagged as a Property.
        """
        if self.hasHTMLOutFile():
            return self.args.web
        else:
            return None

    def hasTextOutFile(self):
        """
        Checks to determine if user requested an output text file.
        Returns True if user requested text file output, False if not.

        Argument(s):
        No arguments are required.

        Return value(s):
        Boolean.

        Restriction(s):
        The Method has no restrictions.
        """
        if self.args.output:
            return True
        else:
            return False

    @property
    def TextOutFile(self):
        """
        Checks if there is a text output requested.
        Returns string name of text output file if requested
        or None if not requested.

        Argument(s):
        No arguments are required.

        Return value(s):
        string -- Name of an output file to write to system.
        None -- if output file was not requested.

        Restriction(s):
        This Method is tagged as a Property.
        """
        if self.hasTextOutFile():
            return self.args.output
        else:
            return None

    def hasCSVOutSet(self):
        """
        Checks to determine if user requested an output file delimited by commas.
        Returns True if user requested file output, False if not.

        Argument(s):
        No arguments are required.

        Return value(s):
        Boolean.

        Restriction(s):
        The Method has no restrictions.
        """
        if self.args.csv:
            return True
        else:
            return False

    @property
    def CSVOutFile(self):
        """
        Checks if there is a comma delimited output requested.
        Returns string name of comma delimited output file if requested
        or None if not requested.

        Argument(s):
        No arguments are required.

        Return value(s):
        string -- Name of an comma delimited file to write to system.
        None -- if comma delimited output was not requested.

        Restriction(s):
        This Method is tagged as a Property.
        """
        if self.hasCSVOutSet():
            return self.args.csv
        else:
            return None

    @property
    def Delay(self):
        """
        Returns delay set by input parameters to the program.

        Argument(s):
        No arguments are required.

        Return value(s):
        string -- String containing integer to tell program how long to delay
        between each site query. Default delay is 2 seconds.

        Restriction(s):
        This Method is tagged as a Property.
        """
        return self.args.delay

    def hasProxy(self):
        """
        Checks to determine if user requested a proxy.
        Returns True if user requested a proxy, False if not.

        Argument(s):
        No arguments are required.

        Return value(s):
        Boolean.

        Restriction(s):
        The Method has no restrictions.
        """
        if self.args.proxy:
            return True
        else:
            return False

    @property
    def Proxy(self):
        """
        Returns proxy set by input parameters to the program.

        Argument(s):
        No arguments are required.

        Return value(s):
        string -- String containing proxy server in format server:port,
        default is none

        Restriction(s):
        This Method is tagged as a Property.
        """
        if self.hasProxy():
            return self.args.proxy
        else:
            return None

    def print_help(self):
        """
        Returns standard help information to determine usage for program.

        Argument(s):
        No arguments are required.

        Return value(s):
        string -- Standard argparse help information to show program usage.

        Restriction(s):
        This Method has no restrictions.
        """
        self._parser.print_help()

    def hasTarget(self):
        """
        Checks to determine if a target was provided to the program.
        Returns True if a target was provided, False if not.

        Argument(s):
        No arguments are required.

        Return value(s):
        Boolean.

        Restriction(s):
        The Method has no restrictions.
        """
        if self.args.target is None:
            return False
        else:
            return True

    def hasNoTarget(self):
        """
        Checks to determine if a target was provided to the program.
        Returns False if a target was provided, True if not.

        Argument(s):
        No arguments are required.

        Return value(s):
        Boolean.

        Restriction(s):
        The Method has no restrictions.
        """
        return not(self.hasTarget())

    @property
    def Target(self):
        """
        Checks to determine the target info provided to the program.
        Returns string name of target or string name of file
        or None if a target is not provided.

        Argument(s):
        No arguments are required.

        Return value(s):
        string -- String target info or filename based on target parameter to program.

        Restriction(s):
        This Method is tagged as a Property.
        """
        if self.hasNoTarget():
            return None
        else:
            return self.args.target

    def hasInputFile(self):
        """
        Checks to determine if input file is the target of the program.
        Returns True if a target is an input file, False if not.

        Argument(s):
        No arguments are required.

        Return value(s):
        Boolean.

        Restriction(s):
        The Method has no restrictions.
        """
        if os.path.exists(self.args.target) and os.path.isfile(self.args.target):
            return True
        else:
            return False

    @property
    def Source(self):
        """
        Checks to determine if a source parameter was provided to the program.
        Returns string name of source or None if a source is not provided

        Argument(s):
        No arguments are required.

        Return value(s):
        string -- String source name based on source parameter to program.
        None -- If the -s parameter is not used.

        Restriction(s):
        This Method is tagged as a Property.
        """
        if self.hasSource():
            return self.args.source
        else:
            return None

    def hasSource(self):
        """
        Checks to determine if -s parameter and source name
        was provided to the program.
        Returns True if source name was provided, False if not.

        Argument(s):
        No arguments are required.

        Return value(s):
        Boolean.

        Restriction(s):
        The Method has no restrictions.
        """
        if self.args.source:
            return True
        else:
            return False

    def hasPost(self):
        """
        Checks to determine if --p parameter was provided to the program.
        Returns True if --p was provided, False if not.

        Argument(s):
        No arguments are required.

        Return value(s):
        Boolean.

        Restriction(s):
        The Method has no restrictions.
        """
        if self.args.p:
            return True
        else:
            return False

    @property
    def InputFile(self):
        """
        Checks to determine if an input file string representation of
        a target was provided as a parameter to the program.
        Returns string name of file or None if file name is not provided

        Argument(s):
        No arguments are required.

        Return value(s):
        string -- String file name based on target filename parameter to program.
        None -- If the target is not a filename.

        Restriction(s):
        This Method is tagged as a Property.
        """
        if self.hasNoTarget():
            return None
        elif self.hasInputFile():
            return self.Target
        else:
            return None

    @property
    def UserAgent(self):
        """
        Returns useragent setting invoked by user at command line or the default
        user agent provided by the program.

        Argument(s):
        No arguments are required.

        Return value(s):
        string -- Name utilized as the useragent for the program.

        Restriction(s):
        This Method is tagged as a Property.
        """
        return self.args.useragent

class IPWrapper(object):
    """
    IPWrapper provides Class Methods to enable checks
    against strings to determine if the string is an IP Address
    or an IP Address in CIDR or dash notation.

    Public Method(s):
    (Class Method) isIPorIPList
    (Class Method) getTarget

    Instance variable(s):
    No instance variables.
    """

    @classmethod
    def isIPorIPList(self, target):
        """
        Checks if an input string is an IP Address or if it is
        an IP Address in CIDR or dash notation.
        Returns True if IP Address or CIDR/dash. Returns False if not.

        Argument(s):
        target -- string target provided as the first argument to the program.

        Return value(s):
        Boolean.

        Restriction(s):
        This Method is tagged as a Class Method
        """
        # IP Address range using prefix syntax
        ipRangePrefix = re.compile('\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\/\d{1,2}')
        ipRgeFind = re.findall(ipRangePrefix,target)
        if (ipRgeFind is not None or len(ipRgeFind) != 0):
            return True
        ipRangeDash = re.compile('\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}-\d{1,3}')
        ipRgeDashFind = re.findall(ipRangeDash,target)
        if (ipRgeDashFind is not None or len(ipRgeDashFind) != 0):
            return True
        ipAddress = re.compile('\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}')
        ipFind = re.findall(ipAddress,target)
        if (ipFind is not None and len(ipFind) != 0):
            return True

        return False

    @classmethod
    def getTarget(self, target):
        """
        Determines whether the target provided is an IP Address or
        an IP Address in CIDR or dash notation. Then creates a list
        that can be utilized as targets by the program.
        Returns a list of string IP Addresses that can be used as targets.

        Argument(s):
        target -- string target provided as the first argument to the program.

        Return value(s):
        Iterator of string(s) representing IP Addresses.

        Restriction(s):
        This Method is tagged as a Class Method
        """
        # IP Address range using prefix syntax
        ipRangePrefix = re.compile('\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\/\d{1,2}', re.IGNORECASE)
        ipRgeFind = re.findall(ipRangePrefix, target)
        ipRangeDash = re.compile('\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}-\d{1,3}')
        ipRgeDashFind = re.findall(ipRangeDash, target)
        ipAddress = re.compile('\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}')
        ipFind = re.findall(ipAddress, target)
        if ipRgeFind is not None and len(ipRgeFind) > 0:
            # this can be used if we ever get bigger than a class C
            # but truthfully we don't need to split the whole address
            # since we'll only be using the last octet.
            iplist = target[:target.index("/")].split(".")
            ipprefix = givenipprefix=target[target.index("/")+1:]
            # create a bytearry to hold the one byte
            # this would be 4 bytes for IPv4 and gives us the capability to grow
            # if we ever want to go larger than a class C
            bytearr = bytearray(2)
            bytearr[0] = int(iplist[3])
            # prefix must be class C or larger
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
        # IP Address range seperated with a dash
        elif ipRgeDashFind is not None and len(ipRgeDashFind) > 0:
            iplist = target[:target.index("-")].split(".")
            iplast = target[target.index("-")+1:]
            if int(iplist[3])<int(iplast):
                for lastoctet in range(int(iplist[3]),int(iplast)+1):
                    yield target[:target.rindex(".")+1]+str(lastoctet)
            else:
                yield target[:target.rindex(".")+1]+str(iplist[3])
        # it's just an IP address at this point
        else:
            yield target
