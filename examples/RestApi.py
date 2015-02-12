#!/usr/bin/python
"""
Example of Automater automation as a Rest API.
Results returned as JSON string
Usage:
python example/RestApi.py <list of target domains URLS>

HTTP Request format:
  http://127.0.0.1:8880/<site name>/<host name>

example HTTP grequest
GET /fortinet_classify/masterdiskeurope.com

{"masterdiskeurope.com": {"Fortinet URL": [{"Type": "hostname", "Result": "Malicious Websites"}]}}
"""
import io
import sys
import csv
from twisted.web.server import Site
from twisted.web.resource import Resource
from twisted.internet import reactor

sys.path.append(".") #Path to TekDefense-Automater if you havent installed it already
from siteinfo import SiteFacade,SiteError
from automater_outputs import SiteDetailOutput

class AutomaterRestApi(Resource):
    def __init__(self):
        sitefac = SiteFacade()
        Resource.__init__(self)
        for site in sitefac.available_sites():
            self.putChild(site, AutomaterRouter(site))
        self.putChild("allsources", AutomaterRouter(site))
 
class AutomaterRouter(Resource):
    def __init__(self, site):
        self.site = site
        Resource.__init__(self)
 
    def getChild(self, path, request):
        return AutomaterHandler(self.site, path)


class AutomaterHandler(Resource):
    def __init__(self, site,path):
        Resource.__init__(self)
        self.site = site
        self.target = path

    def run_automater(self):
      """
      Runs Automator on list of target strings
      and returns results as json encoded string object.
      """
      targetlist = self.target
      sitefac = SiteFacade()
      
      try:
          sitefac.runSiteAutomation(1,
                                    [targetlist],
                                    self.site,
                                    False,silent=True)
          sites = sitefac.Sites
          if sites is not None:
              out = SiteDetailOutput(sites)
              return out.jsonOutput()
          return "{}"
              # If you just want results as string just return output.getvalue()
      except SiteError as e:
          print e.message
          return None
      
    def render_GET(self, request):
        return  self.run_automater()

def main():
    root = AutomaterRestApi()
    factory = Site(root)
    reactor.listenTCP(8880, factory)
    reactor.run()

if __name__ == "__main__":
    main()
