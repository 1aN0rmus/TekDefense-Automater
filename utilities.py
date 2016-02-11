"""
The utilities.py module handles all utility functions that Automater
requires.

Class(es):
Parser -- Class to handle standard argparse functions with
a class-based structure.
IPWrapper -- Class to provide IP Address formatting and parsing.
VersionChecker -- Class to check if modifications to any files are available

Function(s):
No global exportable functions are defined.

Exception(s):
No exceptions exported.
"""
import argparse
import re
import os
import hashlib
import requests

class Parser(object):
    """
    Parser represents an argparse object representing the
    program's input parameters.

    Public Method(s):
    hasBotOut
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

    def __init__(self, desc, version):
        """
        Class constructor. Adds the argparse info into the instance variables.

        Argument(s):
        desc -- ArgumentParser description.

        Return value(s):
        Nothing is returned from this Method.
        """
        # Adding arguments
        self._parser = argparse.ArgumentParser(description=desc)
        self._parser.add_argument('target', help='List one IP Address (CIDR or dash notation accepted), URL or Hash to query or pass the filename of a file containing IP Address info, URL or Hash to query each separated by a newline.')
        self._parser.add_argument('-o', '--output', help='This option will output the results to a file.')
        self._parser.add_argument('-b', '--bot', action="store_true", help='This option will output minimized results for a bot.')
        self._parser.add_argument('-f', '--cef', help='This option will output the results to a CEF formatted file.')
        self._parser.add_argument('-w', '--web', help='This option will output the results to an HTML file.')
        self._parser.add_argument('-c', '--csv', help='This option will output the results to a CSV file.')
        self._parser.add_argument('-d', '--delay', type=int, default=2, help='This will change the delay to the inputted seconds. Default is 2.')
        self._parser.add_argument('-s', '--source', help='This option will only run the target against a specific source engine to pull associated domains. Options are defined in the name attribute of the site element in the XML configuration file. This can be a list of names separated by a semicolon.')
        self._parser.add_argument('--proxy', help='This option will set a proxy to use (eg. proxy.example.com:8080)')
        self._parser.add_argument('-a', '--useragent', default='Automater/{version}'.format(version=version), help='This option allows the user to set the user-agent seen by web servers being utilized. By default, the user-agent is set to Automater/version')
        self._parser.add_argument('-V', '--vercheck', action='store_true', help='This option checks and reports versioning for Automater. Checks each python module in the Automater scope. Default, (no -V) is False')
        self._parser.add_argument('-r', '--refreshxml', action='store_true', help='This option refreshes the tekdefense.xml file from the remote GitHub site. Default (no -r) is False.')
        self._parser.add_argument('-v', '--verbose', action='store_true', help='This option prints messages to the screen. Default (no -v) is False.')
        self.args = self._parser.parse_args()

    def hasBotOut(self):
        """
        Checks to determine if user requested an output file minimized for use with a Bot.
        Returns True if user requested minimized Bot output, False if not.

        Argument(s):
        No arguments are required.

        Return value(s):
        Boolean.

        Restriction(s):
        The Method has no restrictions.
        """
        if self.args.bot:
            return True
        else:
            return False

    def hasCEFOutFile(self):
        """
        Checks to determine if user requested an output file formatted in CEF.
        Returns True if user requested CEF output, False if not.

        Argument(s):
        No arguments are required.

        Return value(s):
        Boolean.

        Restriction(s):
        The Method has no restrictions.
        """
        if self.args.cef:
            return True
        else:
            return False

    @property
    def CEFOutFile(self):
        """
        Checks if there is an CEF output requested.
        Returns string name of CEF output file if requested
        or None if not requested.

        Argument(s):
        No arguments are required.

        Return value(s):
        string -- Name of an output file to write to system.
        None -- if CEF output was not requested.

        Restriction(s):
        This Method is tagged as a Property.
        """
        if self.hasCEFOutFile():
            return self.args.cef
        else:
            return None

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

    def versionCheck(self):
        """
        Checks to determine if the user wants the program to check for versioning. By default this is True which means
        the user wants to check for versions.

        Argument(s):
        No arguments are required.

        Return value(s):
        Boolean.

        Restriction(s):
        The Method has no restrictions.
        """
        if self.args.vercheck:
            return True
        else:
            return False

    @property
    def VersionCheck(self):
        """
        Checks to determine if the user wants the program to check for versioning. By default this is True which means
        the user wants to check for versions.

        Argument(s):
        No arguments are required.

        Return value(s):
        Boolean.

        Restriction(s):
        The Method has no restrictions.
        """
        return self.versionCheck()

    def verbose(self):
        """
        Checks to determine if the user wants the program to send standard output to the screen.

        Argument(s):
        No arguments are required.

        Return value(s):
        Boolean.

        Restriction(s):
        The Method has no restrictions.
        """
        if self.args.verbose:
            return True
        else:
            return False

    @property
    def Verbose(self):
        """
        Checks to determine if the user wants the program to send standard output to the screen.

        Argument(s):
        No arguments are required.

        Return value(s):
        Boolean.

        Restriction(s):
        The Method has no restrictions.
        """
        return self.verbose()

    def refreshRemoteXML(self):
        """
        Checks to determine if the user wants the program to grab the tekdefense.xml information each run.
        By default this is True.

        Argument(s):
        No arguments are required.

        Return value(s):
        Boolean.

        Restriction(s):
        The Method has no restrictions.
        """
        if self.args.refreshxml:
            return True
        else:
            return False

    @property
    def RefreshRemoteXML(self):
        """
        Checks to determine if the user wants the program to grab the tekdefense.xml information each run.
        By default this is True.

        Argument(s):
        No arguments are required.

        Return value(s):
        Boolean.

        Restriction(s):
        The Method has no restrictions.
        """
        return self.refreshRemoteXML()

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
    def isIPorIPList(cls, target):
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
        #ipRangePrefix = re.compile('\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\/\d{1,2}')
        #ipRgeFind = re.findall(ipRangePrefix, target)
        #if ipRgeFind is not None or len(ipRgeFind) != 0:
        #    return True
        ipRangeDash = re.compile('\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}-\d{1,3}')
        ipRgeDashFind = re.findall(ipRangeDash,target)
        if ipRgeDashFind is not None or len(ipRgeDashFind) != 0:
            return True
        ipAddress = re.compile('\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}')
        ipFind = re.findall(ipAddress, target)
        if ipFind is not None and len(ipFind) != 0:
            return True

        return False

    @classmethod
    def getTarget(cls, target):
        """
        Determines whether the target provided is an IP Address or
        an IP Address in dash notation. Then creates a list
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
        ipRangeDash = re.compile('\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}-\d{1,3}')
        ipRgeDashFind = re.findall(ipRangeDash, target)
        # IP Address range seperated with a dash
        if ipRgeDashFind is not None and len(ipRgeDashFind) > 0:
            iplist = target[:target.index("-")].split(".")
            iplast = target[target.index("-") + 1:]
            if int(iplist[3]) < int(iplast):
                for lastoctet in xrange(int(iplist[3]), int(iplast) + 1):
                    yield target[:target.rindex(".") + 1] + str(lastoctet)
            else:
                yield target[:target.rindex(".") + 1] + str(iplist[3])
        # it's just an IP address at this point
        else:
            yield target


