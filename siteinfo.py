import urllib, urllib2, time, re
from operator import attrgetter
from inputs import SitesFile
from utilities import Parser

class SiteFacade(object):
    def __init__(self):
        self._sites = []
        
    def runSiteAutomation(self,webretrievedelay,targetlist,source,postbydefault):
        #SingleResultsSite(String URL, Int Delay, String TargetType, String ReportStringForResults, String Target, String SiteFriendlyName,
                          #String RegEx, String FullUrlToSubmitToSite,String ImportantAttributeForSiteToReport,Dict Parameters, 
                          #Dict Headers)
        
        if SitesFile.fileExists():
            sitetree = SitesFile.getXMLTree()
            for siteelement in sitetree.iter(tag="site"):
                if source == "allsources" or source == siteelement.get("name"):
                    for targ in targetlist:
                        sitetypematch=False
                        targettype = self.identifyTargetType(targ)
                        for st in siteelement.find("sitetype").findall("entry"):
                            if st.text==targettype:
                                sitetypematch=True
                        if sitetypematch:
                            site = Site.buildSiteFromXML(siteelement,webretrievedelay,targettype,targ)
                            if (site.Params != None or site.Headers != None) and site.APIKey != None:
                                self._sites.append(PostTransactionAPIKeySite(site))                            
                            elif site.Params != None or site.Headers != None:
                                self._sites.append(PostTransactionPositiveCapableSite(site,postbydefault))
                            elif isinstance(site.RegEx,basestring):
                                self._sites.append(SingleResultsSite(site))                            
                            else:
                                self._sites.append(MultiResultsSite(site))
        
    @property    
    def Sites(self):
        if self._sites is None or len(self._sites) == 0:
            return None
        return self._sites
    
    # Identify if the target is an IP, URL, or HASH
    def identifyTargetType(self,target):
        ipAddress = re.compile('\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}', re.IGNORECASE)
        ipFind = re.findall(ipAddress,target)
        if ipFind is not None and len(ipFind) > 0:
            return "ip"
    
        md5 = re.compile('[a-fA-F0-9]{32}', re.IGNORECASE)
        md5Find = re.findall(md5,target)
        if md5Find is not None and len(md5Find) > 0:
            return "md5"
        
        return "hostname"            

class Site(object):
    def __init__(self,domainurl,webretrievedelay,targettype,reportstringforresult,target,friendlyname,regex,fullurl,importantproperty,params,headers,apikey):
        self._sourceurl = domainurl
        self._webretrievedelay=webretrievedelay
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
    
    @classmethod
    def buildSiteFromXML(self,siteelement,webretrievedelay,targettype,target):
        domainurl = siteelement.find("domainurl").text
        reportstringforresult = Site.buildStringOrListfromXML(siteelement,"reportstringforresult")
        sitefriendlyname = Site.buildStringOrListfromXML(siteelement,"sitefriendlyname")
        regex = Site.buildStringOrListfromXML(siteelement,"regex")
        fullurl = siteelement.find("fullurl").text
        importantproperty = Site.buildStringOrListfromXML(siteelement,"importantproperty")
        params = Site.buildDictionaryFromXML(siteelement,"params")
        headers = Site.buildDictionaryFromXML(siteelement,"headers")
        apikey = Site.buildStringOrListfromXML(siteelement,"apikey")
        return Site(domainurl,webretrievedelay,targettype,reportstringforresult,target,sitefriendlyname,regex,fullurl,importantproperty,params,headers,apikey)
        
    @classmethod
    def buildStringOrListfromXML(self,siteelement,elementstring):
        variablename = ""
        if len(siteelement.find(elementstring).findall("entry"))==0:
            return None
        
        if len(siteelement.find(elementstring).findall("entry"))>1:
            variablename = []
            for entry in siteelement.find(elementstring).findall("entry"):
                variablename.append(entry.text)
        else:
            variablename = ""
            variablename = siteelement.find(elementstring).find("entry").text
        return variablename

    @classmethod
    def buildDictionaryFromXML(self,siteelement,elementstring):
        variablename = ""
        if len(siteelement.find(elementstring).findall("entry"))>0:
            variablename = {}
            for entry in siteelement.find(elementstring).findall("entry"):
                variablename[entry.get("key")] =  entry.text
        else:
            return None
        return variablename    
        
    
    @property
    def WebRetrieveDelay(self):
        return self._webretrievedelay
    
    @property    
    def TargetType(self):
        return self._targetType    
    
    @property    
    def ReportStringForResult(self):
        return self._reportstringforresult
    
    @property    
    def FriendlyName(self):
        return self._friendlyName   
    
    @property
    def RegEx(self):
        return self._regex
    
    @property    
    def URL(self):
        return self._sourceurl
    
    @property
    def MessageToPost(self):
        return self._messagetopost    
    
    @property
    def ErrorMessage(self):
        return self._errormessage
    
    @property
    def UserMessage(self):
        return self._usermessage
    
    @property
    def FullURL(self):
        return self._fullURL
    
    @FullURL.setter           
    def FullURL(self,fullurl):
        if len(fullurl) > 0:
            fullurlreplaced = fullurl.replace("%TARGET%",self._target)
            self._fullURL = fullurlreplaced
        else:
            self._fullURL = ""    

    @property    
    def ImportantPropertyString(self):
        return self._importantProperty
    
    @property
    def Params(self):
        if self._params is None:
            return None
        if len(self._params) == 0:
            return None
        return self._params
    
    @Params.setter           
    def Params(self,params):
        if len(params) > 0:
            for key in params:
                if params[key] == "%TARGET%":
                    params[key] = self._target
            self._params = params
        else:
            self._params = None
    
    @property
    def Headers(self):
        if self._headers is None:
            return None
        if len(self._headers) == 0:
            return None
        return self._headers
    
    @property
    def APIKey(self):
        if self._apikey is None:
            return None
        if len(self._apikey) == 0:
            return None
        return self._apikey

    @property            
    def Target(self):
        return self._target
    
    @property
    def Results(self):
        if self._results is None or len(self._results) == 0:
            return None
        return self._results    
    
    def addResults(self,results):
        #if no return from site, seed the results with an empty list
        if results is None or len(results) == 0:
            self._results = None
        else:
            self._results = results
            
    def postMessage(self,message):
        self._messagetopost = message
        print self.MessageToPost
    
    def getImportantProperty(self,index):
        if isinstance(self._importantProperty,basestring):
            siteimpprop = getattr(self,"get"+self._importantProperty,Site.getResults)
        else:
            siteimpprop = getattr(self,"get"+self._importantProperty[index],Site.getResults)
        return siteimpprop()
    
    def getTarget(self):
        return self.Target
    
    def getResults(self):
        return self.Results
    
    def getFullURL(self):
        return self.FullURL   
       
