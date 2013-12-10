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
from xml.etree.ElementTree import ElementTree
import os

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
    def TargetList(self, filename):
        """
        Opens a file for reading.
        Returns each string from each line of a single or multi-line file.
        
        Argument(s):
        filename -- string based name of the file that will be retrieved and parsed.
        
        Return value(s):
        Iterator of string(s) found in a single or multi-line file.
        
        Restriction(s):
        This Method is tagged as a Class Method
        """
        try:
            target = ""
            with open(filename) as f:
                li = f.readlines()
                for i in li:
                    target = str(i).strip()
                    yield target
        except IOError:
            print "There was an error reading from the target input file."


class SitesFile(object):
    """
    SitesFile represents an XML Elementree object representing the
    program's configuration file. Returns XML Elementree object.
    
    Method(s):
    (Class Method) getXMLTree
    (Class Method) fileExists
    
    Instance variable(s):
    No instance variables.
    """    

    @classmethod
    def getXMLTree(self):
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
        try:
            with open("sites.xml") as f:
                sitetree = ElementTree()
                sitetree.parse(f)
                return sitetree
        except:
            print "There was an error reading from the sites input file.",
            print "Please check that the XML file is present and correctly formatted."

    @classmethod
    def fileExists(self):
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
        return os.path.exists("sites.xml") and os.path.isfile("sites.xml")
