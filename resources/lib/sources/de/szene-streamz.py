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

import urlparse
import re
import requests

from resources.lib.modules import cache
from resources.lib.modules import cleantitle
from resources.lib.modules import client
from resources.lib.modules import dom_parser
from resources.lib.modules import source_utils
from resources.lib.modules import source_faultlog


class source:
    def __init__(self):
        self.priority = 1
        self.language = ['de']
        self.domains = ['szene-streamz.com']
        self.base_link = 'http://www.szene-streamz.com'
        self.search_link = self.base_link + '/publ/'

    def movie(self, imdb, title, localtitle, aliases):
        try:
            return self.__search([localtitle, title] + source_utils.aliases_to_array(aliases))
        except:
            return

    def sources(self, url, hostDict, hostprDict):
        sources = []
        try:
            if not url:
                return sources

            content = cache.get(client.request, 4, urlparse.urljoin(self.base_link, url))

            hoster = re.findall('blank"[^>]*href="([^"]+)">', content)

            for link in hoster:
                link = link.strip()
                quali, info = source_utils.get_release_quality(link)

                valid, hoster = source_utils.is_host_valid(link, hostDict)
                if not valid: continue

                sources.append({'source': hoster, 'quality': quali, 'language': 'de', 'info': info, 'url': link, 'direct': False, 'debridonly': False, 'checkquality': True})

            return sources
        except:
            source_faultlog.logFault(__name__, source_faultlog.tagScrape, url)
            return sources

    def resolve(self, url):
        return url

    def __search(self, titles):
        try:
            t = [cleantitle.get(i) for i in set(titles) if i]
            for title in titles:
                params = {'a': '2', 'query': title}
                content = cache.get(client.request, 4, self.search_link, post=params)

                if content is not None and "noEntry" not in content:
                    content = content.replace('entryLink" <a=""', 'entryLink"')

                    entryLinks = dom_parser.parse_dom(content, 'a', attrs={"class": "entryLink"})
                    if len(entryLinks) == 0: continue
                    links = [link.attrs['href'] for link in entryLinks if cleantitle.get(link.content) in t]

                    if len(links) > 0:
                        return source_utils.strip_domain(links[0])
            return
        except:
            try:
                source_faultlog.logFault(__name__, source_faultlog.tagSearch, titles[0])
            except:
                return
            return
