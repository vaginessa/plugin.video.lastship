# -*- coding: UTF-8 -*-

"""
    Lastship Add-on (C) 2019
    Credits to Placenta and Covenant; our thanks go to their creators

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

# Addon Name: Lastship
# Addon id: plugin.video.lastship
# Addon Provider: LastShip

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


