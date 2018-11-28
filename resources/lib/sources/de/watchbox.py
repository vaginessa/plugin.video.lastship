# -*- coding: utf-8 -*-

import re, urllib
import requests
import simplejson
from resources.lib.modules import cleantitle


class source:
    def __init__(self):
        self.priority = 1
        self.language = ['de']
        
        #'https://api.watchbox.de/v1/search/?active=true&maxPerPage=28&page=1&term=Gamer&types=serie'
    

    def movie(self, imdb, title, localtitle, aliases, year):
        try:
            title=cleantitle.getsearch(localtitle) 
            r = requests.get("https://api.watchbox.de/v1/search/?page=1&maxPerPage=28&active=true&type=film&term=" + urllib.quote_plus(title))
            #print "print WB search response",r,r.content
            
            data = r.json()
            url=""

            #print "print WB search title",title,year
            for i in data['items']:            
                #print "print titelname & titel",i['formatTitle'].encode("utf-8"),i['entityId'],i['productionYear'],i['seoPath'], year,type(year)
                if int(i['productionYear']) == int(year) or int(i['productionYear']) == int(year)+1 or int(i['productionYear']) == int(year)-1:                    
                    if cleantitle.getsearch(i['formatTitle'].encode("utf-8")) in title or title in cleantitle.getsearch(i['formatTitle'].encode("utf-8")):                        
                        url="https://www.watchbox.de/filme/" + str(i['seoPath']) + "-" + str(i['entityId'])                        
                        break             
            return url
        except:
            return

    def tvshow(self, imdb, tvdb, tvshowtitle, localtvshowtitle, aliases, year):

        
                
        return url

    def episode(self, url, imdb, tvdb, title, premiered, season, episode):
        return url
        

    def sources(self, url, hostDict, hostprDict):
        sources = []
        
        try:
            if not url:
                return sources

            
            html = requests.get(url)
            print "print WB reqeust get",html#,html.content
            url_regex = "hls.*?(http.*?m3u8)"
            link = re.findall(url_regex, html.content)
            print "print WB request find url",link[0].replace("\\","")
            link=link[0].replace("\\","")
            
            

            
            sources.append({'source': 'CDN', 'quality': 'HD', 'language': 'de', 'url': link, 'direct': True, 'debridonly': False,'info': 'Low qHD 960x540'})
           
            return sources
        except:
            return sources

    def resolve(self, url):        

        return url

   
        
   
