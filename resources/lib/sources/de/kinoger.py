# -*- coding: utf-8 -*-

import urllib
import urlparse
import re

from resources.lib.modules import cfscrape
from resources.lib.modules import dom_parser
from resources.lib.modules import source_utils
from resources.lib.modules import cleantitle
from resources.lib.modules import source_faultlog
from resources.lib.modules import hdgo


class source:
    def __init__(self):
        self.priority = 1
        self.language = ['de']
        self.domains = ['kinoger.com']
        self.base_link = 'http://kinoger.com/'
        self.search = self.base_link + 'index.php?do=search&subaction=search&search_start=1&full_search=0&result_from=1&story=%s'
        self.scraper = cfscrape.create_scraper()

    def movie(self, imdb, title, localtitle, aliases, year):
        try:
            url = self.__search([localtitle] + source_utils.aliases_to_array(aliases), year)

            if not url and title != localtitle:
                url = self.__search([title] + source_utils.aliases_to_array(aliases), year)
            return urllib.urlencode({'url': url, 'imdb': re.sub('[^0-9]', '', imdb)}) if url else None
            
        except:
            return

    def tvshow(self, imdb, tvdb, tvshowtitle, localtvshowtitle, aliases, year):
        try:
            url = self.__search([localtvshowtitle] + source_utils.aliases_to_array(aliases), year)
            if not url and tvshowtitle != localtvshowtitle:
                url = self.__search([tvshowtitle] + source_utils.aliases_to_array(aliases), year)
            return urllib.urlencode({'url': url, 'imdb': re.sub('[^0-9]', '', imdb)}) if url else None
        except:
            return

    def episode(self, url, imdb, tvdb, title, premiered, season, episode):
        try:
            if not url:
                return

            data = urlparse.parse_qs(url)
            data = dict([(i, data[i][0]) if data[i] else (i, '') for i in data])
            if not data["url"]:
                return
            data.update({'season': season, 'episode': episode})
            return urllib.urlencode(data)
        except:
            return

    def sources(self, url, hostDict, hostprDict):
        sources = []
        try:
            if not url:
                return sources

            data = urlparse.parse_qs(url)
            data = dict([(i, data[i][0]) if data[i] else (i, '') for i in data])
            url = urlparse.urljoin(self.base_link, data.get('url', ''))
            season = data.get('season')
            episode = data.get('episode')

            sHtmlContent=self.scraper.get(url).content

            quality = "SD"

            # do we have multiple hoster?
            # i.e. http://kinoger.com/stream/1911-bloodrayne-2-deliverance-2007.html
            link_containers = dom_parser.parse_dom(sHtmlContent,"section")
            if len(link_containers) == 0: #only one, i.e. http://kinoger.com/stream/890-lucy-2014.html
                #only one
                link_containers = dom_parser.parse_dom(sHtmlContent,"div",attrs={"id":"container-video"})

            for container in link_containers:
                #3 different types found till now: hdgo.show, namba.show and direct (mail.ru etc.)
                # i.e. http://kinoger.com/stream/1911-bloodrayne-2-deliverance-2007.html

                if ".show" in container.content:
                    pattern = ',\[\[(.*?)\]\]'
                    links = re.compile(pattern, re.DOTALL).findall(container.content)
                    if len(links) == 0: continue;
                    #split them up to get season and episode
                    season_array = links[0].split("],[")

                    source_link = None
                    if season and episode:
                        if len(season_array) < int(season):
                            continue
                        episode_array = season_array[int(season)-1].split(",")
                        if len(episode_array) < int(episode):
                            continue
                        source_link = episode_array[int(episode)-1]
                    elif len(season_array) == 1:
                        source_link = season_array[0]

                    if source_link:
                        source_link = source_link.strip("'")
                        if "hdgo" in container.content:
                            sources = hdgo.getStreams(source_link, sources)

                        elif "namba" in container.content:
                            sources.append({'source': 'kinoger.com', 'quality': quality, 'language': 'de', 'url': "http://v1.kinoger.pw/vod/"+source_link, 'direct': False,
                                    'debridonly': False, 'checkquality': True})

                elif "iframe" in container.content:
                    frame = dom_parser.parse_dom(container.content, "iframe")
                    if len(frame) == 0:
                        continue
                    if 'hdgo' in frame[0].attrs["src"]:
                        sources = hdgo.getStreams(frame[0].attrs["src"], sources)

                    else:
                        valid, host = source_utils.is_host_valid(frame[0].attrs["src"], hostDict)
                        if not valid: continue

                        sources.append({'source': host, 'quality': quality, 'language': 'de', 'url': frame[0].attrs["src"], 'direct': False,
                                        'debridonly': False, 'checkquality': True})

                else:
                    continue
                    
            return sources
        except:
            source_faultlog.logFault(__name__, source_faultlog.tagScrape)
            return sources


    def resolve(self, url):
        try:
            if 'kinoger' in url:
                request = self.scraper.get(url).content
                pattern = 'src:  "(.*?)"'
                request = re.compile(pattern, re.DOTALL).findall(request)
                return request[0] + '|Referer=' + url
            return url
        except:
            source_faultlog.logFault(__name__, source_faultlog.tagResolve)
            return url

    def __search(self, titles, year):
        try:
            t = [cleantitle.get(i) for i in set(titles) if i]
            url = self.search % titles[0]

            sHtmlContent = self.scraper.get(url).content
            search_results = dom_parser.parse_dom(sHtmlContent, 'div', attrs={'class': 'title'})
            search_results = dom_parser.parse_dom(search_results, 'a')
            search_results = [(i.attrs['href'], i.content) for i in search_results]
            search_results = [(i[0], re.findall('(.*?)\((\d+)', i[1])[0]) for i in search_results]
            search_results = [i[0] for i in search_results if cleantitle.get(i[1][0]) in t and i[1][1] in year]
                
            if len(search_results) > 0:
                return source_utils.strip_domain(search_results[0])
            return
        except:
            try:
                source_faultlog.logFault(__name__, source_faultlog.tagSearch, localtitle)
            except:
                return
            return
