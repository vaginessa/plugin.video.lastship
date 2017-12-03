# -*- coding: utf-8 -*-

"""
    Lastship Add-on (C) 2017
    Credits to Exodus and Covenant; our thanks go to their creators

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

import base64
import json
import re
import urllib
import urlparse
import requests


from resources.lib.modules import anilist
from resources.lib.modules import cache
from resources.lib.modules import cleantitle
from resources.lib.modules import client
from resources.lib.modules import directstream
from resources.lib.modules import dom_parser
from resources.lib.modules import jsunpack
from resources.lib.modules import source_utils
from resources.lib.modules import tvmaze

class source:
    def __init__(self):
        self.priority = 1
        self.language = ['de']
        self.domains = ['foxx.to']
        self.base_link = 'http://foxx.to'
        self.search_link = '/wp-json/dooplay/search/?keyword=%s&nonce=%s'
        
        
    def movie(self, imdb, title, localtitle, aliases, year):
        try:
            url = self.__search([localtitle] + source_utils.aliases_to_array(aliases), year)
            if not url and title != localtitle: url = self.__search([title] + source_utils.aliases_to_array(aliases), year)
            if not url and source_utils.is_anime('movie', 'imdb', imdb): url = self.__search([anilist.getAlternativTitle(title)] + source_utils.aliases_to_array(aliases), year)
            
            return url
        except:
            return

    def tvshow(self, imdb, tvdb, tvshowtitle, localtvshowtitle, aliases, year):
        try:
            url = self.__search([localtvshowtitle] + source_utils.aliases_to_array(aliases), year)
            if not url and tvshowtitle != localtvshowtitle: url = self.__search([tvshowtitle] + source_utils.aliases_to_array(aliases), year)
            if not url and source_utils.is_anime('show', 'tvdb', tvdb): url = self.__search([tvmaze.tvMaze().showLookup('thetvdb', tvdb).get('name')] + source_utils.aliases_to_array(aliases), year)
            return url
        except:
            return

    def episode(self, url, imdb, tvdb, title, premiered, season, episode):
        try:
            if not url:
                return

            url = urlparse.urljoin(self.base_link, url)
            url = client.request(url, output='geturl')

            if season == 1 and episode == 1:
                season = episode = ''

            r = client.request(url)
            r = dom_parser.parse_dom(r, 'ul', attrs={'class': 'episodios'})
            r = dom_parser.parse_dom(r, 'a', attrs={'href': re.compile('[^\'"]*%s' % ('-%sx%s' % (season, episode)))})[0].attrs['href']
            return source_utils.strip_domain(r)
        except:
            return

    def sources(self, url, hostDict, hostprDict):
        sources = []
        try:
            if not url:
                return sources

            url = urlparse.urljoin(self.base_link, url)            
            r = client.request(url, output='extended')
            regex= ur'iframe src="(.+?)"+?'
            url_iframe=re.findall(regex,r[0])
            r = client.request(url_iframe[0], output='extended')
            headers = r[3]
            headers.update({'Cookie': r[2].get('Set-Cookie'), 'Referer': self.base_link})
            r = r[0]     
            links=re.findall('''(?:link|file)["']?\s*:\s*["'](.+?)["']''', r) 
            url2redirect=links[3]            
            final_url_redirected = requests.get(url2redirect,headers=headers, allow_redirects=False)
            url = final_url_redirected.headers['Location']
            # quick&dirty fix Nov2017 - sources.py had to be changed to make this compatible    
            sources.append({'source': 'CDN', 'quality': '1080p', 'language': 'de', 'url':url+'|%s' % urllib.urlencode(headers) , 'direct': True, 'debridonly': False})
            
            return sources
        except:
            return sources

    def resolve(self, url):
        return url

    def __search(self, titles, year):
        try:
            n = cache.get(self.__get_nonce, 24)

            query = self.search_link % (urllib.quote_plus(cleantitle.query(titles[0])), n)
            query = urlparse.urljoin(self.base_link, query)

            t = [cleantitle.get(i) for i in set(titles) if i]
            y = ['%s' % str(year), '%s' % str(int(year) + 1), '%s' % str(int(year) - 1), '0']

            r = client.request(query)
            r = json.loads(r)
            r = [(r[i].get('url'), r[i].get('title'), r[i].get('extra').get('date')) for i in r]
            r = sorted(r, key=lambda i: int(i[2]), reverse=True)  # with year > no year
            r = [i[0] for i in r if cleantitle.get(i[1]) in t and i[2] in y][0]

            return source_utils.strip_domain(r)
        except:
            return

    def __get_nonce(self):
        n = client.request(self.base_link)
        try: n = re.findall('nonce"?\s*:\s*"?([0-9a-zA-Z]+)', n)[0]
        except: n = '5d12d0fa54'
        return n
