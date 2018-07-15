# -*- coding: utf-8 -*-

import xbmc

import requests
from resources.lib.modules import source_faultlog

from resources.lib.modules import cleantitle

BaseUrl = 'https://www.amazon.de'
ATVUrl = 'https://atv-ps-eu.amazon.de'
MarketID = 'A1PA6795UKMFR9'
pkg = 'com.fivecent.amazonvideowrapper'
act = ''

class source:
    def __init__(self):
        self.priority = 1
        self.language = ['de']    

    def movie(self, imdb, title, localtitle, aliases, year):
        try:
            url = self.__search(localtitle,year)                    
            return url
        except:
            return url

    def tvshow(self, imdb, tvdb, tvshowtitle, localtvshowtitle, aliases, year):
        url=cleantitle.getsearch(localtvshowtitle)    
        return url

    def episode(self, url, imdb, tvdb, title, premiered, season, episode):        
        localtitle=url    

        url="https://atv-ps-eu.amazon.de/cdp/catalog/Search?firmware=fmw:17-app:2.0.45.1210&deviceTypeID=A2M4YX06LWP8WI&deviceID=1&format=json&version=2&formatVersion=3&marketplaceId=A1PA6795UKMFR9&IncludeAll=T&AID=1&searchString="+localtitle+"&OfferGroups=B0043YVHMY&SuppressBlackedoutEST=T&NumberOfResults=40&StartIndex=0"
        
        easin="empty"
        data = requests.get(url).json()
       
        for i in data['message']['body']['titles']:           
            
            if localtitle in cleantitle.getsearch(str(i['ancestorTitles'][0]['title'])):
                
                if str(season) == str(i['number']):
                    easin=str(i['childTitles'][0]['feedUrl'])
                    
                    break;
                        

       
        url="https://atv-ps-eu.amazon.de/cdp/catalog/Browse?firmware=fmw:17-app:2.0.45.1210&deviceTypeID=A2M4YX06LWP8WI&deviceID=d24ff55e99d2e8d6353cd941f9f63fbb3d242b92576e09b6b8a90660&format=json&version=2&formatVersion=3&marketplaceId=A1PA6795UKMFR9&IncludeAll=T&AID=1&version=2&"+easin
        
        data = requests.get(url).json()
        
        for i in data['message']['body']['titles']:            
            if str(episode)==str(i['number']):
                return url

    def sources(self, url, hostDict, hostprDict):
        sources = []
        
        try:
            if not url:
                return sources

            
            sources.append({'source': 'Prime', 'quality': '4K', 'language': 'de', 'url': BaseUrl+url, 'info': '', 'direct': True, 'debridonly': False})
           
            return sources
        except:
            return sources

    def resolve(self, url):
        
        url = self.__amazon(url)

        return url

    def __search(self, localtitle,year):
        try:
            localtitle=cleantitle.getsearch(localtitle)
        
            query="https://atv-ps-eu.amazon.de/cdp/catalog/Search?firmware=fmw:17-app:2.0.45.1210&deviceTypeID=A2M4YX06LWP8WI&deviceID=1&format=json&version=2&formatVersion=3&marketplaceId=A1PA6795UKMFR9&IncludeAll=T&AID=1&searchString="+str(localtitle)+"&NumberOfResults=10&StartIndex=0&Detailed=T"

            data = requests.get(query).json()


            for i in data['message']['body']['titles']:
                jahr=str(i['releaseOrFirstAiringDate']['valueFormatted'])
                print "print AP Titel &Jahr",jahr,i['title']
                if str(year)==jahr[0:4]:
                    prime=i['formats'][0]['offers'][0]['offerType']

                    if prime == "SUBSCRIPTION":
                        asin = data['message']['body']['titles'][0]['titleId']

                    break;

            return asin
        except:
            try:
                source_faultlog.logFault(__name__, source_faultlog.tagSearch, asin)
            except:
                return
            return ""

    

    def __amazon(self, url):
        
        url=url.decode('utf-8')        
        url=url.replace("https://www.amazon.de","")
        print "print AP __amazon wrapper, url split2 url, pkg,act",url,pkg,act
        #xbmc.executebuiltin('StartAndroidActivity("%s", "%s", "", "%s")' % (pkg, act, url))
        # return dummy to avoid skipping to next hoster
        xbmc.executebuiltin('RunPlugin("plugin://plugin.video.amazon-test/?mode=PlayVideo&asin=%s")' % url )

        #xbmc.executebuiltin("ActivateWindow(4000,'plugin://plugin.video.amazon-test/?mode=PlayVideo&asin=%s',return)" % url)
        
        return "https://www.amazon.de"
        
