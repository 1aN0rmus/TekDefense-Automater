"""
The siteinfo.py module provides site lookup and result
storage for those sites based on the xml config
file and the arguments sent in to the Automater.

Class(es):
SiteFacade -- Class used to run the automation necessary to retrieve
site information and store results.
Site -- Parent Class used to store sites and information retrieved.
SingleResultsSite -- Class used to store information from a site that
only has one result requested and discovered.
MultiResultsSite -- Class used to store information from a site that
has multiple results requested and discovered.
PostTransactionPositiveCapableSite -- Class used to store information
from a site that has single or multiple results requested and discovered.
This Class is utilized to post information to web sites if a post is
required and requested via a --p argument utilized when the program is
called. This Class expects to find the first regular expression listed
in the xml config file. If that regex is found, it tells the class
that a post is necessary.

Function(s):
No global exportable functions are defined.

Exception(s):
No exceptions exported.
"""
import requests
import re
import time
import os
from os import listdir
from os.path import isfile, join
from requests.exceptions import ConnectionError
from outputs import SiteDetailOutput
from inputs import SitesFile
from utilities import VersionChecker

requests.packages.urllib3.disable_warnings()

__TEKDEFENSEXML__ = 'tekdefense.xml'
__SITESXML__ = 'sites.xml'

class SiteFacade(object):
    """
    SiteFacade provides a Facade to run the multiple requirements needed
    to automate the site retrieval and storage processes.

    Public Method(s):
    runSiteAutomation
    (Property) Sites

    Instance variable(s):
    _sites
    """

    def __init__(self, verbose):
        """
        Class constructor. Simply creates a blank list and assigns it to
        instance variable _sites that will be filled with retrieved info
        from sites defined in the xml configuration file.

        Argument(s):
        No arguments are required.

        Return value(s):
        Nothing is returned from this Method.
        """

        self._sites = []
        self._verbose = verbose

    def runSiteAutomation(self, webretrievedelay, proxy, targetlist, sourcelist,
                          useragent, botoutputrequested, refreshremotexml, versionlocation):
        """
        Builds site objects representative of each site listed in the xml
        config file. Appends a Site object or one of it's subordinate objects
        to the _sites instance variable so retrieved information can be used.
        Returns nothing.

        Argument(s):
        webretrievedelay -- The amount of seconds to wait between site retrieve
        calls. Default delay is 2 seconds.
        proxy -- proxy server address as server:port_number
        targetlist -- list of strings representing targets to be investigated.
        Targets can be IP Addresses, MD5 hashes, or hostnames.
        sourcelist -- list of strings representing a specific site that should only be used
        for investigation purposes instead of all sites listed in the xml
        config file.
        useragent -- String representing user-agent that will be utilized when
        requesting or submitting data to or from a web site.
        botoutputrequested -- true or false representing if a minimalized output
        will be required for the site.
        refreshremotexml -- true or false representing if Automater will refresh 
        the tekdefense.xml file on each run.

        Return value(s):
        Nothing is returned from this Method.

        Restriction(s):
        The Method has no restrictions.
        """
        if refreshremotexml:
            SitesFile.updateTekDefenseXMLTree(proxy, self._verbose)

        remotesitetree = SitesFile.getXMLTree(__TEKDEFENSEXML__, self._verbose)
        localsitetree = SitesFile.getXMLTree(__SITESXML__, self._verbose)

        if not localsitetree and not remotesitetree:
            print 'Unfortunately there is neither a {tekd} file nor a {sites} file that can be utilized for proper' \
                  ' parsing.\nAt least one configuration XML file must be available for Automater to work properly.\n' \
                  'Please see {url} for further instructions.'\
                .format(tekd=__TEKDEFENSEXML__, sites=__SITESXML__, url=versionlocation)
        else:
            if localsitetree:
                for siteelement in localsitetree.iter(tag="site"):
                    if self.siteEntryIsValid(siteelement):
                        for targ in targetlist:
                            for source in sourcelist:
                                sitetypematch, targettype, target = self.getSiteInfoIfSiteTypesMatch(source, targ,
                                                                                                     siteelement)
                                if sitetypematch:
                                    self.buildSiteList(siteelement, webretrievedelay, proxy, targettype, target,
                                                       useragent, botoutputrequested)
                    else:
                        print 'A problem was found in the {sites} file. There appears to be a site entry with ' \
                              'unequal numbers of regexs and reporting requirements'.format(sites=__SITESXML__)
            if remotesitetree:
                for siteelement in remotesitetree.iter(tag="site"):
                    if self.siteEntryIsValid(siteelement):
                        for targ in targetlist:
                            for source in sourcelist:
                                sitetypematch, targettype, target = self.getSiteInfoIfSiteTypesMatch(source, targ,
                                                                                                     siteelement)
                                if sitetypematch:
                                    self.buildSiteList(siteelement, webretrievedelay, proxy, targettype, target,
                                                       useragent, botoutputrequested)
                    else:
                        print 'A problem was found in the {sites} file. There appears to be a site entry with ' \
                              'unequal numbers of regexs and reporting requirements'.format(sites=__SITESXML__)

    def getSiteInfoIfSiteTypesMatch(self, source, target, siteelement):
        if source == "allsources" or source == siteelement.get("name"):
            targettype = self.identifyTargetType(target)
            for st in siteelement.find("sitetype").findall("entry"):
                if st.text == targettype:
                    return True, targettype, target

        return False, None, None

    def siteEntryIsValid(self, siteelement):
        reportstringcount = len(siteelement.find("reportstringforresult").findall("entry"))
        sitefriendlynamecount = len(siteelement.find("sitefriendlyname").findall("entry"))
        regexcount = len(siteelement.find("regex").findall("entry"))
        importantpropertycount = len(siteelement.find("importantproperty").findall("entry"))

        if reportstringcount == sitefriendlynamecount and reportstringcount == regexcount and reportstringcount == importantpropertycount:
            return True
        return False

    def buildSiteList(self, siteelement, webretrievedelay, proxy, targettype, targ, useragent, botoutputrequested):
        site = Site.buildSiteFromXML(siteelement, webretrievedelay, proxy, targettype, targ, useragent,
                                     botoutputrequested, self._verbose)
        if site.Method == "POST":
            self._sites.append(MethodPostSite(site))
        elif isinstance(site.RegEx, basestring):
            self._sites.append(SingleResultsSite(site))
        else:
            self._sites.append(MultiResultsSite(site))

    @property
    def Sites(self):
        """
        Checks the instance variable _sites is empty or None.
        Returns _sites (the site list) or None if it is empty.

        Argument(s):
        No arguments are required.

        Return value(s):
        list -- of Site objects or its subordinates.
        None -- if _sites is empty or None.

        Restriction(s):
        This Method is tagged as a Property.
        """
        if self._sites is None or len(self._sites) == 0:
            return None
        return self._sites

    def identifyTargetType(self, target):
        """
        Checks the target information provided to determine if it is a(n)
        IP Address in standard; CIDR or dash notation, or an MD5 hash,
        or a string hostname.
        Returns a string md5 if MD5 hash is identified. Returns the string
        ip if any IP Address format is found. Returns the string hostname
        if neither of those two are found.

        Argument(s):
        target -- string representing the target provided as the first
        argument to the program when Automater is run.

        Return value(s):
        string.

        Restriction(s):
        The Method has no restrictions.
        """
        ipAddress = re.compile('\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}')
        ipFind = re.findall(ipAddress, target)
        if ipFind is not None and len(ipFind) > 0:
            return "ip"

        md5 = re.compile('[a-fA-F0-9]{32}', re.IGNORECASE)
        md5Find = re.findall(md5,target)
        if md5Find is not None and len(md5Find) > 0:
            return "md5"

        return "hostname"

