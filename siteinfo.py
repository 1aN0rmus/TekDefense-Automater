"""
The siteinfo.py module provides site lookup and result
storage for those sites based on the sites.xml config
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
in the sites.xml config file. If that regex is found, it tells the class
that a post is necessary.
PostTransactionAPIKeySite -- Class used to store information from a 
site that has single or multiple results requested and discovered. This
Class is utilized if an API key is provided in the sites.xml
configuration file.

See references to Silent mode in Site class documentation for
inhibiting console output.

Function(s):
No global exportable functions are defined.

Exception(s):
SiteError when Site or a subclass there of is used in Silent mode
"""
import urllib
import urllib2
import time
import re
from operator import attrgetter
from inputs import SitesFile
from utilities import Parser

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

    def __init__(self):
        """
        Class constructor. Simply creates a blank list and assigns it to
        instance variable _sites that will be filled with retrieved info
        from sites defined in the sites.xml configuration file.
        
        Argument(s):
        No arguments are required.
        
        Return value(s):
        Nothing is returned from this Method.
        """
        self._sites = []
        self._targetresultlist = []

    def runSiteAutomation(self, webretrievedelay, targetlist, source, postbydefault,**kwargs):
        """
        Builds site objects representative of each site listed in the sites.xml
        config file. Appends a Site object or one of it's subordinate objects
        to the _sites instance variable so retrieved information can be used.
        Returns nothing.

        Argument(s):
        webretrievedelay -- The amount of seconds to wait between site retrieve
        calls. Default delay is 2 seconds.
        targetlist -- list of strings representing targets to be investigated.
        Targets can be IP Addresses, MD5 hashes, or hostnames.
        source -- String representing a specific site that should only be used
        for investigation purposes instead of all sites listed in the sites.xml
        config file.
        postbydefault -- Boolean value to tell the program if the user wants
        to post data to a site if a post is required. Default is to NOT post.

        Return value(s):
        Nothing is returned from this Method.

        Restriction(s):
        The Method has no restrictions.
        """
        targetresultlist = []
        if SitesFile.fileExists():
            for targ in targetlist:
                sitetree = SitesFile.getXMLTree()
                sitelist = []
                for siteelement in sitetree.iter(tag = "site"):
                    if source == "allsources" or source == siteelement.get("name"):
                    
                        sitetypematch = False
                        targettype = self.identifyTargetType(targ)
                        
                        for st in siteelement.find("sitetype").findall("entry"):
                            if st.text == targettype:
                                sitetypematch = True
                        if sitetypematch:
                            site = Site.buildSiteFromXML(siteelement, webretrievedelay, targettype, targ,silent=kwargs.get('silent', False))
                            if (site.Params != None or site.Headers != None) and site.APIKey != None:
                                s = PostTransactionAPIKeySite(site)
                                self._sites.append(s)
                                sitelist.append(s)
                            elif site.Params != None or site.Headers != None:
                                s = PostTransactionPositiveCapableSite(site, postbydefault)
                                self._sites.append(s)
                                sitelist.append(s)
                            elif isinstance(site.RegEx, basestring):
                                s = SingleResultsSite(site)
                                self._sites.append(s)
                                sitelist.append(s)
                            else:
                                s = MultiResultsSite(site)
                                self._sites.append(s)
                                sitelist.append(s)
                targetresultlist.append(Target(targ,targettype,sites=sitelist))
        self._targetresultlist = targetresultlist
    @property
    def TargetResultList(self):
        return self._targetresultlist

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

    def available_sites(self):
        """
        Builds site objects representative of each site listed in the sites.xml
        config file. Appends a Site object or one of it's subordinate objects
        to the _sites instance variable so retrieved information can be used.
        Returns nothing.
        """
        if SitesFile.fileExists():
            sitetree = SitesFile.getXMLTree()
            sitelist = []
            for siteelement in sitetree.iter(tag = "site"):
                sitelist.append(siteelement.get("name"))

        return sitelist
class SiteError(Exception):
    """
    Custom exception for exceptions rasied from site objects
    """
    def __init__(self, value):
         self.value = value
    def __str__(self):
         return repr(self.value)

class Target(object):
    def __init__(self,target,target_type,sites=[]):
        self._target = target
        self._target_type = target_type
        self._sites = sites
    
    @property
    def Target(self):
        return self._target
    
    @property
    def Target_type(self):
        return self.target_type
    
    @property
    def Sites(self):
        return self._sites
    
