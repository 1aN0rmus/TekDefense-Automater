#!/usr/bin/python

import sys
from siteinfo import SiteFacade, Site
from utilities import Parser, IPWrapper
from outputs import SiteDetailOutput
from inputs import TargetFile
    
       
def main():
    sites = []
    parser = Parser('IP, URL, and Hash Passive Analysis tool')
    
    #if no target run and print help
    if parser.hasNoTarget():
        print '[!] No argument given.'
        parser.print_help() #need to fix this. Will later
        sys.exit()
        
    #user may only want to run against one source - allsources is the seed used to check if the user did not enter an s tag
    source = "allsources"
    if parser.hasSource():
        source = parser.Source
    
    #a file input capability provides a possibility of multiple lines of targets
    targetlist = []
    if parser.hasInputFile():
        for tgtstr in TargetFile.TargetList(parser.InputFile):
            if IPWrapper.isIPorIPList(tgtstr):
                for targ in IPWrapper.getTarget(tgtstr):
                    targetlist.append(targ)
            else:
                targetlist.append(tgtstr)              
    else: #one target or list of range of targets added on console
        target = parser.Target
        if IPWrapper.isIPorIPList(target):
            for targ in IPWrapper.getTarget(target):
                targetlist.append(targ)
        else:
            targetlist.append(target)
    
    sitefac = SiteFacade()
    sitefac.runSiteAutomation(parser.Delay,targetlist,source,parser.hasPost())
    sites = sitefac.Sites
    if sites is not None:
        SiteDetailOutput(sites).createOutputInfo(parser)        

if __name__ == "__main__":
    main()
