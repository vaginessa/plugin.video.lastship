# -*- coding: utf-8 -*-

import urllib
import urlparse
import re

from resources.lib.modules import client
from resources.lib.modules import dom_parser
from resources.lib.modules import source_utils
from resources.lib.modules import cleantitle
from resources.lib.modules import source_faultlog
from resources.lib.modules import hdgo


class source:
    def __init__(self):
        self.priority = 1
        self.language = ['de']
        self.domains = ['cinemaxx.cc']
        self.base_link = 'http://cinemaxx.cc/'

    def movie(self, imdb, title, localtitle, aliases, year):
        try:
            url = self.__search([localtitle] + source_utils.aliases_to_array(aliases))
            if not url and title != localtitle: url = self.__search([title] + source_utils.aliases_to_array(aliases))
            return url
        except:
            return

    def tvshow(self, imdb, tvdb, tvshowtitle, localtvshowtitle, aliases, year):
        try:
            url = self.__search([localtvshowtitle] + source_utils.aliases_to_array(aliases))
            if not url and tvshowtitle != localtvshowtitle:
                url = self.__search([tvshowtitle] + source_utils.aliases_to_array(aliases))

            return url
        except:
            return

    def episode(self, url, imdb, tvdb, title, premiered, season, episode):
        try:
            if not url:
                return
            return [season, episode, url]
        except:
            return

    def sources(self, url, hostDict, hostprDict):
        sources = []
        try:
            if not url:
                return sources
            episode = None
            season = None
            if isinstance(url, list):
                season, episode, url = url
            url = urlparse.urljoin(self.base_link, url)
            
            content = client.request(url)
            link = dom_parser.parse_dom(content, 'div', attrs={'id': 'full-video'})
            if season:
                link = re.findall("vk.show\(\d+,(.*?)\)", link[0].content)[0]
                link = re.findall("\[(.*?)\]", link)[int(season)-1]
                link = re.findall("'(.*?)'", link)
                sources = hdgo.getStreams(link[int(episode)-1], sources)
            else:
                link = dom_parser.parse_dom(link, 'iframe')
                sources = hdgo.getStreams(link[0].attrs['src'], sources)

            if len(sources) == 0:
                raise Exception()
            return sources
        except:
            source_faultlog.logFault(__name__, source_faultlog.tagScrape, url)
            return sources


    def resolve(self, url):
        try:
            return url
        except:
            source_faultlog.logFault(__name__, source_faultlog.tagResolve)
            return url

    def __search(self, titles):
        try:
            t = [cleantitle.get(i) for i in set(titles) if i]

            for title in titles:
                params = {
                    'do': 'search',
                    'subaction': 'search',
                    'story': title
                }

                result = client.request(self.base_link, post=params, headers={'Content-Type': 'application/x-www-form-urlencoded'}, error=True)

                links = dom_parser.parse_dom(result, 'div', attrs={'class': 'shortstory-in'})
                links = [dom_parser.parse_dom(i, 'a')[0] for i in links]
                links = [(i.attrs['href'], i.attrs['title']) for i in links]
                links = [i[0] for i in links if any(a in cleantitle.get(i[1]) for a in t)]

                if len(links) > 0:
                    return source_utils.strip_domain(links[0])
            return
        except:
            try:
                source_faultlog.logFault(__name__, source_faultlog.tagSearch, titles[0])
            except:
                return
            return