# Function to pull content from a website
    def getWebScrape(self):
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
    def __init__(self,site):
        self._site = site
        super(SingleResultsSite,self).__init__(self._site.URL,self._site.WebRetrieveDelay,self._site.TargetType,\
                                               self._site.ReportStringForResult,self._site.Target,self._site.FriendlyName,self._site.RegEx,\
                                               self._site.FullURL,self._site.ImportantPropertyString,self._site.Params,self._site.Headers,self._site.APIKey)
        self.postMessage(self.UserMessage + " " + self.FullURL)
        websitecontent = self.getContentList()
        if websitecontent is not None:
            self.addResults(websitecontent)
    
    def getContentList(self):
        try:
            content = self.getWebScrape()
            repattern = re.compile(self.RegEx, re.IGNORECASE)
            foundlist = re.findall(repattern,content)
            return foundlist
        except:
            self.postMessage(self.ErrorMessage + " " + self.FullURL)
            return None


class MultiResultsSite(Site):
    def __init__(self,site):
        self._site = site        
        super(MultiResultsSite,self).__init__(self._site.URL,self._site.WebRetrieveDelay,self._site.TargetType,\
                                              self._site.ReportStringForResult,self._site.Target,self._site.FriendlyName,self._site.RegEx,\
                                              self._site.FullURL,self._site.ImportantPropertyString,self._site.Params,self._site.Headers,self._site.APIKey)        
        self._results = [[] for x in xrange(len(self._site.RegEx))]
        self.postMessage(self.UserMessage + " " + self.FullURL)
        for index in range(len(self.RegEx)):
            websitecontent = self.getContentList(index)
            if websitecontent is not None:
                self.addResults(websitecontent,index)            
        
    def addResults(self,results,index):
        #if no return from site, seed the results with an empty list
        if results is None or len(results) == 0:
            self._results[index] = None
        else:
            self._results[index] = results    
        
    def getContentList(self,index):
        try:
            content = self.getWebScrape()
            repattern = re.compile(self.RegEx[index], re.IGNORECASE)
            foundlist = re.findall(repattern,content)
            return foundlist
        except:
            self.postMessage(self.ErrorMessage + " " + self.FullURL)
            return None
        
