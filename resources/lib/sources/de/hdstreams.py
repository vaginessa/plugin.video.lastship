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
from binascii import unhexlify
from hashlib import md5
from resources.lib.modules import pyaes, utils

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
                    {'source': hoster, 'quality': quali, 'language': 'de', 'url': (e, h, url), 'direct': False, 'debridonly': False, 'captcha': True})

            if len(sources) == 0:
                raise Exception()
            return sources
        except Exception:
            source_faultlog.logFault(__name__, source_faultlog.tagScrape, url)
            return sources

    def cryptoJS_AES_decrypt(self, encrypted, password, salt):
        def derive_key_and_iv(password, salt, key_length, iv_length):
            d = d_i = ''
            while len(d) < key_length + iv_length:
                d_i = md5(d_i + password + salt).digest()
                d += d_i
            return d[:key_length], d[key_length:key_length + iv_length]

        key, iv = derive_key_and_iv(password, salt, 32, 16)
        cipher = pyaes.AESModeOfOperationCBC(key=key, iv=iv)
        decrypted_data = ""
        for part in [encrypted[i:i+16] for i in range(0, len(encrypted), 16)]:
            decrypted_data += cipher.decrypt(part)

        return decrypted_data[0:-ord(decrypted_data[-1])]

    def __getlinks(self, e, h, url, key):
        try:
            url = url + '/stream'

            params = {'e': e, 'h': h, 'lang': 'de', 'q': '', 'grecaptcha': key}
            r = self.scraper.get(url[:-7])
            csrf = dom_parser.parse_dom(r.content, "meta", attrs={"name": "csrf-token"})[0].attrs["content"]
            sHtmlContent = self.scraper.post(url, headers={'X-CSRF-TOKEN': csrf, 'X-Requested-With': 'XMLHttpRequest'}, data=params).content

            helper = json.loads(sHtmlContent)

            mainData = utils.byteify(helper)

            tmp = mainData.get('d', '') + mainData.get('c', '') + mainData.get('iv', '') + mainData.get('f','') + mainData.get('h', '') + mainData.get('b', '')

            tmp = utils.byteify(json.loads(base64.b64decode(tmp)))

            salt = unhexlify(tmp['s'])
            ciphertext = base64.b64decode(tmp['ct'][::-1])
            b = base64.b64encode(csrf[::-1])

            tmp = self.cryptoJS_AES_decrypt(ciphertext, b, salt)

            tmp = utils.byteify(json.loads(base64.b64decode(tmp)))
            ciphertext = base64.b64decode(tmp['ct'][::-1])
            salt = unhexlify(tmp['s'])
            b = ''
            a = csrf
            for idx in range(len(a) - 1, 0, -2):
                b += a[idx]
            if mainData.get('e', None):
                b += '1'
            else:
                b += '0'
            tmp = self.cryptoJS_AES_decrypt(ciphertext, str(b), salt)

            return utils.byteify(json.loads(tmp))
        except Exception:
            return

    def resolve(self, url):
        try:
            e, h, url = url
            return self.__getlinks(e, h, url, '')
        except:
            return

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
