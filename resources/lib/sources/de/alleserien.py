# -*- coding: utf-8 -*-


"""
    Lastship Add-on (C) 2018
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
import urlparse

from resources.lib.modules import cleantitle
from resources.lib.modules import cfscrape
from resources.lib.modules import dom_parser
from resources.lib.modules import source_faultlog
from resources.lib.modules import source_utils


class source:
    def __init__(self):
        self.priority = 1
        self.language = ['de']
        self.domains = ['alleserien.com']
        self.base_link = 'http://alleserien.com'
        self.search_link = '/filme'
        self.link_url = '/getpart'
        self.link_url_movie = '/film-getpart'
        self.scraper = cfscrape.create_scraper()

    def movie(self, imdb, title, localtitle, aliases, year):
        try:
            url = self.__search([localtitle] + source_utils.aliases_to_array(aliases), True)
            if not url and title != localtitle: url = self.__search([title] + source_utils.aliases_to_array(aliases), True)
            return url
        except:
            return ""

    def tvshow(self, imdb, tvdb, tvshowtitle, localtvshowtitle, aliases, year):
        try:
            url = self.__search([localtvshowtitle] + source_utils.aliases_to_array(aliases))
            if not url and tvshowtitle != localtvshowtitle: url = self.__search(
                [tvshowtitle] + source_utils.aliases_to_array(aliases))
            return url
        except:
            return

    def episode(self, url, imdb, tvdb, title, premiered, season, episode):
        try:
            if not url:
                return
            url = urlparse.urljoin(self.base_link, url)

            r = self.scraper.get(url).content

            def getLinks(content, searchSeason=False):
                links = dom_parser.parse_dom(content, 'div', attrs={'class': 'hosterSiteDirectNav'})
                links = dom_parser.parse_dom(links, 'a')
                if searchSeason:
                    return [i.attrs['href'] for i in links if i.attrs['title'].lower() == 'staffel %s' % season]
                else:
                    return [i.attrs['href'] for i in links if
                            i.attrs['title'].lower().strip() == 'staffel %s folge %s' % (season, episode)]

            seasonLinks = getLinks(r, True)

            if len(seasonLinks) > 0:
                r = self.scraper.get(seasonLinks[0]).content
                episodeLink = getLinks(r)
                if len(episodeLink) > 0:
                    return source_utils.strip_domain(episodeLink[0])

            return
        except:
            return

    def sources(self, url, hostDict, hostprDict):
        sources = []
        try:
            if not url:
                return sources
            url = urlparse.urljoin(self.base_link, url)
            content = self.scraper.get(url).content

            links = dom_parser.parse_dom(content, 'a', attrs={'class': 'PartChange'})
            links = [(i.attrs['data-id'], i.attrs['data-controlid'], dom_parser.parse_dom(i, 'h4')[0].content) for i in
                     links if 'data-id' in i[0]]

            temp = [i for i in links if i[2].lower() == 'vip']
            for id, controlId, host in temp:
                link = self.resolve((url, id, controlId, 'film' in url))
                import json
                params = {
                    'Referer': url,
                    'Host': 'www.alleserienplayer.com',
                    'Upgrade-Insecure-Requests': '1'
                }

                result = self.scraper.get(link, headers=params).content
                result = re.findall('sources:\s(.*?])', result, flags=re.S)[0]
                result = json.loads(result)
                [sources.append({'source': 'CDN', 'quality': source_utils.label_to_quality(i['label']), 'language': 'de', 'url': i['file'],
                                'direct': True, 'debridonly': False, 'checkquality': False}) for i in result]

            for id, controlId, hoster in links:
                valid, hoster = source_utils.is_host_valid(hoster, hostDict)
                if not valid: continue

                sources.append({'source': hoster, 'quality': 'SD', 'language': 'de', 'url': (url, id, controlId, 'film' in url),
                                'direct': False, 'debridonly': False, 'checkquality': False})

            return sources
        except:
            source_faultlog.logFault(__name__, source_faultlog.tagScrape)
            return sources

    def resolve(self, url):
        try:
            if 'google' in url:
                return url
            url, id, controlId, movieSearch = url

            content = self.scraper.get(url).content
            token = re.findall("_token':'(.*?)'", content)[0]

            params = {
                '_token': token,
                'PartID': id,
                'ControlID': controlId
            }

            link = urlparse.urljoin(self.base_link, self.link_url_movie if movieSearch else self.link_url)
            result = self.scraper.post(link, data=params).content
            if 'false' in result:
                return
            else:
                return dom_parser.parse_dom(result, 'iframe')[0].attrs['src']
        except:
            source_faultlog.logFault(__name__, source_faultlog.tagResolve)
            return

    def __search(self, titles, movieSearch = False):
        try:
            t = [cleantitle.get(i) for i in set(titles) if i]

            query = urlparse.urljoin(self.base_link, self.search_link if movieSearch else '/')

            content = self.scraper.get(query).content

            seriesList = dom_parser.parse_dom(content, 'div', attrs={'class': 'seriesList'})
            seriesList = dom_parser.parse_dom(seriesList, 'a')
            seriesList = [(i.content, i.attrs['href']) for i in seriesList]

            seriesList = [i for i in seriesList if any(a in cleantitle.get(i[0]) for a in t)]

            if len(seriesList) > 0:
                return seriesList[0][1]

            return


        except:
            try:
                source_faultlog.logFault(__name__, source_faultlog.tagSearch, titles[0])
            except:
                return
            return ""