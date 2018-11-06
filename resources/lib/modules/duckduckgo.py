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

from resources.lib.modules import client
from resources.lib.modules import dom_parser
from resources.lib.modules import cleantitle
from resources.lib.modules import source_faultlog
from resources.lib.modules import source_utils
import re

base_url = 'https://duckduckgo.com/html'

def cleanhtml(raw_html):
  cleanr = re.compile('<.*?>')
  cleantext = re.sub(cleanr, '', raw_html)
  return cleantext


def search(titles, year, site, titleRegex):
    try:
        params = {
            'q': '%s site:%s' % (titles[0], site),
            's': '0'
        }

        result = client.request(base_url, post=params, headers={'Content-Type': 'application/x-www-form-urlencoded'}, error=True)
        if cleantitle.get(params['q'].lower()) in cleantitle.get(result.lower()):
            links = dom_parser.parse_dom(result, 'h2', attrs={'class': 'result__title'})
            links = dom_parser.parse_dom(links, 'a')
            links = [(client.replaceHTMLCodes(i.content), i.attrs['href']) for i in links if site in i.attrs['href']]

            links = [(re.findall(titleRegex, i[0])[0], i[1]) for i in links if re.search(titleRegex, i[0]) is not None]
            links = [(cleanhtml(i[0]), i[1], year in i[1]) for i in links]

            links = sorted(links, key=lambda i: i[2], reverse=True)  # with year > no year

            t = [cleantitle.get(i) for i in set(titles) if i]

            links = [i[1] for i in links if cleantitle.get(i[0]) in t]

            if len(links) > 0:
                return source_utils.strip_domain(links[0])

        return
    except:
        source_faultlog.logFault(site, source_faultlog.tagSearch, titles[0] + '&' + site)
