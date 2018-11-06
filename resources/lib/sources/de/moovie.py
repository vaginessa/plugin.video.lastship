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

import base64
import json
import requests

from resources.lib.modules import source_utils


class source:
    def __init__(self):
        self.priority = 1
        self.language = ['de']
        self.domains = ['']
        self.base_link = base64.b64decode('aHR0cHM6Ly92amFja3Nvbi5pbmZvLw==')
        self.search_link = '/movie-search?key=%s'
        self.get_link = '/movie/getlink/%s/%s'

    def movie(self, imdb, title, localtitle, aliases, year):
        try:

            query = self.base_link + "all?type=movie&query=" + title
            response = requests.Session().get(query)
            content = json.loads(response.text)

            d = {}
            for data in content:
                d[data["imdb"]] = data["id"]
                print(d)

            for key, value in d.iteritems():
                if key == imdb:
                    jid = str(value)

            query = self.base_link + "get?locale=de&hosters=!tata.to,!hdfilme.tv,!1fichier.com,!share-online.biz,!uploadrocket.net,!oboom.com,!rockfile.eu,!kinoger.com,!uptobox.com&resolutions=hd&language=de&id=" + jid

            response = requests.Session().get(query)

            content = response.json()

            array = content['get']['links']

            linklist = dict()
            for idx, word in enumerate(array):
                link = self.base_link + "link?hoster=" + (word['hoster']) + "&language=de&resolution=" + word['resolution'] + "&id=" + jid + "&parts=1" + "&quality=" + str(word['quality']) + "&subtitles="
                # link=self.base_link+"link?hoster="+(word['hoster'])+"&language=de&resolution=hd&id="+jid+"&parts=1"+"&quality="+str(word['quality'])+"&subtitles="+"&season="+season+"&episode="+episode
                linklist[link] = word['resolution']

            urllist = dict()
            for items, quality in linklist.iteritems():

                response = requests.Session().get(items)

                try:
                    content = response.json()

                    dict1 = content['parts']
                    link = dict1['1']

                    urllist[link] = quality

                except:
                    print "print exception"
                    # print "print linklist", urllist
            url = urllist

            return url
        except:
            return

    def tvshow(self, imdb, tvdb, tvshowtitle, localtvshowtitle, aliases, year):
        return tvshowtitle

    def episode(self, tvshowtitle, imdb, tvdb, title, premiered, season, episode):
        try:

            query = self.base_link + "all?type=serie&query=" + tvshowtitle
            response = requests.Session().get(query)
            content = json.loads(response.text)

            d = {}
            for data in content:
                d[data["imdb"]] = data["id"]

            for key, value in d.iteritems():
                if key == imdb:
                    jid = str(value)

            query = self.base_link + "get?locale=de&hosters=!tata.to,!hdfilme.tv,!1fichier.com,!share-online.biz,!uploadrocket.net,!oboom.com,!rockfile.eu,!kinoger.com&resolutions=all&language=de&id=" + jid + "&season=" + season + "&episode=" + episode

            response = requests.Session().get(query)

            content = response.json()

            array = content['get']['links']

            linklist = dict()
            for idx, word in enumerate(array):
                # enable resolution to retrieve all possible links, however quality checkmissing
                link = self.base_link + "link?hoster=" + (word['hoster']) + "&language=de&resolution=" + word['resolution'] + "&id=" + jid + "&parts=1" + "&quality=" + str(word['quality']) + "&subtitles=" + "&season=" + season + "&episode=" + episode
                # link=self.base_link+"link?hoster="+(word['hoster'])+"&language=de&resolution=hd&id="+jid+"&parts=1"+"&quality="+str(word['quality'])+"&subtitles="+"&season="+season+"&episode="+episode
                linklist[link] = word['resolution']

            urllist = dict()
            for items, quality in linklist.iteritems():

                response = requests.Session().get(items)

                try:
                    content = response.json()

                    dict1 = content['parts']
                    link = dict1['1']

                    urllist[link] = quality

                except:
                    print "print moovie exception"
                    # print "print linklist", urllist
            url = urllist

            return url
        except:
            return

    def sources(self, url, hostDict, hostprDict):
        sources = []

        try:
            if not url:
                return sources

            for items, quality in url.iteritems():
                if "clip" in items:
                    sources.append({'source': "clipboard.cc", 'quality': quality.upper(), 'language': 'de', 'url': items, 'direct': True, 'debridonly': False})

                valid, host = source_utils.is_host_valid(items, hostDict)
                if not valid: continue

                #print "print vavoo items", type(items), items
                if "original" in quality:
                    quality = "SD"
                sources.append({'source': host, 'quality': quality.upper(), 'language': 'de', 'url': items, 'direct': False, 'debridonly': False, 'checkquality': True})

            return sources
        except:
            return sources

    def resolve(self, url):
        return url
