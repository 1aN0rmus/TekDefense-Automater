#!/usr/bin/python
"""
Example of Automater automation as a Rest API.
Also provides a WEB console interface
Results returned as JSON string

The site names must match the site name attribute in the sites sites.xml file
Available sites as defined in the sites.xml file in this repository are:
  robtex
  fortinet_classify
  vtpDNSIP
  ipvoid
  virustotal
  threatexpert
  vxvault
  unshortme
  urlvoid
  vtpDNSDom
  malc0de
'allsources' queries all available sites

Usage:
python example/RestApi.py

HTTP Request format:
  http://127.0.0.1:8880/<site name>/<host name>

example HTTP grequest
GET /fortinet_classify/masterdiskeurope.com

{"masterdiskeurope.com": {"Fortinet URL": [{"Type": "hostname", "Result": "Malicious Websites"}]}}

Web Console Interface:
  http://127.0.0.1:8880
"""
import io
import sys
import csv
import argparse
from twisted.web.server import Site
from twisted.web.resource import Resource
from twisted.internet import reactor

sys.path.append(".") #Path to TekDefense-Automater if you havent installed it already
from siteinfo import SiteFacade
from outputs import SiteDetailOutput

class AutomaterRestApi(Resource):
    def __init__(self):
        self.isLeaf = False
        sitefac = SiteFacade()
        Resource.__init__(self)
        for site in sitefac.available_sites():
            #print site
            self.putChild(site, AutomaterRouter(site))
        self.putChild("allsources", AutomaterRouter("allsources"))
        
    def getChild(self, path, request):
        if path == '':
            return self
        return  Resource.getChild(self,path, request)

    def render_GET(self, request):
        with open ("examples/webroot/index.html", "r") as myfile:
            return "".join(myfile.readlines())
        
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
      #print targetlist
      #print self.site
      try:
          sitefac.runSiteAutomation(1,None,
                                    [targetlist],
                                    self.site,
                                    False,"Automater/2.1", quiet=False) 
          sites = sitefac.Sites
          if sites is not None:
              out = SiteDetailOutput(sites)
              return out.jsonOutput()
          else:
              return "{}"
      except Exception as e:
          print e.message
          return None
      
    def render_GET(self, request):
        return  self.run_automater()

def main():
    parser = argparse.ArgumentParser(description='Automator Web and Rest Interface')
    parser.add_argument('--port',default=8880, type=int,help='port to listen on')
    parser.add_argument('--bindip',default="127.0.0.1", help='Address to bind to')
    parser.add_argument('--ssl', help="Use SSL",action="store_true")
    parser.add_argument('--privkey', default='./privkey.pem', help="Path to private key")
    parser.add_argument('--cert', default='./cacert.pem', help="Path to public cert")
    args = parser.parse_args()
    root = AutomaterRestApi()
    factory = Site(root)
    if not args.ssl:
      reactor.listenTCP(args.port, factory, interface=args.bindip)
    else:
      from twisted.internet import ssl
      sslContext = ssl.DefaultOpenSSLContextFactory(
          args.privkey,
          args.cacert
      )
      reactor.listenSSL(
          args.port, 
          factory,
          contextFactory = sslContext,
          interface=args.bindip,
      )

    
    reactor.run()

if __name__ == "__main__":
    main()