class Site(object):
    """
    Site is the parent object that represents each site used
    for retrieving information. Site stores the results
    discovered from each web site discovered when running Automater.
    Site is the parent object to SingleResultsSite, MultiResultsSite,
    PostTransactionPositiveCapableSite and MethodPostSite.

    Public Method(s):
    (Class Method) buildSiteFromXML
    (Class Method) buildStringOrListfromXML
    (Class Method) buildDictionaryFromXML
    (Property) WebRetrieveDelay
    (Property) TargetType
    (Property) ReportStringForResult
    (Property) FriendlyName
    (Property) RegEx
    (Property) URL
    (Property) ErrorMessage
    (Property) UserMessage
    (Property) FullURL
    (Setter) FullURL
    (Property) BotOutputRequested
    (Property) SourceURL
    (Property) ImportantPropertyString
    (Property) Params
    (Setter) Params
    (Property) Headers
    (Property) Target
    (Property) UserAgent
    (Property) Results
    (Property) Method
    addResults
    postMessage
    getImportantProperty
    getTarget
    getResults
    getFullURL
    getWebScrape

    Instance variable(s):
    _sites
    _sourceurl
    _webretrievedelay
    _targetType
    _reportstringforresult
    _errormessage
    _usermessage
    _target
    _userAgent
    _friendlyName
    _regex
    _fullURL
    _botOutputRequested
    _importantProperty
    _params
    _headers
    _results
    _method
    """
    def __init__(self, domainurl, webretrievedelay, proxy, targettype,
                 reportstringforresult, target, useragent, friendlyname, regex,
                 fullurl, boutoutputrequested, importantproperty, params, headers, method, postdata, verbose):
        """
        Class constructor. Sets the instance variables based on input from
        the arguments supplied when Automater is run and what the xml
        config file stores.

        Argument(s):
        domainurl -- string defined in xml in the domainurl XML tag.
        webretrievedelay -- the amount of seconds to wait between site retrieve
        calls. Default delay is 2 seconds.
        proxy -- will set a proxy to use (eg. proxy.example.com:8080).
        targettype -- the targettype as defined. Either ip, md5, or hostname.
        reportstringforresult -- string or list of strings that are entered in
        the entry XML tag within the reportstringforresult XML tag in the
        xml configuration file.
        target -- the target that will be used to gather information on.
        useragent -- the user-agent string that will be utilized when submitting
        information to or requesting information from a website
        friendlyname -- string or list of strings that are entered in
        the entry XML tag within the sitefriendlyname XML tag in the
        xml configuration file.
        regex -- the regexs defined in the entry XML tag within the
        regex XML tag in the xml configuration file.
        fullurl -- string representation of fullurl pulled from the
        xml file in the fullurl XML tag.
        boutoutputrequested -- true or false representation of whether the -b option was used
        when running the program. If true, it slims the output so a bot can be
        used and the output is minimalized.
        importantproperty -- string defined in the the xml config file
        in the importantproperty XML tag.
        params -- string or list provided in the entry XML tags within the params
        XML tag in the xml configuration file.
        headers -- string or list provided in the entry XML tags within the headers
        XML tag in the xml configuration file.
        method -- holds whether this is a GET or POST required site. by default = GET
        postdata -- dict holding data required for posting values to a site. by default = None
        verbose -- boolean representing whether text will be printed to stdout

        Return value(s):
        Nothing is returned from this Method.
        """
        self._sourceurl = domainurl
        self._webretrievedelay = webretrievedelay
        self._proxy = proxy
        self._targetType = targettype
        self._reportstringforresult = reportstringforresult
        self._errormessage = "[-] Cannot scrape"
        self._usermessage = "[*] Checking"
        self._target = target
        self._userAgent = useragent
        self._friendlyName = friendlyname
        self._regex = ""
        self.RegEx = regex  # call the helper method to clean %TARGET% from regex string
        self._fullURL = ""
        self.FullURL = fullurl  # call the helper method to clean %TARGET% from fullurl string
        self._botOutputRequested = boutoutputrequested
        self._importantProperty = importantproperty
        self._params = None
        if params is not None:
            self.Params = params  # call the helper method to clean %TARGET% from params string
        self._headers = None
        if headers is not None:
            self.Headers = headers  # call the helper method to clean %TARGET% from params string
        self._postdata = None
        if postdata:
            self.PostData = postdata
        self._method = None
        self.Method = method  # call the helper method to ensure result is either GET or POST
        self._results = []
        self._verbose = verbose

    @classmethod
    def checkmoduleversion(self, prefix, gitlocation, proxy, verbose):
        execpath = os.path.dirname(os.path.realpath(__file__))
        pythonfiles = [f for f in listdir(execpath) if isfile(join(execpath, f)) and f[-3:] == '.py']
        if proxy:
            proxies = {'https': proxy, 'http': proxy}
        else:
            proxies = None
        SiteDetailOutput.PrintStandardOutput(VersionChecker.getModifiedFileInfo(prefix, gitlocation, pythonfiles),
                                             verbose=verbose)

    @classmethod
    def buildSiteFromXML(self, siteelement, webretrievedelay, proxy, targettype,
                         target, useragent, botoutputrequested, verbose):
        """
        Utilizes the Class Methods within this Class to build the Site object.
        Returns a Site object that defines results returned during the web
        retrieval investigations.

        Argument(s):
        siteelement -- the siteelement object that will be used as the
        start element.
        webretrievedelay -- the amount of seconds to wait between site retrieve
        calls. Default delay is 2 seconds.
        proxy -- sets a proxy to use in the form of proxy.example.com:8080.
        targettype -- the targettype as defined. Either ip, md5, or hostname.
        target -- the target that will be used to gather information on.
        useragent -- the string utilized to represent the user-agent when
        web requests or submissions are made.
        botoutputrequested -- true or false representing if a minimalized output
        will be required for the site.

        Return value(s):
        Site object.

        Restriction(s):
        This Method is tagged as a Class Method
        """
        domainurl = siteelement.find("domainurl").text
        try:
            method = siteelement.find("method").text
            if method.upper() != "GET" and method.upper() != "POST":
                method = "GET"
        except:
            method = "GET"
        postdata = Site.buildDictionaryFromXML(siteelement, "postdata")
        reportstringforresult = Site.buildStringOrListfromXML(siteelement, "reportstringforresult")
        sitefriendlyname = Site.buildStringOrListfromXML(siteelement, "sitefriendlyname")
        regex = Site.buildStringOrListfromXML(siteelement, "regex")
        fullurl = siteelement.find("fullurl").text
        importantproperty = Site.buildStringOrListfromXML(siteelement, "importantproperty")
        params = Site.buildDictionaryFromXML(siteelement, "params")
        headers = Site.buildDictionaryFromXML(siteelement, "headers")

        return Site(domainurl, webretrievedelay, proxy, targettype, reportstringforresult, target,
                    useragent, sitefriendlyname, regex, fullurl, botoutputrequested, importantproperty,
                    params, headers, method.upper(), postdata, verbose)

    @classmethod
    def buildStringOrListfromXML(self, siteelement, elementstring):
        """
        Takes in a siteelement and then elementstring and builds a string
        or list from multiple entry XML tags defined in the xml config
        file. Returns None if there are no entry XML tags for this
        specific elementstring. Returns a list of those entries
        if entry XML tags are found or a string of that entry if only
        one entry XML tag is found.

        Argument(s):
        siteelement -- the siteelement object that will be used as the
        start element.
        elementstring -- the string representation within the siteelement
        that will be utilized to get to the single or multiple entry
        XML tags.

        Return value(s):
        None if no entry XML tags are found.
        List representing all entry keys found within the elementstring.
        string representing an entry key if only one is found
        within the elementstring.

        Restriction(s):
        This Method is tagged as a Class Method
        """
        variablename = ""
        if len(siteelement.find(elementstring).findall("entry")) == 0:
            return None

        if len(siteelement.find(elementstring).findall("entry")) > 1:
            variablename = []
            for entry in siteelement.find(elementstring).findall("entry"):
                variablename.append(entry.text)
        else:
            variablename = ""
            variablename = siteelement.find(elementstring).find("entry").text
        return variablename

    @classmethod
    def buildDictionaryFromXML(self, siteelement, elementstring):
        """
        Takes in a siteelement and then elementstring and builds a dictionary
        from multiple entry XML tags defined in the xml config file.
        Returns None if there are no entry XML tags for this
        specific elementstring. Returns a dictionary of those entries
        if entry XML tags are found.

        Argument(s):
        siteelement -- the siteelement object that will be used as the
        start element.
        elementstring -- the string representation within the siteelement
        that will be utilized to get to the single or multiple entry
        XML tags.

        Return value(s):
        None if no entry XML tags are found.
        Dictionary representing all entry keys found within the elementstring.

        Restriction(s):
        This Method is tagged as a Class Method
        """
        variablename = ""
        try:
            if len(siteelement.find(elementstring).findall("entry")) > 0:
                variablename = {}
                for entry in siteelement.find(elementstring).findall("entry"):
                    variablename[entry.get("key")] = entry.text
            else:
                return None
        except:
            return None
        return variablename

    @property
    def WebRetrieveDelay(self):
        """
        Returns the string representation of the number of
        seconds that will be delayed between site retrievals.

        Argument(s):
        No arguments are required.

        Return value(s):
        string -- representation of an integer that is the delay in
        seconds that will be used between each web site retrieval.

        Restriction(s):
        This Method is tagged as a Property.
        """
        return self._webretrievedelay

    @property
    def Proxy(self):
        """
        Returns the string representation of the proxy used.

        Argument(s):
        No arguments are required.

        Return value(s):
        string -- representation of the proxy used

        Restriction(s):
        This Method is tagged as a Property.
        """
        return self._proxy

    @property
    def TargetType(self):
        """
        Returns the target type information whether that be ip,
        md5, or hostname.

        Argument(s):
        No arguments are required.

        Return value(s):
        string -- defined as ip, md5, or hostname.

        Restriction(s):
        This Method is tagged as a Property.
        """
        return self._targetType

    @property
    def ReportStringForResult(self):
        """
        Returns the string representing a report string tag that
        precedes reporting information so the user knows what
        specifics are being found.

        Argument(s):
        No arguments are required.

        Return value(s):
        string -- representing a tag for reporting information.

        Restriction(s):
        This Method is tagged as a Property.
        """
        return self._reportstringforresult

    @property
    def FriendlyName(self):
        """
        Returns the string representing a friendly string name.

        Argument(s):
        No arguments are required.

        Return value(s):
        string -- representing friendly name for a tag for reporting.

        Restriction(s):
        This Method is tagged as a Property.
        """
        return self._friendlyName

    @property
    def URL(self):
        """
        Returns the string representing the Domain URL which is
        required to retrieve the information being investigated.

        Argument(s):
        No arguments are required.

        Return value(s):
        string -- representing the URL of the site.

        Restriction(s):
        This Method is tagged as a Property.
        """
        return self._sourceurl

    @property
    def ErrorMessage(self):
        """
        Returns the string representing the Error Message.

        Argument(s):
        No arguments are required.

        Return value(s):
        string -- representing the error message to print to
        the standard output.

        Restriction(s):
        This Method is tagged as a Property.
        """
        return self._errormessage

    @property
    def UserMessage(self):
        """
        Returns the string representing the Full URL which is the
        domain URL plus querystrings and other information required
        to retrieve the information being investigated.

        Argument(s):
        No arguments are required.

        Return value(s):
        string -- representing the full URL of the site including
        querystring information and any other info required.

        Restriction(s):
        This Method is tagged as a Property.
        """
        return self._usermessage

    @property
    def FullURL(self):
        """
        Returns the string representing the Full URL which is the
        domain URL plus querystrings and other information required
        to retrieve the information being investigated.

        Argument(s):
        No arguments are required.

        Return value(s):
        string -- representing the full URL of the site including
        querystring information and any other info required.

        Restriction(s):
        This Method is tagged as a Property.
        """
        return self._fullURL

    @FullURL.setter
    def FullURL(self, fullurl):
        """
        Determines if the parameter has characters and assigns it to the
        instance variable _fullURL if it does after replacing the target
        information where the keyword %TARGET% is used. This keyword will
        be used in the xml configuration file where the user wants
        the target information to be placed in the URL.

        Argument(s):
        fullurl -- string representation of fullurl pulled from the
        xml file in the fullurl XML tag.

        Return value(s):
        Nothing is returned from this Method.

        Restriction(s):
        This Method is tagged as a Setter.
        """
        if len(fullurl) > 0:
            fullurlreplaced = fullurl.replace("%TARGET%", self._target)
            self._fullURL = fullurlreplaced
        else:
            self._fullURL = ""

    @property
    def RegEx(self):
        """
        Returns string representing the regex being investigated.

        Argument(s):
        No arguments are required.

        Return value(s):
        string -- representation of the Regex from the _regex
        instance variable.

        Restriction(s):
        This Method is tagged as a Property.
        """
        return self._regex

    @RegEx.setter
    def RegEx(self, regex):
        """
        Determines if the parameter has characters and assigns it to the
        instance variable _regex if it does after replacing the target
        information where the keyword %TARGET% is used. This keyword will
        be used in the xml configuration file where the user wants
        the target information to be placed in the regex.

        Argument(s):
        regex -- string representation of regex pulled from the
        xml file in the regex entry XML tag.

        Return value(s):
        Nothing is returned from this Method.

        Restriction(s):
        This Method is tagged as a Setter.
        """
        if len(regex) > 0:
            try:
                regexreplaced = regex.replace("%TARGET%", self._target)
                self._regex = regexreplaced
            except AttributeError:
                regexreplaced = []
                for r in regex:
                    regexreplaced.append(r.replace("%TARGET%", self._target))
                self._regex = regexreplaced
        else:
            self._regex = ""

    @property
    def BotOutputRequested(self):
        """
        Returns a true if the -b option was requested when the
        program was run. This identifies if the program is to
        run a more silent version of output during the run to help
        bots and other small format requirements.

        Argument(s):
        No arguments are required.

        Return value(s):
        boolean -- True if the -b option was used and am more silent
        output is required. False if normal output should be utilized.

        Restriction(s):
        This Method is tagged as a Property.
        """
        return self._botOutputRequested

    @property
    def SourceURL(self):
        """
        Returns the string representing the Source URL which is simply
        the domain URL entered in the xml config file.

        Argument(s):
        No arguments are required.

        Return value(s):
        string -- representing the source URL of the site.

        Restriction(s):
        This Method is tagged as a Property.
        """
        return self._sourceurl

    @property
    def ImportantPropertyString(self):
        """
        Returns the string representing the Important Property
        that the user wants the site to report. This is set using
        the xml config file in the importantproperty XML tag.

        Argument(s):
        No arguments are required.

        Return value(s):
        string -- representing the important property of the site
        that needs to be reported.

        Restriction(s):
        This Method is tagged as a Property.
        """
        return self._importantProperty

    @property
    def Params(self):
        """
        Determines if web Parameters were set for this specific site.
        Returns the string representing the Parameters using the
        _params instance variable or returns None if the instance
        variable is empty or not set.

        Argument(s):
        No arguments are required.

        Return value(s):
        string -- representation of the Parameters from the _params
        instance variable.

        Restriction(s):
        This Method is tagged as a Property.
        """
        if self._params is None:
            return None
        if len(self._params) == 0:
            return None
        return self._params

    @Params.setter
    def Params(self, params):
        """
        Determines if Parameters were required for this specific site.
        If web Parameters were set, this places the target into the
        parameters where required marked with the %TARGET% keyword
        in the xml config file.

        Argument(s):
        params -- dictionary representing web Parameters required.

        Return value(s):
        Nothing is returned from this Method.

        Restriction(s):
        This Method is tagged as a Setter.
        """
        if len(params) > 0:
            for key in params:
                if params[key] == "%TARGET%":
                    params[key] = self._target
            self._params = params
        else:
            self._params = None

    @property
    def Headers(self):
        """
        Determines if Headers were set for this specific site.
        Returns the string representing the Headers using the
        _headers instance variable or returns None if the instance
        variable is empty or not set.

        Argument(s):
        No arguments are required.

        Return value(s):
        string -- representation of the Headers from the _headers
        instance variable.

        Restriction(s):
        This Method is tagged as a Property.
        """
        if self._headers is None:
            return None
        if len(self._headers) == 0:
            return None
        return self._headers

    @Headers.setter
    def Headers(self, headers):
        """
        Determines if Headers were required for this specific site.
        If web Headers were set, this places the target into the
        headers where required or marked with the %TARGET% keyword
        in the xml config file.

        Argument(s):
        headers -- dictionary representing web Headers required.

        Return value(s):
        Nothing is returned from this Method.

        Restriction(s):
        This Method is tagged as a Setter.
        """
        if len(headers) > 0:
            for key in headers:
                if headers[key] == "%TARGET%":
                    headers[key] = self._target
            self._headers = headers
        else:
            self._headers = None

    @property
    def PostData(self):
        """
        Determines if PostData was set for this specific site.
        Returns the dict representing the PostHeaders using the
        _postdata instance variable or returns None if the instance
        variable is empty or not set.

        Argument(s):
        No arguments are required.

        Return value(s):
        dict -- representation of the PostData from the _postdata
        instance variable.

        Restriction(s):
        This Method is tagged as a Property.
        """
        if self._postdata is None:
            return None
        if len(self._postdata) == 0:
            return None
        return self._postdata

    @PostData.setter
    def PostData(self, postdata):
        """
        Determines if post data was required for this specific site.
        If postdata is set, this ensures %TARGET% is stripped if necessary.

        Argument(s):
        postdata -- dictionary representing web postdata required.

        Return value(s):
        Nothing is returned from this Method.

        Restriction(s):
        This Method is tagged as a Setter.
        """
        if len(postdata) > 0:
            for key in postdata:
                if postdata[key] == "%TARGET%":
                    postdata[key] = self._target
            self._postdata = postdata
        else:
            self._postdata = None

    @property
    def Target(self):
        """
        Returns string representing the target being investigated.
        The string may be an IP Address, MD5 hash, or hostname.

        Argument(s):
        No arguments are required.

        Return value(s):
        string -- representation of the Target from the _target
        instance variable.

        Restriction(s):
        This Method is tagged as a Property.
        """
        return self._target

    @property
    def UserAgent(self):
        """
        Returns string representing the user-agent that will
        be used when requesting or submitting information to
        a web site. This is a user-provided string implemented
        on the command line at execution or provided by default
        if not added during execution.

        Argument(s):
        No arguments are required.

        Return value(s):
        string -- representation of the UserAgent from the _userAgent
        instance variable.

        Restriction(s):
        This Method is tagged as a Property.
        """
        return self._userAgent

    @property
    def Method(self):
        """
        Determines if a method (GET or POST) was established for this specific site.
        Defaults to GET

        Argument(s):
        No arguments are required.

        Return value(s):
        string -- representation of the method used to access the site GET or POST.

        Restriction(s):
        This Method is tagged as a Property.
        """
        if self._method is None:
            return "GET"
        if len(self._method) == 0:
            return "GET"
        return self._method

    @Method.setter
    def Method(self, method):
        """
        Ensures the method type is set to either GET or POST. By default GET is assigned

        Argument(s):
        method -- string repr GET or POST. If neither, GET is assigned.

        Return value(s):
        Nothing is returned from this Method.

        Restriction(s):
        This Method is tagged as a Setter.
        """
        if not self.PostData:
            self._method = "GET"
            return
        if len(method) > 0:
            if method.upper() == "GET" or method.upper() == "POST":
                self._method = method.upper()
                return

        self._method = "GET"

    @property
    def Results(self):
        """
        Checks the instance variable _results is empty or None.
        Returns _results (the results list) or None if it is empty.
        Argument(s):
        No arguments are required.
        Return value(s):
        list -- list of results discovered from the site being investigated.
        None -- if _results is empty or None.
        Restriction(s):
        This Method is tagged as a Property.
        """
        if self._results is None or len(self._results) == 0:
            return None
        return self._results

    def addResults(self, results):
        """
        Assigns the argument to the _results instance variable to build
        the list or results retrieved from the site. Assign None to the
        _results instance variable if the argument is empty.

        Argument(s):
        results -- list of results retrieved from the site.

        Return value(s):
        Nothing is returned from this Method.

        Restriction(s):
        The Method has no restrictions.
        """
        if results is None or len(results) == 0:
            self._results = None
        else:
            self._results = results

    def postMessage(self, message):
        """
        Prints multiple messages to inform the user of progress.

        Argument(s):
        message -- string to be utilized as a message to post.

        Return value(s):
        Nothing is returned from this Method.

        Restriction(s):
        The Method has no restrictions.
        """
        if self.BotOutputRequested:
            pass
        else:
            SiteDetailOutput.PrintStandardOutput(message, verbose=self._verbose)

    def postErrorMessage(self, message):
        """
        Prints multiple error messages to inform the user of progress.

        Argument(s):
        message -- string to be utilized as an error message to post.

        Return value(s):
        Nothing is returned from this Method.

        Restriction(s):
        The Method has no restrictions.
        """
        self.postMessage(message)

    def getImportantProperty(self, index):
        """
        Gets the property information from the property value listed in the
        xml file for that specific site in the importantproperty xml tag.
        This Method allows for the property that will be printed to be changed
        using the configuration file.
        Returns the return value listed in the property attribute discovered.

        Argument(s):
        index -- integer representing which important property is retrieved if
        more than one important property value is listed in the config file.

        Return value(s):
        Multiple options -- returns the return value of the property listed in
        the config file. Most likely a string or a list.

        Restriction(s):
        The Method has no restrictions.
        """
        if isinstance(self._importantProperty, basestring):
            siteimpprop = getattr(self, "get" + self._importantProperty, Site.getResults)
        else:
            siteimpprop = getattr(self, "get" + self._importantProperty[index], Site.getResults)
        return siteimpprop()

    def getTarget(self):
        """
        Returns the Target property information.

        Argument(s):
        No arguments are required.

        Return value(s):
        string.

        Restriction(s):
        The Method has no restrictions.
        """
        return self.Target

    def getResults(self):
        """
        Returns the Results property information.

        Argument(s):
        No arguments are required.

        Return value(s):
        string.

        Restriction(s):
        The Method has no restrictions.
        """
        return self.Results

    def getFullURL(self):
        """
        Returns the FullURL property information.

        Argument(s):
        No arguments are required.

        Return value(s):
        string.

        Restriction(s):
        The Method has no restrictions.
        """
        return self.FullURL

    def getSourceURL(self):
        """
        Returns the SourceURL property information.

        Argument(s):
        No arguments are required.

        Return value(s):
        string.

        Restriction(s):
        The Method has no restrictions.
        """
        return self.SourceURL

    def getHeaderParamProxyInfo(self):
        if self.Headers:
            headers = {x: self.Headers[x] for x in self.Headers}
            headers['User-agent'] = self.UserAgent
        else:
            headers = {'User-agent': self.UserAgent}
        if self.Proxy:
            proxy = {'https': self.Proxy, 'http': self.Proxy}
        else:
            proxy = None
        if self.Params:
            params = {x: self.Params[x] for x in self.Params}
        else:
            params = None
        return headers, params, proxy

    def getWebScrape(self):
        """
        Attempts to retrieve a string from a web site. String retrieved is
        the entire web site including HTML markup. Requests via proxy if
        --proxy option was chosen during execution of the Automater.
        Returns the string representing the entire web site including the
        HTML markup retrieved from the site.

        Argument(s):
        No arguments are required.

        Return value(s):
        string.

        Restriction(s):
        The Method has no restrictions.
        """
        delay = self.WebRetrieveDelay
        headers, params, proxy = self.getHeaderParamProxyInfo()
        try:
            time.sleep(delay)
            resp = requests.get(self.FullURL, headers=headers, params=params, proxies=proxy, verify=False, timeout=5)
            return str(resp.content)
        except ConnectionError as ce:
            try:
                self.postErrorMessage('[-] Cannot connect to {url}. Server response is {resp} Server error code is {code}'.
                                      format(url=self.FullURL, resp=ce.message[0], code=ce.message[1][0]))
            except:
                self.postErrorMessage('[-] Cannot connect to ' + self.FullURL)
        except:
            self.postErrorMessage('[-] Cannot connect to ' + self.FullURL)

    def addMultiResults(self, results, index):
        """
        Assigns the argument to the _results instance variable to build
        the list or results retrieved from the site. Assign None to the
        _results instance variable if the argument is empty.

        Argument(s):
        results -- list of results retrieved from the site.
        index -- integer value representing the index of the result found.

        Return value(s):
        Nothing is returned from this Method.

        Restriction(s):
        The Method has no restrictions.
        """
        # if no return from site, seed the results with an empty list
        if results is None or len(results) == 0:
            self._results[index] = None
        else:
            self._results[index] = results

    def submitPost(self):
        """
        Submits information to a web site being used as a resource that
        requires a post of information. Submits via proxy if --proxy
        option was chosen during execution of the Automater.
        Returns a string that contains entire web site being used as a
        resource including HTML markup information.

        Argument(s):
        raw_params -- string info detailing parameters provided from
        xml configuration file in the params XML tag.
        headers -- string info detailing headers provided from
        xml configuration file in the headers XML tag.

        Return value(s):
        string -- contains entire web site being used as a
        resource including HTML markup information.

        Restriction(s):
        The Method has no restrictions.
        """
        headers, params, proxy = self.getHeaderParamProxyInfo()
        try:
            resp = requests.post(self.FullURL, data=self.PostData, headers=headers, params=params, proxies=proxy, verify=False)
            return str(resp.content)
        except ConnectionError as ce:
            try:
                self.postErrorMessage('[-] Cannot connect to {url}. Server response is {resp} Server error code is {code}'.
                                      format(url=self.FullURL, resp=ce.message[0], code=ce.message[1][0]))
            except:
                self.postErrorMessage('[-] Cannot connect to ' + self.FullURL)
        except:
            self.postErrorMessage('[-] Cannot connect to ' + self.FullURL)


