from siteinfo import SiteFacade
from utilities import IPWrapper
from operator import attrgetter
from threading import Thread

__VERSION__ = '0.21'
__GITLOCATION__ = 'https://github.com/1aN0rmus/TekDefense-Automater'
__GITFILEPREFIX__ = 'https://raw.githubusercontent.com/1aN0rmus/TekDefense-Automater/master/'

class Automater():
    def __init__(self, Proxy=None):
        self.sourcelist = ['allsources']
        self.Target = []
        self.Proxy = Proxy
        self.Verbose = False
        self.VersionCheck = False
        self.UserAgent = 'CITDB/1.0'
        self.hasBotOut = True
        self.RefreshRemoteXML = True

        #Delay used for accessing sites.
        self.Delay = 2

    def GetResults(self, Target):
        targetlist = []
        resultList = []
        for tgt in Target:
            tgt = tgt.replace('[.]', '.').replace('{.}', '.').replace('(.)', '.')
            if IPWrapper.isIPorIPList(tgt):
                for targ in IPWrapper.getTarget(tgt):
                    targetlist.append(targ)
            else:
                targetlist.append(tgt)

        sitefac = SiteFacade(self.Verbose)
        sitefac.runSiteAutomation(self.Delay, self.Proxy, Target, self.sourcelist, self.UserAgent, self.hasBotOut,
                                  self.RefreshRemoteXML, __GITLOCATION__)

        sites = sorted(sitefac.Sites, key=attrgetter('Target'))

        if sites is not None:
            for site in sites:
                if not isinstance(site._regex,basestring): #this is a multisite:
                    for index in range(len(site.RegEx)): #the regexs will ensure we have the exact number of lookups
                        siteimpprop = site.getImportantProperty(index)
                        if siteimpprop is None or len(siteimpprop)==0:
                            continue
                        else:
                            if siteimpprop[index] is None or len(siteimpprop[index])==0:
                                continue
                            else:
                                laststring = ""
                                #if it's just a string we don't want it to output like a list
                                if isinstance(siteimpprop, basestring):
                                    tgt = site.Target
                                    typ = site.TargetType
                                    source = site.FriendlyName
                                    res = siteimpprop
                                    if "" + tgt + typ + source + res != laststring:
                                        resultList.append([tgt,typ,source,res])
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
                                            resultList.append([tgt,typ,source,res])
                                            laststring = "" + tgt + typ + source + str(res)
                else:#this is a singlesite
                    siteimpprop = site.getImportantProperty(0)
                    if siteimpprop is None or len(siteimpprop)==0:
                        continue
                    else:
                        laststring = ""
                        #if it's just a string we don't want it output like a list
                        if isinstance(siteimpprop, basestring):
                            tgt = site.Target
                            typ = site.TargetType
                            source = site.FriendlyName
                            res = siteimpprop
                            if "" + tgt + typ + source + res != laststring:
                                resultList.append([tgt,typ,source,res])
                                laststring = "" + tgt + typ + source + res
                        else:
                            laststring = ""
                            for siteresult in siteimpprop:
                                tgt = site.Target
                                typ = site.TargetType
                                source = site.FriendlyName
                                res = siteresult
                                if "" + tgt + typ + source + str(res) != laststring:
                                    resultList.append([tgt,typ,source,res])
                                    laststring = "" + tgt + typ + source + str(res)
        return resultList

    def hasProxy(self):
        if self.Proxy:
            return True
        else:
            return False

if __name__ == '__main__':
    c = Automater()
    print c.GetResults(['199.116.248.115'])
