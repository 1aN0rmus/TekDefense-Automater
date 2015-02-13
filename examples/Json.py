#!/usr/bin/python
"""
Example of Automater automation.
Usage:
python example/AutoAutomater.py <list of target domains URLS>

"""
import io
import sys
import csv

sys.path.append(".") #Path to TekDefense-Automater if you havent installed it already
from siteinfo import SiteFacade
from outputs import SiteDetailOutput

 
def run_automater(targets):
    """
    Runs Automator on list of target strings
    and returns results as json encoded string object.
    """
    targetlist = targets
    source = "allsources"
    sitefac = SiteFacade()
    try:
        sitefac.runSiteAutomation(1,None,
                              targetlist,
                              source,
                              False,"Automater/2.1",quiet=True)
        sites = sitefac.Sites
        if sites is not None:
            out = SiteDetailOutput(sites)
            return out.jsonOutput()
        return None
            # If you just want results as string just return output.getvalue()
    except Exception as e:
        print e.message
        return None
        
def main():
    print run_automater(sys.argv[1:])


if __name__ == "__main__":
    main()