class SingleResultsSite(Site):
    """
    SingleResultsSite inherits from the Site object and represents
    a site that is being used that has a single result returned.

    Public Method(s):
    getContentList

    Instance variable(s):
    _site
    """

    def __init__(self, site):
        """
        Class constructor. Assigns a site from the parameter into the _site
        instance variable. This is a play on the decorator pattern.

        Argument(s):
        site -- the site that we will decorate.

        Return value(s):
        Nothing is returned from this Method.
        """
        self._site = site
        super(SingleResultsSite, self).__init__(self._site.URL, self._site.WebRetrieveDelay, self._site.Proxy,
                                                self._site.TargetType, self._site.ReportStringForResult,
                                                self._site.Target, self._site.UserAgent, self._site.FriendlyName,
                                                self._site.RegEx, self._site.FullURL, self._site.BotOutputRequested,
                                                self._site.ImportantPropertyString, self._site.Params,
                                                self._site.Headers, self._site.Method, self._site.PostData,
                                                site._verbose)
        self.postMessage(self.UserMessage + " " + self.FullURL)
        websitecontent = self.getContentList(self.getWebScrape())
        if websitecontent:
            self.addResults(websitecontent)

    def getContentList(self, webcontent):
        """
        Retrieves a list of information retrieved from the sites defined
        in the xml configuration file.
        Returns the list of found information from the sites being used
        as resources or returns None if the site cannot be discovered.

        Argument(s):
        webcontent -- actual content of the web page that's been returned
        from a request.

        Return value(s):
        list -- information found from a web site being used as a resource.

        Restriction(s):
        The Method has no restrictions.
        """
        try:
            repattern = re.compile(self.RegEx, re.IGNORECASE)
            foundlist = re.findall(repattern, webcontent)
            return foundlist
        except:
            self.postErrorMessage(self.ErrorMessage + " " + self.FullURL)
            return None