class Site(object):
    """
    Site is the parent object that represents each site used
    for retrieving information. Site stores the results
    discovered from each web site discovered when running Automater.
    Site is the parent object to SingleResultsSite, MultiResultsSite,
    PostTransactionPositiveCapableSite, and PostTransactionAPIKeySite.

    Console output can be turned off by setting the Silent property to True
    When in silent mode when errors are encountered a SiteError is raised
    Silent mode can be set in the constructor or in the factory buildSiteFromXML 
    py passing silent=True as a keyword arg.
    
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
    (Property) MessageToPost
    (Property) ErrorMessage
    (Property) UserMessage
    (Property) FullURL
    (Setter) FullURL
    (Property) ImportantPropertyString
    (Property) Params
    (Setter) Params
    (Property) Headers
    (Property) APIKey
    (Property) Target
    (Property) Results
    (Property) Silent
    (Property) ResultType
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
    _friendlyName
    _regex
    _fullURL
    _importantProperty
    _params
    _headers
    _apikey
    _results
    _messagetopost
    _resulttype
    """
    def __init__(self, domainurl, webretrievedelay, targettype, \
                 reportstringforresult, target, friendlyname, regex, fullurl, \
                 importantproperty, params, headers, apikey, resulttype,**kwargs):
        """
        Class constructor. Sets the instance variables based on input from
        the arguments supplied when Automater is run and what the sites.xml
        config file stores.

        Argument(s):
        domainurl -- string defined in sites.xml in the domainurl XML tag.
        webretrievedelay -- the amount of seconds to wait between site retrieve
        calls. Default delay is 2 seconds.
        targettype -- the targettype as defined. Either ip, md5, or hostname.
        reportstringforresult -- string or list of strings that are entered in
        the entry XML tag within the reportstringforresult XML tag in the
        sites.xml configuration file.
        target -- the target that will be used to gather information on.
        friendlyname -- string or list of strings that are entered in
        the entry XML tag within the sitefriendlyname XML tag in the
        sites.xml configuration file.
        regex -- the regexs defined in the entry XML tag within the
        regex XML tag in the sites.xml configuration file.
        fullurl -- string representation of fullurl pulled from the
        sites.xml file in the fullurl XML tag.
        importantproperty -- string defined in the the sites.xml config file
        in the importantproperty XML tag.
        params -- string or list provided in the entry XML tags within the params
        XML tag in the sites.xml configuration file.
        headers -- string or list provided in the entry XML tags within the headers
        XML tag in the sites.xml configuration file.
        apikey -- string or list of strings found in the entry XML tags within
        the apikey XML tag in the sites.xml configuration file.

        Return value(s):
        Nothing is returned from this Method.
        """
        self._sourceurl = domainurl
        self._webretrievedelay = webretrievedelay
        self._targetType = targettype
        self._reportstringforresult = reportstringforresult
        self._errormessage = "[-] Cannot scrape"
        self._usermessage = "[*] Checking"
        self._target = target
        self._friendlyName = friendlyname
        self._regex = regex
        self._fullURL = ""
        self.FullURL = fullurl # call the helper method to clean %TARGET% from fullurl string
        self._importantProperty = importantproperty
        self._params = None
        if params is not None:
            self.Params = params # call the helper method to clean %TARGET% from params string
        if headers is None:
            self._headers = None
        else:
            self._headers = headers
        if apikey is None:
            self._apikey = None
        else:
            self._apikey = apikey
        self._results = []
        self._messagetopost = ""
        self._resulttype = resulttype
        self.Silent = kwargs.get('silent', False)

    @classmethod
    def buildSiteFromXML(self, siteelement, webretrievedelay, targettype, target, **kwargs):
        """
        Utilizes the Class Methods within this Class to build the Site object.
        Returns a Site object that defines results returned during the web
        retrieval investigations.

        Argument(s):
        siteelement -- the siteelement object that will be used as the
        start element.
        webretrievedelay -- the amount of seconds to wait between site retrieve
        calls. Default delay is 2 seconds.
        targettype -- the targettype as defined. Either ip, md5, or hostname.
        target -- the target that will be used to gather information on.

        Return value(s):
        Site object.

        Restriction(s):
        This Method is tagged as a Class Method
        """
        domainurl = siteelement.find("domainurl").text
        reportstringforresult = Site.buildStringOrListfromXML(siteelement, "reportstringforresult")
        sitefriendlyname = Site.buildStringOrListfromXML(siteelement, "sitefriendlyname")
        resulttype = Site.buildStringOrListfromXML(siteelement, "resulttype")
        regex = Site.buildStringOrListfromXML(siteelement, "regex")
        fullurl = siteelement.find("fullurl").text
        importantproperty = Site.buildStringOrListfromXML(siteelement, "importantproperty")
        params = Site.buildDictionaryFromXML(siteelement, "params")
        headers = Site.buildDictionaryFromXML(siteelement, "headers")
        apikey = Site.buildStringOrListfromXML(siteelement, "apikey")
        return Site(domainurl, webretrievedelay, targettype, reportstringforresult, target, \
                    sitefriendlyname, regex, fullurl, importantproperty, params, headers, apikey, \
                    resulttype,silent=kwargs.get('silent', False))

    @classmethod
    def buildStringOrListfromXML(self, siteelement, elementstring):
        """
        Takes in a siteelement and then elementstring and builds a string
        or list from multiple entry XML tags defined in the sites.xml config
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
        from multiple entry XML tags defined in the sites.xml config file.
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
        if len(siteelement.find(elementstring).findall("entry")) > 0:
            variablename = {}
            for entry in siteelement.find(elementstring).findall("entry"):
                variablename[entry.get("key")] = entry.text
        else:
            return None
        return variablename

    @property
    def ResultType(self):
        self._resulttype
    
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
    def RegEx(self):
        """
        Returns the string representing a regular expression
        required to retrieve the information being investigated.

        Argument(s):
        No arguments are required.

        Return value(s):
        string -- representing a regex used to find info on the site.

        Restriction(s):
        This Method is tagged as a Property.
        """
        return self._regex

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
    def MessageToPost(self):
        """
        Returns the string representing a message to the user.

        Argument(s):
        No arguments are required.

        Return value(s):
        string -- representing a message to print to
        the standard output.

        Restriction(s):
        This Method is tagged as a Property.
        """    
        return self._messagetopost

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
        instance variable _fullURL if it does after replaceing the target
        information where the keyword %TARGET% is used. This keyword will
        be used in the sites.xml configuration file where the user wants
        the target information to be placed in the URL.

        Argument(s):
        fullurl -- string representation of fullurl pulled from the
        sites.xml file in the fullurl XML tag.

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
    def ImportantPropertyString(self):
        """
        Returns the string representing the Important Property
        that the user wants the site to report. This is set using
        the sites.xml config file in the importantproperty XML tag.

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
        parameters where required maekred with the %TARGET% keyword
        in the sites.xml config file.

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

    @property
    def APIKey(self):
        """
        Determines if an APIKey was set for this specific site.
        Returns the string representing the APIKey using the
        _apikey instance variable or returns None if the instance
        variable is empty or not set.

        Argument(s):
        No arguments are required.

        Return value(s):
        string -- representation of the APIKey from the _apikey
        instance variable.

        Restriction(s):
        This Method is tagged as a Property.
        """
        if self._apikey is None:
            return None
        if len(self._apikey) == 0:
            return None
        return self._apikey

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
        Prints multiple messages to inform the user of progress. Assignes
        the _messagetopost instance variable to the message. Uses the
        MessageToPost property.

        Argument(s):
        message -- string to be utilized as a message to post.

        Return value(s):
        Nothing is returned from this Method.

        Restriction(s):
        The Method has no restrictions.
        """
        
        self._messagetopost = message
        if not self.Silent:
            print self.MessageToPost

    def getImportantProperty(self, index):
        """
        Gets the property information from the property value listed in the
        sites.xml file for that specific site in the importantproperty xml tag.
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

    def getWebScrape(self):
        """
        Attempts to retrieve a string from a web site. String retrieved is
        the entire web site including HTML markup.
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
        proxy = urllib2.ProxyHandler()
        opener = urllib2.build_opener(proxy)
        try:
            response = opener.open(self.FullURL)
            content = response.read()
            contentString = str(content)
            time.sleep(delay)
            return contentString
        except:
            self.postMessage('[-] Cannot connect to ' + self.FullURL)

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
        super(SingleResultsSite, self).__init__(self._site.URL, self._site.WebRetrieveDelay, self._site.TargetType,\
                                               self._site.ReportStringForResult, self._site.Target, \
                                               self._site.FriendlyName, self._site.RegEx, self._site.FullURL, \
                                               self._site.ImportantPropertyString, self._site.Params, \
                                                self._site.Headers, self._site.APIKey,self._site._resulttype,silent=self._site.Silent)
        self.postMessage(self.UserMessage + " " + self.FullURL)
        websitecontent = self.getContentList()
        if websitecontent is not None:
            self.addResults(websitecontent)

    def getContentList(self):
        """
        Retrieves a list of information retrieved from the sites defined
        in the sites.xml configuration file.
        Returns the list of found information from the sites being used
        as resources or returns None if the site cannot be discovered.

        Argument(s):
        No arguments are required.

        Return value(s):
        list -- information found from a web site being used as a resource.

        Restriction(s):
        The Method has no restrictions.
        """
        try:
            content = self.getWebScrape()
            repattern = re.compile(self.RegEx, re.IGNORECASE)
            foundlist = re.findall(repattern, content)
            return foundlist
        except:
            message = self.ErrorMessage + " " + self.FullURL
            if self.Silent:
                raise SiteError(message)
            else:
                self.postMessage(message)
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
        super(MultiResultsSite,self).__init__(self._site.URL, self._site.WebRetrieveDelay, self._site.TargetType,\
                                              self._site.ReportStringForResult, self._site.Target, \
                                              self._site.FriendlyName, self._site.RegEx, self._site.FullURL, \
                                              self._site.ImportantPropertyString, self._site.Params, \
                                              self._site.Headers, self._site._resulttype,self._site.APIKey,silent=self._site.Silent)        
        self._results = [[] for x in xrange(len(self._site.RegEx))]
        self.postMessage(self.UserMessage + " " + self.FullURL)
        for index in range(len(self.RegEx)):
            websitecontent = self.getContentList(index)
            if websitecontent is not None:
                self.addResults(websitecontent, index)

    def addResults(self, results, index):
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

    def getContentList(self, index):
        """
        Retrieves a list of information retrieved from the sites defined
        in the sites.xml configuration file.
        Returns the list of found information from the sites being used
        as resources or returns None if the site cannot be discovered.

        Argument(s):
        index -- the integer representing the index of the regex list.

        Return value(s):
        list -- information found from a web site being used as a resource.

        Restriction(s):
        The Method has no restrictions.
        """
        try:
            content = self.getWebScrape()
            repattern = re.compile(self.RegEx[index], re.IGNORECASE)
            foundlist = re.findall(repattern, content)
            return foundlist
        except:
            message = self.ErrorMessage + " " + self.FullURL
            if self.Silent:
                raise SiteError(message)
            else:
                self.postMessage(message)
            
        return None

class PostTransactionPositiveCapableSite(Site):
    """
    PostTransactionPositiveCapableSite inherits from the Site object
    and represents a site that may need to post information.

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

    def __init__(self, site, postbydefault):
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
        self._postByDefault = postbydefault
        # first entry of regexlist is the check - if we find something here (positive), there is no list of regexs and thus
        # we cannot run the post
        if isinstance(self._site.RegEx, basestring):
            return
        else:
            regextofindforpost = self._site.RegEx[0]
            newregexlist = self._site.RegEx[1:]
            super(PostTransactionPositiveCapableSite, self).__init__(self._site.URL, self._site.WebRetrieveDelay, \
                                                                     self._site.TargetType, self._site.ReportStringForResult, \
                                                                     self._site.Target, self._site.FriendlyName, \
                                                                     newregexlist, self._site.FullURL, \
                                                                     self._site.ImportantPropertyString, \
                                                                     self._site.Params, self._site.Headers, \
                                                                     self._site.APIKey, self._site._resulttype,silent=self._site.Silent)            
            self.postMessage(self.UserMessage + " " + self.FullURL)
            content = self.getContent()
            if content != None:
                if self.postIsNecessary(regextofindforpost, content) and self.Params is not None and self.Headers is not None:
                    print '[-] This target requires a submission. Submitting now, this may take a moment.'
                    content = self.submitPost(self.Params, self.Headers)
                else:
                    pass
                if content != None:
                    if not isinstance(self.FriendlyName, basestring):#this is a multi instance
                        self._results = [[] for x in xrange(len(self.RegEx))]
                        for index in range(len(self.RegEx)):
                            self.addMultiResults(self.getContentList(content, index), index)
                    else:#this is a single instance
                        self.addResults(self.getContentList(content))

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

    def getContentList(self, content, index=-1):
        """
        Retrieves a list of information retrieved from the sites defined
        in the sites.xml configuration file.
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
            message = self.ErrorMessage + " " + self.FullURL
            if self.Silent:
                raise SiteError(message)
            else:
                self.postMessage(message)
        return None

    def getContent(self):
        """
        Attempts to retrieve a string from a web site. String retrieved is
        the entire web site including HTML markup.
        Returns the string representing the entire web site including the
        HTML markup retrieved from the site.

        Argument(s):
        No arguments are required.

        Return value(s):
        string.

        Restriction(s):
        The Method has no restrictions.
        """
        try:
            content = self.getWebScrape()
            return content
        except:
            message = self.ErrorMessage + " " + self.FullURL
            if self.Silent:
                raise SiteError(message)
            else:
                self.postMessage(message)
            return None

    def postIsNecessary(self, regex, content):
        """
        Checks to determine if the user wants the Automater to post information
        if the site takes a post. The user does this through the argument
        switch --p. By default this is False. If the regex given is found
        on the site, and a post is requested, a post will be attempted.
        Returns True if --p is used and a regex is found on the site, else
        return False.

        Argument(s):
        regex -- string regex that will be searched for on the web site used
        as a resource.
        content -- string that contains entire web site being used as a
        resource including HTML markup information.

        Return value(s):
        Boolean.

        Restriction(s):
        The Method has no restrictions.
        """
        # check if the user set to post or not on the cmd line
        if not self._postByDefault:
            return False
        else:
            repattern = re.compile(regex, re.IGNORECASE)
            found = re.findall(repattern, content)
            if found:
                return True
            else:
                return False
        # here to catch any fall through
        return False

    def submitPost(self, raw_params, headers):
        """
        Submits information to a web site being used as a resource that
        requires a post of information.
        Returns a string that contains entire web site being used as a
        resource including HTML markup information.

        Argument(s):
        raw_params -- string info detailing parameters provided from
        sites.xml configuration file in the params XML tag.
        headers -- string info detailing headers provided from
        sites.xml configuration file in the headers XML tag.

        Return value(s):
        string -- contains entire web site being used as a
        resource including HTML markup information.

        Restriction(s):
        The Method has no restrictions.
        """
        try:
            url = (self.URL)
            params = urllib.urlencode(raw_params)
            request = urllib2.Request(url, params, headers)
            page = urllib2.urlopen(request)
            page = page.read()
            content = str(page)
            return content
        except:
            message = self.ErrorMessage + " " + self.FullURL
            if self.Silent:
                raise SiteError(message)
            else:
                self.postMessage(message)
        return None

class PostTransactionAPIKeySite(Site):
    """
    PostTransactionAPIKeySite inherits from the Site object
    and represents a site that needs an API Key for discovering
    information.

    Public Method(s):
    addMultiResults
    getContentList
    submitPost

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
        super(PostTransactionAPIKeySite,self).__init__(self._site.URL, self._site.WebRetrieveDelay, self._site.TargetType, \
                                                       self._site.ReportStringForResult, self._site.Target, \
                                                       self._site.FriendlyName, self._site.RegEx, self._site.FullURL, \
                                                       self._site.ImportantPropertyString, self._site.Params, \
                                                       self._site.Headers, self._site.APIKey,self._site._resulttype, silent=self._site.Silent)
        self.postMessage(self.UserMessage + " " + self.FullURL)
        content = self.submitPost(self.Params, self.Headers)
        if content != None:
            if not isinstance(self.FriendlyName, basestring):#this is a multi instance
                self._results = [[] for x in xrange(len(self.RegEx))]
                for index in range(len(self.RegEx)):
                    self.addMultiResults(self.getContentList(content, index), index)
            else:#this is a single instance
                self.addResults(self.getContentList(content))

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

    def getContentList(self, content, index = -1):
        """
        Retrieves a list of information retrieved from the sites defined
        in the sites.xml configuration file.
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
            message = self.ErrorMessage + " " + self.FullURL
            if self.Silent:
                raise SiteError(message)
            else:
                self.postMessage(message)
        return None

    def submitPost(self, raw_params, headers):
        """
        Submits information to a web site being used as a resource that
        requires a post of information.
        Returns a string that contains entire web site being used as a
        resource including HTML markup information.

        Argument(s):
        raw_params -- string info detailing parameters provided from
        sites.xml configuration file in the params XML tag.
        headers -- string info detailing headers provided from
        sites.xml configuration file in the headers XML tag.

        Return value(s):
        string -- contains entire web site being used as a
        resource including HTML markup information.

        Restriction(s):
        The Method has no restrictions.
        """
        try:
            url = (self.FullURL)
            params = urllib.urlencode(raw_params)
            request = urllib2.Request(url, params, headers)
            page = urllib2.urlopen(request)
            page = page.read()
            content = str(page)
            return content
        except:
            message = self.ErrorMessage + " " + self.FullURL
            if self.Silent:
                raise SiteError(message)
            else:
                self.postMessage(message)
        return None
