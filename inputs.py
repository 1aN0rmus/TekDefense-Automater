"""
The inputs.py module represents some form of all inputs
to the Automater program to include target files, and
the standard config file - sites.xml. Any addition to
Automater that brings any other input requirement should
be programmed in this module.

Class(es):
TargetFile -- Provides a representation of a file containing target
              strings for Automater to utilize.
SitesFile -- Provides a representation of the sites.xml
             configuration file.
              
Function(s):
No global exportable functions are defined.

Exception(s):
No exceptions exported.
"""
import os
import hashlib
import requests
from outputs import SiteDetailOutput
from requests.exceptions import ConnectionError
from requests.exceptions import HTTPError
from xml.etree.ElementTree import ElementTree

__REMOTE_TEKD_XML_LOCATION__ = 'https://raw.githubusercontent.com/1aN0rmus/TekDefense-Automater/master/tekdefense.xml'
__TEKDEFENSEXML__ = 'tekdefense.xml'

class TargetFile(object):
    """
    TargetFile provides a Class Method to retrieve information from a file-
    based target when one is entered as the first parameter to the program.
    
    Public Method(s):
    (Class Method) TargetList
    
    Instance variable(s):
    No instance variables.
    """

    @classmethod
    def TargetList(self, filename, verbose):
        """
        Opens a file for reading.
        Returns each string from each line of a single or multi-line file.
        
        Argument(s):
        filename -- string based name of the file that will be retrieved and parsed.
        verbose -- boolean value representing whether output will be printed to stdout

        Return value(s):
        Iterator of string(s) found in a single or multi-line file.
        
        Restriction(s):
        This Method is tagged as a Class Method
        """
        try:
            target = ''
            with open(filename) as f:
                li = f.readlines()
                for i in li:
                    target = str(i).strip()
                    yield target
        except IOError:
            SiteDetailOutput.PrintStandardOutput('There was an error reading from the target input file.',
                                                 verbose=verbose)


class SitesFile(object):
    """
    SitesFile represents an XML Elementree object representing the
    program's configuration file. Returns XML Elementree object. The tekdefense.xml file is hosted on tekdefense.com's
    github and unless asked otherwise, will be checked to ensure the versions are correct. If they are not, the new
    tekdefense.xml will be downloaded and used by default. The local sites.xml is the user's capability to have local
    decisions made on top of the tekdefense.xml configuration file. Switches will be created to enable and disable
    these capabilities.
    
    Method(s):
    (Class Method) getXMLTree
    (Class Method) fileExists
    
    Instance variable(s):
    No instance variables.
    """

    @classmethod
    def updateTekDefenseXMLTree(cls, prox, verbose):
        if prox:
            proxy = {'https': prox, 'http': prox}
        else:
            proxy = None
        remotemd5 = None
        localmd5 = None
        localfileexists = False
        try:
            localmd5 = SitesFile.getMD5OfLocalFile(__TEKDEFENSEXML__)
            localfileexists = True
        except IOError:
            SiteDetailOutput.PrintStandardOutput('Local file {xmlfile} not located. Attempting download.'.
                                                 format(xmlfile=__TEKDEFENSEXML__), verbose=verbose)
        try:
            if localfileexists:
                remotemd5 = SitesFile.getMD5OfRemoteFile(__REMOTE_TEKD_XML_LOCATION__, proxy=proxy)
                if remotemd5 and remotemd5 != localmd5:
                    SiteDetailOutput.PrintStandardOutput('There is an updated remote {xmlfile} file at {url}. '
                                                         'Attempting download.'.
                                                         format(url=__REMOTE_TEKD_XML_LOCATION__,
                                                                xmlfile=__TEKDEFENSEXML__), verbose=verbose)
                    SitesFile.getRemoteFile(__REMOTE_TEKD_XML_LOCATION__, proxy)
            else:
                SitesFile.getRemoteFile(__REMOTE_TEKD_XML_LOCATION__, proxy)
        except ConnectionError as ce:
            try:
                SiteDetailOutput.PrintStandardOutput('Cannot connect to {url}. Server response is {resp} Server error '
                                                     'code is {code}'.format(url=__REMOTE_TEKD_XML_LOCATION__,
                                                                             resp=ce.message[0],
                                                                             code=ce.message[1][0]), verbose=verbose)
            except:
                SiteDetailOutput.PrintStandardOutput('Cannot connect to {url} to retreive the {xmlfile} for use.'.
                                                     format(url=__REMOTE_TEKD_XML_LOCATION__,
                                                            xmlfile=__TEKDEFENSEXML__), verbose=verbose)
        except HTTPError as he:
            try:
                SiteDetailOutput.PrintStandardOutput('Cannot connect to {url}. Server response is {resp}.'.
                                                     format(url=__REMOTE_TEKD_XML_LOCATION__, resp=he.message),
                                                     verbose=verbose)
            except:
                SiteDetailOutput.PrintStandardOutput('Cannot connect to {url} to retreive the {xmlfile} for use.'.
                                                     format(url=__REMOTE_TEKD_XML_LOCATION__,
                                                            xmlfile=__TEKDEFENSEXML__), verbose=verbose)

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

    @classmethod
    def getRemoteFile(cls, location, proxy=None):
        chunk_size = 65535
        resp = requests.get(location, proxies=proxy, verify=False, timeout=5)
        resp.raise_for_status()
        with open(__TEKDEFENSEXML__, 'wb') as fd:
            for chunk in resp.iter_content(chunk_size):
                fd.write(chunk)

    @classmethod
    def getXMLTree(cls, filename, verbose):
        """
        Opens a config file for reading.
        Returns XML Elementree object representing XML Config file.
        
        Argument(s):
        No arguments are required.
        
        Return value(s):
        ElementTree
        
        Restrictions:
        File must be named sites.xml and must be in same directory as caller.
        This Method is tagged as a Class Method
        """
        if SitesFile.fileExists(filename):
            try:
                with open(filename) as f:
                    sitetree = ElementTree()
                    sitetree.parse(f)
                    return sitetree
            except:
                SiteDetailOutput.PrintStandardOutput('There was an error reading from the {xmlfile} input file.\n'
                                                     'Please check that the {xmlfile} file is present and correctly '
                                                     'formatted.'.format(xmlfile=filename), verbose=verbose)
        else:
            SiteDetailOutput.PrintStandardOutput('No local {xmlfile} file present.'.format(xmlfile=filename),
                                                 verbose=verbose)
        return None

    @classmethod
    def fileExists(cls, filename):
        """
        Checks if a file exists. Returns boolean representing if file exists.
        
        Argument(s):
        No arguments are required.
        
        Return value(s):
        Boolean
        
        Restrictions:
        File must be named sites.xml and must be in same directory as caller.
        This Method is tagged as a Class Method
        """
        return os.path.exists(filename) and os.path.isfile(filename)