class MultiResultsSite(Site):
    """
    MultiResultsSite inherits from the Site object and represents
    a site that is being used that has multiple results returned.

    Public Method(s):
    addResults
    getContentList

    Instance variable(s):
    _site
    _results
    """

    def __init__(self, site):
        """
        Class constructor. Assigns a site from the parameter into the _site
        instance variable. This is a play on the decorator pattern.

        Argument(s):
        site -- the site that we will decorate.

        Return value(s):
        Nothing is returned from this Method.
        """
        self._site = site
        super(MultiResultsSite, self).__init__(self._site.URL, self._site.WebRetrieveDelay,
                                              self._site.Proxy, self._site.TargetType,
                                              self._site.ReportStringForResult, self._site.Target,
                                              self._site.UserAgent, self._site.FriendlyName,
                                              self._site.RegEx, self._site.FullURL, self._site.BotOutputRequested,
                                              self._site.ImportantPropertyString, self._site.Params,
                                              self._site.Headers, self._site.Method, self._site.PostData, site._verbose)
        self._results = [[] for x in xrange(len(self._site.RegEx))]
        self.postMessage(self.UserMessage + " " + self.FullURL)

        webcontent = self.getWebScrape()
        for index in xrange(len(self.RegEx)):
            websitecontent = self.getContentList(webcontent, index)
            if websitecontent:
                self.addMultiResults(websitecontent, index)

    def getContentList(self, webcontent, index):
        """
        Retrieves a list of information retrieved from the sites defined
        in the xml configuration file.
        Returns the list of found information from the sites being used
        as resources or returns None if the site cannot be discovered.

        Argument(s):
        webcontent -- actual content of the web page that's been returned
        from a request.
        index -- the integer representing the index of the regex list.

        Return value(s):
        list -- information found from a web site being used as a resource.

        Restriction(s):
        The Method has no restrictions.
        """
        try:
            repattern = re.compile(self.RegEx[index], re.IGNORECASE)
            foundlist = re.findall(repattern, webcontent)
            return foundlist
        except:
            self.postErrorMessage(self.ErrorMessage + " " + self.FullURL)
            return None

