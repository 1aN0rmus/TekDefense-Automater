"""
The outputs.py module represents some form of all outputs
from the Automater program to include all variation of
output files. Any addition to the Automater that brings
any other output requirement should be programmed in this module.

Class(es):
SiteDetailOutput -- Wrapper class around all functions that print output
from Automater, to include standard output and file system output.

Function(s):
No global exportable functions are defined.

Exception(s):
No exceptions exported.
"""

import csv
import socket
import re
from datetime import datetime
from operator import attrgetter

class SiteDetailOutput(object):
    """
    SiteDetailOutput provides the capability to output information
    to the screen, a text file, a comma-seperated value file, or
    a file formatted with html markup (readable by web browsers).

    Public Method(s):
    createOutputInfo

    Instance variable(s):
    _listofsites - list storing the list of site results stored.
    """

    def __init__(self,sitelist):
        """
        Class constructor. Stores the incoming list of sites in the _listofsites list.

        Argument(s):
        sitelist -- list containing site result information to be printed.

        Return value(s):
        Nothing is returned from this Method.
        """
        self._listofsites = []
        self._listofsites = sitelist

    @property
    def ListOfSites(self):
        """
        Checks instance variable _listofsites for content.
        Returns _listofsites if it has content or None if it does not.

        Argument(s):
        No arguments are required.

        Return value(s):
        _listofsites -- list containing list of site results if variable contains data.
        None -- if _listofsites is empty or not assigned.

        Restriction(s):
        This Method is tagged as a Property.
        """
        if self._listofsites is None or len(self._listofsites) == 0:
            return None
        return self._listofsites

    def createOutputInfo(self,parser):
        """
        Checks parser information calls correct print methods based on parser requirements.
        Returns nothing.

        Argument(s):
        parser -- Parser object storing program input parameters used when program was run.

        Return value(s):
        Nothing is returned from this Method.

        Restriction(s):
        The Method has no restrictions.
        """
        self.PrintToScreen(parser.hasBotOut())
        if parser.hasCEFOutFile():
            self.PrintToCEFFile(parser.CEFOutFile)
        if parser.hasTextOutFile():
            self.PrintToTextFile(parser.TextOutFile)
        if parser.hasHTMLOutFile():
            self.PrintToHTMLFile(parser.HTMLOutFile)
        if parser.hasCSVOutSet():
            self.PrintToCSVFile(parser.CSVOutFile)

    def PrintToScreen(self, printinbotformat):
        """
        Calls correct function to ensure site information is printed to the user's standard output correctly.
        Returns nothing.

        Argument(s):
        printinbotformat -- True or False argument representing minimized output. True if minimized requested.

        Return value(s):
        Nothing is returned from this Method.

        Restriction(s):
        The Method has no restrictions.
        """

        if printinbotformat:
            self.PrintToScreenBot()
        else:
            self.PrintToScreenNormal()

    def PrintToScreenBot(self):
        """
        Formats site information minimized and prints it to the user's standard output.
        Returns nothing.

        Argument(s):
        No arguments are required.

        Return value(s):
        Nothing is returned from this Method.

        Restriction(s):
        The Method has no restrictions.
        """
        sites = sorted(self.ListOfSites, key=attrgetter('Target'))
        target = ""
        if sites is not None:
            for site in sites:
                if not isinstance(site._regex,basestring):  # this is a multisite
                    for index in range(len(site.RegEx)):  # the regexs will ensure we have the exact number of lookups
                        siteimpprop = site.getImportantProperty(index)
                        if target != site.Target:
                            print "\n**_ Results found for: " + site.Target + " _**"
                            target = site.Target
                            # Check for them ALL to be None or 0 length
                        sourceurlhasnoreturn = True
                        for answer in siteimpprop:
                            if answer is not None:
                                if len(answer) > 0:
                                    sourceurlhasnoreturn = False

                        if sourceurlhasnoreturn:
                            print '[+] ' + site.SourceURL + ' No results found'
                            break
                        else:
                            if siteimpprop is None or len(siteimpprop) == 0:
                                print "No results in the " + site.FriendlyName[index] + " category"
                            else:
                                if siteimpprop[index] is None or len(siteimpprop[index]) == 0:
                                    print site.ReportStringForResult[index] + ' No results found'
                                else:
                                    laststring = ""
                                    # if it's just a string we don't want it output like a list
                                    if isinstance(siteimpprop[index], basestring):
                                        if "" + site.ReportStringForResult[index] + " " + str(siteimpprop) != laststring:
                                            print "" + site.ReportStringForResult[index] + " " + str(siteimpprop).replace('www.', 'www[.]').replace('http', 'hxxp')
                                            laststring = "" + site.ReportStringForResult[index] + " " + str(siteimpprop)
                                    # must be a list since it failed the isinstance check on string
                                    else:
                                        laststring = ""
                                        for siteresult in siteimpprop[index]:
                                            if "" + site.ReportStringForResult[index] + " " + str(siteresult) != laststring:
                                                print "" + site.ReportStringForResult[index] + " " + str(siteresult).replace('www.', 'www[.]').replace('http', 'hxxp')
                                                laststring = "" + site.ReportStringForResult[index] + " " + str(siteresult)
                else:#this is a singlesite
                    siteimpprop = site.getImportantProperty(0)
                    if target != site.Target:
                        print "\n**_ Results found for: " + site.Target + " _**"
                        target = site.Target
                    if siteimpprop is None or len(siteimpprop)==0:
                        print '[+] ' + site.FriendlyName + ' No results found'
                    else:
                        laststring = ""
                        #if it's just a string we don't want it output like a list
                        if isinstance(siteimpprop, basestring):
                            if "" + site.ReportStringForResult + " " + str(siteimpprop) != laststring:
                                print "" + site.ReportStringForResult + " " + str(siteimpprop).replace('www.', 'www[.]').replace('http', 'hxxp')
                                laststring = "" + site.ReportStringForResult + " " + str(siteimpprop)
                        #must be a list since it failed the isinstance check on string
                        else:
                            laststring = ""
                            for siteresult in siteimpprop:
                                if "" + site.ReportStringForResult + " " + str(siteresult) != laststring:
                                    print "" + site.ReportStringForResult + " " + str(siteresult).replace('www.', 'www[.]').replace('http', 'hxxp')
                                    laststring = "" + site.ReportStringForResult + " " + str(siteresult)
        else:
            pass

    def PrintToScreenNormal(self):
        """
        Formats site information correctly and prints it to the user's standard output.
        Returns nothing.

        Argument(s):
        No arguments are required.

        Return value(s):
        Nothing is returned from this Method.

        Restriction(s):
        The Method has no restrictions.
        """
        sites = sorted(self.ListOfSites, key=attrgetter('Target'))
        target = ""
        if sites is not None:
            for site in sites:
                if not isinstance(site._regex, basestring):  # this is a multisite
                    for index in range(len(site.RegEx)):  # the regexs will ensure we have the exact number of lookups
                        siteimpprop = site.getImportantProperty(index)
                        if target != site.Target:
                            print "\n____________________     Results found for: " + site.Target + "     ____________________"
                            target = site.Target
                        if siteimpprop is None or len(siteimpprop) == 0:
                            print "No results in the " + site.FriendlyName[index] + " category"
                        else:
                            if siteimpprop[index] is None or len(siteimpprop[index]) == 0:
                                print site.ReportStringForResult[index] + ' No results found'
                            else:
                                laststring = ""
                                # if it's just a string we don't want it output like a list
                                if isinstance(siteimpprop[index], basestring):
                                    if "" + site.ReportStringForResult[index] + " " + str(siteimpprop) != laststring:
                                        print "" + site.ReportStringForResult[index] + " " + str(siteimpprop).replace('www.', 'www[.]').replace('http', 'hxxp')
                                        laststring = "" + site.ReportStringForResult[index] + " " + str(siteimpprop)
                                # must be a list since it failed the isinstance check on string
                                else:
                                    laststring = ""
                                    for siteresult in siteimpprop[index]:
                                        if "" + site.ReportStringForResult[index] + " " + str(siteresult) != laststring:
                                            print "" + site.ReportStringForResult[index] + " " + str(siteresult).replace('www.', 'www[.]').replace('http', 'hxxp')
                                            laststring = "" + site.ReportStringForResult[index] + " " + str(siteresult)
                else:  # this is a singlesite
                    siteimpprop = site.getImportantProperty(0)
                    if target != site.Target:
                        print "\n____________________     Results found for: " + site.Target + "     ____________________"
                        target = site.Target
                    if siteimpprop is None or len(siteimpprop) == 0:
                        print "No results found in the " + site.FriendlyName
                    else:
                        laststring = ""
                        # if it's just a string we don't want it output like a list
                        if isinstance(siteimpprop, basestring):
                            if "" + site.ReportStringForResult + " " + str(siteimpprop) != laststring:
                                print "" + site.ReportStringForResult + " " + str(siteimpprop).replace('www.', 'www[.]').replace('http', 'hxxp')
                                laststring = "" + site.ReportStringForResult + " " + str(siteimpprop)
                        # must be a list since it failed the isinstance check on string
                        else:
                            laststring = ""
                            for siteresult in siteimpprop:
                                if "" + site.ReportStringForResult + " " + str(siteresult) != laststring:
                                    print "" + site.ReportStringForResult + " " + str(siteresult).replace('www.', 'www[.]').replace('http', 'hxxp')
                                    laststring = "" + site.ReportStringForResult + " " + str(siteresult)
        else:
            pass

    def PrintToCEFFile(self,cefoutfile):
        """
        Formats site information correctly and prints it to an output file in CEF format.
        CEF format specification from http://mita-tac.wikispaces.com/file/view/CEF+White+Paper+071709.pdf
        "Jan 18 11:07:53 host message"
        where message:
        "CEF:Version|Device Vendor|Device Product|Device Version|Signature ID|Name|Severity|Extension"
        Returns nothing.

        Argument(s):
        cefoutfile -- A string representation of a file that will store the output.

        Return value(s):
        Nothing is returned from this Method.

        Restriction(s):
        The Method has no restrictions.
        """
        sites = sorted(self.ListOfSites, key=attrgetter('Target'))
        curr_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        hostname = socket.gethostname()
        prefix = ' '.join([curr_date,hostname])
        cef_version = "CEF:Version1.1"
        cef_deviceVendor = "TekDefense"
        cef_deviceProduct = "Automater"
        cef_deviceVersion = "2.1"
        cef_SignatureID = "0"
        cef_Severity = "2"
        cef_Extension = " "
        cef_fields = [cef_version,cef_deviceVendor,cef_deviceProduct,cef_deviceVersion, \
                       cef_SignatureID, cef_Severity, cef_Extension]
        pattern = "^\[\+\]\s+"
        target = ""
        print '\n[+] Generating CEF output: ' + cefoutfile
        f = open(cefoutfile, "wb")
        csv.register_dialect('escaped', delimiter='|', escapechar='\\', doublequote=False, quoting=csv.QUOTE_NONE)
        cefRW = csv.writer(f, 'escaped')
        # cefRW.writerow(['Target', 'Type', 'Source', 'Result'])
        if sites is not None:
            for site in sites:
                if not isinstance(site._regex,basestring):  # this is a multisite:
                    for index in range(len(site.RegEx)):  # the regexs will ensure we have the exact number of lookups
                        siteimpprop = site.getImportantProperty(index)
                        if siteimpprop is None or len(siteimpprop)==0:
                            tgt = site.Target
                            typ = site.TargetType
                            source = site.FriendlyName[index]
                            res = "No results found"
                            cefRW.writerow([prefix] + cef_fields[:5] + \
                                           ["["+",".join(["tgt="+tgt,"typ="+typ,"src="+source,"res="+res])+"] "] + \
                                           [1] + [tgt])
                        else:
                            if siteimpprop[index] is None or len(siteimpprop[index])==0:
                                tgt = site.Target
                                typ = site.TargetType
                                source = site.FriendlyName[index]
                                res = "No results found"
                                cefRW.writerow([prefix] + cef_fields[:5] + \
                                           ["["+",".join(["tgt="+tgt,"typ="+typ,"src="+source,"res="+res])+"] "] + \
                                           [1] + [tgt])
                            else:
                                laststring = ""
                                # if it's just a string we don't want it to output like a list
                                if isinstance(siteimpprop, basestring):
                                    tgt = site.Target
                                    typ = site.TargetType
                                    source = site.FriendlyName
                                    res = siteimpprop
                                    if "" + tgt + typ + source + res != laststring:
                                        cefRW.writerow([prefix] + cef_fields[:5] + \
                                          ["["+",".join(["tgt="+tgt,"typ="+typ,"src="+source,"res="+res])+"] " + \
                                               re.sub(pattern,"",site.ReportStringForResult[index])+ str(siteimpprop)] + \
                                           [cef_Severity] + [tgt])
                                        laststring = "" + tgt + typ + source + res
                                # must be a list since it failed the isinstance check on string
                                else:
                                    laststring = ""
                                    for siteresult in siteimpprop[index]:
                                        tgt = site.Target
                                        typ = site.TargetType
                                        source = site.FriendlyName[index]
                                        res =   siteresult
                                        if "" + tgt + typ + source + str(res) != laststring:
                                            cefRW.writerow([prefix] + cef_fields[:5] + ["["+",".join(["tgt="+tgt,"typ="+typ,"src="+source,"res="+str(res)])+"] " + re.sub(pattern, "", site.ReportStringForResult[index]) + str(siteresult)] + [cef_Severity] + [tgt])
                                            laststring = "" + tgt + typ + source + str(res)
                else: # this is a singlesite
                    siteimpprop = site.getImportantProperty(0)
                    if siteimpprop is None or len(siteimpprop)==0:
                        tgt = site.Target
                        typ = site.TargetType
                        source = site.FriendlyName
                        res = "No results found"
                        cefRW.writerow([prefix] + cef_fields[:5] + \
                                          ["["+",".join(["tgt="+tgt,"typ="+typ,"src="+source,"res="+res])+"] "] + \
                                           [1] + [tgt])
                    else:
                        laststring = ""
                        # if it's just a string we don't want it output like a list
                        if isinstance(siteimpprop, basestring):
                            tgt = site.Target
                            typ = site.TargetType
                            source = site.FriendlyName
                            res = siteimpprop
                            if "" + tgt + typ + source + res != laststring:
                                cefRW.writerow([prefix] + cef_fields[:5] + \
                                          ["["+",".join(["tgt="+tgt,"typ="+typ,"src="+source,"res="+res])+"] " + \
                                               re.sub(pattern,"",site.ReportStringForResult)+ str(siteimpprop)] + \
                                           [cef_Severity] + [tgt])
                                laststring = "" + tgt + typ + source + res
                        else:
                            laststring = ""
                            for siteresult in siteimpprop:
                                tgt = site.Target
                                typ = site.TargetType
                                source = site.FriendlyName
                                res = siteresult
                                if "" + tgt + typ + source + str(res) != laststring:
                                    cefRW.writerow([prefix] + cef_fields[:5] + \
                                         ["["+",".join(["tgt="+tgt,"typ="+typ,"src="+source,"res="+str(res)])+"] " + \
                                               re.sub(pattern,"",site.ReportStringForResult)+ str(siteimpprop)] + \
                                           [cef_Severity] + [tgt])
                                    laststring = "" + tgt + typ + source + str(res)

        f.flush()
        f.close()
        print "" + cefoutfile + " Generated"


    def PrintToTextFile(self,textoutfile):
        """
        Formats site information correctly and prints it to an output file in text format.
        Returns nothing.

        Argument(s):
        textoutfile -- A string representation of a file that will store the output.

        Return value(s):
        Nothing is returned from this Method.

        Restriction(s):
        The Method has no restrictions.
        """
        sites = sorted(self.ListOfSites, key=attrgetter('Target'))
        target = ""
        print "\n[+] Generating text output: " + textoutfile
        f = open(textoutfile, "w")
        if sites is not None:
            for site in sites:
                if not isinstance(site._regex,basestring): #this is a multisite
                    for index in range(len(site.RegEx)): #the regexs will ensure we have the exact number of lookups
                        siteimpprop = site.getImportantProperty(index)
                        if target != site.Target:
                            f.write("\n____________________     Results found for: " + site.Target + "     ____________________")
                            target = site.Target
                        if siteimpprop is None or len(siteimpprop)==0:
                            f.write("\nNo results in the " + site.FriendlyName[index] + " category")
                        else:
                            if siteimpprop[index] is None or len(siteimpprop[index]) == 0:
                                f.write('\n' + site.ReportStringForResult[index] + ' No results found')
                            else:
                                laststring = ""
                                #if it's just a string we don't want it to output like a list
                                if isinstance(siteimpprop[index], basestring):
                                    if "" + site.ReportStringForResult[index] + " " + str(siteimpprop) != laststring:
                                        f.write("\n" + site.ReportStringForResult[index] + " " + str(siteimpprop))
                                        laststring = "" + site.ReportStringForResult[index] + " " + str(siteimpprop)
                                #must be a list since it failed the isinstance check on string
                                else:
                                    laststring = ""
                                    for siteresult in siteimpprop[index]:
                                        if "" + site.ReportStringForResult[index] + " " + str(siteresult) != laststring:
                                            f.write("\n" + site.ReportStringForResult[index] + " " + str(siteresult))
                                            laststring = "" + site.ReportStringForResult[index] + " " + str(siteresult)
                else:#this is a singlesite
                    siteimpprop = site.getImportantProperty(0)
                    if target != site.Target:
                        f.write("\n____________________     Results found for: " + site.Target + "     ____________________")
                        target = site.Target
                    if siteimpprop is None or len(siteimpprop)==0:
                        f.write("\nNo results found in the " + site.FriendlyName)
                    else:
                        laststring = ""
                        #if it's just a string we don't want it output like a list
                        if isinstance(siteimpprop, basestring):
                            if "" + site.ReportStringForResult + " " + str(siteimpprop) != laststring:
                                f.write("\n" + site.ReportStringForResult + " " + str(siteimpprop))
                                laststring = "" + site.ReportStringForResult + " " + str(siteimpprop)
                        else:
                            laststring = ""
                            for siteresult in siteimpprop:
                                if "" + site.ReportStringForResult + " " + str(siteresult) != laststring:
                                    f.write("\n" + site.ReportStringForResult + " " + str(siteresult))
                                    laststring = "" + site.ReportStringForResult + " " + str(siteresult)
        f.flush()
        f.close()
        print "" + textoutfile + " Generated"

    def PrintToCSVFile(self,csvoutfile):
        """
        Formats site information correctly and prints it to an output file with comma-seperators.
        Returns nothing.

        Argument(s):
        csvoutfile -- A string representation of a file that will store the output.

        Return value(s):
        Nothing is returned from this Method.

        Restriction(s):
        The Method has no restrictions.
        """
        sites = sorted(self.ListOfSites, key=attrgetter('Target'))
        target = ""
        print '\n[+] Generating CSV output: ' + csvoutfile
        f = open(csvoutfile, "wb")
        csvRW = csv.writer(f, quoting=csv.QUOTE_ALL)
        csvRW.writerow(['Target', 'Type', 'Source', 'Result'])
        if sites is not None:
            for site in sites:
                if not isinstance(site._regex,basestring): #this is a multisite:
                    for index in range(len(site.RegEx)): #the regexs will ensure we have the exact number of lookups
                        siteimpprop = site.getImportantProperty(index)
                        if siteimpprop is None or len(siteimpprop)==0:
                            tgt = site.Target
                            typ = site.TargetType
                            source = site.FriendlyName[index]
                            res = "No results found"
                            csvRW.writerow([tgt,typ,source,res])
                        else:
                            if siteimpprop[index] is None or len(siteimpprop[index])==0:
                                tgt = site.Target
                                typ = site.TargetType
                                source = site.FriendlyName[index]
                                res = "No results found"
                                csvRW.writerow([tgt,typ,source,res])
                            else:
                                laststring = ""
                                #if it's just a string we don't want it to output like a list
                                if isinstance(siteimpprop, basestring):
                                    tgt = site.Target
                                    typ = site.TargetType
                                    source = site.FriendlyName
                                    res = siteimpprop
                                    if "" + tgt + typ + source + res != laststring:
                                        csvRW.writerow([tgt,typ,source,res])
                                        laststring = "" + tgt + typ + source + res
                                #must be a list since it failed the isinstance check on string
                                else:
                                    laststring = ""
                                    for siteresult in siteimpprop[index]:
                                        tgt = site.Target
                                        typ = site.TargetType
                                        source = site.FriendlyName[index]
                                        res = siteresult
                                        if "" + tgt + typ + source + str(res) != laststring:
                                            csvRW.writerow([tgt,typ,source,res])
                                            laststring = "" + tgt + typ + source + str(res)
                else:#this is a singlesite
                    siteimpprop = site.getImportantProperty(0)
                    if siteimpprop is None or len(siteimpprop)==0:
                        tgt = site.Target
                        typ = site.TargetType
                        source = site.FriendlyName
                        res = "No results found"
                        csvRW.writerow([tgt,typ,source,res])
                    else:
                        laststring = ""
                        #if it's just a string we don't want it output like a list
                        if isinstance(siteimpprop, basestring):
                            tgt = site.Target
                            typ = site.TargetType
                            source = site.FriendlyName
                            res = siteimpprop
                            if "" + tgt + typ + source + res != laststring:
                                csvRW.writerow([tgt,typ,source,res])
                                laststring = "" + tgt + typ + source + res
                        else:
                            laststring = ""
                            for siteresult in siteimpprop:
                                tgt = site.Target
                                typ = site.TargetType
                                source = site.FriendlyName
                                res = siteresult
                                if "" + tgt + typ + source + str(res) != laststring:
                                    csvRW.writerow([tgt,typ,source,res])
                                    laststring = "" + tgt + typ + source + str(res)

        f.flush()
        f.close()
        print "" + csvoutfile + " Generated"

    def PrintToHTMLFile(self, htmloutfile):
        """
        Formats site information correctly and prints it to an output file using HTML markup.
        Returns nothing.

        Argument(s):
        htmloutfile -- A string representation of a file that will store the output.

        Return value(s):
        Nothing is returned from this Method.

        Restriction(s):
        The Method has no restrictions.
        """
        sites = sorted(self.ListOfSites, key=attrgetter('Target'))
        target = ""
        print '\n[+] Generating HTML output: ' + htmloutfile
        f = open(htmloutfile, "w")
        f.write(self.getHTMLOpening())
        if sites is not None:
            for site in sites:
                if not isinstance(site._regex,basestring): #this is a multisite:
                    for index in range(len(site.RegEx)): #the regexs will ensure we have the exact number of lookups
                        siteimpprop = site.getImportantProperty(index)
                        if siteimpprop is None or len(siteimpprop)==0:
                            tgt = site.Target
                            typ = site.TargetType
                            source = site.FriendlyName[index]
                            res = "No results found"
                            tableData = '<tr><td>' + tgt + '</td><td>' + typ + '</td><td>' + source + '</td><td>' + str(res) + '</td></tr>'
                            f.write(tableData)
                        else:
                            if siteimpprop[index] is None or len(siteimpprop[index])==0:
                                tgt = site.Target
                                typ = site.TargetType
                                source = site.FriendlyName[index]
                                res = "No results found"
                                tableData = '<tr><td>' + tgt + '</td><td>' + typ + '</td><td>' + source + '</td><td>' + str(res) + '</td></tr>'
                                f.write(tableData)
                            else:
                                # if it's just a string we don't want it to output like a list
                                if isinstance(siteimpprop, basestring):
                                    tgt = site.Target
                                    typ = site.TargetType
                                    source = site.FriendlyName
                                    res = siteimpprop
                                    tableData = '<tr><td>' + tgt + '</td><td>' + typ + '</td><td>' + source + '</td><td>' + str(res) + '</td></tr>'
                                    f.write(tableData)
                                else:
                                    for siteresult in siteimpprop[index]:
                                        tgt = site.Target
                                        typ = site.TargetType
                                        source = site.FriendlyName[index]
                                        res = siteresult
                                        tableData = '<tr><td>' + tgt + '</td><td>' + typ + '</td><td>' + source + '</td><td>' + str(res) + '</td></tr>'
                                        f.write(tableData)
                else:  # this is a singlesite
                    siteimpprop = site.getImportantProperty(0)
                    if siteimpprop is None or len(siteimpprop)==0:
                        tgt = site.Target
                        typ = site.TargetType
                        source = site.FriendlyName
                        res = "No results found"
                        tableData = '<tr><td>' + tgt + '</td><td>' + typ + '</td><td>' + source + '</td><td>' + str(res) + '</td></tr>'
                        f.write(tableData)
                    else:
                        # if it's just a string we don't want it output like a list
                        if isinstance(siteimpprop, basestring):
                            tgt = site.Target
                            typ = site.TargetType
                            source = site.FriendlyName
                            res = siteimpprop
                            tableData = '<tr><td>' + tgt + '</td><td>' + typ + '</td><td>' + source + '</td><td>' + str(res) + '</td></tr>'
                            f.write(tableData)
                        else:
                            for siteresult in siteimpprop:
                                tgt = site.Target
                                typ = site.TargetType
                                source = site.FriendlyName
                                res = siteresult
                                tableData = '<tr><td>' + tgt + '</td><td>' + typ + '</td><td>' + source + '</td><td>' + str(res) + '</td></tr>'
                                f.write(tableData)
        f.write(self.getHTMLClosing())
        f.flush()
        f.close()
        print "" + htmloutfile + " Generated"

    @classmethod
    def PrintStandardOutput(cls, strout, *args, **kwargs):
        if 'verbose' in kwargs.keys():
            if kwargs['verbose'] is True:
                print strout
            else:
                return
        else:
            print strout

    def getHTMLOpening(self):
        """
        Creates HTML markup to provide correct formatting for initial HTML file requirements.
        Returns string that contains opening HTML markup information for HTML output file.

        Argument(s):
        No arguments required.

        Return value(s):
        string.

        Restriction(s):
        The Method has no restrictions.
        """
        return '''<style type="text/css">
                        #table-3 {
                            border: 1px solid #DFDFDF;
                            background-color: #F9F9F9;
                            width: 100%;
                            -moz-border-radius: 3px;
                            -webkit-border-radius: 3px;
                            border-radius: 3px;
                            font-family: Arial,"Bitstream Vera Sans",Helvetica,Verdana,sans-serif;
                            color: #333;
                        }
                        #table-3 td, #table-3 th {
                            border-top-color: white;
                            border-bottom: 1px solid #DFDFDF;
                            color: #555;
                        }
                        #table-3 th {
                            text-shadow: rgba(255, 255, 255, 0.796875) 0px 1px 0px;
                            font-family: Georgia,"Times New Roman","Bitstream Charter",Times,serif;
                            font-weight: normal;
                            padding: 7px 7px 8px;
                            text-align: left;
                            line-height: 1.3em;
                            font-size: 14px;
                        }
                        #table-3 td {
                            font-size: 12px;
                            padding: 4px 7px 2px;
                            vertical-align: top;
                        }res
                        h1 {
                            text-shadow: rgba(255, 255, 255, 0.796875) 0px 1px 0px;
                            font-family: Georgia,"Times New Roman","Bitstream Charter",Times,serif;
                            font-weight: normal;
                            padding: 7px 7px 8px;
                            text-align: Center;
                            line-height: 1.3em;
                            font-size: 40px;
                        }
                        h2 {
                            text-shadow: rgba(255, 255, 255, 0.796875) 0px 1px 0px;
                            font-family: Georgia,"Times New Roman","Bitstream Charter",Times,serif;
                            font-weight: normal;
                            padding: 7px 7px 8px;
                            text-align: left;
                            line-height: 1.3em;
                            font-size: 16px;
                        }
                        h4 {
                            text-shadow: rgba(255, 255, 255, 0.796875) 0px 1px 0px;
                            font-family: Georgia,"Times New Roman","Bitstream Charter",Times,serif;
                            font-weight: normal;
                            padding: 7px 7px 8px;
                            text-align: left;
                            line-height: 1.3em;
                            font-size: 10px;
                        }
                        </style>
                        <html>
                        <body>
                        <title> Automater Results </title>
                        <h1> Automater Results </h1>
                        <table id="table-3">
                        <tr>
                        <th>Target</th>
                        <th>Type</th>
                        <th>Source</th>
                        <th>Result</th>
                        </tr>
                        '''

    def getHTMLClosing(self):
        """
        Creates HTML markup to provide correct formatting for closing HTML file requirements.
        Returns string that contains closing HTML markup information for HTML output file.

        Argument(s):
        No arguments required.

        Return value(s):
        string.

        Restriction(s):
        The Method has no restrictions.
        """
        return '''
            </table>
            <br>
            <br>
            <p>Created using Automater.py by @TekDefense <a href="http://www.tekdefense.com">http://www.tekdefense.com</a>; <a href="https://github.com/1aN0rmus/TekDefense">https://github.com/1aN0rmus/TekDefense</a></p>
            </body>
            </html>
            '''
