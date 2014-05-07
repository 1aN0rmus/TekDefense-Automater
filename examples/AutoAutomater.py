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
from siteinfo import SiteFacade,SiteError
from outputs import SiteDetailOutput

 
def run_automater(targets):
    """
    Runs Automator on list of target strings
    and returns results as csvreader object.
    The csvreader implements the iterator protocol.
    Rows are returned as lists of strings
    example:
        rows = run_automater("masterdiskeurope.com")
        for row in rows:
            print row
    
    ['Target', 'Type', 'Source', 'Result']
    ['masterdiskeurope.com', 'hostname', 'Fortinet URL', 'Unclassified']
    ...

    """
    targetlist = targets
    source = "allsources"
    sitefac = SiteFacade()
    try:
        sitefac.runSiteAutomation(1,
                              targetlist,
                              source,
                              False,silent=True)
        sites = sitefac.Sites
        if sites is not None:
            output = io.BytesIO()
            SiteDetailOutput(sites).PrintToCSVFileHandle(output)
            return csv.reader(iter(output.getvalue().splitlines()))
            # If you just want results as string just return output.getvalue()
    except SiteError as e:
        print e.message
        return None
        
def main():
    run_automater(sys.argv[1:])

if __name__ == "__main__":
    main()
