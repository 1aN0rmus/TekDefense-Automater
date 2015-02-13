#!/usr/bin/python
"""
The Automater.py module defines the main() function for Automater.

Parameter Required is:
target -- List one IP Address (CIDR or dash notation accepted), URL or Hash
to query or pass the filename of a file containing IP Address info, URL or
Hash to query each separated by a newline.

Optional Parameters are:
-o, --output -- This option will output the results to a file.
-f, --cef -- This option will output the results to a CEF formatted file.
-w, --web -- This option will output the results to an HTML file.
-c, --csv -- This option will output the results to a CSV file.
-d, --delay -- Change the delay to the inputted seconds. Default is 2.
-s, --source -- Will only run the target against a specific source engine
to pull associated domains.  Options are defined in the name attribute of
the site element in the XML configuration file
--p --post -- Tells the program to post information to sites that allow posting.
By default the program will NOT post to sites that require a post.
--proxy -- This option will set a proxy (eg. proxy.example.com:8080)
-a --useragent -- Will set a user-agent string in the header of a web request.
is set by default to Automater/version#

Class(es):
No classes are defined in this module.

Function(s):
main -- Provides the instantiation point for Automater.

Exception(s):
No exceptions exported.
"""

import sys
from siteinfo import SiteFacade
from utilities import Parser, IPWrapper
from outputs import SiteDetailOutput
from inputs import TargetFile

def main():
    """
    Serves as the instantiation point to start Automater.

    Argument(s):
    No arguments are required.

    Return value(s):
    Nothing is returned from this Method.

    Restriction(s):
    The Method has no restrictions.
    """
    sites = []
    parser = Parser('IP, URL, and Hash Passive Analysis tool')

    # if no target run and print help
    if parser.hasNoTarget():
        print '[!] No argument given.'
        parser.print_help()  # need to fix this. Will later
        sys.exit()

    # user may only want to run against one source - allsources
    # is the seed used to check if the user did not enter an s tag
    source = "allsources"
    if parser.hasSource():
        source = parser.Source

    # a file input capability provides a possibility of
    # multiple lines of targets
    targetlist = []
    if parser.hasInputFile():
        for tgtstr in TargetFile.TargetList(parser.InputFile):
            if IPWrapper.isIPorIPList(tgtstr):
                for targ in IPWrapper.getTarget(tgtstr):
                    targetlist.append(targ)
            else:
                targetlist.append(tgtstr)
    else:  # one target or list of range of targets added on console
        target = parser.Target
        if IPWrapper.isIPorIPList(target):
            for targ in IPWrapper.getTarget(target):
                targetlist.append(targ)
        else:
            targetlist.append(target)

    sitefac = SiteFacade()
    sitefac.runSiteAutomation(parser.Delay, parser.Proxy, targetlist, \
                              source, parser.hasPost(), parser.UserAgent)
    sites = sitefac.Sites
    if sites is not None:
        SiteDetailOutput(sites).createOutputInfo(parser)

if __name__ == "__main__":
    main()
