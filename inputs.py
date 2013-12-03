from xml.etree.ElementTree import ElementTree
import os

class TargetFile(object):
    
    @classmethod
    def FileName(self):
        return self._filename
    
    @classmethod
    def TargetList(self,filename):
        try:
            target=""
            with open(filename) as f:
                li = f.readlines()
                for i in li:
                    target = str(i).strip()
                    yield target
        except IOError:
            print "There was an error reading from the target input file."
    
class SitesFile(object):
    
    @classmethod
    def getXMLTree(self):
        try:        
            with open("sites.xml") as f:
                sitetree = ElementTree()
                sitetree.parse(f)
                return sitetree
        except:
            print "There was an error reading from the sites input file. Please check that the xml file is present and correctly formatted."
                
    @classmethod
    def fileExists(self):
        return os.path.exists("sites.xml") and os.path.isfile("sites.xml")
