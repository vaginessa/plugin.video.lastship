# -*- coding: utf-8 -*-

import re
import urllib
import requests
import json

from resources.lib.modules import source_utils
from resources.lib.modules import duckduckgo

class source:
    def __init__(self):
        self.priority = 1
        self.language = ['de']
        

    def movie(self, imdb, title, localtitle, aliases, year):
        try:            
            titles = [localtitle] + source_utils.aliases_to_array(aliases)
            result = duckduckgo.search(titles, year, 'netflix.com',  '(.*?)\|\sNetflix')
            result=re.findall('(\d+)', result)[0]
            
            return result
        except:
            return result

    def tvshow(self, imdb, tvdb, tvshowtitle, localtvshowtitle, aliases, year):        
        titles = [localtvshowtitle] + source_utils.aliases_to_array(aliases)        
        result = duckduckgo.search(titles, year, 'netflix.com',  '(.*?)\|\sNetflix')        
        tvshowid=re.findall('(\d+)', result)[0]
        #print "print NF tvshowid",tvshowid
        return tvshowid

    def episode(self, tvshowid, imdb, tvdb, title, premiered, season, episode):        
        
        url="https://www.netflix.com/api/shakti/57e85dca/metadata?movieid="+str(tvshowid)
        s = requests.Session()
        ## get netflix session cookies for api call
        data = s.get("https://www.netflix.com")
        data = s.get(url).json()
        episodeid=data['video']['seasons'][int(season)-1]['episodes'][int(episode)-1]['episodeId']
        url=str(episodeid)
        return url



    def sources(self, url, hostDict, hostprDict):
        sources = []
        
        try:
            if not url:
                return sources
            #print "print NF source url",url
            sources.append({'source': 'Account', 'quality': '1080p', 'language': 'de', 'url': 'plugin://plugin.video.netflix/?action=play_video&video_id='+url, 'info': '', 'direct': True,'local': True, 'debridonly': False})
           
            return sources
        except:
            return sources

    def resolve(self, url):
        return url