class VersionChecker(object):

    def __init__(self):
        super(VersionChecker, self).__init__()

    @classmethod
    def getModifiedFileInfo(cls, prefix, gitlocation, filelist):
        modifiedfiles = []
        try:
            for filename in filelist:
                md5local = VersionChecker.getMD5OfLocalFile(filename)
                md5remote = VersionChecker.getMD5OfRemoteFile(prefix + filename)
                if md5local != md5remote:
                    modifiedfiles.append(filename)
            if len(modifiedfiles) == 0:
                return 'All Automater files are up to date'
            else:
                return 'The following files require update: {files}.\nSee {gitlocation} to update these files'.\
                    format(files=', '.join(modifiedfiles), gitlocation=gitlocation)
        except:
            return 'There was an error while checking the version of the Automater files. Please see {gitlocation} ' \
                   'to determine if there is an issue with your local files'.format(gitlocation=gitlocation)

    @classmethod
    def getMD5OfLocalFile(cls, filename):
        md5offile = None
        with open(filename, 'rb') as f:
            md5offile = hashlib.md5(f.read()).hexdigest()
        return md5offile

    @classmethod
    def getMD5OfRemoteFile(cls, location, proxy=None):
        md5offile = None
        resp = requests.get(location, proxies=proxy, verify=False, timeout=5)
        md5offile = hashlib.md5(str(resp.content)).hexdigest()
        return md5offile
