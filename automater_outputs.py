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
import json
from operator import attrgetter


class NormalizedSourceOutput(object):
    def __init__(self,source,source_type,results):
        self._source = source
        self._source_type = source_type
        self._results = results

    @property
    def Source(self):
        return self._source

    @property
    def SourceType(self):
        return self._source_type
    
    @property
    def Results(self):
        return self._results
    
    def pprint(self):
        print "\tSource: %s" % self._source
        print "\tSource Type: %s" % self._source_type
        print "\tResults:"
        for i in self._results:
            print "\t\t%s" % str(i)

    def __str__(self):
        return \
""" 
    Source: %(source)s
    Source Type: %(source_type)s
    Results:
        %(results)s
"""     % {'source':self._source,
           'source_type':self._source_type,
           'results':"\n".join(map((lambda (s):"        "+str(s)),self._results))}
  
    __repr__ = __str__

class NormalizedSiteOutput(object):
    def __init__(self,target,target_type,sources):
        self._target = target
        self._target_type = target_type
        self._sources = sources

    @property
    def Target(self):
        return self._target
    
    @property
    def TargetType(self):
        return self._target_type
    
    @property
    def Sources(self):
        return self._sources
        
    def __str__(self):
        return \
"""
Target: %(target)s
Target Type: %(target_type)s
Sources:
        %(sources)s
"""      % {'target':self._target,
            'target_type':self._target_type,
            'sources':"\n".join(map((lambda (s):"        "+str(s)),self._sources))}
  
    __repr__ = __str__


    
class PrettySiteOutput(NormalizedSiteOutput):
    """
    Custom outputr formatter provides console style output of source output.
    
    Simply override the __str__ method to implement behavior. To use pass this class
    as the source_output_class argument to the SiteDetailOutput class
    """
    
    HeaderPrinted = False
    
    def __str__(self):
        output = []
        
        output.append(self.Sources)
        #print self.Sources
        return "\n".join(str(self.Sources))
      
    __repr__ = __str__
    
    
class PrettySourceOutput(NormalizedSourceOutput):
    """
    Custom outputr formatter provides console style output of source output.
    
    Simply override the __str__ method to implement behavior. To use pass this class
    as the source_output_class argument to the SiteDetailOutput class
    """
    
    def __str__(self):
        return \
        "\n".join(map((lambda (s):"[+] %s %s"%(self.Source,str(s))),self._results))
  
    __repr__ = __str__

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
    
    def __init__(self,sitelist,site_output_class=NormalizedSiteOutput,source_output_class=NormalizedSourceOutput):
        """
        Class constructor. Stores the incoming list of sites in the _listofsites list.
        
        Argument(s):
        sitelist -- list containing site result information to be printed.
        
        Return value(s):
        Nothing is returned from this Method.
        """
        self._list_of_sites = []
        self._list_of_sites = sitelist
        self._site_output_class = site_output_class
        self._source_output_class = source_output_class
        self._normalized_output = self.normalize_output()
        
    @property
    def list_of_sites(self):
        """
        Argument(s):
        No arguments are required.
        
        Return value(s):
        _list_of_sites -- list containing list of site results if variable contains data.
        None -- if _list_of_sites is empty or not assigned.
        
        Restriction(s):
        This Method is tagged as a Property.
        """
        if self._list_of_sites is None or len(self._list_of_sites) == 0:
            return None
        return self._list_of_sites

    @property
    def normalized_output(self):
        """
        Argument(s): 
        None
        
        Return value(s):
        List of NormalizedSiteOutput objects 
        """
        return self._normalized_output

    def normalize_output(self):
        """
        Normalizes list site results in to a structured consistent form.
        List of NormalizedSiteOutput:
            target: string : name of target
            target_type: string : type of target (eg. hostname,URL,MD5)
            sources: List of NormalizedSourceOutput : 
                [NormalizedSourceOutput:
                   source: string : Source of results
                   source_type: string : Type of results  
                   results: List of strings : Result data]
                
        Argument(s):
        None
        
        Return value(s):
        List of NormalizedSiteOutput
        
        Restriction(s):
        The Method has no restrictions.
        """
        
        outputs = []
        sites = sorted(self.list_of_sites, key=attrgetter('Target'))
        target = ""
        def normalize_result(result):
            if type(result) is tuple:
                return list(result)
            else:
                return result
            
        def normalize_source(site,index = -1):
            results = []
            if index >-1 :
                 siteimpprop = site.getImportantProperty(0)
                 source = site.FriendlyName[index]
                 source_type = site.ResultType
            else:
                 siteimpprop = site.getImportantProperty(index)
                 source = site.FriendlyName
                 source_type = site.ResultType
            if not (siteimpprop is None or len(siteimpprop)==0):
                if siteimpprop[index] is None or len(siteimpprop[index])==0:
                    source = site.FriendlyName[index]
                else:
                    laststring = ""
                    #if it's just a string we don't want it to output like a list
                    if isinstance(siteimpprop, basestring):
                        if "" + siteimpprop != laststring:
                            results.append(siteimpprop)
                            laststring = "" + siteimprop
                    #must be a list since it failed the isinstance check on string
                    else:
                        laststring = ""
                        if isinstance(siteimpprop[index], basestring):
                            if "" + siteimpprop[index] != laststring:
                                 results.append(normalize_result(siteimpprop[index]))
                                 laststring = "" + siteimpprop[index]   
                        else:
                            for siteresult in siteimpprop[index]:
                                if str(siteresult) != laststring:
                                    results.append(normalize_result(siteresult))
                                    laststring = "" + str(siteresult)
            return self._source_output_class(source,source_type,results)
             
        if sites is not None:
            for site in sites:
                sources = []
                tgt = site.Target
                typ = site.TargetType
                index = -1
                if not isinstance(site._regex,basestring): #this is a multisite:
                    for index in range(len(site.RegEx)): #the regexs will ensure we have the exact number of lookups
                       sources.append(normalize_source(site,index))
                else:#this is a singlesite
                    sources.append(normalize_source(site,index))
                outputs.append(self._site_output_class(tgt,typ,sources))
        return outputs
    