class MethodPostSite(Site):
    """
    MethodPostSite inherits from the Site object
    and represents a site that may posts information instead of running a GET initially.

    Public Method(s):
    addMultiResults
    getContentList
    getContent
    postIsNecessary
    submitPost

    Instance variable(s):
    _site
    _postByDefault
    """

    def __init__(self, site):
        """
        Class constructor. Assigns a site from the parameter into the _site
        instance variable. This is a play on the decorator pattern. Also
        assigns the postbydefault parameter to the _postByDefault instance
        variable to determine if the Automater should post information
        to a site. By default Automater will NOT post information.

        Argument(s):
        site -- the site that we will decorate.
        postbydefault -- a Boolean representing whether a post will occur.

        Return value(s):
        Nothing is returned from this Method.
        """
        self._site = site
        super(MethodPostSite, self).__init__(self._site.URL, self._site.WebRetrieveDelay,
                                             self._site.Proxy, self._site.TargetType,
                                             self._site.ReportStringForResult,
                                             self._site.Target, self._site.UserAgent,
                                             self._site.FriendlyName,
                                             self._site.RegEx, self._site.FullURL,
                                             self._site.BotOutputRequested,
                                             self._site.ImportantPropertyString,
                                             self._site.Params, self._site.Headers,
                                             self._site.Method, self._site.PostData, site._verbose)
        self.postMessage(self.UserMessage + " " + self.FullURL)
        SiteDetailOutput.PrintStandardOutput('[-] {url} requires a submission for {target}. '
                                             'Submitting now, this may take a moment.'.
                                             format(url=self._site.URL, target=self._site.Target),
                                             verbose=site._verbose)
        content = self.submitPost()
        if content:
            if not isinstance(self.FriendlyName, basestring):  # this is a multi instance
                self._results = [[] for x in xrange(len(self.RegEx))]
                for index in range(len(self.RegEx)):
                    self.addMultiResults(self.getContentList(content, index), index)
            else:  # this is a single instance
                self.addResults(self.getContentList(content))

    def getContentList(self, content, index=-1):
        """
        Retrieves a list of information retrieved from the sites defined
        in the xml configuration file.
        Returns the list of found information from the sites being used
        as resources or returns None if the site cannot be discovered.

        Argument(s):
        content -- string representation of the web site being used
        as a resource.
        index -- the integer representing the index of the regex list.

        Return value(s):
        list -- information found from a web site being used as a resource.

        Restriction(s):
        The Method has no restrictions.
        """
        try:
            if index == -1: # this is a return for a single instance site
                repattern = re.compile(self.RegEx, re.IGNORECASE)
                foundlist = re.findall(repattern, content)
                return foundlist
            else: # this is the return for a multisite
                repattern = re.compile(self.RegEx[index], re.IGNORECASE)
                foundlist = re.findall(repattern, content)
                return foundlist
        except:
            self.postErrorMessage(self.ErrorMessage + " " + self.FullURL)
            return None
