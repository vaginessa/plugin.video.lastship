# -*- coding: utf-8 -*-

import re, urllib
import requests
import simplejson
from resources.lib.modules import cleantitle
from resources.lib.modules import dom_parser


class source:
    def __init__(self):
        self.priority = 1
        self.language = ['de']    

    def movie(self, imdb, title, localtitle, aliases, year):
        try:
            title=cleantitle.getsearch(localtitle) 
            r = requests.get("https://api.watchbox.de/v1/search/?page=1&maxPerPage=28&active=true&type=film&term=" + urllib.quote_plus(title))                        
            data = r.json()
            url=""
            
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
        try:
            r = requests.get("https://api.watchbox.de/v1/search/?page=1&maxPerPage=28&active=true&type=serie&term=" + urllib.quote_plus(tvshowtitle))            
            data = r.json()
            url=""

        #print "print WB search title",title,year
            for i in data['items']:
                if i['type']=="serie":
                    #print "print titel",i['formatTitle'].encode("utf-8"),tvshowtitle,localtvshowtitle#,i['entityId'],i['productionYear'],i['seoPath'], year,type(year)
                    if int(i['productionYear']) == int(year) or int(i['productionYear']) == int(year)+1 or int(i['productionYear']) == int(year)-1:                    
                        #print "print year match",cleantitle.getsearch(i['formatTitle'].encode("utf-8")), tvshowtitle
                        if cleantitle.getsearch(i['formatTitle'].encode("utf-8")) in tvshowtitle.lower() or tvshowtitle.lower() in cleantitle.getsearch(i['formatTitle'].encode("utf-8")):                        
                            url="https://www.watchbox.de/serien/" + str(i['seoPath']) + "-" + str(i['entityId'])                            
                            break 
            return url
        except:
            return

    def episode(self, url, imdb, tvdb, title, premiered, season, episode):        
        try:
            
            html = requests.get(url)            
            links = dom_parser.parse_dom(html.content, 'article', attrs={'class': 'row'})[0]            
            links = dom_parser.parse_dom(links, 'section')            
            links = [dom_parser.parse_dom(i, 'a')[0] for i in links if 'Staffel %s, Episode %s' % (season, episode) in i.content]            
            url = "https://www.watchbox.de" + links[0].attrs['href']
            return url
        except:
            return
            

    def sources(self, url, hostDict, hostprDict):
        sources = []
        
        try:
            if not url:
                return sources
            
            html = requests.get(url)            
            url_regex = "hls.*?(http.*?m3u8)"
            link = re.findall(url_regex, html.content)            
            link=link[0].replace("\\","")   
            sources.append({'source': 'CDN', 'quality': 'HD', 'language': 'de', 'url': link, 'direct': True, 'debridonly': False,'info': 'Low qHD 960x540'})
           
            return sources
        except:
            return sources

    def resolve(self, url): 
        return url

   
        
   