class PostTransactionPositiveCapableSite(Site):
    def __init__(self,site,postbydefault):
        self._site = site
        self._postByDefault = postbydefault
        #first entry of regexlist is the check - if we find something here (positive), there is no list of regexs and thus
        #we cannot run the post
        if isinstance(self._site.RegEx,basestring):
            return
        else:
            regextofindforpost = self._site.RegEx[0]
            newregexlist = self._site.RegEx[1:]
            super(PostTransactionPositiveCapableSite,self).__init__(self._site.URL,self._site.WebRetrieveDelay,self._site.TargetType,\
                                                  self._site.ReportStringForResult,self._site.Target,\
                                                  self._site.FriendlyName,newregexlist,self._site.FullURL,\
                                                  self._site.ImportantPropertyString,self._site.Params,self._site.Headers,self._site.APIKey)            
            self.postMessage(self.UserMessage + " " + self.FullURL)
            content = self.getContent()
            if content != None:
                if self.postIsNecessary(regextofindforpost,content) and self.Params is not None and self.Headers is not None:
                    print '[-] This target requires a submission. Submitting now, this may take a moment.'
                    content = self.submitPost(self.Params,self.Headers)
                else:
                    pass
                if content != None:
                    if not isinstance(self.FriendlyName,basestring):#this is a multi instance
                        self._results = [[] for x in xrange(len(self.RegEx))]
                        for index in range(len(self.RegEx)):
                            self.addMultiResults(self.getContentList(content,index),index)
                    else:#this is a single instance
                        self.addResults(self.getContentList(content))

    def addMultiResults(self,results,index):
        #if no return from site, seed the results with an empty list
        if results is None or len(results) == 0:
            self._results[index] = None
        else:
            self._results[index] = results     

    def getContentList(self,content,index=-1):
        try:
            if index==-1:#this is a return for a single instance site
                repattern = re.compile(self.RegEx, re.IGNORECASE)
                foundlist = re.findall(repattern,content)
                return foundlist                
            else:#this is the return for a multisite
                repattern = re.compile(self.RegEx[index], re.IGNORECASE)
                foundlist = re.findall(repattern,content)
                return foundlist
        except:
            self.postMessage(self.ErrorMessage + " " + self.FullURL)
            return None        
    
    def getContent(self):
        try:
            content = self.getWebScrape()
            return content
        except:
            self.postMessage(self.ErrorMessage + " " + self.FullURL)
            return None
    
    def postIsNecessary(self,regex,content):
        #check if the user set to post or not on the cmd line
        if not self._postByDefault:
            return False
        else:
            repattern = re.compile(regex, re.IGNORECASE)
            found = re.findall(repattern,content)
            if found:
                return True
            else:
                return False
        #here to catch any fall through
        return False
    
    def submitPost(self,raw_params,headers):
        try:
            url = (self.URL)
            params = urllib.urlencode(raw_params)
            request = urllib2.Request(url,params,headers)
            page = urllib2.urlopen(request)
            page = page.read()
            content = str(page)
            return content
        except:
            self.postMessage(self.ErrorMessage + " " + self.FullURL)
            return None

class PostTransactionAPIKeySite(Site):
    def __init__(self,site):
        self._site = site
        super(PostTransactionAPIKeySite,self).__init__(self._site.URL,self._site.WebRetrieveDelay,self._site.TargetType,\
                                              self._site.ReportStringForResult,self._site.Target,\
                                              self._site.FriendlyName,self._site.RegEx,self._site.FullURL,\
                                              self._site.ImportantPropertyString,self._site.Params,self._site.Headers,self._site.APIKey)            
        self.postMessage(self.UserMessage + " " + self.FullURL)
        content = self.submitPost(self.Params,self.Headers)
        if content != None:
            if not isinstance(self.FriendlyName,basestring):#this is a multi instance
                self._results = [[] for x in xrange(len(self.RegEx))]
                for index in range(len(self.RegEx)):
                    self.addMultiResults(self.getContentList(content,index),index)
            else:#this is a single instance
                self.addResults(self.getContentList(content))

    def addMultiResults(self,results,index):
        #if no return from site, seed the results with an empty list
        if results is None or len(results) == 0:
            self._results[index] = None
        else:
            self._results[index] = results     

    def getContentList(self,content,index=-1):
        try:
            if index==-1:#this is a return for a single instance site
                repattern = re.compile(self.RegEx, re.IGNORECASE)
                foundlist = re.findall(repattern,content)
                return foundlist                
            else:#this is the return for a multisite
                repattern = re.compile(self.RegEx[index], re.IGNORECASE)
                foundlist = re.findall(repattern,content)
                return foundlist
        except:
            self.postMessage(self.ErrorMessage + " " + self.FullURL)
            return None
    
    def submitPost(self,raw_params,headers):
        try:
            url = (self.FullURL)
            params = urllib.urlencode(raw_params)
            request = urllib2.Request(url,params,headers)
            page = urllib2.urlopen(request)
            page = page.read()
            content = str(page)
            return content
        except:
            self.postMessage(self.ErrorMessage + " " + self.FullURL)
            return None
