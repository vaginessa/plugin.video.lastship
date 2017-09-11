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

import re
import urllib
import urlparse

from resources.lib.modules import cleantitle
from resources.lib.modules import client
from resources.lib.modules import source_utils
from resources.lib.modules import dom_parser


class source:
    def __init__(self):
        self.priority = 1
        self.language = ['de']
        self.domains = ['movie2k.ac']
        self.base_link = 'http://www.movie2k.ac'
        self.search_link = '/search/%s'

    def movie(self, imdb, title, localtitle, aliases, year):
        try:
            url = self.__search([localtitle] + source_utils.aliases_to_array(aliases))
            if not url and title != localtitle: url = self.__search([title] + source_utils.aliases_to_array(aliases))
            return url
        except:
            return

    def sources(self, url, hostDict, hostprDict):
        sources = []

        try:
            if not url:
                return sources

            query = urlparse.urljoin(self.base_link, url)
            r = client.request(query)

            r = dom_parser.parse_dom(r, 'div', attrs={'id': 'tab-plot_german'})
            r = dom_parser.parse_dom(r, 'tbody')
            r = dom_parser.parse_dom(r, 'tr')

            for i in r:
                if re.search('(?<=">)(\n.*?)(?=<\/a>)', i[1]).group().strip():
                    hoster = re.search('(?<=">)(\n.*?)(?=<\/a>)', i[1]).group().strip()
                    link = re.search('(?<=href=\")(.*?)(?=\")', i[1]).group()
                    rel = re.search('(?<=oddCell qualityCell">)(\n.*?)(?=<\/td>)', i[1]).group().strip()

                    valid, hoster = source_utils.is_host_valid(hoster, hostDict)
                    if not valid: continue

                    try:
                        quality, info = source_utils.get_release_quality(rel)
                    except:
                        quality = 'SD'
                    
                    sources.append({'source': hoster, 'quality': quality, 'language': 'de', 'url': link, 'direct': False, 'debridonly': False, 'checkquality': True})

            return sources
        except:
            return sources

    def resolve(self, url):
        return url

    def __search(self, titles):
        try:
            query = self.search_link % (urllib.quote_plus(urllib.quote_plus(cleantitle.query(titles[0]))))
            query = urlparse.urljoin(self.base_link, query)

            t = [cleantitle.get(i) for i in set(titles) if i]

            r = client.request(query)

            r = dom_parser.parse_dom(r, 'ul', attrs={'class': 'coverBox'})
            r = dom_parser.parse_dom(r, 'li')
            r = dom_parser.parse_dom(r, 'span', attrs={'class': 'name'})
            r = dom_parser.parse_dom(r, 'a')

            for i in r:
                title = i[1]
                title = cleantitle.get(title)
                if title in t:
                    return source_utils.strip_domain(i[0]['href'])
                else:
                    return
        except:
            return