#    def __str__(self):
#        "\n".join(map(str, self.normalized_output))
            
    #def __str__(self):
    #    str(self._normalized_output)
    
#    __repr__ = __str__

    def hashOutput(self):
        """
        Returns output of automater as a hash table sutible for JSON encoding.
        The format is:
        {<target>:{<site>:{'Type':<Result Type>, 'Result':<Result>}}}
        """
        sites = sorted(self.list_of_sites, key=attrgetter('Target'))
        target = ""
        thash = {}
        def get_hash(h,k):
            if k in h:
                h[k]
            else:
                h[k] = {}
            return h[k]
        def get_array(h,k):
            if k in h:
                h[k]
            else:
                h[k] = []
            return h[k]
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
                            get_array(get_hash(thash,tgt),source).append({'Type':typ,'Result':res})
                        else:
                            if siteimpprop[index] is None or len(siteimpprop[index])==0:
                                tgt = site.Target
                                typ = site.TargetType
                                source = site.FriendlyName[index]
                                res = "No results found"
                                #csvRW.writerow([tgt,typ,source,res])
                                get_array(get_hash(thash,tgt),source).append({'Type':typ,'Result':res})
                            else:
                                laststring = ""
                                #if it's just a string we don't want it to output like a list
                                if isinstance(siteimpprop, basestring):
                                    tgt = site.Target
                                    typ = site.TargetType
                                    source = site.FriendlyName
                                    res = siteimpprop
                                    if "" + tgt + typ + source + res != laststring:
                                        get_array(get_hash(thash,tgt),source).append({'Type':typ,'Result':res})
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
                                            get_array(get_hash(thash,tgt),source).append({'Type':typ,'Result':res})
                                            laststring = "" + tgt + typ + source + str(res)
                else:#this is a singlesite
                    siteimpprop = site.getImportantProperty(0)
                    if siteimpprop is None or len(siteimpprop)==0:
                        tgt = site.Target
                        typ = site.TargetType
                        source = site.FriendlyName
                        res = "No results found"
                    else:
                        laststring = ""
                        #if it's just a string we don't want it output like a list
                        if isinstance(siteimpprop, basestring):
                            tgt = site.Target
                            typ = site.TargetType
                            source = site.FriendlyName
                            res = siteimpprop
                            if "" + tgt + typ + source + res != laststring:
                                get_array(get_hash(thash,tgt),source).append({'Type':typ,'Result':res})
                                
                                laststring = "" + tgt + typ + source + res
                        else:
                            laststring = ""
                            for siteresult in siteimpprop:
                                tgt = site.Target
                                typ = site.TargetType
                                source = site.FriendlyName if site.FriendlyName else "UNK"
                                res = siteresult
                                if "" + tgt + typ + source + str(res) != laststring:
                                    get_array(get_hash(thash,tgt),source).append({'Type':typ,'Result':res})
                                    laststring = "" + tgt + typ + source + str(res)
                                    
        return thash
    def jsonOutput(self):
        """
        Returns output of automater as JSON encoded string
        """
        return json.dumps(self.hashOutput())

    def PrintToScreen(self):
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
        sites = sorted(self.list_of_sites, key=attrgetter('Target'))
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
                                laststring = ""
                                #if it's just a string we don't want it output like a list
                                if isinstance(siteimpprop[index], basestring):
                                    if "" + site.ReportStringForResult[index] + " " + str(siteimpprop[index]) != laststring:
                                        print "" + site.ReportStringForResult[index] + " " + str(siteimpprop[index])
                                        laststring = "" + site.ReportStringForResult[index] + " " + str(siteimpprop[index])
                                #must be a list since it failed the isinstance check on string
                                else:
                                    laststring = ""
                                    for siteresult in siteimpprop[index]:
                                        if "" + site.ReportStringForResult[index] + " " + str(siteresult) != laststring:
                                            print "" + site.ReportStringForResult[index] + " " + str(siteresult)
                                            laststring = "" + site.ReportStringForResult[index] + " " + str(siteresult)
                else:#this is a singlesite
                    siteimpprop = site.getImportantProperty(0)
                    if target != site.Target:
                        print "\n____________________     Results found for: " + site.Target + "     ____________________"
                        target = site.Target
                    if siteimpprop is None or len(siteimpprop)==0:
                        print "No results found in the " + site.FriendlyName
                    else:
                        laststring = ""
                        #if it's just a string we don't want it output like a list
                        if isinstance(siteimpprop, basestring):
                            if "" + site.ReportStringForResult + " " + str(siteimpprop) != laststring:
                                print "" + site.ReportStringForResult + " " + str(siteimpprop)
                                laststring = "" + site.ReportStringForResult + " " + str(siteimpprop)
                        #must be a list since it failed the isinstance check on string
                        else:
                            laststring = ""
                            for siteresult in siteimpprop:
                                if "" + site.ReportStringForResult + " " + str(siteresult) != laststring:
                                    print "" + site.ReportStringForResult + " " + str(siteresult)
                                    laststring = "" + site.ReportStringForResult + " " + str(siteresult)
        else:
            pass

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
        sites = sorted(self.list_of_sites, key=attrgetter('Target'))
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
                                laststring = ""
                                #if it's just a string we don't want it to output like a list
                                if isinstance(siteimpprop[index], basestring):
                                    if "" + site.ReportStringForResult[index] + " " + str(siteimpprop[index]) != laststring:
                                        f.write("\n" + site.ReportStringForResult[index] + " " + str(siteimpprop[index]))
                                        laststring = "" + site.ReportStringForResult[index] + " " + str(siteimpprop[index])
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
        f = open(csvoutfile, "wb")
        self.PrintToCSVFileHandle(f)
        f.close()
        
    def PrintToCSVFileHandle(self,csvoutfilehandle):
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
        sites = sorted(self.list_of_sites, key=attrgetter('Target'))
        target = ""
        
        f = csvoutfilehandle
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
        #f.close()
        
        

    def PrintToHTMLFile(self,htmloutfile):
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
        sites = sorted(self.list_of_sites, key=attrgetter('Target'))
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
