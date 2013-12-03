import csv,siteinfo
from operator import attrgetter
from utilities import Parser

class SiteDetailOutput(object):
    
    def __init__(self,sitelist):
        self._listofsites = []
        self._listofsites = sitelist
        
    @property
    def ListOfSites(self):
        if self._listofsites is None or len(self._listofsites) == 0:
            return None
        return self._listofsites
    
    def createOutputInfo(self,parser):
        self.PrintToScreen()
        if parser.hasTextOutFile():
            self.PrintToTextFile(parser.TextOutFile)
        if parser.hasHTMLOutFile():
            self.PrintToHTMLFile(parser.HTMLOutFile)
        if parser.hasCSVOutSet():
            self.PrintToCSVFile(parser.CSVOutFile)
        
    def PrintToScreen(self):
            sites = sorted(self.ListOfSites, key=attrgetter('Target'))
            target = ""
            if sites is not None:
                for site in sites:
                    if not isinstance(site._regex,basestring): #this is a multisite
                        for index in range(len(site.RegEx)): #the regexs will ensure we have the exact number of lookups
                            siteimpprop = site.getImportantProperty(index)
                            if target != site.Target:
                                print "\n____________________     Results found for: " + site.Target + "     ____________________"
                                target = site.Target
                            if siteimpprop is None or len(siteimpprop)==0:
                                print "No results in the " + site.FriendlyName[index] + " category"
                            else:
                                if siteimpprop[index] is None or len(siteimpprop[index])==0:
                                    print "No results found for: " + site.ReportStringForResult[index]
                                else:
                                    #if it's just a string we don't want it output like a list
                                    if isinstance(siteimpprop[index], basestring):
                                        print "" + site.ReportStringForResult[index] + " " + str(siteimpprop[index])
                                    #must be a list since it failed the isinstance check on string
                                    else:
                                        for siteresult in siteimpprop[index]:
                                            print "" + site.ReportStringForResult[index] + " " + str(siteresult)
                    else:#this is a singlesite
                        siteimpprop = site.getImportantProperty(0)
                        if target != site.Target:
                            print "\n____________________     Results found for: " + site.Target + "     ____________________"
                            target = site.Target                        
                        if siteimpprop is None or len(siteimpprop)==0:
                            print "No results found in the " + site.FriendlyName
                        else:
                            #if it's just a string we don't want it output like a list
                            if isinstance(siteimpprop, basestring):
                                print "" + site.ReportStringForResult + " " + str(siteimpprop)
                            #must be a list since it failed the isinstance check on string
                            else:
                                for siteresult in siteimpprop:
                                    print "" + site.ReportStringForResult + " " + str(siteresult)
            else:
                pass

    def PrintToTextFile(self,textoutfile):
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
                            if siteimpprop[index] is None or len(siteimpprop[index])==0:
                                f.write("\nNo results found for: " + site.ReportStringForResult[index])
                            else:
                                #if it's just a string we don't want it to output like a list
                                if isinstance(siteimpprop[index], basestring):
                                    f.write("\n" + site.ReportStringForResult[index] + " " + str(siteimpprop[index]))
                                #must be a list since it failed the isinstance check on string
                                else:
                                    for siteresult in siteimpprop[index]:
                                        f.write("\n" + site.ReportStringForResult[index] + " " + str(siteresult))
                else:#this is a singlesite
                    siteimpprop = site.getImportantProperty(0)
                    if target != site.Target:
                        f.write("\n____________________     Results found for: " + site.Target + "     ____________________")
                        target = site.Target                    
                    if siteimpprop is None or len(siteimpprop)==0:
                        f.write("\nNo results found in the " + site.FriendlyName)
                    else:
                        #if it's just a string we don't want it output like a list
                        if isinstance(siteimpprop, basestring):
                            f.write("\n" + site.ReportStringForResult + " " + str(siteimpprop))
                        else:
                            for siteresult in siteimpprop:
                                f.write("\n" + site.ReportStringForResult + " " + str(siteresult))
        f.flush()        
        f.close()
        print "" + textoutfile + " Generated"
    
    
    def PrintToCSVFile(self,csvoutfile):
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
                                #if it's just a string we don't want it to output like a list
                                if isinstance(siteimpprop, basestring):
                                    tgt = site.Target
                                    typ = site.TargetType
                                    source = site.FriendlyName
                                    res = siteimpprop
                                    csvRW.writerow([tgt,typ,source,res])  
                                #must be a list since it failed the isinstance check on string
                                else:
                                    for siteresult in siteimpprop[index]:
                                        tgt = site.Target
                                        typ = site.TargetType
                                        source = site.FriendlyName[index]
                                        res = siteresult
                                        csvRW.writerow([tgt,typ,source,res])                                 
                else:#this is a singlesite
                    siteimpprop = site.getImportantProperty(0)
                    if siteimpprop is None or len(siteimpprop)==0:
                        tgt = site.Target
                        typ = site.TargetType
                        source = site.FriendlyName
                        res = "No results found"                    
                        csvRW.writerow([tgt,typ,source,res])
                    else:
                        #if it's just a string we don't want it output like a list
                        if isinstance(siteimpprop, basestring):
                            tgt = site.Target
                            typ = site.TargetType
                            source = site.FriendlyName
                            res = siteimpprop
                            csvRW.writerow([tgt,typ,source,res])                    
                        else:
                            for siteresult in siteimpprop:
                                tgt = site.Target
                                typ = site.TargetType
                                source = site.FriendlyName
                                res = siteresult
                                csvRW.writerow([tgt,typ,source,res])        
        f.flush()        
        f.close()
        print "" + csvoutfile + " Generated"
        
    def PrintToHTMLFile(self,htmloutfile):
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
                                #if it's just a string we don't want it to output like a list
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
                else:#this is a singlesite
                    siteimpprop = site.getImportantProperty(0)
                    if siteimpprop is None or len(siteimpprop)==0:
                        tgt = site.Target
                        typ = site.TargetType
                        source = site.FriendlyName
                        res = "No results found"                    
                        tableData = '<tr><td>' + tgt + '</td><td>' + typ + '</td><td>' + source + '</td><td>' + str(res) + '</td></tr>'
                        f.write(tableData)
                    else:
                        #if it's just a string we don't want it output like a list
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
        
    def getHTMLOpening(self):
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
            return '''    
                </table>
                <br>
                <br>
                <p>Created using Automater.py by @TekDefense <a href="http://www.tekdefense.com">http://www.tekdefense.com</a>; <a href="https://github.com/1aN0rmus/TekDefense">https://github.com/1aN0rmus/TekDefense</a></p>
                </body>
                </html>
                '''
