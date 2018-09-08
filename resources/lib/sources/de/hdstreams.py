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

import json
import re
import base64

from resources.lib.modules import cfscrape
from resources.lib.modules import dom_parser
from resources.lib.modules import source_faultlog
from resources.lib.modules import source_utils
from resources.lib.modules import cleantitle
from resources.lib.modules.recaptcha import recaptcha_app


class source:
    def __init__(self):
        self.priority = 1
        self.language = ['de']
        self.domains = ['hd-streams.org']
        self.base_link = 'https://hd-streams.org/'
        self.movie_link = self.base_link + 'movies?perPage=54'
        self.movie_link = self.base_link + 'seasons?perPage=54'
        self.search = self.base_link + 'search?q=%s&movies=true&seasons=true&actors=false&didyoumean=false'
        self.scraper = cfscrape.create_scraper()
        self.recapInfo = ""

    def movie(self, imdb, title, localtitle, aliases, year):
        try:
            objects = self.__search(imdb, True)

            t = [cleantitle.get(i) for i in set(source_utils.aliases_to_array(aliases)) if i]
            t.append(cleantitle.get(title))
            t.append(cleantitle.get(localtitle))

            for i in range(1, len(objects)):
                if cleantitle.get(objects[i]['title']) in t:
                    url = objects[i]['url']
                    break

            return url
            
        except:
            return

    def tvshow(self, imdb, tvdb, tvshowtitle, localtvshowtitle, aliases, year):
        try:
            objects = self.__search(imdb, False)

            t = [cleantitle.get(i) for i in set(source_utils.aliases_to_array(aliases)) if i]
            t.append(cleantitle.get(tvshowtitle))
            t.append(cleantitle.get(localtvshowtitle))

            for i in range(1, len(objects)):
                if cleantitle.get(objects[i]['title']) in t:
                    return objects[i]['seasons']
        except:
            return

    def episode(self, url, imdb, tvdb, title, premiered, season, episode):
        try:
            if not url:
                return

            url = [i['url'] for i in url if 'season/' + season in i['url']]

            return url[0]
        except:
            return

    def sources(self, url, hostDict, hostprDict):
        sources = []
        try:
            if not url:
                return sources
            r = self.scraper.get(url).content

            links = dom_parser.parse_dom(r, "v-tabs")
            links = [i for i in links if 'alt="de"' in dom_parser.parse_dom(i, "v-tab")[0].content]
            links = dom_parser.parse_dom(links, "v-tab-item")
            links = dom_parser.parse_dom(links, "v-flex")
            links = [dom_parser.parse_dom(i, "v-btn") for i in links]
            links = [[(a.attrs["@click"], re.findall("\n(.*)", a.content)[0].strip(), i[0].content) for a in i if "@click" in a.attrs] for i in links]
            links = [item for sublist in links for item in sublist]
            links = [(re.findall("\d+", i[0]), i[1], i[2]) for i in links]
            links = [(i[0][0], i[0][1], i[1], i[2]) for i in links]

            for e, h, sName, quali in links:
                valid, hoster = source_utils.is_host_valid(sName, hostDict)
                if not valid: continue

                sources.append(
                    {'source': hoster, 'quality': quali, 'info': '|'.join([hoster, quali]),'language': 'de', 'url': (e, h, url), 'direct': False, 'debridonly': False})

            if len(sources) == 0:
                raise Exception()
            return sources
        except Exception:
            source_faultlog.logFault(__name__, source_faultlog.tagScrape, url)
            return sources

    def __getlinks(self, e, h, url, key):
            url = url + '/stream'
            # hardcoded german language
            params = {'e': e, 'h': h, 'lang': 'de', 'q': '', 'grecaptcha': key}
            r = self.scraper.get(url[:-7])
            xsrf = r.cookies.get("XSRF-TOKEN")
            csrf = dom_parser.parse_dom(r.content, "meta", attrs={"name": "csrf-token"})[0].attrs["content"]
            sHtmlContent = self.scraper.post(url, headers={'X-CSRF-TOKEN': csrf, 'XSRF-TOKEN': xsrf, 'X-Requested-With': 'XMLHttpRequest'}, data=params).content

            pattern = 'ct[^>]":[^>]"([^"]+).*?iv[^>]":[^>]"([^"]+).*?s[^>]":[^>]"([^"]+).*?e"[^>]([^}]+)'
            
            aResult = re.compile(pattern, re.DOTALL).findall(sHtmlContent)
            
            token = base64.b64encode(csrf)
           
            for ct, iv, s, e in aResult:                
                ct = re.sub(r"\\", "", ct[::-1])
                s = re.sub(r"\\", "", s)

            from resources.lib.modules import source_utils

            sUrl2 = source_utils.evp_decode(ct, token, s.decode('hex'))
            fUrl=sUrl2.replace('\/', '/').replace('"', '')       
                
            return fUrl

    def resolve(self, url):
        try:
            e, h, url = url

            recap = recaptcha_app.recaptchaApp()
            key = recap.getSolutionWithDialog(url, "6LdWQEUUAAAAAOLikUMWfs8JIJK2CAShlLzsPE9v", self.recapInfo)
            print "Recaptcha2 Key: " + key

            response = ""

            if key != "" and "skipped" not in key.lower():
                response = self.__getlinks(e, h, url, key)

            elif response == "" or "skipped" in key.lower():
                return ""

            return response
        except:
            return ""

    def __search(self, imdb, isMovieSearch):
        try:
            sHtmlContent = self.scraper.get(self.base_link).content

            pattern = '<meta name="csrf-token" content="([^"]+)">'
            string = str(sHtmlContent)
            token = re.compile(pattern, flags=re.I | re.M).findall(string)

            if len(token) == 0:
                return #No Entry found?
            # first iteration of session object to be parsed for search

            sHtmlContent = self.scraper.get(self.search % imdb, headers={'X-CSRF-TOKEN':token[0],'X-Requested-With':'XMLHttpRequest'}).text

            content = json.loads(sHtmlContent)

            if isMovieSearch:
                returnObjects = content["movies"]
            else:
                returnObjects = content["series"]

            return returnObjects
        except:
            try:
                source_faultlog.logFault(__name__, source_faultlog.tagSearch, imdb)
            except:
                return
        return

    def setRecapInfo(self, info):
        self.recapInfo = info