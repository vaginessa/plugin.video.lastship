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
from resources.lib.modules import dom_parser
from resources.lib.modules import client

def getPlaylistLinks(url):
    hdgoContent = client.request(url)
    playlistLink = dom_parser.parse_dom(hdgoContent, 'iframe')
    if len(playlistLink) > 0:
        playlistLink = playlistLink[0].attrs['src']
        playListContent = client.request('http:' + playlistLink)
        links = re.findall('\[(".*?)\]', playListContent, re.DOTALL)
        links = links[0].split(',')
        links = [i.replace('"', '').replace('\r\n','').replace('/?ref=hdgo.cc', '') for i in links]
        return [urlparse.urljoin('http://hdgo.cc', i) for i in links]
    return


def getStreams(url, sources):
    hdgostreams = getHDGOStreams(url)
    if hdgostreams is not None:
        if len(hdgostreams) > 1:
            hdgostreams.pop(0)
        quality = ["SD", "HD", "1080p", "2K", "4K"]
        for i, stream in enumerate(hdgostreams):
            sources.append({'source': 'hdgo.cc', 'quality': quality[i], 'language': 'de',
                            'url': stream + '|Referer=' + url, 'direct': True,
                            'debridonly': False})
    return sources


def getHDGOStreams(url):
    try:
        request = client.request(url, referer=url)
        request = dom_parser.parse_dom(request, 'iframe')[0].attrs['src']
        request = client.request(urlparse.urljoin('http://', request), referer=url)
        pattern = "url:[^>]'([^']+)"
        request = re.findall(pattern, request, re.DOTALL)
        return request
    except:
        return None
